# PawPal+ Project Reflection

## ✨ Features

### 1. Priority-First Greedy Scheduling
Tasks are ranked using a two-key sort: **priority (1–5)** descending, then **category weight** as a tiebreaker (`medication=6 > appointment=5 > feeding=4 > walk=3 > grooming=2 > enrichment=1`). The scheduler iterates this sorted list and greedily fits tasks into the owner's daily time budget — highest-stakes tasks are always selected first.
*Implemented in:* `Scheduler.generate_plan()` → `effective_score()`

### 2. Special Needs Priority Boost
When a pet has entries in `special_needs` (e.g. `"diabetic"`, `"arthritis"`), any `medication` or `appointment` task for that pet receives an automatic **+1 priority boost** (capped at 5). This ensures critical health tasks for vulnerable animals are never bumped by lower-priority tasks of an identical base priority.
*Implemented in:* `Scheduler.generate_plan()` → `effective_score()`

### 3. Time-Slot Display Sorting
After budget allocation, the scheduled plan is re-sorted by `time_preference` for display: **morning → afternoon → evening → flexible**. If the owner's `preferences["morning_person"]` is `False`, the order flips to **evening → afternoon → morning**. Crucially, this sort only affects the *display* — it never changes which tasks were selected.
*Implemented in:* `Scheduler.generate_plan()` — post-allocation `.sort()`

### 4. Daily Time Budget Enforcement
The scheduler tracks `time_used` against `owner.available_minutes`. Tasks that push usage over budget are skipped and logged with a reason: `"not enough time remaining"` (budget exceeded mid-list) vs. `"task duration exceeds daily budget"` (single task longer than the entire day).
*Implemented in:* `Scheduler.generate_plan()`

### 5. Conflict Detection
After generating a plan, `find_conflicts()` scans for two types of scheduling conflicts:
- **Same-pet / same-slot**: one pet has multiple tasks assigned to the same time slot (e.g. two morning tasks).
- **Slot overload**: total minutes in a named slot exceed its capacity (`morning=120`, `afternoon=120`, `evening=90` min).
Conflicts are returned as human-readable warning strings and surfaced as `st.warning()` boxes in the UI.
*Implemented in:* `Scheduler.find_conflicts()`

### 6. Daily Recurrence
When `mark_complete()` is called on a `daily` or `weekly` task, it automatically calls `task.next_occurrence()` to create a copy of the task with `due_date` advanced by the interval (1 day or 7 days). The new task is immediately appended to the pet's task list, ready for the next scheduling run. Tasks with `frequency="once"` or `"as_needed"` produce no recurrence.
*Implemented in:* `Task.next_occurrence()`, `Scheduler.mark_complete()`

### 7. Task Completion Tracking & Day Reset
Every `Task` carries a `completed` flag and a `due_date`. `Scheduler.mark_all_complete()` finishes every task in one call. `Scheduler.reset_day()` clears `completed` on every task across all pets and wipes the plan, allowing a fresh `generate_plan()` call the next morning.
*Implemented in:* `Task.complete()`, `Task.reset()`, `Scheduler.reset_day()`

### 8. Cross-Pet Task Filtering
`Owner.filter_by_pet(name)` returns all `(Pet, Task)` pairs for a single named pet (case-insensitive). `Owner.filter_by_status(completed=True/False)` returns pairs matching a completion state across *all* pets. These power the pending/completed metrics and per-pet task breakdown in the UI.
*Implemented in:* `Owner.filter_by_pet()`, `Owner.filter_by_status()`

### 9. Senior Pet Detection
`Pet.is_senior()` checks the pet's age against a species-specific threshold (`dog ≥ 7 yrs`, `cat ≥ 10 yrs`, others default to 10). This is displayed as a `[Senior]` badge in `get_info()` and is designed to be extended — e.g., future versions could auto-boost medication priorities for senior pets.
*Implemented in:* `Pet.is_senior()`

---

## 1. System Design

Three core actions the user should be able to perform is scheduling walks, scheduling feeding, as well as enrichment. 

**a. Initial design**

- Briefly describe your initial UML design.

At first I sketched a simple UML with User, Pet, Schedule, and maybe Task/Activity.
User owns pets and preferences, Pet has stuff like energy level, Schedule manages time slots, and Task is “walk/feed/enrich”.
I gave each class one main job (e.g., scheduler decides if a slot is free and fits constraints, task knows duration/type).

- What classes did you include, and what responsibilities did you assign to each?

- **User**: Manages account data, pet collection, and preferences (e.g., work hours, notification settings).
- **Pet**: Stores attributes like name, breed, age, energy level, and last activity timestamp.
- **Schedule**: Maintains a calendar of time slots and checks availability based on pet constraints and user availability.
- **Task/Activity**: Represents a specific action (walk, feed, enrich) with duration, type, and priority level.
- **Scheduler**: Orchestrates task assignment by evaluating constraints and finding optimal time slots for each activity.



**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- **Constraints**: The scheduler considers pet energy levels, user availability windows, task priority (walks > feeding > enrichment), and time since last activity. We weight energy level heavily—high-energy pets need walks sooner, while low-energy ones can wait longer.
- **Why these mattered most**: Time availability is a hard limit (can't schedule outside work hours), and energy level directly affects pet health, so those became our top priorities. Priority ranking came from what makes the most sense—pets gotta eat, but a bored pet isn't as urgent as a hungry one.

**b. Tradeoffs**

- **Speed vs. optimality**: We prioritize finding a valid slot quickly over always finding the absolute best time. For a busy pet owner, a good schedule now beats a perfect one tomorrow.
- **Why it works**: Pet care is time-sensitive—scheduling a walk in 30 seconds that fits most constraints beats spending minutes searching for the mathematically optimal slot. Real users won't wait, and "good enough" keeps pets happy and owners sane.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
I used AI for initial architecture brainstorming to validate my three-class model, and later for debugging priority-sorting logic when tasks weren't ranking correctly.

- What kinds of prompts or questions were most helpful?
Specific code questions like "why isn't my sort by priority then category weight working?" and "how do I detect time-slot conflicts?" were most useful—AI excels at targeted debugging.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
AI suggested using a dictionary lookup for category weights, but I kept the explicit enum-style constants for readability and future extensibility.

- How did you evaluate or verify what the AI suggested?
I tested both approaches locally against sample task lists to see which produced clearer, more maintainable code.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
I tested budget enforcement (tasks over limit are skipped), priority ranking (medication tasks always beat grooming), conflict detection (same-slot duplicates and slot overload), and recurrence (daily tasks generate next-day copies).

- Why were these tests important?
These are the core promises of the scheduler—if budget breaks or priorities invert, the whole system fails; users won't trust it.

**b. Confidence**

- How confident are you that your scheduler works correctly?
About 80%—happy path and most constraints work, but I haven't stress-tested with 50+ tasks or unusual edge cases.

- What edge cases would you test next if you had more time?
Tasks with zero duration, all tasks exceeding daily budget, a pet with conflicting special needs, and rapid mark-complete/reset-day cycles.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
The two-key sort (priority + category weight) is elegant and immediately makes scheduling decisions transparent and defensible.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
I'd add a "snooze" or "defer" mechanism for skipped tasks so they don't vanish, and I'd refactor conflict detection into a cleaner validation pipeline.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
Constraints and tradeoffs should be explicit from the start—AI helps implement them, but *you* must decide what "good enough" means for your users.

