# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

Beyond the base priority-based planner, the scheduler includes:

- **Sort by time** — Re-sort the daily plan chronologically using a lambda key that converts "HH:MM" strings to minutes, useful after manual edits or future time-window features.
- **Filter tasks** — Query tasks by pet name, completion status, or both with case-insensitive matching. Returns the same `(pet, task)` tuple format used throughout the system.
- **Recurring tasks** — Tasks can be set to `"daily"` or `"weekly"` recurrence. When all occurrences are marked complete, the scheduler auto-creates a new task with the next due date using `timedelta`.
- **Conflict detection** — After generating a plan (or injecting manual slots), `detect_conflicts()` compares every pair of slots for time overlaps and returns warning messages instead of crashing.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
