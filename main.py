"""
main.py — PawPal+ testing ground
Run with: python main.py
"""

from pawpal_system import Owner, Pet, Task, Scheduler

# ── 1. Create the owner ────────────────────────────────────────────────────
jordan = Owner(
    name="Jordan",
    available_minutes=90,
    preferences={"morning_person": True},
)

# ── 2. Create two pets ─────────────────────────────────────────────────────
mochi = Pet(name="Mochi", species="dog", breed="Shiba Inu", age=8.0,
            special_needs=["arthritis"])

luna = Pet(name="Luna", species="cat", age=3.0)

# ── 3. Add tasks to Mochi ─────────────────────────────────────────────────
mochi.add_task(Task(
    title="Joint supplement",
    category="medication",
    duration_minutes=5,
    priority=5,
    frequency="daily",
    time_preference="morning",
    notes="Mix into food",
))

mochi.add_task(Task(
    title="Morning walk",
    category="walk",
    duration_minutes=30,
    priority=3,
    frequency="daily",
    time_preference="morning",
))

mochi.add_task(Task(
    title="Breakfast",
    category="feeding",
    duration_minutes=10,
    priority=4,
    frequency="daily",
    time_preference="morning",
))

# ── 4. Add tasks to Luna ──────────────────────────────────────────────────
luna.add_task(Task(
    title="Wet food dinner",
    category="feeding",
    duration_minutes=5,
    priority=4,
    frequency="daily",
    time_preference="evening",
))

luna.add_task(Task(
    title="Vet check-up",
    category="appointment",
    duration_minutes=60,
    priority=5,
    frequency="once",
    time_preference="afternoon",
    notes="Annual vaccines due",
))

luna.add_task(Task(
    title="Puzzle toy enrichment",
    category="enrichment",
    duration_minutes=15,
    priority=2,
    frequency="as_needed",
    time_preference="evening",
))

# ── 5. Register pets with the owner ───────────────────────────────────────
jordan.add_pet(mochi)
jordan.add_pet(luna)

# ── 6. Run the scheduler ──────────────────────────────────────────────────
scheduler = Scheduler(owner=jordan)
scheduler.generate_plan()

# ── 7. Print today's schedule ─────────────────────────────────────────────
print(jordan.get_info())
print()
print(scheduler.get_plan_summary())
print()
print(scheduler.explain_reasoning())
