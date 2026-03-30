"""
main.py — PawPal+ conflict detection demo
Run with: python3 main.py
"""

from pawpal_system import Owner, Pet, Task, Scheduler

# ── Setup ──────────────────────────────────────────────────────────────────
jordan = Owner(name="Jordan", available_minutes=240,
               preferences={"morning_person": True})

mochi = Pet(name="Mochi", species="dog", age=8.0, special_needs=["arthritis"])
luna  = Pet(name="Luna",  species="cat", age=3.0)

# -- Mochi: two tasks intentionally placed in the same 'morning' slot -------
mochi.add_task(Task("Joint supplement", "medication", duration_minutes=5,  priority=5,
                    frequency="daily",  time_preference="morning"))
mochi.add_task(Task("Morning walk",     "walk",       duration_minutes=30, priority=3,
                    frequency="daily",  time_preference="morning"))   # conflict: same pet, same slot
mochi.add_task(Task("Breakfast",        "feeding",    duration_minutes=10, priority=4,
                    frequency="daily",  time_preference="morning"))   # conflict: same pet, same slot

# -- Luna: tasks that together overload the evening slot (>90 min) ----------
luna.add_task(Task("Wet food dinner",   "feeding",    duration_minutes=5,  priority=4,
                   frequency="daily",   time_preference="evening"))
luna.add_task(Task("Grooming session",  "grooming",   duration_minutes=50, priority=3,
                   frequency="weekly",  time_preference="evening"))
luna.add_task(Task("Enrichment play",   "enrichment", duration_minutes=45, priority=2,
                   frequency="daily",   time_preference="evening"))   # pushes evening over 90 min

# -- Cross-pet same slot: both Mochi and Luna in afternoon ------------------
mochi.add_task(Task("Vet check-up",     "appointment", duration_minutes=60, priority=5,
                    frequency="once",   time_preference="afternoon"))
luna.add_task(Task("Vet check-up",      "appointment", duration_minutes=60, priority=5,
                   frequency="once",    time_preference="afternoon"))  # two pets, same slot

jordan.add_pet(mochi)
jordan.add_pet(luna)

# ── Generate and print schedule (conflicts appear at the bottom) ───────────
scheduler = Scheduler(owner=jordan)
scheduler.generate_plan()
print(scheduler.get_plan_summary())

# ── Also call find_conflicts() directly to show raw warning list ───────────
print("\n--- find_conflicts() raw output ---")
conflicts = scheduler.find_conflicts()
if conflicts:
    for w in conflicts:
        print(" ", w)
else:
    print("  No conflicts found.")
