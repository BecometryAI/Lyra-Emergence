"""
Test for Sanctuary Meta-cognition Module
"""
import tempfile
from .metacognition import MetaCognition

def test_metacognition():
    with tempfile.TemporaryDirectory(prefix="metacog_test_") as tmpdir:
        meta = MetaCognition(log_dir=tmpdir)
        meta.log_event("decision", {"action": "respond", "input": "Hello Sanctuary!"})
        meta.reflect("Test reflection", ["Learned to log events.", "Reflection works."])
        log = meta.get_log()
        assert len(log["events"]) == 1
        assert len(log["reflections"]) == 1

if __name__ == "__main__":
    test_metacognition()
