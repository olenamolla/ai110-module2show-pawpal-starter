from dataclasses import dataclass, field

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int
    color: str
    favorite_activities: list[str] = field(default_factory=list)
    special_instructions: str = ""
    tasks: list["Task"] = field(default_factory=list)

    def add_task(self, task: "Task") -> None:
        """Append a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task: "Task") -> None:
        """Remove a task from this pet's task list."""
        self.tasks.remove(task)

    def update(self, **kwargs) -> None:
        """Update one or more pet attributes by keyword."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def summary(self) -> str:
        """Return a human-readable one-line description of this pet."""
        base = f"{self.name} — {self.age}-year-old {self.color} {self.breed} ({self.species})"
        if self.special_instructions:
            base += f" | Note: {self.special_instructions}"
        return base


@dataclass
class Task:
    name: str
    category: str  # walk, feeding, meds, enrichment, grooming
    duration: int  # in minutes
    priority: str  # high, medium, low
    frequency: int = 1
    is_completed: int = 0

    def update(self, **kwargs) -> None:
        """Update one or more task attributes by keyword."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def mark_complete(self) -> None:
        """Increment completion count by one, up to the task's frequency."""
        if not self.is_fully_done():
            self.is_completed += 1

    def is_fully_done(self) -> bool:
        """Return True if all occurrences of this task are completed."""
        return self.is_completed >= self.frequency

    def total_time(self) -> int:
        """Return total daily time needed: duration * frequency."""
        return self.duration * self.frequency


@dataclass
class ScheduledSlot:
    """A single scheduled occurrence of a task with a start time."""
    task: Task
    start_time: str  # e.g. "08:00"
    occurrence: int = 1  # which occurrence (1st, 2nd, etc.) for repeating tasks


class Owner:
    def __init__(self, name: str, available_minutes: int, preferences: str = ""):
        self.name = name
        self.available_minutes = available_minutes
        self.preferences = preferences
        self.pets: list[Pet] = []

    def update(self, **kwargs) -> None:
        """Update one or more owner attributes by keyword."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner's list."""
        self.pets.remove(pet)

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Collect all tasks across all pets as (pet, task) tuples."""
        all_tasks = []
        for pet in self.pets:
            for task in pet.tasks:
                all_tasks.append((pet, task))
        return all_tasks


class Scheduler:
    def __init__(self, owner: Owner, day_start: str = "08:00"):
        self.owner = owner
        self.day_start = day_start
        self.daily_plan: list[ScheduledSlot] = []
        self._unscheduled: list[Task] = []
        self._reasoning: list[str] = []

    def _minutes_to_time(self, total_minutes: int) -> str:
        """Convert total minutes since midnight to 'HH:MM' format."""
        hours = total_minutes // 60
        minutes = total_minutes % 60
        return f"{hours:02d}:{minutes:02d}"

    def _time_to_minutes(self, time_str: str) -> int:
        """Convert 'HH:MM' format to total minutes since midnight."""
        hours, minutes = time_str.split(":")
        return int(hours) * 60 + int(minutes)

    def generate_plan(self) -> list[ScheduledSlot]:
        """Build a daily schedule sorted by priority, fitting within the owner's time budget."""
        self.daily_plan = []
        self._unscheduled = []
        self._reasoning = []

        all_tasks = self.owner.get_all_tasks()
        sorted_tasks = sorted(
            all_tasks,
            key=lambda pt: PRIORITY_ORDER.get(pt[1].priority, 99),
        )

        remaining_minutes = self.owner.available_minutes
        current_minutes = self._time_to_minutes(self.day_start)

        for pet, task in sorted_tasks:
            time_needed = task.total_time()

            if time_needed <= remaining_minutes:
                for occ in range(1, task.frequency + 1):
                    start = self._minutes_to_time(current_minutes)
                    self.daily_plan.append(
                        ScheduledSlot(task=task, start_time=start, occurrence=occ)
                    )
                    current_minutes += task.duration
                remaining_minutes -= time_needed
                self._reasoning.append(
                    f"Scheduled '{task.name}' ({task.priority} priority, "
                    f"{task.frequency}x{task.duration}min) for {pet.name}."
                )
            else:
                self._unscheduled.append(task)
                self._reasoning.append(
                    f"Dropped '{task.name}' ({task.priority} priority, "
                    f"{time_needed}min needed) — only {remaining_minutes}min left."
                )

        return self.daily_plan

    def get_reasoning(self) -> str:
        """Return a human-readable explanation of all scheduling decisions."""
        return "\n".join(self._reasoning)

    def get_unscheduled_tasks(self) -> list[Task]:
        """Return tasks that were dropped due to insufficient time."""
        return list(self._unscheduled)
