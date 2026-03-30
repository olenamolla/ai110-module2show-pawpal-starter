from pawpal_system import Pet, Task, Owner, Scheduler

# Create owner
owner = Owner(name="Olena", available_minutes=90, preferences="walks first")

# Create pets
bella = Pet(name="Bella", species="dog", breed="Golden Retriever", age=3, color="golden")
milo = Pet(name="Milo", species="cat", breed="Siamese", age=5, color="cream")

owner.add_pet(bella)
owner.add_pet(milo)

# Add tasks to pets
bella.add_task(Task(name="Morning walk", category="walk", duration=30, priority="high"))
bella.add_task(Task(name="Feeding", category="feeding", duration=10, priority="high", frequency=2))
milo.add_task(Task(name="Grooming", category="grooming", duration=20, priority="medium"))
milo.add_task(Task(name="Play time", category="enrichment", duration=15, priority="low"))

# Generate schedule
scheduler = Scheduler(owner=owner, day_start="07:00")
scheduler.generate_plan()

# Print schedule
print(f"Owner: {owner.name} | Available: {owner.available_minutes} min")
print(f"Pets: {bella.summary()}")
print(f"      {milo.summary()}")
print()
print("=== Today's Schedule ===")
for slot in scheduler.daily_plan:
    label = f" (#{slot.occurrence})" if slot.task.frequency > 1 else ""
    print(f"  {slot.start_time} — {slot.task.name}{label} [{slot.task.category}] ({slot.task.duration} min)")

# Show dropped tasks
unscheduled = scheduler.get_unscheduled_tasks()
if unscheduled:
    print()
    print("=== Could Not Fit ===")
    for task in unscheduled:
        print(f"  {task.name} — {task.total_time()} min needed ({task.priority} priority)")

# Show reasoning
print()
print("=== Reasoning ===")
print(scheduler.get_reasoning())
