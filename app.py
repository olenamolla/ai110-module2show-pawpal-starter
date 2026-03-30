from datetime import date, time as dt_time

import streamlit as st
from pawpal_system import Pet, Task, Owner, Scheduler, ScheduledSlot

PRIORITY_ICONS = {"high": "🔴", "medium": "🟡", "low": "🟢"}
CATEGORY_ICONS = {
    "walk": "🚶", "feeding": "🍽️", "meds": "💊",
    "enrichment": "🧩", "grooming": "✂️",
}

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

# --- Session state defaults ---
# owners: dict mapping owner name -> Owner object
# schedulers: dict mapping owner name -> Scheduler object
# active_owner: name of the currently selected owner
if "owners" not in st.session_state:
    st.session_state.owners = {}
if "schedulers" not in st.session_state:
    st.session_state.schedulers = {}
if "active_owner" not in st.session_state:
    st.session_state.active_owner = None


# ================================================================
# SIDEBAR — Setup (Owner, Pets, Tasks)
# ================================================================
with st.sidebar:
    st.title("🐾 PawPal+")
    st.caption("Your pet care planning assistant")

    # --- Owner Setup ---
    st.header("Owner Setup")
    owner_name = st.text_input("Owner name", value="Jordan")
    available_minutes = st.slider(
        "Available minutes per day", min_value=10, max_value=480, value=90, step=5,
    )
    if st.button("Save Owner", use_container_width=True):
        if owner_name.strip() == "":
            st.error("Owner name cannot be empty.")
        elif owner_name in st.session_state.owners:
            # Update existing owner's minutes
            st.session_state.owners[owner_name].available_minutes = int(available_minutes)
            st.session_state.schedulers.pop(owner_name, None)
            st.success(f"Updated {owner_name} to {available_minutes} min/day")
        else:
            st.session_state.owners[owner_name] = Owner(
                name=owner_name, available_minutes=int(available_minutes),
            )
            st.success(f"Saved {owner_name} ({available_minutes} min/day)")
        st.session_state.active_owner = owner_name

    if not st.session_state.owners:
        st.info("Save an owner to get started.")
        st.stop()

    st.divider()

    # --- Select Active Owner ---
    st.header("Switch Owner")
    owner_names = list(st.session_state.owners.keys())
    active_name = st.selectbox(
        "Active owner",
        owner_names,
        index=owner_names.index(st.session_state.active_owner)
        if st.session_state.active_owner in owner_names
        else 0,
        key="owner_selector",
    )
    st.session_state.active_owner = active_name
    owner = st.session_state.owners[active_name]

    st.caption(
        f"**{owner.name}** — {owner.available_minutes} min/day, "
        f"{len(owner.pets)} pet(s), "
        f"{len(owner.get_all_tasks())} task(s)"
    )

    st.divider()

    # --- Add Pet ---
    st.header("Add a Pet")
    pet_name = st.text_input("Pet name", value="Mochi")
    col_sp, col_br = st.columns(2)
    with col_sp:
        species = st.selectbox("Species", ["dog", "cat", "bird", "rabbit", "other"])
    with col_br:
        breed = st.text_input("Breed", value="")
    col_ag, col_co = st.columns(2)
    with col_ag:
        age = st.number_input("Age", min_value=0, max_value=30, value=2)
    with col_co:
        color = st.text_input("Color", value="")

    if st.button("Add Pet", use_container_width=True):
        new_pet = Pet(name=pet_name, species=species, breed=breed, age=int(age), color=color)
        owner.add_pet(new_pet)
        st.session_state.schedulers.pop(active_name, None)
        st.success(f"Added {pet_name} to {owner.name}!")

    if not owner.pets:
        st.info("Add at least one pet to continue.")
        st.stop()

    # Show registered pets
    st.markdown("**Your pets:**")
    for p in owner.pets:
        st.markdown(f"- {p.summary()}")

    st.divider()

    # --- Add Task ---
    st.header("Add a Task")
    pet_names = [p.name for p in owner.pets]
    selected_pet_name = st.selectbox("For which pet?", pet_names)
    selected_pet = next(p for p in owner.pets if p.name == selected_pet_name)

    task_name = st.text_input("Task name", value="Morning walk")
    category = st.selectbox("Category", ["walk", "feeding", "meds", "enrichment", "grooming"])
    col_dur, col_pri = st.columns(2)
    with col_dur:
        duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
    with col_pri:
        priority = st.selectbox("Priority", ["high", "medium", "low"])
    col_freq, col_rec = st.columns(2)
    with col_freq:
        frequency = st.number_input("Times/day", min_value=1, max_value=5, value=1)
    with col_rec:
        recurrence = st.selectbox("Recurrence", ["none", "daily", "weekly"])

    due_date = None
    if recurrence != "none":
        due_date = st.date_input("Due date", value=date.today())

    use_preferred = st.checkbox("Set a specific start time?")
    preferred_time = None
    if use_preferred:
        preferred_time_obj = st.time_input("Preferred start time", value=dt_time(8, 0))
        preferred_time = preferred_time_obj.strftime("%H:%M")

    if st.button("Add Task", use_container_width=True):
        new_task = Task(
            name=task_name, category=category, duration=int(duration),
            priority=priority, frequency=int(frequency),
            recurrence=recurrence,
            due_date=due_date,
            preferred_time=preferred_time,
        )
        selected_pet.add_task(new_task)
        st.session_state.schedulers.pop(active_name, None)
        st.success(f"Added '{task_name}' to {selected_pet.name}")


# ================================================================
# MAIN AREA
# ================================================================
owner = st.session_state.owners[st.session_state.active_owner]
active_name = st.session_state.active_owner

st.markdown(f"## 🐾 PawPal+ — {owner.name}'s Dashboard")

all_tasks = owner.get_all_tasks()
if not all_tasks:
    st.info(
        "No tasks yet. Use the sidebar to add pets and tasks, "
        "then come back here to generate your schedule."
    )
    st.stop()

tab_schedule, tab_progress, tab_tasks, tab_owners = st.tabs([
    "📅 Today's Schedule",
    "✅ Track Progress",
    "📋 All Tasks",
    "👥 All Owners",
])


# ── Tab 1: Today's Schedule ────────────────────────────────────────
with tab_schedule:
    col_start, col_gen = st.columns([2, 1])
    with col_start:
        day_start = st.text_input("Day starts at", value="08:00", key="day_start")
    with col_gen:
        st.markdown("<br>", unsafe_allow_html=True)
        generate = st.button("Generate Schedule", use_container_width=True, type="primary")

    if generate:
        scheduler = Scheduler(owner=owner, day_start=day_start)
        scheduler.generate_plan()
        scheduler.sort_by_time()
        st.session_state.schedulers[active_name] = scheduler

    scheduler = st.session_state.schedulers.get(active_name)

    if scheduler and scheduler.daily_plan:
        # Metrics row
        total_scheduled = len(scheduler.daily_plan)
        total_minutes = sum(s.task.duration for s in scheduler.daily_plan)
        remaining = owner.available_minutes - total_minutes
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("Scheduled", total_scheduled)
        col_m2.metric("Planned", f"{total_minutes} min")
        col_m3.metric("Remaining", f"{remaining} min")
        col_m4.metric("Budget", f"{owner.available_minutes} min")

        st.markdown("---")

        # Schedule as visual cards
        for slot in scheduler.daily_plan:
            t = slot.task
            cat_icon = CATEGORY_ICONS.get(t.category, "📌")
            pri_icon = PRIORITY_ICONS.get(t.priority, "⚪")
            occ_label = f" (#{slot.occurrence})" if t.frequency > 1 else ""
            rec_label = f" | Repeats {t.recurrence}" if t.recurrence != "none" else ""

            with st.container():
                col_time, col_detail = st.columns([1, 4])
                with col_time:
                    st.markdown(f"### {slot.start_time}")
                with col_detail:
                    st.markdown(
                        f"**{cat_icon} {t.name}**{occ_label}  \n"
                        f"{pri_icon} {t.priority} &nbsp;|&nbsp; "
                        f"{t.duration} min &nbsp;|&nbsp; "
                        f"{t.category}{rec_label}"
                    )
                st.divider()

        # Conflicts
        conflicts = scheduler.detect_conflicts()
        if conflicts:
            st.subheader("⚠️ Schedule Conflicts")
            for warning in conflicts:
                st.error(f"**Time Overlap Detected**\n\n{warning}")
                st.caption(
                    "Tip: Adjust the duration or start time of one of these tasks "
                    "so they no longer overlap. High-priority tasks like meds "
                    "should keep their slot."
                )
        else:
            st.success("No scheduling conflicts — you're all set!")

        # Unscheduled
        unscheduled = scheduler.get_unscheduled_tasks()
        if unscheduled:
            st.subheader("Could Not Fit")
            for task in unscheduled:
                icon = PRIORITY_ICONS.get(task.priority, "⚪")
                st.warning(
                    f"**{task.name}** ({icon} {task.priority}) needs "
                    f"{task.total_time()} min but only {remaining} min remain. "
                    f"Try freeing up time or reducing the duration."
                )

        # Reasoning
        with st.expander("View Scheduling Reasoning"):
            st.code(scheduler.get_reasoning(), language=None)

    elif scheduler:
        st.info("No tasks to schedule. Add tasks in the sidebar.")
    else:
        st.info("Click **Generate Schedule** to build your daily plan.")


# ── Tab 2: Track Progress ──────────────────────────────────────────
with tab_progress:
    scheduler = st.session_state.schedulers.get(active_name)

    if not scheduler or not scheduler.daily_plan:
        st.info("Generate a schedule first in the **Today's Schedule** tab.")
    else:
        st.subheader("Mark Tasks Complete")

        # Show current progress overview
        for slot in scheduler.daily_plan:
            t = slot.task
            cat_icon = CATEGORY_ICONS.get(t.category, "📌")
            done_ratio = t.is_completed / t.frequency
            status = "✅ Done" if t.is_fully_done() else f"⏳ {t.is_completed}/{t.frequency}"

            col_info, col_bar = st.columns([2, 3])
            with col_info:
                occ_label = f" #{slot.occurrence}" if t.frequency > 1 else ""
                st.markdown(f"**{cat_icon} {t.name}**{occ_label} — {status}")
            with col_bar:
                st.progress(done_ratio)

        st.markdown("---")

        # Complete a task
        slot_labels = [
            f"{s.start_time} — {s.task.name}"
            + (f" #{s.occurrence}" if s.task.frequency > 1 else "")
            for s in scheduler.daily_plan
        ]
        selected_slot_label = st.selectbox("Select a task to complete", slot_labels)
        if st.button("Mark Complete", type="primary", use_container_width=True):
            slot_idx = slot_labels.index(selected_slot_label)
            slot = scheduler.daily_plan[slot_idx]
            pet = next(p for p in owner.pets for t in p.tasks if t is slot.task)
            next_task = scheduler.mark_task_complete(pet, slot.task)
            if slot.task.is_fully_done():
                st.success(f"'{slot.task.name}' fully completed!")
                st.balloons()
                if next_task:
                    st.info(
                        f"Next {slot.task.recurrence} occurrence of "
                        f"'{next_task.name}' auto-created for **{next_task.due_date}**."
                    )
            else:
                st.success(
                    f"'{slot.task.name}' — "
                    f"{slot.task.is_completed}/{slot.task.frequency} completions"
                )
                st.rerun()


# ── Tab 3: All Tasks ───────────────────────────────────────────────
with tab_tasks:
    st.subheader(f"{owner.name}'s Task List")

    # Filters
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        filter_pet = st.selectbox(
            "Filter by pet", ["All"] + [p.name for p in owner.pets], key="filter_pet"
        )
    with col_f2:
        filter_status = st.selectbox(
            "Filter by status", ["All", "Incomplete", "Complete"], key="filter_status"
        )

    pet_filter = None if filter_pet == "All" else filter_pet
    completed_filter = (
        None if filter_status == "All"
        else filter_status == "Complete"
    )
    filtered = owner.filter_tasks(pet_name=pet_filter, completed=completed_filter)

    if filtered:
        STATUS_ICONS = {True: "✅", False: "⏳"}
        st.table([
            {
                "Pet": pet.name,
                "Task": f"{CATEGORY_ICONS.get(task.category, '📌')} {task.name}",
                "Priority": f"{PRIORITY_ICONS.get(task.priority, '⚪')} {task.priority}",
                "Duration": f"{task.duration} min",
                "Freq.": f"{task.frequency}x/day",
                "Status": (
                    f"{STATUS_ICONS[task.is_fully_done()]} "
                    f"{'Done' if task.is_fully_done() else f'{task.is_completed}/{task.frequency}'}"
                ),
                "Repeats": task.recurrence if task.recurrence != "none" else "-",
                "Due": str(task.due_date) if task.due_date else "-",
            }
            for pet, task in filtered
        ])

        # Summary stats
        total = len(filtered)
        done = sum(1 for _, t in filtered if t.is_fully_done())
        st.caption(f"Showing {total} tasks — {done} complete, {total - done} remaining")
    else:
        st.info("No tasks match the current filter.")


# ── Tab 4: All Owners ─────────────────────────────────────────────
with tab_owners:
    st.subheader("All Owners Overview")

    if not st.session_state.owners:
        st.info("No owners yet.")
    else:
        for oname, o in st.session_state.owners.items():
            is_active = oname == active_name
            label = f"**{o.name}** (active)" if is_active else f"**{o.name}**"

            with st.container():
                st.markdown(f"### {label}")
                col_s1, col_s2, col_s3 = st.columns(3)
                col_s1.metric("Available", f"{o.available_minutes} min/day")
                col_s2.metric("Pets", len(o.pets))
                col_s3.metric("Tasks", len(o.get_all_tasks()))

                # Show pets and tasks
                if o.pets:
                    for p in o.pets:
                        with st.expander(f"{p.name} — {p.species}, {p.breed}"):
                            if p.tasks:
                                st.table([
                                    {
                                        "Task": f"{CATEGORY_ICONS.get(t.category, '📌')} {t.name}",
                                        "Priority": f"{PRIORITY_ICONS.get(t.priority, '⚪')} {t.priority}",
                                        "Duration": f"{t.duration} min",
                                        "Freq.": f"{t.frequency}x/day",
                                        "Repeats": t.recurrence if t.recurrence != "none" else "-",
                                    }
                                    for t in p.tasks
                                ])
                            else:
                                st.caption("No tasks for this pet yet.")

                # Show schedule summary if one exists
                sched = st.session_state.schedulers.get(oname)
                if sched and sched.daily_plan:
                    with st.expander("View Schedule"):
                        st.table([
                            {
                                "Time": s.start_time,
                                "Task": f"{CATEGORY_ICONS.get(s.task.category, '📌')} {s.task.name}",
                                "Duration": f"{s.task.duration} min",
                                "Priority": f"{PRIORITY_ICONS.get(s.task.priority, '⚪')} {s.task.priority}",
                            }
                            for s in sched.daily_plan
                        ])
                        conflicts = sched.detect_conflicts()
                        if conflicts:
                            for w in conflicts:
                                st.error(w)
                        else:
                            st.success("No conflicts")
                else:
                    st.caption("No schedule generated yet.")

                st.divider()
