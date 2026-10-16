from app_testable import task_completion_rate, build_task_summary


def test_completion_rate_empty():
    assert task_completion_rate([]) == 0


def test_completion_rate_mixed():
    tasks = [{"done": True}, {"done": False}, {"done": True}]
    assert task_completion_rate(tasks) == 67


def test_summary_counts_priorities():
    tasks = [
        {"done": False, "priority": "High"},
        {"done": True, "priority": "High"},
        {"done": False, "priority": "Low"},
    ]
    result = build_task_summary(tasks)
    assert result["total"] == 3
    assert result["completed"] == 1
    assert result["open_high"] == 1
