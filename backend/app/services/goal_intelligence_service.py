"""Goal Intelligence System.

Turns a free-text goal + category into a concrete daily/weekly/monthly task
roadmap via category-matched templates. Not a generative model -- a curated
template bank keyed by keyword match against the goal's category/title, with
a sensible generic fallback for anything unrecognized.
"""
import uuid
from datetime import datetime, timedelta, timezone

from app.models.goal import GoalTask

_TEMPLATES: dict[str, dict[str, list[str]]] = {
    "dsa": {
        "daily": ["Solve 2 DSA problems", "Review yesterday's solutions"],
        "weekly": ["Complete one topic (e.g. Trees, DP, Graphs)", "Take a timed mock contest"],
        "monthly": ["Finish a full topic category end-to-end", "Redo all previously-failed problems"],
    },
    "placement": {
        "daily": ["Solve 1 DSA problem", "Read one system design / CS fundamentals topic"],
        "weekly": ["Mock interview (technical or HR)", "Update resume / portfolio project"],
        "monthly": ["Apply to 10+ relevant openings", "Complete one full mock interview loop"],
    },
    "fitness": {
        "daily": ["30 min workout or activity", "Track meals / hydration"],
        "weekly": ["Long-duration cardio or sport session", "Rest & recovery day"],
        "monthly": ["Reassess measurements / progress photos", "Adjust routine based on progress"],
    },
    "project": {
        "daily": ["Code for at least 1 focused hour", "Commit progress with a clear message"],
        "weekly": ["Ship one complete feature", "Write/update project documentation"],
        "monthly": ["Demo the project milestone", "Refactor and address tech debt"],
    },
    "learning": {
        "daily": ["Study for 45-60 minutes", "Summarize what you learned in 3 bullet points"],
        "weekly": ["Complete one module/chapter", "Build a small exercise applying the concept"],
        "monthly": ["Complete a mini project using the skill", "Take a self-assessment"],
    },
    "general": {
        "daily": ["Spend 30 minutes making progress on this goal"],
        "weekly": ["Review progress and adjust the plan"],
        "monthly": ["Reassess whether the goal timeline still makes sense"],
    },
}


def _match_template(category: str, title: str) -> dict[str, list[str]]:
    haystack = f"{category} {title}".lower()
    for key, template in _TEMPLATES.items():
        if key == "general":
            continue
        if key in haystack:
            return template
    return _TEMPLATES["general"]


def generate_tasks_for_goal(title: str, category: str, target_date: datetime | None) -> list[GoalTask]:
    template = _match_template(category, title)
    now = datetime.now(timezone.utc)
    tasks: list[GoalTask] = []

    for description in template.get("daily", []):
        tasks.append(GoalTask(id=uuid.uuid4().hex, title=description, frequency="daily", due_date=now + timedelta(days=1)))
    for description in template.get("weekly", []):
        tasks.append(GoalTask(id=uuid.uuid4().hex, title=description, frequency="weekly", due_date=now + timedelta(weeks=1)))
    for description in template.get("monthly", []):
        tasks.append(GoalTask(id=uuid.uuid4().hex, title=description, frequency="monthly", due_date=target_date or now + timedelta(days=30)))

    return tasks
