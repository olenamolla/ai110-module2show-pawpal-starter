# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

**Initial UML Design:**

The system is built around four classes, each with a clear responsibility:

- **Pet** (dataclass): Holds all descriptive information about a pet — name, species, breed, age, color, favorite activities, and special instructions (e.g., illnesses or dietary needs). Its main responsibility is storing pet data and providing a readable summary. Breed and color are display-only and do not affect scheduling.

- **Owner**: Represents the pet owner and acts as the central hub of the system. It stores the owner's name, daily available time (in minutes), and preferences. It also manages lists of pets and tasks, with methods to add, remove, and filter them. An owner can have multiple pets.

- **Task** (dataclass): Represents a single care activity such as a walk, feeding, or grooming session. Each task has a name, category, duration, priority (high/medium/low), frequency (how many times per day), and a reference to the pet it belongs to. It tracks completion count against frequency so repeating tasks (e.g., feeding twice a day) are handled correctly.

- **Scheduler**: Contains the core planning logic. It takes an Owner, reads their tasks and available time, and generates an optimized daily plan. It sorts tasks by priority, fits them within the time budget, and can explain its reasoning. It also tracks which tasks were dropped if time ran out.

The relationships are: Owner has many Pets, Owner has many Tasks, each Task is assigned to one Pet, and Scheduler reads from the Owner to build the plan.

**Core User Actions:**

1. **Add a pet (and owner profile):** The user enters basic information about themselves (name, time available per day) and their pet (name, species, age). This sets up the context the scheduler needs to build a personalized plan.

2. **Add or edit a care task:** The user creates pet care tasks such as walks, feeding, medication, enrichment, or grooming. Each task includes at least a duration and a priority level. Tasks can be edited later if the owner's needs or the pet's routine changes.

3. **Generate and view a daily plan:** The user requests a daily schedule. The system considers all added tasks, their priorities, and the owner's available time, then produces an optimized plan for the day. The plan is displayed clearly and includes reasoning for why tasks were ordered or included the way they were.

**b. Design changes**

- Did your design change during implementation?

Yes. 

- If yes, describe at least one change and why you made it.

Yes, the design changed after reviewing the skeleton for logic bottlenecks. Three issues were identified and addressed:

1. **Added a new `ScheduledSlot` class.** The original design stored the daily plan as a flat `list[Task]`, but this caused two problems: repeating tasks (e.g., feeding twice a day) would mean the same Task object appearing multiple times with no way to tell them apart, and there was no concept of *when* each task happens. `ScheduledSlot` wraps a Task with a `start_time` (e.g., "08:00") and an `occurrence` number (1st feeding vs 2nd feeding), giving each entry in the plan a clear identity and time placement.

2. **Added reasoning storage to the Scheduler.** The original `get_reasoning()` method had no data to work with — `generate_plan()` had no way to record *why* it made decisions. A private `_reasoning: list[str]` attribute was added so the scheduler can log explanations as it builds the plan (e.g., "Medication scheduled first because it is high priority").

3. **Added `_unscheduled` tracking and `day_start` to the Scheduler.** A private `_unscheduled: list[Task]` attribute was added so `get_unscheduled_tasks()` has a concrete list to return. A `day_start` parameter (defaulting to "08:00") was also added so the scheduler knows what time to begin assigning slots from.

4. **Moved task ownership from Owner to Pet.** Originally, Owner held a flat `tasks` list and each Task had a `pet` reference pointing back. This was redundant. Tasks now live on each Pet (`pet.tasks`), and Owner collects them via `get_all_tasks()` which returns `(pet, task)` tuples across all pets. This makes the data flow cleaner: `Scheduler → Owner → Pets → Tasks`.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.

The scheduler uses a greedy single-pass approach: it sorts tasks by priority and packs them in order, never backtracking to try a better combination. This means a large high-priority task could leave a gap too small for the next task, even if rearranging would fit more overall.

- Why is that tradeoff reasonable for this scenario?

This is reasonable because pet owners need critical tasks (meds, feeding) guaranteed first, and the simplicity keeps the scheduler's decisions easy to understand.

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
