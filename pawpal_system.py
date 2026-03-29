from dataclasses import dataclass, field


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int
    color: str
    favorite_activities: list[str] = field(default_factory=list)
    special_instructions: str = ""

    def update(self, **kwargs) -> None:
        pass

    def summary(self) -> str:
        pass


@dataclass
class Task:
    name: str
    category: str  # walk, feeding, meds, enrichment, grooming
    duration: int  # in minutes
    priority: str  # high, medium, low
    pet: Pet = None
    frequency: int = 1
    is_completed: int = 0

    def update(self, **kwargs) -> None:
        pass

    def mark_complete(self) -> None:
        pass

    def is_fully_done(self) -> bool:
        pass

    def total_time(self) -> int:
        pass


class Owner:
    def __init__(self, name: str, available_minutes: int, preferences: str = ""):
        self.name = name
        self.available_minutes = available_minutes
        self.preferences = preferences
        self.pets: list[Pet] = []
        self.tasks: list[Task] = []

    def update(self, **kwargs) -> None:
        pass

    def add_pet(self, pet: Pet) -> None:
        pass

    def remove_pet(self, pet: Pet) -> None:
        pass

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task: Task) -> None:
        pass

    def get_tasks_for_pet(self, pet: Pet) -> list[Task]:
        pass


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner
        self.daily_plan: list[Task] = []

    def generate_plan(self) -> list[Task]:
        pass

    def get_reasoning(self) -> str:
        pass

    def get_unscheduled_tasks(self) -> list[Task]:
        pass
