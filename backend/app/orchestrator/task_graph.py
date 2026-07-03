class TaskGraph:
    """
    Wraps a list of subtask dicts (id, depends_on) and yields them in
    dependency-respecting batches, so independent subtasks execute in
    parallel while dependent ones wait — this is what gives the orchestrator
    both 'sequential' and 'parallel' execution from a single structure.
    """

    def __init__(self, subtasks: list[dict]):
        self.subtasks = {t["id"]: t for t in subtasks}

    def batches(self) -> list[list[dict]]:
        remaining = dict(self.subtasks)
        done = set()
        batches = []
        guard = 0
        while remaining and guard < 100:
            guard += 1
            ready = [
                t for t in remaining.values()
                if all(dep in done for dep in t.get("depends_on", []))
            ]
            if not ready:
                # circular or bad dependency reference -> flush remaining as final batch
                ready = list(remaining.values())
            batches.append(ready)
            for t in ready:
                done.add(t["id"])
                remaining.pop(t["id"], None)
        return batches
