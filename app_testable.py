"""Pure helpers used by NeuralDesk; kept separate for easy tests."""


def task_completion_rate(tasks):
    if not tasks:
        return 0
    completed = sum(1 for task in tasks if task.get("done", False))
    return round(100 * completed / len(tasks))


def build_task_summary(tasks):
    return {
        "total": len(tasks),
        "completed": sum(1 for task in tasks if task.get("done", False)),
        "open_high": sum(
            1 for task in tasks
            if not task.get("done", False) and task.get("priority") == "High"
        ),
    }
