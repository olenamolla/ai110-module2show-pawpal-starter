import streamlit as st
from pawpal_system import Pet, Task, Owner, Scheduler, ScheduledSlot

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

if "owner" not in st.session_state:
    st.session_state.owner = None
if "scheduler" not in st.session_state:
    st.session_state.scheduler = None

st.title("🐾 PawPal+")
st.markdown("A pet care planning assistant that helps you stay on top of daily tasks.")

st.divider()

# --- Owner Setup ---
st.subheader("Owner Info")
col_o1, col_o2 = st.columns(2)
with col_o1:
    owner_name = st.text_input("Owner name", value="Jordan")
with col_o2:
    available_minutes = st.number_input("Available minutes per day", min_value=10, max_value=480, value=90)

if st.button("Save Owner"):
    st.session_state.owner = Owner(name=owner_name, available_minutes=int(available_minutes))
    st.session_state.scheduler = None
    st.success(f"Owner '{owner_name}' saved with {available_minutes} min/day.")

if st.session_state.owner is None:
    st.info("Set up an owner above to get started.")
    st.stop()

owner = st.session_state.owner

st.divider()

# --- Add Pet ---
st.subheader("Add a Pet")
col_p1, col_p2, col_p3 = st.columns(3)
with col_p1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col_p2:
    species = st.selectbox("Species", ["dog", "cat", "bird", "rabbit", "other"])
with col_p3:
    breed = st.text_input("Breed", value="")
col_p4, col_p5 = st.columns(2)
with col_p4:
    age = st.number_input("Age", min_value=0, max_value=30, value=2)
with col_p5:
    color = st.text_input("Color", value="")

if st.button("Add Pet"):
    new_pet = Pet(name=pet_name, species=species, breed=breed, age=int(age), color=color)
    owner.add_pet(new_pet)
    st.session_state.scheduler = None
    st.success(f"Added {new_pet.summary()}")

if owner.pets:
    st.write("Your pets:")
    for p in owner.pets:
        st.write(f"- {p.summary()}")
else:
    st.info("Add at least one pet to continue.")
    st.stop()

st.divider()

# --- Add Tasks ---
st.subheader("Add Tasks")
pet_names = [p.name for p in owner.pets]
selected_pet_name = st.selectbox("Select pet", pet_names)
selected_pet = next(p for p in owner.pets if p.name == selected_pet_name)

col_t1, col_t2 = st.columns(2)
with col_t1:
    task_name = st.text_input("Task name", value="Morning walk")
with col_t2:
    category = st.selectbox("Category", ["walk", "feeding", "meds", "enrichment", "grooming"])
col_t3, col_t4, col_t5 = st.columns(3)
with col_t3:
    duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
with col_t4:
    priority = st.selectbox("Priority", ["high", "medium", "low"])
with col_t5:
    frequency = st.number_input("Times per day", min_value=1, max_value=5, value=1)

if st.button("Add Task"):
    new_task = Task(
        name=task_name, category=category, duration=int(duration),
        priority=priority, frequency=int(frequency),
    )
    selected_pet.add_task(new_task)
    st.session_state.scheduler = None
    st.success(f"Added '{task_name}' to {selected_pet.name}")

all_tasks = owner.get_all_tasks()
if all_tasks:
    st.write("All tasks:")
    task_data = [
        {"Pet": pet.name, "Task": task.name, "Category": task.category,
         "Duration": f"{task.duration} min", "Priority": task.priority,
         "Frequency": f"{task.frequency}x/day"}
        for pet, task in all_tasks
    ]
    st.table(task_data)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# --- Generate Schedule ---
st.subheader("Today's Schedule")
day_start = st.text_input("Day starts at", value="08:00")

if st.button("Generate Schedule"):
    scheduler = Scheduler(owner=owner, day_start=day_start)
    scheduler.generate_plan()
    st.session_state.scheduler = scheduler

if st.session_state.scheduler:
    scheduler = st.session_state.scheduler
    if scheduler.daily_plan:
        schedule_data = [
            {"Time": slot.start_time, "Task": slot.task.name,
             "Category": slot.task.category, "Duration": f"{slot.task.duration} min",
             "Occurrence": f"#{slot.occurrence}" if slot.task.frequency > 1 else "-"}
            for slot in scheduler.daily_plan
        ]
        st.table(schedule_data)

        unscheduled = scheduler.get_unscheduled_tasks()
        if unscheduled:
            st.warning("Could not fit:")
            for task in unscheduled:
                st.write(f"- {task.name} ({task.total_time()} min, {task.priority} priority)")

        with st.expander("Reasoning"):
            st.text(scheduler.get_reasoning())
    else:
        st.info("No tasks to schedule.")
