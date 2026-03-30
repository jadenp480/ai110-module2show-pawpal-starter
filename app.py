import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ---------------------------------------------------------------------------
# Session state bootstrap
# Each key holds a live object from pawpal_system.py so state persists
# across Streamlit reruns within the same session.
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = None   # Owner instance
if "scheduler" not in st.session_state:
    st.session_state.scheduler = None  # Scheduler instance

# ---------------------------------------------------------------------------
# Section 1 — Owner Setup
# ---------------------------------------------------------------------------
st.subheader("Owner Setup")

col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Your name", value="Jordan")
with col2:
    available_minutes = st.number_input(
        "Daily time budget (minutes)", min_value=10, max_value=480, value=120, step=10
    )

morning_person = st.checkbox("I'm a morning person", value=True)

if st.button("Save owner"):
    # Create (or replace) the Owner object and store it in session state
    st.session_state.owner = Owner(
        name=owner_name,
        available_minutes=available_minutes,
        preferences={"morning_person": morning_person},
    )
    st.session_state.scheduler = None  # reset stale plan when owner changes
    st.success(f"Owner '{owner_name}' saved with {available_minutes}-minute daily budget.")

st.divider()

# ---------------------------------------------------------------------------
# Section 2 — Add a Pet
# Calls Owner.add_pet(Pet(...)) when the form is submitted.
# The updated owner.pets list is shown immediately on the next Streamlit rerun.
# ---------------------------------------------------------------------------
st.subheader("Add a Pet")

if st.session_state.owner is None:
    st.info("Save an owner first before adding pets.")
else:
    with st.form("add_pet_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            pet_name = st.text_input("Pet name", value="Mochi")
            species = st.selectbox("Species", ["dog", "cat", "other"])
            breed = st.text_input("Breed (optional)")
        with col2:
            age = st.number_input("Age (years)", min_value=0.0, max_value=30.0,
                                  value=3.0, step=0.5)
            weight = st.number_input("Weight (lbs)", min_value=0.0, max_value=200.0,
                                     value=0.0, step=0.5)
            special_needs_raw = st.text_input(
                "Special needs (comma-separated)", placeholder="e.g. diabetic, anxiety"
            )

        submitted = st.form_submit_button("Add pet")
        if submitted:
            special_needs = [s.strip() for s in special_needs_raw.split(",") if s.strip()]
            new_pet = Pet(
                name=pet_name,
                species=species,
                breed=breed,
                age=age,
                weight=weight,
                special_needs=special_needs,
            )
            # ← Owner.add_pet() is the method that handles this data
            st.session_state.owner.add_pet(new_pet)
            st.session_state.scheduler = None  # reset stale plan
            st.success(f"Added {pet_name} to {st.session_state.owner.name}'s pets.")

    # Show current pets — Streamlit reruns after every interaction,
    # so owner.pets always reflects the latest state
    if st.session_state.owner.pets:
        st.markdown("**Your pets:**")
        for pet in st.session_state.owner.pets:
            st.caption(pet.get_info())

st.divider()

# ---------------------------------------------------------------------------
# Section 3 — Add a Task to a Pet
# Calls Pet.add_task(Task(...)) when the form is submitted.
# ---------------------------------------------------------------------------
st.subheader("Add a Task")

owner = st.session_state.owner
has_pets = owner is not None and len(owner.pets) > 0

if not has_pets:
    st.info("Add at least one pet before adding tasks.")
else:
    pet_names = [p.name for p in owner.pets]

    with st.form("add_task_form", clear_on_submit=True):
        selected_pet_name = st.selectbox("Assign to pet", pet_names)

        col1, col2 = st.columns(2)
        with col1:
            task_title = st.text_input("Task title", value="Morning walk")
            category = st.selectbox(
                "Category",
                ["walk", "feeding", "medication", "appointment", "grooming", "enrichment"],
            )
            duration = st.number_input(
                "Duration (minutes)", min_value=1, max_value=240, value=20
            )
        with col2:
            priority = st.selectbox(
                "Priority",
                ["1 - Low", "2 - Routine", "3 - Normal", "4 - Urgent", "5 - Critical"],
                index=2,
            )
            frequency = st.selectbox(
                "Frequency", ["daily", "once", "weekly", "as_needed"]
            )
            time_pref = st.selectbox(
                "Preferred time", ["morning", "afternoon", "evening", "flexible"]
            )

        notes = st.text_input("Notes (optional)")
        submitted = st.form_submit_button("Add task")

        if submitted:
            # Find the selected Pet object in the owner's list
            target_pet = next(p for p in owner.pets if p.name == selected_pet_name)
            priority_value = int(priority[0])   # "3 - Normal" → 3
            time_preference = None if time_pref == "flexible" else time_pref

            new_task = Task(
                title=task_title,
                category=category,
                duration_minutes=int(duration),
                priority=priority_value,
                frequency=frequency,
                time_preference=time_preference,
                notes=notes,
            )
            # ← Pet.add_task() is the method that handles this data
            target_pet.add_task(new_task)
            st.session_state.scheduler = None  # reset stale plan
            st.success(f"Added '{task_title}' to {selected_pet_name}.")

    # Show current tasks per pet
    if any(p.tasks for p in owner.pets):
        st.markdown("**Current tasks:**")
        for pet in owner.pets:
            if pet.tasks:
                st.markdown(f"*{pet.name}*")
                for task in pet.tasks:
                    st.caption(str(task))

st.divider()

# ---------------------------------------------------------------------------
# Section 4 — Generate Schedule
# Creates a Scheduler, calls generate_plan(), then displays the results.
# ---------------------------------------------------------------------------
st.subheader("Generate Schedule")

if not has_pets or not any(p.tasks for p in owner.pets):
    st.info("Add at least one pet and one task before generating a schedule.")
else:
    if st.button("Generate schedule"):
        scheduler = Scheduler(owner=owner)
        scheduler.generate_plan()
        st.session_state.scheduler = scheduler   # store so it survives reruns

    if st.session_state.scheduler is not None:
        sched = st.session_state.scheduler
        st.code(sched.get_plan_summary(), language=None)
        with st.expander("Why this order?"):
            st.markdown(sched.explain_reasoning())
