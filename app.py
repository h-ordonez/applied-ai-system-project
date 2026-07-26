from datetime import time

import streamlit as st
from pawpal_system import Frequency
from pawpal_system import Task
from pawpal_system import Pet
from pawpal_system import Owner
from pawpal_system import Scheduler


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("Plan and track daily care tasks for your pets.")

st.divider()

owner_name = st.text_input("Owner name", value="Jordan")

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name=owner_name)
if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler(owner=st.session_state.owner)

st.session_state.owner.name = owner_name

st.markdown("### Pets")

pcol1, pcol2, pcol3 = st.columns([2, 2, 1])
with pcol1:
    pet_name = st.text_input("Pet name", value="Mochi")
with pcol2:
    species = st.selectbox("Species", ["dog", "cat", "other"])
with pcol3:
    st.write("")
    if st.button("Add pet"):
        st.session_state.owner.addPet(Pet(name=pet_name, species=species, age=0))
        st.success(f"Added {pet_name} the {species}.")

if st.session_state.owner.petList:
    for p in list(st.session_state.owner.petList):
        rcol1, rcol2 = st.columns([4, 1])
        with rcol1:
            st.write(f"🐾 {p.name} ({p.species})")
        with rcol2:
            if st.button("Remove", key=f"remove_pet_{id(p)}"):
                st.session_state.owner.removePet(p)
                st.toast(f"Removed {p.name}.")
                st.rerun()
else:
    st.info("No pets yet. Add one above to get started.")

st.markdown("### Tasks")

if not st.session_state.owner.petList:
    st.info("Add a pet above before adding tasks.")
else:
    pet_names = [p.name for p in st.session_state.owner.petList]
    selected_pet_name = st.selectbox("Pet", pet_names)
    selected_pet = next(p for p in st.session_state.owner.petList if p.name == selected_pet_name)

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        task_time = st.time_input("Time", value=time(8, 0))
    with col3:
        task_frequency = st.selectbox("Frequency", [f.value for f in Frequency], index=0)

    if st.button("Add task"):
        new_task = Task(
            description=task_title,
            time=task_time.strftime("%H:%M"),
            frequency=Frequency(task_frequency),
        )
        st.session_state.scheduler.scheduleTask(selected_pet, new_task)
        st.success(f"Added '{task_title}' for {selected_pet_name}.")

    current_tasks = st.session_state.scheduler.getTasksByPet(selected_pet)
    if current_tasks:
        st.write("Current tasks:")
        for t in list(current_tasks):
            tcol1, tcol2, tcol3, tcol4, tcol5 = st.columns([3, 1.5, 1.5, 1.5, 1])
            with tcol1:
                st.write(t.description)
            with tcol2:
                st.write(t.time)
            with tcol3:
                st.write(t.frequency.value)
            with tcol4:
                done = st.checkbox("Done", value=t.completed, key=f"done_{id(t)}")
                if done and not t.completed:
                    st.session_state.scheduler.complete_task(selected_pet, t)
                    st.toast(f"'{t.description}' marked done.")
                    st.rerun()
            with tcol5:
                if st.button("Remove", key=f"remove_task_{id(t)}"):
                    st.session_state.scheduler.removeTask(selected_pet, t)
                    st.toast(f"Removed '{t.description}'.")
                    st.rerun()
    else:
        st.info(f"No tasks yet for {selected_pet_name}. Add one above.")

st.divider()

st.subheader("Today's Schedule")

if not st.session_state.owner.petList:
    st.info("Add a pet and some tasks above to build a schedule.")
else:
    all_pet_names = [p.name for p in st.session_state.owner.petList]

    fcol1, fcol2 = st.columns([2, 2])
    with fcol1:
        pet_filter = st.multiselect("Filter by pet", all_pet_names, default=all_pet_names)
    with fcol2:
        status_filter = st.radio("Filter by status", ["All", "Pending", "Done"], horizontal=True)

    scheduler = st.session_state.scheduler
    all_tasks = scheduler.getAllTasks()

    filtered_tasks = []
    for pet_name in pet_filter:
        pet_obj = next(p for p in st.session_state.owner.petList if p.name == pet_name)
        filtered_tasks.extend(scheduler.filter_by_pet(pet_obj, all_tasks))

    if status_filter == "Pending":
        filtered_tasks = scheduler.filter_by_status(False, filtered_tasks)
    elif status_filter == "Done":
        filtered_tasks = scheduler.filter_by_status(True, filtered_tasks)

    if not all_tasks:
        st.info("No tasks to schedule yet. Add some tasks above.")
    elif not filtered_tasks:
        st.info("No tasks match the selected filters.")
    else:
        conflicts = scheduler.get_conflict_warnings()
        conflict_signature = tuple(conflicts)

        st.session_state.setdefault("conflict_signature", None)
        st.session_state.setdefault("conflict_decision", None)
        if conflict_signature != st.session_state.conflict_signature:
            # A different set of conflicts than last time (tasks changed) - ask again.
            st.session_state.conflict_signature = conflict_signature
            st.session_state.conflict_decision = None

        if conflicts and st.session_state.conflict_decision is None:
            @st.dialog("⚠️ Scheduling Conflicts Detected", dismissible=False)
            def confirm_conflicts():
                st.write("These pending tasks overlap:")
                for warning in conflicts:
                    st.warning(warning)
                st.write("Do you want to proceed with this schedule anyway?")
                dcol1, dcol2 = st.columns(2)
                with dcol1:
                    if st.button("Proceed anyway", type="primary", use_container_width=True):
                        st.session_state.conflict_decision = "proceed"
                        st.rerun()
                with dcol2:
                    if st.button("Not now", use_container_width=True):
                        st.session_state.conflict_decision = "dismissed"
                        st.rerun()

            confirm_conflicts()

        if conflicts and st.session_state.conflict_decision == "dismissed":
            st.warning("Schedule hidden until you resolve the conflicts above or choose to proceed anyway.")
            if st.button("Review conflicts again"):
                st.session_state.conflict_decision = None
                st.rerun()
        elif conflicts and st.session_state.conflict_decision is None:
            st.info("Waiting on your decision in the popup above.")
        else:
            pet_by_task_id = {
                id(t): p for p in st.session_state.owner.petList for t in p.taskList
            }
            ordered = scheduler.sort_by_time(filtered_tasks)

            pending_count = len(scheduler.filter_by_status(False, filtered_tasks))
            done_count = len(scheduler.filter_by_status(True, filtered_tasks))

            mcol1, mcol2, mcol3 = st.columns(3)
            mcol1.metric("Total", len(filtered_tasks))
            mcol2.metric("Pending", pending_count)
            mcol3.metric("Done", done_count)

            st.table(
                [
                    {
                        "day": t.dueDate.strftime("%A"),
                        "time": t.time,
                        "pet": pet_by_task_id[id(t)].name,
                        "task": t.description,
                        "frequency": t.frequency.value,
                        "status": "Done" if t.completed else "Pending",
                    }
                    for t in ordered
                ]
            )

            if conflicts:
                st.caption("Showing schedule despite unresolved conflicts (confirmed above).")
            else:
                st.success("No scheduling conflicts detected.")
