"""
PawPal+ — Core System
Modular OOP backend for pet care scheduling.
"""

from datetime import date as today_date


# ---------------------------------------------------------------------------
# Task categories and their scheduling weights (higher = higher priority tie-break)
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
# Pet
# ---------------------------------------------------------------------------
class Pet:
    """Represents the animal being cared for."""

    def __init__(
        self,
        name: str,
        species: str,
        breed: str = "",
        age: float = 0.0,
        weight: float = 0.0,
        special_needs: list = None,
    ):
        self.name = name
        self.species = species.lower()
        self.breed = breed
        self.age = age
        self.weight = weight
        self.special_needs = special_needs or []

    def get_info(self) -> str:
        """Returns a formatted summary of the pet."""
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
            parts.append("[Senior pet]")
        return " | ".join(parts)

    def is_senior(self) -> bool:
        """Returns True if the pet qualifies as a senior based on species and age."""
        threshold = SENIOR_AGE.get(self.species, 10)
        return self.age >= threshold


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------
class Owner:
    """Represents the human caring for the pet."""

    def __init__(
        self,
        name: str,
        available_minutes: int = 120,
        preferences: dict = None,
    ):
        self.name = name
        self.available_minutes = available_minutes
        self.preferences = preferences or {}

    def get_info(self) -> str:
        """Returns a formatted summary of the owner."""
        return (
            f"Owner: {self.name} | "
            f"Daily time budget: {self.available_minutes} min"
        )

    def set_availability(self, minutes: int):
        """Update the owner's daily time budget."""
        self.available_minutes = minutes


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------
class Task:
    """Represents a single pet care task."""

    VALID_CATEGORIES = list(CATEGORY_WEIGHT.keys())

    def __init__(
        self,
        title: str,
        category: str,
        duration_minutes: int,
        priority: int,
        time_preference: str = None,
        notes: str = "",
    ):
        if category not in self.VALID_CATEGORIES:
            raise ValueError(
                f"Invalid category '{category}'. "
                f"Choose from: {self.VALID_CATEGORIES}"
            )
        if not (1 <= priority <= 5):
            raise ValueError("Priority must be between 1 (low) and 5 (critical).")

        self.title = title
        self.category = category
        self.duration_minutes = duration_minutes
        self.priority = priority
        self.time_preference = time_preference  # "morning", "afternoon", "evening", or None
        self.notes = notes

    def get_priority_score(self) -> int:
        """Returns the numeric priority (1–5) used by the scheduler."""
        return self.priority

    def is_urgent(self) -> bool:
        """Returns True if the task has a priority of 4 or 5."""
        return self.priority >= 4

    def __str__(self) -> str:
        urgency = " [URGENT]" if self.is_urgent() else ""
        pref = f" ({self.time_preference})" if self.time_preference else ""
        return (
            f"[P{self.priority}] {self.title}{urgency} — "
            f"{self.category}{pref}, {self.duration_minutes} min"
        )


# ---------------------------------------------------------------------------
# Schedule
# ---------------------------------------------------------------------------
class Schedule:
    """Holds the daily task pool and generates a prioritized plan."""

    def __init__(self, pet: Pet, owner: Owner, date: str = None):
        self.pet = pet
        self.owner = owner
        self.tasks: list[Task] = []
        self.plan: list[Task] = []
        self.skipped: list[tuple[Task, str]] = []  # (task, reason)
        self.date = date or str(today_date.today())
        self._plan_generated = False  # Fix 5: distinguish "not yet run" from "ran but empty"

    def add_task(self, task: Task):
        """Add a task to the pool."""
        self.tasks.append(task)

    def remove_task(self, title: str):
        """Remove a task by title (case-insensitive) from the pool, plan, and skipped list."""
        lower = title.lower()
        self.tasks = [t for t in self.tasks if t.title.lower() != lower]
        self.plan = [t for t in self.plan if t.title.lower() != lower]          # Fix 6
        self.skipped = [(t, r) for t, r in self.skipped if t.title.lower() != lower]  # Fix 6

    def generate_plan(self):
        """
        Run the scheduling algorithm.

        Strategy: Priority-first, time-constrained greedy sort.
        1. Sort globally by effective priority desc (boosted by pet special_needs),
           break ties by category weight desc.
        2. Greedily fit tasks into available_minutes budget in priority order.
        3. After allocation, sort the plan by time_preference for display,
           respecting the owner's morning_person preference.
        4. Record skipped tasks with a specific reason.
        """
        self.plan = []
        self.skipped = []
        self._plan_generated = True  # Fix 5
        budget = self.owner.available_minutes
        display_order = ["morning", "afternoon", "evening", None]

        # Fix 2: flip display order if owner is explicitly NOT a morning person
        if self.owner.preferences.get("morning_person") is False:
            display_order = ["evening", "afternoon", "morning", None]

        # Fix 1: boost medication/appointment priority by 1 (capped at 5) when pet has special needs
        def effective_score(task: Task) -> tuple:
            score = task.priority
            if self.pet.special_needs and task.category in ("medication", "appointment"):
                score = min(5, score + 1)
            return (score, CATEGORY_WEIGHT.get(task.category, 0))

        # Fix 3: sort globally by priority — time preference is display-only, not allocation order
        sorted_tasks = sorted(self.tasks, key=effective_score, reverse=True)

        # Fix 3 + Fix 4: allocate budget in strict priority order
        time_used = 0
        for task in sorted_tasks:
            if task.duration_minutes > budget:
                # Fix 4: single task too long for the entire day — specific message
                self.skipped.append((task, "task duration exceeds daily budget"))
            elif time_used + task.duration_minutes <= budget:
                self.plan.append(task)
                time_used += task.duration_minutes
            else:
                self.skipped.append((task, "not enough time remaining"))

        # Fix 3: sort scheduled tasks by time preference for display only
        self.plan.sort(
            key=lambda t: display_order.index(
                t.time_preference if t.time_preference in display_order else None
            )
        )

    def total_scheduled_time(self) -> int:
        """Returns the sum of duration_minutes for all scheduled tasks."""
        return sum(t.duration_minutes for t in self.plan)

    def get_plan_summary(self) -> str:
        """Returns the ordered plan as a readable string."""
        # Fix 7: distinguish "never generated" from "generated but all tasks skipped"
        if not self._plan_generated:
            return "No plan generated yet. Call generate_plan() first."

        lines = [
            f"=== Daily Plan for {self.pet.name} ({self.date}) ===",
            f"Owner: {self.owner.name} | "
            f"Time used: {self.total_scheduled_time()}/{self.owner.available_minutes} min",
            "",
        ]

        if not self.plan:
            lines.append("  No tasks could be scheduled within the available time budget.")
        else:
            for i, task in enumerate(self.plan, 1):
                lines.append(f"  {i}. {task}")

        if self.skipped:
            lines.append("\n  [Skipped tasks]")
            for task, reason in self.skipped:
                lines.append(f"  - {task.title} ({reason})")

        return "\n".join(lines)

    def explain_reasoning(self) -> str:
        """Explains why tasks were ordered as they were."""
        if not self._plan_generated:  # Fix 7
            return "No plan to explain. Call generate_plan() first."

        lines = ["=== Scheduling Reasoning ===", ""]
        lines.append(
            "Tasks were allocated by priority (5=critical → 1=low). "
            "Ties were broken by category importance: "
            "medication > appointment > feeding > walk > grooming > enrichment."
        )
        if self.pet.special_needs:
            lines.append(
                f"Because {self.pet.name} has special needs "
                f"({', '.join(self.pet.special_needs)}), medication and appointment "
                "tasks received a +1 priority boost."
            )
        pref = self.owner.preferences.get("morning_person")
        if pref is False:
            lines.append(
                f"{self.owner.name} is not a morning person, so tasks are displayed "
                "evening → afternoon → morning."
            )
        elif pref is True:
            lines.append(
                f"{self.owner.name} is a morning person, so tasks are displayed "
                "morning → afternoon → evening."
            )
        lines.append(
            f"Tasks were fit into {self.owner.name}'s daily budget of "
            f"{self.owner.available_minutes} minutes in priority order. "
            "Time preference only affects display order, not which tasks are selected."
        )
        if self.skipped:
            for task, reason in self.skipped:
                lines.append(f"Skipped '{task.title}': {reason}.")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# PawPalSystem  (Facade / coordinator)
# ---------------------------------------------------------------------------
class PawPalSystem:
    """Top-level coordinator — single entry point for the app and CLI demo."""

    def __init__(self):
        self.owner: Owner = None
        self.pet: Pet = None
        self.schedule: Schedule = None

    def setup(
        self,
        owner_name: str,
        pet_name: str,
        species: str,
        available_minutes: int = 120,
        pet_age: float = 0.0,
        pet_breed: str = "",
        pet_special_needs: list = None,
    ):
        """Initialize the owner, pet, and schedule."""
        self.owner = Owner(name=owner_name, available_minutes=available_minutes)
        self.pet = Pet(
            name=pet_name,
            species=species,
            breed=pet_breed,
            age=pet_age,
            special_needs=pet_special_needs,
        )
        self.schedule = Schedule(pet=self.pet, owner=self.owner)

    def add_task(
        self,
        title: str,
        category: str,
        duration_minutes: int,
        priority: int,
        time_preference: str = None,
        notes: str = "",
    ):
        """Create a Task and add it to the schedule."""
        if self.schedule is None:
            raise RuntimeError("Call setup() before adding tasks.")
        task = Task(
            title=title,
            category=category,
            duration_minutes=duration_minutes,
            priority=priority,
            time_preference=time_preference,
            notes=notes,
        )
        self.schedule.add_task(task)

    def run_schedule(self) -> str:
        """Generate the plan and return the summary string."""
        if self.schedule is None:
            raise RuntimeError("Call setup() before running the schedule.")
        self.schedule.generate_plan()
        return self.schedule.get_plan_summary()

    def get_summary(self) -> str:
        """Return a full system summary including pet/owner info and the plan."""
        if self.owner is None or self.pet is None:
            return "System not initialized. Call setup() first."
        lines = [
            self.owner.get_info(),
            self.pet.get_info(),
            "",
            self.schedule.get_plan_summary() if self.schedule.plan else "(no plan generated)",
            "",
            self.schedule.explain_reasoning() if self.schedule.plan else "",
        ]
        return "\n".join(lines)
