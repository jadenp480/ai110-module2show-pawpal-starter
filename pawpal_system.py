"""
PawPal+ — Core System
Modular OOP backend for pet care scheduling.

Classes:
    Task      — a single care activity with frequency and completion tracking
    Pet       — a pet that owns its own task list
    Owner     — manages one or more pets and a daily time budget
    Scheduler — the scheduling brain; pulls tasks from all of an owner's pets
"""

from datetime import date as today_date, timedelta


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
CATEGORY_WEIGHT = {
    "medication": 6,
    "appointment": 5,
    "feeding": 4,
    "walk": 3,
    "grooming": 2,
    "enrichment": 1,
}

SENIOR_AGE = {
    "dog": 7,
    "cat": 10,
}


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------
class Task:
    """
    Represents a single pet care activity.

    Attributes:
        title            (str)  — short name for the task
        category         (str)  — one of the CATEGORY_WEIGHT keys
        duration_minutes (int)  — how long the task takes
        priority         (int)  — 1 (low) to 5 (critical)
        frequency        (str)  — "once" | "daily" | "weekly" | "as_needed"
        time_preference  (str)  — "morning" | "afternoon" | "evening" | None
        notes            (str)  — optional free-text context
        completed        (bool) — whether the task is done for today
    """

    VALID_CATEGORIES = list(CATEGORY_WEIGHT.keys())
    VALID_FREQUENCIES = ["once", "daily", "weekly", "as_needed"]

    def __init__(
        self,
        title: str,
        category: str,
        duration_minutes: int,
        priority: int,
        frequency: str = "daily",
        time_preference: str = None,
        notes: str = "",
    ):
        """Create a Task, validating category, priority, and frequency."""
        if category not in self.VALID_CATEGORIES:
            raise ValueError(
                f"Invalid category '{category}'. "
                f"Choose from: {self.VALID_CATEGORIES}"
            )
        if not (1 <= priority <= 5):
            raise ValueError("Priority must be between 1 (low) and 5 (critical).")
        if frequency not in self.VALID_FREQUENCIES:
            raise ValueError(
                f"Invalid frequency '{frequency}'. "
                f"Choose from: {self.VALID_FREQUENCIES}"
            )

        self.title = title
        self.category = category
        self.duration_minutes = duration_minutes
        self.priority = priority
        self.frequency = frequency
        self.time_preference = time_preference
        self.notes = notes
        self.completed = False
        self.due_date: today_date = today_date.today()

    # ------------------------------------------------------------------
    # State
    # ------------------------------------------------------------------
    def complete(self):
        """Mark this task as done."""
        self.completed = True

    def reset(self):
        """Clear the completion status (use at the start of a new day)."""
        self.completed = False

    def next_occurrence(self) -> "Task":
        """Return a new, incomplete Task scheduled for the next recurrence date.

        Algorithm:
            Uses a fixed interval map — {"daily": 1, "weekly": 7} — to compute
            the next due_date as self.due_date + timedelta(days=interval).
            All other attributes (title, category, duration, priority, etc.) are
            copied verbatim so the new task is identical except for due_date and
            the default completed=False.

        Returns:
            Task  — a fresh Task instance with due_date advanced by the interval.
            None  — if frequency is "once" or "as_needed" (no automatic recurrence).

        Frequency mapping:
            daily      → due_date + 1 day
            weekly     → due_date + 7 days
            once       → None (task does not repeat)
            as_needed  → None (recurrence is caller-managed)
        """
        intervals = {"daily": 1, "weekly": 7}
        days = intervals.get(self.frequency)
        if days is None:
            return None
        next_task = Task(
            title=self.title,
            category=self.category,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            frequency=self.frequency,
            time_preference=self.time_preference,
            notes=self.notes,
        )
        next_task.due_date = self.due_date + timedelta(days=days)
        return next_task

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------
    def get_priority_score(self) -> int:
        """Return the numeric priority used by the Scheduler."""
        return self.priority

    def is_urgent(self) -> bool:
        """Return True when priority is 4 or 5."""
        return self.priority >= 4

    def __str__(self) -> str:
        """Return a compact, human-readable description of this task."""
        status = "✓" if self.completed else "○"
        urgency = " [URGENT]" if self.is_urgent() else ""
        pref = f" ({self.time_preference})" if self.time_preference else ""
        return (
            f"[{status}][P{self.priority}] {self.title}{urgency} — "
            f"{self.category}{pref}, {self.duration_minutes} min, "
            f"{self.frequency}, due {self.due_date}"
        )


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------
class Pet:
    """
    Stores pet details and owns a list of Tasks.

    Attributes:
        name          (str)        — pet's name
        species       (str)        — "dog" | "cat" | "other"
        breed         (str)        — optional breed
        age           (float)      — age in years
        weight        (float)      — weight in lbs
        special_needs (list[str])  — e.g. ["diabetic", "anxiety"]
        tasks         (list[Task]) — all care tasks for this pet
    """

    def __init__(
        self,
        name: str,
        species: str,
        breed: str = "",
        age: float = 0.0,
        weight: float = 0.0,
        special_needs: list = None,
    ):
        """Create a Pet with an empty task list."""
        self.name = name
        self.species = species.lower()
        self.breed = breed
        self.age = age
        self.weight = weight
        self.special_needs = special_needs or []
        self.tasks: list[Task] = []

    # ------------------------------------------------------------------
    # Task management
    # ------------------------------------------------------------------
    def add_task(self, task: Task):
        """Attach a Task to this pet."""
        self.tasks.append(task)

    def remove_task(self, title: str):
        """Remove a task by title (case-insensitive)."""
        lower = title.lower()
        self.tasks = [t for t in self.tasks if t.title.lower() != lower]

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------
    def get_pending_tasks(self) -> list:
        """Return tasks that are not yet completed."""
        return [t for t in self.tasks if not t.completed]

    def get_tasks_by_category(self, category: str) -> list:
        """Return all tasks matching the given category."""
        return [t for t in self.tasks if t.category == category]

    def is_senior(self) -> bool:
        """Return True if the pet's age meets the senior threshold for its species."""
        return self.age >= SENIOR_AGE.get(self.species, 10)

    def get_info(self) -> str:
        """Return a formatted one-line summary of this pet."""
        parts = [f"{self.name} ({self.species}"]
        if self.breed:
            parts[0] += f", {self.breed}"
        parts[0] += ")"
        if self.age:
            parts.append(f"Age: {self.age} yrs")
        if self.weight:
            parts.append(f"Weight: {self.weight} lbs")
        if self.special_needs:
            parts.append(f"Special needs: {', '.join(self.special_needs)}")
        if self.is_senior():
            parts.append("[Senior]")
        pending = len(self.get_pending_tasks())
        parts.append(f"{pending}/{len(self.tasks)} tasks pending")
        return " | ".join(parts)


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------
class Owner:
    """
    Manages one or more pets and a daily time budget.

    Attributes:
        name              (str)       — owner's name
        available_minutes (int)       — total care time available per day
        preferences       (dict)      — e.g. {"morning_person": True}
        pets              (list[Pet]) — all pets this owner cares for
    """

    def __init__(
        self,
        name: str,
        available_minutes: int = 120,
        preferences: dict = None,
    ):
        """Create an Owner with an empty pet list."""
        self.name = name
        self.available_minutes = available_minutes
        self.preferences = preferences or {}
        self.pets: list[Pet] = []

    # ------------------------------------------------------------------
    # Pet management
    # ------------------------------------------------------------------
    def add_pet(self, pet: Pet):
        """Add a pet to this owner's care list."""
        self.pets.append(pet)

    def remove_pet(self, name: str):
        """Remove a pet by name (case-insensitive)."""
        lower = name.lower()
        self.pets = [p for p in self.pets if p.name.lower() != lower]

    def set_availability(self, minutes: int):
        """Update the owner's daily time budget."""
        self.available_minutes = minutes

    # ------------------------------------------------------------------
    # Cross-pet task access
    # ------------------------------------------------------------------
    def get_all_tasks(self) -> list:
        """Return (Pet, Task) pairs for every task across all pets."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]

    def get_all_pending_tasks(self) -> list:
        """Return (Pet, Task) pairs for every incomplete task across all pets."""
        return [(pet, task) for pet in self.pets for task in pet.get_pending_tasks()]

    def filter_by_pet(self, pet_name: str) -> list:
        """Return all (Pet, Task) pairs belonging to a single named pet.

        Algorithm:
            Calls get_all_tasks() to obtain every (Pet, Task) pair across all
            pets, then filters with a case-insensitive string comparison so
            callers don't need to match capitalisation exactly.

        Args:
            pet_name (str): The pet's name to filter by (case-insensitive).

        Returns:
            list[tuple[Pet, Task]]: Pairs for the named pet; empty list if the
            name is not found.
        """
        lower = pet_name.lower()
        return [(pet, task) for pet, task in self.get_all_tasks()
                if pet.name.lower() == lower]

    def filter_by_status(self, completed: bool) -> list:
        """Return all (Pet, Task) pairs whose completion status matches the argument.

        Algorithm:
            Calls get_all_tasks() to obtain every (Pet, Task) pair across all
            pets, then keeps only those where task.completed equals the given
            bool. Pass completed=False to see what still needs doing; pass
            completed=True to review what has already been finished.

        Args:
            completed (bool): True to return finished tasks, False for pending.

        Returns:
            list[tuple[Pet, Task]]: Matching pairs; empty list if none match.
        """
        return [(pet, task) for pet, task in self.get_all_tasks()
                if task.completed == completed]

    # ------------------------------------------------------------------
    # Info
    # ------------------------------------------------------------------
    def get_info(self) -> str:
        """Return a formatted summary of the owner."""
        pet_names = ", ".join(p.name for p in self.pets) if self.pets else "none"
        return (
            f"Owner: {self.name} | "
            f"Daily budget: {self.available_minutes} min | "
            f"Pets: {pet_names}"
        )


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------
class Scheduler:
    """
    The scheduling brain.

    Retrieves pending tasks from all of an owner's pets, fits them into the
    owner's daily time budget ordered by priority, and tracks completion.

    Attributes:
        owner            (Owner)                      — source of pets + budget
        date             (str)                        — date this plan is for
        plan             (list[(Pet, Task)])           — scheduled (pet, task) pairs
        skipped          (list[(Pet, Task, str)])      — skipped with reasons
        _plan_generated  (bool)                       — True once generate_plan() runs
    """

    def __init__(self, owner: Owner, date: str = None):
        """Create a Scheduler tied to an owner; date defaults to today."""
        self.owner = owner
        self.date = date or str(today_date.today())
        self.plan: list[tuple] = []          # (Pet, Task)
        self.skipped: list[tuple] = []       # (Pet, Task, reason)
        self._plan_generated = False

    # ------------------------------------------------------------------
    # Core algorithm
    # ------------------------------------------------------------------
    def generate_plan(self):
        """Sort pending tasks by priority and greedily fit them into the owner's time budget."""
        self.plan = []
        self.skipped = []
        self._plan_generated = True
        budget = self.owner.available_minutes
        display_order = ["morning", "afternoon", "evening", None]

        if self.owner.preferences.get("morning_person") is False:
            display_order = ["evening", "afternoon", "morning", None]

        def effective_score(pair: tuple) -> tuple:
            pet, task = pair
            score = task.priority
            if pet.special_needs and task.category in ("medication", "appointment"):
                score = min(5, score + 1)
            return (score, CATEGORY_WEIGHT.get(task.category, 0))

        pending = self.owner.get_all_pending_tasks()
        sorted_pairs = sorted(pending, key=effective_score, reverse=True)

        time_used = 0
        for pet, task in sorted_pairs:
            if task.duration_minutes > budget:
                self.skipped.append((pet, task, "task duration exceeds daily budget"))
            elif time_used + task.duration_minutes <= budget:
                self.plan.append((pet, task))
                time_used += task.duration_minutes
            else:
                self.skipped.append((pet, task, "not enough time remaining"))

        # Sort plan by time_preference for display only
        self.plan.sort(
            key=lambda pair: display_order.index(
                pair[1].time_preference
                if pair[1].time_preference in display_order
                else None
            )
        )

    # ------------------------------------------------------------------
    # Completion tracking
    # ------------------------------------------------------------------
    def mark_complete(self, pet_name: str, task_title: str) -> bool:
        """Mark a scheduled task done by pet name and task title; returns True if found."""
        lower_pet = pet_name.lower()
        lower_task = task_title.lower()
        for pet, task in self.plan:
            if pet.name.lower() == lower_pet and task.title.lower() == lower_task:
                task.complete()
                next_task = task.next_occurrence()
                if next_task is not None:
                    pet.add_task(next_task)
                return True
        return False

    def mark_all_complete(self):
        """Mark every scheduled task as complete."""
        for _, task in self.plan:
            task.complete()

    def reset_day(self):
        """Clear all task completions and wipe the plan so the day can start fresh."""
        for pet in self.owner.pets:
            for task in pet.tasks:
                task.reset()
        self.plan = []
        self.skipped = []
        self._plan_generated = False

    # ------------------------------------------------------------------
    # Conflict detection
    # ------------------------------------------------------------------
    def find_conflicts(self) -> list:
        """Scan the plan for scheduling conflicts; return a list of warning strings.

        Two conflict types are detected — neither raises an exception:
          1. Same-pet conflict  — one pet has multiple tasks in the same time slot.
          2. Slot overload      — total minutes in a slot exceed its capacity.

        Slot capacities (minutes): morning=120, afternoon=120, evening=90, flexible=480.
        Tasks with time_preference=None are treated as 'flexible' and only trigger
        a same-pet warning, not an overload warning.
        """
        if not self._plan_generated:
            return ["No plan generated yet. Call generate_plan() first."]

        SLOT_CAPACITY = {"morning": 120, "afternoon": 120, "evening": 90}
        warnings = []

        # Group plan entries by time slot
        from collections import defaultdict
        slot_map = defaultdict(list)   # slot → [(pet_name, task_title, duration)]
        for pet, task in self.plan:
            slot = task.time_preference or "flexible"
            slot_map[slot].append((pet.name, task.title, task.duration_minutes))

        for slot, entries in slot_map.items():
            # 1. Same-pet conflict
            pet_tasks = defaultdict(list)
            for pet_name, task_title, _ in entries:
                pet_tasks[pet_name].append(task_title)
            for pet_name, titles in pet_tasks.items():
                if len(titles) > 1:
                    joined = ", ".join(f"'{t}'" for t in titles)
                    warnings.append(
                        f"WARNING: {pet_name} has {len(titles)} tasks in the "
                        f"'{slot}' slot: {joined}"
                    )

            # 2. Slot overload (skip 'flexible' — no meaningful capacity to check)
            if slot in SLOT_CAPACITY:
                total = sum(d for _, _, d in entries)
                cap = SLOT_CAPACITY[slot]
                if total > cap:
                    task_list = ", ".join(
                        f"{p}:'{t}' ({d}m)" for p, t, d in entries
                    )
                    warnings.append(
                        f"WARNING: '{slot}' slot is overloaded — "
                        f"{total} min scheduled, {cap} min capacity "
                        f"({task_list})"
                    )

        return warnings

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------
    def total_scheduled_time(self) -> int:
        """Return the total minutes of all scheduled tasks."""
        return sum(task.duration_minutes for _, task in self.plan)

    def get_plan_summary(self) -> str:
        """Return the daily plan as a readable string."""
        if not self._plan_generated:
            return "No plan generated yet. Call generate_plan() first."

        lines = [
            f"=== PawPal+ Daily Plan ({self.date}) ===",
            f"Owner: {self.owner.name} | "
            f"Time used: {self.total_scheduled_time()}/{self.owner.available_minutes} min",
            "",
        ]

        if not self.plan:
            lines.append("  No tasks could fit within the available time budget.")
        else:
            for i, (pet, task) in enumerate(self.plan, 1):
                lines.append(f"  {i}. [{pet.name}] {task}")

        if self.skipped:
            lines.append("\n  [Skipped]")
            for pet, task, reason in self.skipped:
                lines.append(f"  - [{pet.name}] {task.title} ({reason})")

        conflicts = self.find_conflicts()
        if conflicts:
            lines.append("\n  [Conflict Warnings]")
            for w in conflicts:
                lines.append(f"  ! {w}")

        return "\n".join(lines)

    def explain_reasoning(self) -> str:
        """Explain why the plan was built the way it was."""
        if not self._plan_generated:
            return "No plan to explain. Call generate_plan() first."

        lines = ["=== Scheduling Reasoning ===", ""]
        lines.append(
            "Tasks were allocated by priority (5=critical → 1=low). "
            "Ties were broken by category importance: "
            "medication > appointment > feeding > walk > grooming > enrichment."
        )

        # Mention any special-needs boosts
        boosted_pets = [p for p in self.owner.pets if p.special_needs]
        for pet in boosted_pets:
            lines.append(
                f"{pet.name} has special needs ({', '.join(pet.special_needs)}), "
                "so their medication and appointment tasks received a +1 priority boost."
            )

        # Mention morning_person preference
        pref = self.owner.preferences.get("morning_person")
        if pref is True:
            lines.append(
                f"{self.owner.name} is a morning person — tasks display morning → afternoon → evening."
            )
        elif pref is False:
            lines.append(
                f"{self.owner.name} is not a morning person — tasks display evening → afternoon → morning."
            )

        lines.append(
            f"Tasks were fit greedily into {self.owner.available_minutes} min budget. "
            "Time preference only affects display order, not which tasks are selected."
        )

        for pet, task, reason in self.skipped:
            lines.append(f"Skipped '{task.title}' ({pet.name}): {reason}.")

        return "\n".join(lines)
