# PawPal+ Project Reflection

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
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
