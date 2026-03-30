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
