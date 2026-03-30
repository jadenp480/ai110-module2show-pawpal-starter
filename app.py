import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# ---------------------------------------------------------------------------
# Styling — light pink background, paw print trail, purple text, white buttons
# ---------------------------------------------------------------------------
st.markdown("""
<style>
/* Background */
.stApp { background-color: #FFF0F5; }

/* Content card */
.block-container {
    background-color: rgba(255, 255, 255, 0.88);
    border-radius: 18px;
    padding: 2rem 2.5rem !important;
}

/* Dark purple headers */
h1, h2, h3 { color: #4A1259 !important; font-weight: 700 !important; }
[data-testid="stSubheader"] > div > p { color: #4A1259 !important; font-weight: 700 !important; }

/* Light purple labels and captions */
label, .stCaption, p { color: #7B2D8B !important; }

/* White buttons with dark purple text */
.stButton > button, .stFormSubmitButton > button {
    background-color: #ffffff !important;
    color: #4A1259 !important;
    border: 2px solid #9B59B6 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: background-color 0.2s;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
    background-color: #F3E5F5 !important;
    border-color: #4A1259 !important;
}

/* Dark purple — all text/number inputs */
input, textarea {
    background-color: #4A1259 !important;
    color: #ffffff !important;
    border: 1.5px solid #9B59B6 !important;
    border-radius: 6px !important;
}
input::placeholder, textarea::placeholder {
    color: #D7BDE2 !important;
    opacity: 1 !important;
}

/* Dark purple — selectbox trigger (the visible "button-like" box) */
[data-baseweb="select"] > div:first-child,
[data-baseweb="select"] > div:first-child > div {
    background-color: #4A1259 !important;
    border: 1.5px solid #9B59B6 !important;
    border-radius: 6px !important;
    color: #ffffff !important;
}
/* Selected value text inside selectbox */
[data-baseweb="select"] span,
[data-baseweb="select"] div[aria-selected] {
    color: #ffffff !important;
}
/* Selectbox dropdown menu items */
[data-baseweb="menu"],
[data-baseweb="popover"] {
    background-color: #4A1259 !important;
}
[role="option"] {
    background-color: #4A1259 !important;
    color: #ffffff !important;
}
[role="option"]:hover {
    background-color: #7B2D8B !important;
}

/* Dark purple — number input stepper wrapper */
[data-baseweb="input"],
[data-baseweb="base-input"] {
    background-color: #4A1259 !important;
    border: 1.5px solid #9B59B6 !important;
    border-radius: 6px !important;
}
/* Number input stepper buttons (+ / -) */
button[data-testid="stNumberInputStepUp"],
button[data-testid="stNumberInputStepDown"] {
    background-color: #7B2D8B !important;
    color: #ffffff !important;
    border: none !important;
}
button[data-testid="stNumberInputStepUp"]:hover,
button[data-testid="stNumberInputStepDown"]:hover {
    background-color: #9B59B6 !important;
}

/* Divider color */
hr { border-color: #D7BDE2 !important; }

/* Info / success / warning box tweaks */
[data-testid="stAlert"] { border-radius: 10px !important; }
</style>

<!-- Paw print trail — fixed decorations along both sides of the screen -->
<div style="position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:0;overflow:hidden;">
  <!-- Left trail -->
  <span style="position:fixed;top:6%;left:1.5%;font-size:2rem;opacity:0.13;transform:rotate(-20deg);">🐾</span>
  <span style="position:fixed;top:13%;left:4.5%;font-size:1.4rem;opacity:0.10;transform:rotate(-10deg);">🐾</span>
  <span style="position:fixed;top:21%;left:1%;font-size:2rem;opacity:0.13;transform:rotate(-25deg);">🐾</span>
  <span style="position:fixed;top:29%;left:4%;font-size:1.4rem;opacity:0.10;transform:rotate(-15deg);">🐾</span>
  <span style="position:fixed;top:38%;left:1.5%;font-size:2rem;opacity:0.13;transform:rotate(-20deg);">🐾</span>
  <span style="position:fixed;top:46%;left:4.5%;font-size:1.4rem;opacity:0.10;transform:rotate(-10deg);">🐾</span>
  <span style="position:fixed;top:55%;left:1%;font-size:2rem;opacity:0.13;transform:rotate(-25deg);">🐾</span>
  <span style="position:fixed;top:63%;left:4%;font-size:1.4rem;opacity:0.10;transform:rotate(-15deg);">🐾</span>
  <span style="position:fixed;top:72%;left:1.5%;font-size:2rem;opacity:0.13;transform:rotate(-20deg);">🐾</span>
  <span style="position:fixed;top:80%;left:4.5%;font-size:1.4rem;opacity:0.10;transform:rotate(-10deg);">🐾</span>
  <span style="position:fixed;top:88%;left:1%;font-size:2rem;opacity:0.13;transform:rotate(-25deg);">🐾</span>
  <!-- Right trail -->
  <span style="position:fixed;top:4%;right:1.5%;font-size:2rem;opacity:0.13;transform:rotate(20deg);">🐾</span>
  <span style="position:fixed;top:11%;right:4.5%;font-size:1.4rem;opacity:0.10;transform:rotate(10deg);">🐾</span>
  <span style="position:fixed;top:19%;right:1%;font-size:2rem;opacity:0.13;transform:rotate(25deg);">🐾</span>
  <span style="position:fixed;top:27%;right:4%;font-size:1.4rem;opacity:0.10;transform:rotate(15deg);">🐾</span>
  <span style="position:fixed;top:36%;right:1.5%;font-size:2rem;opacity:0.13;transform:rotate(20deg);">🐾</span>
  <span style="position:fixed;top:44%;right:4.5%;font-size:1.4rem;opacity:0.10;transform:rotate(10deg);">🐾</span>
  <span style="position:fixed;top:53%;right:1%;font-size:2rem;opacity:0.13;transform:rotate(25deg);">🐾</span>
  <span style="position:fixed;top:61%;right:4%;font-size:1.4rem;opacity:0.10;transform:rotate(15deg);">🐾</span>
  <span style="position:fixed;top:70%;right:1.5%;font-size:2rem;opacity:0.13;transform:rotate(20deg);">🐾</span>
  <span style="position:fixed;top:78%;right:4.5%;font-size:1.4rem;opacity:0.10;transform:rotate(10deg);">🐾</span>
  <span style="position:fixed;top:87%;right:1%;font-size:2rem;opacity:0.13;transform:rotate(25deg);">🐾</span>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Title
# ---------------------------------------------------------------------------
st.title("🐾 PawPal+")
st.caption("Smart pet care scheduling — every task, every pet, every day.")

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = None
if "scheduler" not in st.session_state:
    st.session_state.scheduler = None

# Convenience aliases
owner: Owner = st.session_state.owner
has_pets = owner is not None and len(owner.pets) > 0
has_tasks = has_pets and any(p.tasks for p in owner.pets)

# ---------------------------------------------------------------------------
# Section 1 — Owner Setup
# ---------------------------------------------------------------------------
st.subheader("👤 Owner Setup")

with st.form("owner_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        owner_name = st.text_input("Your name")
    with col2:
        available_minutes = st.number_input(
            "Daily time budget (minutes)", min_value=10, max_value=480, value=60, step=10
        )
    morning_person = st.checkbox("I'm a morning person")

    if st.form_submit_button("Save owner"):
        st.session_state.owner = Owner(
            name=owner_name,
            available_minutes=available_minutes,
            preferences={"morning_person": morning_person},
        )
        st.session_state.scheduler = None
        owner = st.session_state.owner
        st.success(f"Owner **{owner_name}** saved — {available_minutes} min daily budget.")

st.divider()

# ---------------------------------------------------------------------------
# Section 2 — Add a Pet  (Owner.add_pet)
# ---------------------------------------------------------------------------
st.subheader("🐶 Your Pets")

if owner is None:
    st.info("Save an owner first before adding pets.")
else:
    with st.form("add_pet_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            pet_name     = st.text_input("Pet name")
            species      = st.selectbox("Species", ["dog", "cat", "other"])
            breed        = st.text_input("Breed (optional)")
        with col2:
            age          = st.number_input("Age (years)", min_value=0.0, max_value=30.0, value=0.0, step=0.5)
            weight       = st.number_input("Weight (lbs)", min_value=0.0, max_value=200.0, value=0.0, step=0.5)
            special_raw  = st.text_input("Special needs (comma-separated)", placeholder="e.g. diabetic, anxiety")

        if st.form_submit_button("Add pet"):
            needs = [s.strip() for s in special_raw.split(",") if s.strip()]
            owner.add_pet(Pet(name=pet_name, species=species, breed=breed,
                              age=age, weight=weight, special_needs=needs))
            st.session_state.scheduler = None
            st.success(f"**{pet_name}** added to {owner.name}'s pets.")

    # Live pet roster using owner.pets
    if owner.pets:
        rows = [{"Name": p.name, "Species": p.species, "Age": f"{p.age} yrs",
                 "Special needs": ", ".join(p.special_needs) or "—",
                 "Senior": "Yes" if p.is_senior() else "No",
                 "Tasks": len(p.tasks)}
                for p in owner.pets]
        st.table(rows)

st.divider()

# ---------------------------------------------------------------------------
# Section 3 — Add a Task  (Pet.add_task)
# ---------------------------------------------------------------------------
st.subheader("📋 Add a Task")

# Refresh alias after potential owner update
owner = st.session_state.owner
has_pets = owner is not None and len(owner.pets) > 0

if not has_pets:
    st.info("Add at least one pet before adding tasks.")
else:
    with st.form("add_task_form", clear_on_submit=True):
        selected_pet_name = st.selectbox("Assign to pet", [p.name for p in owner.pets])
        col1, col2 = st.columns(2)
        with col1:
            task_title = st.text_input("Task title")
            category   = st.selectbox("Category",
                ["walk", "feeding", "medication", "appointment", "grooming", "enrichment"])
            duration   = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=1)
        with col2:
            priority_label = st.selectbox("Priority",
                ["1 - Low", "2 - Routine", "3 - Normal", "4 - Urgent", "5 - Critical"], index=2)
            frequency  = st.selectbox("Frequency", ["daily", "once", "weekly", "as_needed"])
            time_pref  = st.selectbox("Preferred time", ["morning", "afternoon", "evening", "flexible"])
        notes = st.text_input("Notes (optional)")

        if st.form_submit_button("Add task"):
            target_pet = next(p for p in owner.pets if p.name == selected_pet_name)
            target_pet.add_task(Task(
                title=task_title,
                category=category,
                duration_minutes=int(duration),
                priority=int(priority_label[0]),
                frequency=frequency,
                time_preference=None if time_pref == "flexible" else time_pref,
                notes=notes,
            ))
            st.session_state.scheduler = None
            st.success(f"**{task_title}** added to {selected_pet_name}.")

    # Task overview — uses Owner.filter_by_status to split pending vs done
    if any(p.tasks for p in owner.pets):
        pending_pairs = owner.filter_by_status(completed=False)
        done_pairs    = owner.filter_by_status(completed=True)

        col1, col2 = st.columns(2)
        col1.metric("Pending tasks", len(pending_pairs))
        col2.metric("Completed tasks", len(done_pairs))

        # Per-pet task breakdown using Owner.filter_by_pet
        with st.expander("View all tasks by pet"):
            for pet in owner.pets:
                pet_pairs = owner.filter_by_pet(pet.name)
                if pet_pairs:
                    st.markdown(f"**{pet.name}**")
                    rows = [{"Task": t.title, "Category": t.category,
                             "Duration": f"{t.duration_minutes} min",
                             "Priority": f"P{t.priority}", "Frequency": t.frequency,
                             "Time": t.time_preference or "flexible",
                             "Done": "✓" if t.completed else "○"}
                            for _, t in pet_pairs]
                    st.table(rows)

st.divider()

# ---------------------------------------------------------------------------
# Section 4 — Generate Schedule  (Scheduler.generate_plan + find_conflicts)
# ---------------------------------------------------------------------------
st.subheader("📅 Today's Schedule")

owner     = st.session_state.owner
has_tasks = has_pets and any(p.tasks for p in owner.pets)

if not has_tasks:
    st.info("Add at least one pet and one task before generating a schedule.")
else:
    if st.button("Generate schedule"):
        sched = Scheduler(owner=owner)
        sched.generate_plan()
        st.session_state.scheduler = sched

    sched: Scheduler = st.session_state.scheduler
    if sched is not None:

        # ── Scheduled tasks ──────────────────────────────────────────────
        if sched.plan:
            st.success(
                f"✅ {len(sched.plan)} tasks scheduled — "
                f"{sched.total_scheduled_time()} / {owner.available_minutes} min used"
            )
            plan_rows = [
                {"#": i, "Pet": pet.name, "Task": task.title,
                 "Category": task.category,
                 "Time slot": task.time_preference or "flexible",
                 "Duration": f"{task.duration_minutes} min",
                 "Priority": f"P{task.priority}",
                 "Frequency": task.frequency,
                 "Done": "✓" if task.completed else "○"}
                for i, (pet, task) in enumerate(sched.plan, 1)
            ]
            st.table(plan_rows)
        else:
            st.warning("No tasks could fit within the available time budget.")

        # ── Conflict warnings — one st.warning box per conflict ──────────
        # Each warning names the pet, slot, and what's overlapping so the
        # owner knows exactly which task to move and where.
        conflicts = sched.find_conflicts()
        if conflicts:
            st.markdown("#### ⚠️ Schedule Conflicts")
            st.caption(
                "These tasks may be hard to complete as scheduled. "
                "Try moving one task to a different time slot."
            )
            for conflict in conflicts:
                st.warning(conflict)
        else:
            st.success("✅ No scheduling conflicts detected.")

        # ── Skipped tasks ─────────────────────────────────────────────────
        if sched.skipped:
            with st.expander(f"⏭ Skipped tasks ({len(sched.skipped)})"):
                skip_rows = [{"Pet": pet.name, "Task": task.title,
                               "Reason": reason, "Duration": f"{task.duration_minutes} min"}
                              for pet, task, reason in sched.skipped]
                st.table(skip_rows)

        # ── Reasoning ─────────────────────────────────────────────────────
        with st.expander("🧠 Why this order?"):
            st.markdown(sched.explain_reasoning())

        st.divider()

        # ── Mark a task complete  (Scheduler.mark_complete) ──────────────
        st.subheader("✅ Mark a Task Complete")
        st.caption("Completing a daily or weekly task will automatically queue its next recurrence.")

        scheduled_pet_names = list({pet.name for pet, _ in sched.plan})
        if scheduled_pet_names:
            col1, col2 = st.columns(2)
            with col1:
                mark_pet = st.selectbox("Pet", scheduled_pet_names, key="mark_pet")
            with col2:
                tasks_for_pet = [task.title for pet, task in sched.plan
                                 if pet.name == mark_pet and not task.completed]
                mark_task = st.selectbox("Task", tasks_for_pet or ["(all done)"], key="mark_task")

            if tasks_for_pet and st.button("Mark complete"):
                found = sched.mark_complete(mark_pet, mark_task)
                if found:
                    st.success(f"**{mark_task}** marked complete for {mark_pet}!")
                    st.rerun()
                else:
                    st.error("Task not found in the current plan.")
