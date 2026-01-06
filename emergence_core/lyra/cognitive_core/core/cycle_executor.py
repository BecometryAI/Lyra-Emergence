"""
Cognitive cycle executor.

Executes the 9-step cognitive cycle including perception, attention,
memory, affect, action, meta-cognition, and workspace updates.
"""

from __future__ import annotations

import time
import logging
from typing import TYPE_CHECKING, Dict, Any, Optional
from datetime import datetime

from ..workspace import GoalType, Percept
from ..action import ActionType

if TYPE_CHECKING:
    from .subsystem_coordinator import SubsystemCoordinator
    from .state_manager import StateManager

logger = logging.getLogger(__name__)


class CycleExecutor:
    """
    Executes the complete 9-step cognitive cycle.
    
    The cognitive cycle follows these steps:
    1. PERCEPTION: Gather new inputs (if any queued)
    2. MEMORY RETRIEVAL: Check for memory retrieval goals and fetch relevant memories
    3. ATTENTION: Select percepts (including memory-percepts) for workspace
    4. AFFECT UPDATE: Compute emotional dynamics
    5. ACTION SELECTION: Decide what to do
    6. META-COGNITION: Generate introspective percepts
    7. AUTONOMOUS INITIATION: Check for autonomous speech triggers
    8. WORKSPACE UPDATE: Integrate all subsystem outputs
    9. MEMORY CONSOLIDATION: Store significant states to long-term memory
    """
    
    def __init__(self, subsystems: 'SubsystemCoordinator', state: 'StateManager'):
        """
        Initialize cycle executor.
        
        Args:
            subsystems: SubsystemCoordinator instance
            state: StateManager instance
        """
        self.subsystems = subsystems
        self.state = state
    
    async def execute_cycle(self) -> Dict[str, float]:
        """
        Execute one complete cognitive cycle.
        
        Returns:
            Dict of subsystem timings in milliseconds
        """
        subsystem_timings = {}
        
        # 1. PERCEPTION: Process queued inputs
        step_start = time.time()
        new_percepts = await self.state.gather_percepts(self.subsystems.perception)
        subsystem_timings['perception'] = (time.time() - step_start) * 1000
        
        # 2. MEMORY RETRIEVAL: Check for memory retrieval goals
        step_start = time.time()
        new_percepts.extend(await self._retrieve_memories())
        subsystem_timings['memory_retrieval'] = (time.time() - step_start) * 1000
        
        # 3. ATTENTION: Select for conscious awareness
        step_start = time.time()
        attended = self.subsystems.attention.select_for_broadcast(new_percepts)
        subsystem_timings['attention'] = (time.time() - step_start) * 1000
        
        # 4. AFFECT: Update emotional state
        step_start = time.time()
        affect_update = self.subsystems.affect.compute_update(self.state.workspace.broadcast())
        subsystem_timings['affect'] = (time.time() - step_start) * 1000
        
        # 5. ACTION: Decide what to do and execute
        step_start = time.time()
        await self._execute_actions()
        subsystem_timings['action'] = (time.time() - step_start) * 1000
        
        # 6. META-COGNITION: Introspect
        step_start = time.time()
        meta_percepts = await self._run_meta_cognition()
        subsystem_timings['meta_cognition'] = (time.time() - step_start) * 1000
        
        # 7. AUTONOMOUS INITIATION: Check for autonomous speech triggers
        step_start = time.time()
        await self._check_autonomous_triggers()
        subsystem_timings['autonomous_initiation'] = (time.time() - step_start) * 1000
        
        # 8. WORKSPACE UPDATE: Integrate everything
        step_start = time.time()
        self._update_workspace(attended, affect_update, meta_percepts)
        subsystem_timings['workspace_update'] = (time.time() - step_start) * 1000
        
        # 9. MEMORY CONSOLIDATION: Commit workspace to long-term memory
        step_start = time.time()
        await self.subsystems.memory.consolidate(self.state.workspace.broadcast())
        subsystem_timings['memory_consolidation'] = (time.time() - step_start) * 1000
        
        return subsystem_timings
    
    async def _retrieve_memories(self) -> list:
        """
        Retrieve memories if there are memory retrieval goals.
        
        Returns:
            List of memory percepts
        """
        snapshot = self.state.workspace.broadcast()
        retrieve_goals = [
            g for g in snapshot.goals
            if g.type == GoalType.RETRIEVE_MEMORY
        ]
        
        if retrieve_goals:
            # Retrieve memories and add as percepts (fast_mode for performance)
            return await self.subsystems.memory.retrieve_for_workspace(
                snapshot, 
                fast_mode=True,
                timeout=0.05
            )
        return []
    
    async def _execute_actions(self) -> None:
        """Decide on actions and execute them."""
        snapshot = self.state.workspace.broadcast()
        actions = self.subsystems.action.decide(snapshot)
        
        # Record prediction before action execution (Phase 4.3)
        prediction_id = None
        if self.subsystems.meta_cognition and actions:
            prediction_id = self._record_action_prediction(snapshot, actions)
        
        # Execute immediate actions
        for action in actions:
            # Check if this is a tool call and handle specially
            if action.type == ActionType.TOOL_CALL:
                tool_percept = await self._execute_tool_action(action)
                if tool_percept:
                    self.state.add_pending_tool_percept(tool_percept)
            else:
                await self._execute_action(action)
            
            # Extract action outcome for self-model update
            actual_outcome = self._extract_action_outcome(action)
            
            # Update self-model based on action execution
            self.subsystems.meta_cognition.update_self_model(snapshot, actual_outcome)
            
            # Validate prediction after action execution (Phase 4.3)
            if prediction_id and actual_outcome:
                self._validate_action_prediction(prediction_id, action, actual_outcome)
    
    def _record_action_prediction(self, snapshot, actions) -> Optional[str]:
        """Record prediction about action outcome."""
        # Make prediction about action outcome
        predicted_outcome = self.subsystems.meta_cognition.predict_behavior(snapshot)
        
        # Record prediction for later validation
        if predicted_outcome and predicted_outcome.get("likely_actions"):
            return self.subsystems.meta_cognition.record_prediction(
                category="action",
                predicted_state={
                    "action": str(actions[0].type) if actions else "no_action",
                    "predicted_outcome": predicted_outcome
                },
                confidence=predicted_outcome.get("confidence", 0.5),
                context={
                    "cycle": self.state.workspace.cycle_count if hasattr(self.state.workspace, 'cycle_count') else 0,
                    "goal_count": len(snapshot.goals),
                    "emotion_valence": snapshot.emotions.get("valence", 0.0)
                }
            )
        return None
    
    def _validate_action_prediction(self, prediction_id: str, action, actual_outcome: Dict) -> None:
        """Validate prediction after action execution."""
        validated = self.subsystems.meta_cognition.validate_prediction(
            prediction_id,
            actual_state={
                "action": str(action.type),
                "result": actual_outcome
            }
        )
        
        # Trigger self-model refinement if error detected
        if validated and not validated.correct and validated.error_magnitude > self.subsystems.meta_cognition.refinement_threshold:
            self.subsystems.meta_cognition.refine_self_model_from_errors([validated])
    
    async def _execute_action(self, action) -> None:
        """Execute a single action."""
        try:
            if action.type == ActionType.SPEAK:
                await self._execute_speak_action(action)
            elif action.type == ActionType.SPEAK_AUTONOMOUS:
                await self._execute_speak_autonomous_action(action)
            elif action.type == ActionType.COMMIT_MEMORY:
                logger.debug(f"Action COMMIT_MEMORY: {action.reason}")
            elif action.type == ActionType.RETRIEVE_MEMORY:
                query = action.parameters.get("query", "")
                logger.debug(f"Action RETRIEVE_MEMORY: query='{query}'")
            elif action.type == ActionType.INTROSPECT:
                logger.debug(f"Action INTROSPECT: {action.reason}")
            elif action.type == ActionType.UPDATE_GOAL:
                logger.debug(f"Action UPDATE_GOAL: {action.reason}")
            elif action.type == ActionType.WAIT:
                logger.debug("Action WAIT: maintaining current state")
            elif action.type == ActionType.TOOL_CALL:
                result = await self.subsystems.action.execute_action(action)
                logger.debug(f"Action TOOL_CALL: result={result}")
        except Exception as e:
            logger.error(f"Error executing action {action.type}: {e}", exc_info=True)
    
    async def _execute_speak_action(self, action) -> None:
        """Execute SPEAK action."""
        snapshot = self.state.workspace.broadcast()
        context = {
            "user_input": action.metadata.get("responding_to", "")
        }
        
        # Generate response using language output generator
        response = await self.subsystems.language_output.generate(snapshot, context)
        
        # Queue response for external retrieval
        await self.state.queue_output({
            "type": "SPEAK",
            "text": response,
            "emotion": snapshot.emotions,
            "timestamp": datetime.now()
        })
        logger.info(f"🗣️ Lyra: {response[:100]}...")
    
    async def _execute_speak_autonomous_action(self, action) -> None:
        """Execute SPEAK_AUTONOMOUS action."""
        snapshot = self.state.workspace.broadcast()
        context = {
            "autonomous": True,
            "trigger": action.metadata.get("trigger"),
            "introspection_content": action.metadata.get("introspection_content")
        }
        
        # Generate response using language output generator
        response = await self.subsystems.language_output.generate(snapshot, context)
        
        # Queue autonomous response for external retrieval
        await self.state.queue_output({
            "type": "SPEAK_AUTONOMOUS",
            "text": response,
            "trigger": action.metadata.get("trigger"),
            "emotion": snapshot.emotions,
            "timestamp": datetime.now()
        })
        logger.info(f"🗣️💭 Lyra (autonomous): {response[:100]}...")
    
    async def _execute_tool_action(self, action) -> Optional[Percept]:
        """
        Execute a tool call action and return the result percept.
        
        Args:
            action: TOOL_CALL action with tool_name and parameters
            
        Returns:
            Percept from tool execution, or None on error
        """
        if action.type != ActionType.TOOL_CALL:
            logger.error(f"_execute_tool_action called with non-TOOL_CALL action: {action.type}")
            return None
        
        try:
            # Extract tool information from action
            tool_name = action.parameters.get("tool_name")
            tool_params = action.parameters.get("parameters", {})
            
            if not tool_name:
                logger.error("TOOL_CALL action missing tool_name parameter")
                return None
            
            # Check if action subsystem has the new tool registry with percept generation
            if hasattr(self.subsystems.action, 'tool_reg'):
                # Use new tool registry with percept generation
                result = await self.subsystems.action.tool_reg.execute_tool_with_percept(
                    tool_name,
                    parameters=tool_params,
                    create_percept=True
                )
                
                # Log execution result
                if result.success:
                    logger.info(
                        f"✅ Tool '{tool_name}' executed: success "
                        f"({result.execution_time_ms:.1f}ms)"
                    )
                else:
                    logger.warning(
                        f"❌ Tool '{tool_name}' failed: {result.error} "
                        f"({result.execution_time_ms:.1f}ms)"
                    )
                
                # Return the generated percept
                return result.percept
            else:
                # Fallback to legacy tool execution (no percept generation)
                logger.warning("Action subsystem missing tool_reg, using legacy execution")
                result = await self.subsystems.action.execute_action(action)
                logger.debug(f"Action TOOL_CALL (legacy): result={result}")
                return None
                
        except Exception as e:
            logger.error(f"Error executing tool action: {e}", exc_info=True)
            return None
    
    def _extract_action_outcome(self, action) -> Dict[str, Any]:
        """
        Extract outcome information from an executed action.
        
        Args:
            action: The action that was executed
            
        Returns:
            Dictionary containing outcome details for self-model update
        """
        outcome = {
            "action_type": str(action.type) if hasattr(action, 'type') else "unknown",
            "timestamp": datetime.now().isoformat(),
            "success": True,
            "reason": ""
        }
        
        # Add action-specific details
        if hasattr(action, 'metadata'):
            outcome["metadata"] = action.metadata
        
        if hasattr(action, 'reason'):
            outcome["reason"] = action.reason
        
        # Check for failure indicators
        if hasattr(action, 'status'):
            outcome["success"] = action.status == "success"
        
        return outcome
    
    async def _run_meta_cognition(self) -> list:
        """
        Run meta-cognition and return introspective percepts.
        
        Returns:
            List of meta-percepts
        """
        snapshot = self.state.workspace.broadcast()
        meta_percepts = self.subsystems.meta_cognition.observe(snapshot)
        
        # Auto-validate pending predictions (Phase 4.3)
        auto_validated = self.subsystems.meta_cognition.auto_validate_predictions(snapshot)
        if auto_validated:
            logger.debug(f"🔍 Auto-validated {len(auto_validated)} predictions")
        
        # Record significant observations to journal
        for percept in meta_percepts:
            if hasattr(percept, 'raw') and isinstance(percept.raw, dict):
                percept_type = percept.raw.get("type")
                if percept_type in ["self_model_update", "behavioral_inconsistency", "existential_question"]:
                    self.subsystems.introspective_journal.record_observation(percept.raw)
        
        return meta_percepts
    
    async def _check_autonomous_triggers(self) -> None:
        """Check for autonomous speech triggers and add goals if needed."""
        snapshot = self.state.workspace.broadcast()
        autonomous_goal = self.subsystems.autonomous.check_for_autonomous_triggers(snapshot)
        
        if autonomous_goal:
            # Add high-priority autonomous goal
            self.state.workspace.add_goal(autonomous_goal)
            logger.info(f"🗣️ Autonomous speech goal added: {autonomous_goal.description}")
    
    def _update_workspace(self, attended: list, affect_update: dict, meta_percepts: list) -> None:
        """
        Update workspace with all subsystem outputs.
        
        Args:
            attended: List of attended percepts
            affect_update: Affect update dict
            meta_percepts: List of meta-cognition percepts
        """
        updates = []
        
        # Add attended percepts
        for percept in attended:
            updates.append({'type': 'percept', 'data': percept})
        
        # Add affect update
        updates.append({'type': 'emotion', 'data': affect_update})
        
        # Add meta-percepts
        for meta_percept in meta_percepts:
            updates.append({'type': 'percept', 'data': meta_percept})
        
        self.state.workspace.update(updates)
