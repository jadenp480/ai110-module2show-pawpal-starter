"""
tests/test_pawpal.py — Basic tests for PawPal+ core logic
Run with: python3 -m pytest tests/
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Owner, Pet, Task, Scheduler


# ── Helpers ───────────────────────────────────────────────────────────────

def make_task(title="Morning walk", category="walk", duration=30, priority=3):
    """Return a simple Task for use in tests."""
    return Task(title=title, category=category,
                duration_minutes=duration, priority=priority)

def make_pet(name="Mochi", species="dog"):
    """Return a Pet with no tasks attached."""
    return Pet(name=name, species=species)


# ── Test 1: Task Completion ────────────────────────────────────────────────

def test_mark_complete_changes_task_status():
    """
    Calling Scheduler.mark_complete() should flip the task's
    completed flag from False to True.
    """
    pet = make_pet()
    task = make_task()
    pet.add_task(task)

    owner = Owner(name="Jordan", available_minutes=60)
    owner.add_pet(pet)

    scheduler = Scheduler(owner=owner)
    scheduler.generate_plan()

    # Task starts incomplete
    assert task.completed is False

    # Mark it complete via the scheduler
    result = scheduler.mark_complete("Mochi", "Morning walk")

    assert result is True           # scheduler confirmed it found the task
    assert task.completed is True   # the task itself is now marked done


# ── Test 2: Task Addition ─────────────────────────────────────────────────

def test_add_task_increases_pet_task_count():
    """
    Adding a Task to a Pet should increase the pet's task list length by 1
    for each task added.
    """
    pet = make_pet()

    assert len(pet.tasks) == 0

    pet.add_task(make_task("Breakfast", "feeding"))
    assert len(pet.tasks) == 1

    pet.add_task(make_task("Evening walk", "walk"))
    assert len(pet.tasks) == 2


# ── Test 3: Sorting Correctness ───────────────────────────────────────────

def test_plan_sorted_by_time_preference():
    """
    After generate_plan(), tasks should be ordered morning → afternoon → evening
    for a default (morning_person not set) owner.
    The display sort is applied after budget selection, so we need all three
    tasks to fit within the budget.
    """
    pet = make_pet()
    pet.add_task(Task("Evening meds",  "medication", duration_minutes=10, priority=3,
                      time_preference="evening"))
    pet.add_task(Task("Afternoon walk", "walk",      duration_minutes=20, priority=3,
                      time_preference="afternoon"))
    pet.add_task(Task("Morning feed",  "feeding",    duration_minutes=15, priority=3,
                      time_preference="morning"))

    owner = Owner(name="Jordan", available_minutes=120)
    owner.add_pet(pet)

    scheduler = Scheduler(owner=owner)
    scheduler.generate_plan()

    slots = [task.time_preference for _, task in scheduler.plan]
    assert slots == ["morning", "afternoon", "evening"], (
        f"Expected morning → afternoon → evening, got {slots}"
    )


def test_higher_priority_task_scheduled_before_lower():
    """
    When the budget can fit only one task, the higher-priority task should
    be chosen over a lower-priority one, regardless of insertion order.
    """
    pet = make_pet()
    low  = make_task("Low task",  priority=1, duration=30)
    high = make_task("High task", priority=5, duration=30)
    pet.add_task(low)
    pet.add_task(high)

    owner = Owner(name="Jordan", available_minutes=30)   # fits exactly one task
    owner.add_pet(pet)

    scheduler = Scheduler(owner=owner)
    scheduler.generate_plan()

    assert len(scheduler.plan) == 1
    _, scheduled_task = scheduler.plan[0]
    assert scheduled_task.title == "High task", (
        "Lower-priority task was scheduled instead of the higher-priority one"
    )


# ── Test 4: Recurrence Logic ──────────────────────────────────────────────

def test_daily_task_creates_next_occurrence_after_completion():
    """
    Completing a daily task via mark_complete() should add a new task to the
    pet's task list with due_date advanced by exactly 1 day.
    """
    from datetime import timedelta

    pet  = make_pet()
    task = Task("Daily meds", "medication", duration_minutes=5, priority=4,
                frequency="daily")
    original_due = task.due_date
    pet.add_task(task)

    owner = Owner(name="Jordan", available_minutes=60)
    owner.add_pet(pet)

    scheduler = Scheduler(owner=owner)
    scheduler.generate_plan()
    scheduler.mark_complete("Mochi", "Daily meds")

    # Original task is done; a new task should have been appended
    assert task.completed is True
    assert len(pet.tasks) == 2, "Expected a recurrence task to be added"

    next_task = pet.tasks[1]
    assert next_task.completed is False
    assert next_task.due_date == original_due + timedelta(days=1), (
        f"Expected {original_due + timedelta(days=1)}, got {next_task.due_date}"
    )


def test_once_task_does_not_recur_after_completion():
    """
    Completing a 'once' task should NOT add any new task to the pet's list.
    """
    pet  = make_pet()
    task = Task("Vet visit", "appointment", duration_minutes=60, priority=5,
                frequency="once")
    pet.add_task(task)

    owner = Owner(name="Jordan", available_minutes=120)
    owner.add_pet(pet)

    scheduler = Scheduler(owner=owner)
    scheduler.generate_plan()
    scheduler.mark_complete("Mochi", "Vet visit")

    assert task.completed is True
    assert len(pet.tasks) == 1, (
        "A 'once' task should not spawn a recurrence after completion"
    )


# ── Test 5: Conflict Detection ────────────────────────────────────────────

def test_same_pet_same_slot_triggers_conflict_warning():
    """
    Two tasks for the same pet in the same time slot should produce a
    conflict warning from find_conflicts().
    """
    pet = make_pet()
    pet.add_task(Task("Morning walk",  "walk",     duration_minutes=20, priority=3,
                      time_preference="morning"))
    pet.add_task(Task("Morning meds",  "medication", duration_minutes=5, priority=4,
                      time_preference="morning"))

    owner = Owner(name="Jordan", available_minutes=120)
    owner.add_pet(pet)

    scheduler = Scheduler(owner=owner)
    scheduler.generate_plan()
    warnings = scheduler.find_conflicts()

    assert any("morning" in w and "Mochi" in w for w in warnings), (
        f"Expected a same-pet/morning-slot warning, got: {warnings}"
    )


def test_slot_overload_triggers_conflict_warning():
    """
    Tasks in the evening slot whose total duration exceeds 90 minutes should
    produce a slot-overload warning (capacity: evening = 90 min).
    """
    pet = make_pet()
    pet.add_task(Task("Evening walk",    "walk",      duration_minutes=60, priority=3,
                      time_preference="evening"))
    pet.add_task(Task("Evening groom",   "grooming",  duration_minutes=45, priority=2,
                      time_preference="evening"))

    owner = Owner(name="Jordan", available_minutes=200)
    owner.add_pet(pet)

    scheduler = Scheduler(owner=owner)
    scheduler.generate_plan()
    warnings = scheduler.find_conflicts()

    assert any("evening" in w and "overloaded" in w for w in warnings), (
        f"Expected an evening-slot overload warning, got: {warnings}"
    )


def test_no_conflict_when_tasks_in_different_slots():
    """
    Tasks for the same pet in different time slots should produce no warnings.
    """
    pet = make_pet()
    pet.add_task(Task("Morning walk",    "walk",    duration_minutes=20, priority=3,
                      time_preference="morning"))
    pet.add_task(Task("Afternoon meds",  "medication", duration_minutes=5, priority=4,
                      time_preference="afternoon"))

    owner = Owner(name="Jordan", available_minutes=120)
    owner.add_pet(pet)

    scheduler = Scheduler(owner=owner)
    scheduler.generate_plan()
    warnings = scheduler.find_conflicts()

    assert warnings == [], f"Expected no warnings, got: {warnings}"
