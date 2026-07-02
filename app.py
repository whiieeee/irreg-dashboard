import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime


# ==========================================
# 1. DATABASE SETUP
# ==========================================
def init_db():
    conn = sqlite3.connect('dashboard.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_name TEXT NOT NULL,
            category TEXT NOT NULL,
            status TEXT DEFAULT 'Pending'
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_name TEXT NOT NULL,
            event_date DATE NOT NULL,
            event_type TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()


def run_query(query, params=(), fetch=False):
    conn = sqlite3.connect('dashboard.db')
    c = conn.cursor()
    c.execute(query, params)
    if fetch:
        data = c.fetchall()
        conn.close()
        return data
    conn.commit()
    conn.close()


# ==========================================
# 2. APP CONFIGURATION & MINIMALIST THEME
# ==========================================
st.set_page_config(page_title="Personal Dashboard", layout="centered")

# Custom CSS for Dark Grey (#222222) and Warm White (#F5F5DC) Theme
st.markdown("""
    <style>
    /* Main Background and Text */
    .stApp {
        background-color: #222222;
        color: #F5F5DC;
    }

    /* Headers and Text */
    h1, h2, h3, h4, h5, h6, p, span, div, label {
        color: #F5F5DC !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Sidebar Background */
    [data-testid="stSidebar"] {
        background-color: #1a1a1a;
    }

    /* Input Fields */
    .stTextInput > div > div > input, .stSelectbox > div > div > select {
        background-color: #333333 !important;
        color: #F5F5DC !important;
        border: 1px solid #555555 !important;
    }

    /* Buttons */
    .stButton > button {
        background-color: #333333;
        color: #F5F5DC;
        border: 1px solid #F5F5DC;
        border-radius: 4px;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #F5F5DC;
        color: #222222 !important;
    }

    /* DataFrames and Tables */
    .stDataFrame, .stTable {
        background-color: #222222;
    }

    /* Dividers */
    hr {
        border-color: #444444;
    }
    </style>
    """, unsafe_allow_html=True)

init_db()


# ==========================================
# 3. PAGE FUNCTIONS
# ==========================================

def dashboard_page():
    st.title("Command Center")
    st.markdown("*Discipline equals freedom.*")
    st.divider()

    pending_tasks = run_query("SELECT COUNT(*) FROM tasks WHERE status='Pending'", fetch=True)[0][0]

    today_str = datetime.today().strftime('%Y-%m-%d')
    upcoming_event = run_query(
        "SELECT event_name, event_date, event_type FROM events WHERE event_date >= ? ORDER BY event_date ASC LIMIT 1",
        (today_str,), fetch=True
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Pending Tasks")
        st.markdown(f"# {pending_tasks}")

    with col2:
        st.markdown("### Next Event")
        if upcoming_event:
            event_name, event_date, event_type = upcoming_event[0]
            st.markdown(f"**{event_name}** ({event_type})")
            st.markdown(f"{event_date}")
        else:
            st.markdown("No upcoming events.")


def class_schedule_page():
    st.title("Class Schedule")
    st.write("2nd-Year Load")
    st.divider()

    schedule_data = {
        "Course": [
            "Calculus 2 / Integral Calculus",
            "Data Structure and Algorithm Analysis",
            "Fundamentals of Electrical Circuits",
            "The Life and Works of Rizal"
        ],
        "Notes": [
            "Retake (Focus required)",
            "Major Subject",
            "Major Subject",
            "Minor Subject"
        ]
    }
    df = pd.DataFrame(schedule_data)
    st.table(df)


def todo_list_page():
    st.title("To-Do List")

    # QUICK ACTIONS (LESS TYPING)
    st.write("Quick Actions")
    q1, q2, q3 = st.columns(3)
    if q1.button("Add: Review Calculus"):
        run_query("INSERT INTO tasks (task_name, category) VALUES (?, ?)", ("Review Calculus", "Acads"))
        st.rerun()
    if q2.button("Add: DSA Practice"):
        run_query("INSERT INTO tasks (task_name, category) VALUES (?, ?)", ("DSA Practice", "Acads"))
        st.rerun()
    if q3.button("Add: QCYDO Req"):
        run_query("INSERT INTO tasks (task_name, category) VALUES (?, ?)", ("Submit Requirements", "QCYDO Scholarship"))
        st.rerun()

    st.divider()

    # CUSTOM INPUT
    with st.form("add_task_form", clear_on_submit=True):
        st.write("Manual Entry")
        task_name = st.text_input("Task Name")
        category = st.selectbox("Category", ["Acads", "QCYDO Scholarship", "Personal"])
        if st.form_submit_button("Add Task") and task_name.strip():
            run_query("INSERT INTO tasks (task_name, category) VALUES (?, ?)", (task_name, category))
            st.rerun()

    st.divider()

    st.write("Pending Tasks")
    tasks = run_query("SELECT id, task_name, category FROM tasks WHERE status='Pending'")

    if not tasks:
        st.write("All tasks completed.")
    else:
        for task in tasks:
            task_id, name, cat = task
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"**{name}** ({cat})")
            with col2:
                if st.button("Complete", key=f"done_{task_id}"):
                    run_query("DELETE FROM tasks WHERE id = ?", (task_id,))
                    st.rerun()


def gym_events_page():
    st.title("Calendar")

    # QUICK ADD WORKOUTS (LESS TYPING)
    st.write("Quick Log Workout (Today)")
    today_str = datetime.today().strftime('%Y-%m-%d')
    w1, w2, w3 = st.columns(3)

    def log_workout(split):
        run_query("INSERT INTO events (event_name, event_date, event_type) VALUES (?, ?, ?)",
                  (split, today_str, "Gym Split"))
        st.rerun()

    if w1.button("Log Push Day"): log_workout("Push Day")
    if w2.button("Log Pull Day"): log_workout("Pull Day")
    if w3.button("Log Leg Day"): log_workout("Leg Day")

    st.divider()

    with st.form("add_event_form", clear_on_submit=True):
        st.write("Add Custom Event")
        event_name = st.text_input("Event Name")
        event_date = st.date_input("Date")
        event_type = st.selectbox("Event Type", ["Gym Split", "Exam / Acads", "QCYDO Deadline", "Other"])
        if st.form_submit_button("Save Event") and event_name.strip():
            run_query("INSERT INTO events (event_name, event_date, event_type) VALUES (?, ?, ?)",
                      (event_name, event_date, event_type))
            st.rerun()

    st.divider()

    st.write("Upcoming Agenda")
    events = run_query("SELECT event_name, event_date, event_type FROM events ORDER BY event_date ASC")

    if not events:
        st.write("No events found.")
    else:
        df = pd.DataFrame(events, columns=["Event", "Date", "Category"])
        st.dataframe(df, use_container_width=True)


def study_habits_page():
    st.title("Protocols")
    st.write("System rules for peak performance.")
    st.divider()

    with st.expander("DO's & DON'Ts", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            **DO's :**
            * **The "Eat the Frog" Rule:** Kung may mahirap na code o plate, gawin mo agad sa Friday morning. Wag patagalin.
            * **Calculus Rule of 5:** Mag-solve ng 3-5 problems sa Calculus at Physics kada topic. Practice solving, wag lang reading.
            * **Utilize Vacant Hours:** Gamitin ang vacant time sa school (Tues/Thurs) para tapusin ang schoolworks. Para pag-uwi sa Fairview, boss ka na lang.
            * **Code While Fresh:** Mag-code sa umaga (Tuesday/Friday) habang fresh ang utak para iwas bugs at sakit ng ulo.
            """)
        with col2:
            st.markdown("""
            **DON'Ts :**
            * **"Mamaya na" Habit:** Ang backlog sa Calculus ay nagpapatong-patong. Bawal ma-late sa topic.
            * **Gaming sa Byahe:** Matulog ka na lang sa jeep/bus pauwi ng North Fairview. Save your eyes and battery.
            * **Puyat bago ang Wednesday:** Bawal magpuyat ng Tuesday night dahil "Hell Day" ang Wednesday. Kailangan gising ang diwa mo.
            """)

    st.divider()
    st.markdown("### The Core Mindsets")

    with st.expander("1. THE COMPILER MINDSET (Error ≠ Failure)"):
        st.markdown("""
        * **Ang Reality:** Sa programming (at sa math), magkakamali ka. Maraming beses.
        * **Wrong Mindset:** "Ang bobo ko, nag-error na naman code ko." (Personal attack sa sarili).
        * **The Upgrade:** "May bug sa logic ko. Saan banda? Line 42? O sige, ayusin natin."
            * Treat mo ang Mababang Quiz Score o Failed Code bilang ERROR MESSAGE lang. Hindi yan nagsasabing bobo ka. Sinasabi lang niyan kung saan ka kailangang mag-adjust.
            * **Action:** Pag may mali, wag mag-panic. DEBUG. Hanapin ang rason, ayusin, run ulit.
        """)

    with st.expander("2. FIRST PRINCIPLES (Understand > Memorize)"):
        st.markdown("""
        * **Ang Reality:** Sa Calculus at Physics, hindi nauubos ang formulas.
        * **Wrong Mindset:** "Memorize ko na lang 'to para makasagot sa exam."
        * **The Upgrade:** "Paano nakuha yung formula na 'to? Ano ang logic sa likod?"
            * Si Elon Musk at magagaling na Engineer ay gumagamit ng First Principles Thinking. Binabaklas nila ang problema hanggang sa pinaka-basic na katotohanan.
            * **Action:** Sa Calculus, wag mo lang kabisaduhin ang integral ng sec(x). Intindihin mo kung bakit ganun ang sagot. Pag naintindihan mo ang "Why", kahit baliktarin pa ni Sir ang tanong, masasagot mo.
        """)

    with st.expander("3. COMPOUND INTEREST (Consistency > Intensity)"):
        st.markdown("""
        * **Ang Reality:** Nakakapagod mag-aral ng 6 hours straight bago mag-exam.
        * **Wrong Mindset:** "Sa Friday na ako mag-aaral ng todo para sa exam sa Monday." (Cramming).
        * **The Upgrade:** "Magso-solve ako ng 3 problems araw-araw. 30 minutes lang."
            * Mas matindi ang epekto ng maliliit na effort na ginagawa araw-araw kaysa sa isang bagsakang puyatan.
            * **Action:** Yung "Vacant" mo sa school? Gamitin mo yun. Yung byahe mo sa bus? Gamitin mo yun. Build the habit, don't rely on motivation.
        """)

    with st.expander("4. RESOURCEFULNESS IS A SKILL (The Google-Fu)"):
        st.markdown("""
        * **Ang Reality:** Hindi lahat ituturo ng prof mo. Minsan, hindi mo maiintindihan turo nila.
        * **Wrong Mindset:** "Di ko gets turo ni Sir, bahala na."
        * **The Upgrade:** "Di ko gets si Sir. Ano kaya sabi ng Indian guy sa YouTube? Ano sabi ni ChatGPT? Ano sabi sa Stack Overflow?"
            * Ang Engineer, magaling maghanap ng sagot. Hindi mo kailangang alam lahat, kailangan mo lang malaman kung saan hahanapin.
            * **Action:** Gamitin ang Lenovo LOQ mo. Maximise AI (pang-explain, wag pang-cheat), YouTube tutorials, at PDF books.
        """)

    with st.expander("5. COLLABORATION OVER COMPETITION (Support System)"):
        st.markdown("""
        * **Ang Reality:** May mga kaklase kang halimaw mag-code o math wizard.
        * **Wrong Mindset:** "Nakakahiya magtanong, baka isipin nila bobo ako." o "Kalaban ko sila sa ranking."
        * **The Upgrade:** "Pre, paano mo nakuha 'to? Paturo naman ng logic mo."
            * Sa industry, teamwork ang nagpapagana ng projects. Walang Engineer na gumagawa ng building o software nang mag-isa.
            * **Action:** Dumikit ka sa matatalino. Magtanong ka. At kapag ikaw naman ang nakaka-alam, magturo ka. (The best way to learn is to teach).
        """)

    st.divider()
    st.markdown("### Study Techniques")

    t1, t2 = st.columns(2)
    with t1:
        st.markdown("""
        **1. ACTIVE RECALL (The "Pop Quiz" Method)**
        * **Concept:** Testing yourself > Re-reading.
        * **How:** Basa -> Isara ang libro -> Isulat sa papel ang naalala -> I-check kung ano ang mali. Mas masakit sa ulo = Mas tumatatak.

        **2. MUSCLE MEMORY (The "Hand-Brain" Connection)**
        * **Concept:** "The hand remembers what the mind forgets."
        * **How:** Wag titigan ang math solution; KOPYAHIN MO. Wag mag-copy paste ng code; I-TYPE MO.

        **3. THE FEYNMAN TECHNIQUE**
        * **Concept:** If you can't explain it simply, you don't understand it well enough.
        * **How:** I-explain ang concept (ex. Ohm's Law) gamit ang simpleng Tagalog. Bawal jargon. Pag na-stuck ka, balik sa aral.

        **4. FLOWTIME TECHNIQUE (Gamer Mode)**
        * **Concept:** Grind hangga't nasa "Zone."
        * **How:** Start stopwatch. Mag-aral habang may energy (1-2 hours). Kapag sabaw na, take a break (e.g. 1 hr aral = 15 mins break).
        """)
    with t2:
        st.markdown("""
        **5. SPACED REPETITION (Anti-Cramming)**
        * **Concept:** Refreshing the brain's "cache".
        * **Schedule:** Day 0: Understand. Day 1: Recall. Day 3: Apply. Day 7: Maintenance.

        **6. "EAT THE FROG"**
        * **Concept:** Unahin ang Boss Fight habang Full HP ka pa.
        * **Rule:** Unahin ang pinakamahirap (Calculus 2, Physics, Programming). Ihuli ang madali (History, PE) pag lowbat ka na.

        **7. THE 5-MINUTE RULE**
        * **Concept:** Trick your brain to overcome laziness.
        * **Hack:** Sabihin sa sarili: "5 minutes lang ako magbabasa/magco-code." Kadalasan tutuloy-tuloy ka na.

        **8. THE "SLEEP SANDWICH"**
        * **Concept:** Your brain processes info while you sleep.
        * **Routine:** Mag-aral bago matulog -> Sleep (Save to Long Term Memory) -> Recall agad paggising.
        """)


# ==========================================
# 4. SIDEBAR NAVIGATION
# ==========================================
st.sidebar.title("Navigation")
menu = ["Dashboard", "Class Schedule", "To-Do List", "Calendar", "Protocols"]
choice = st.sidebar.radio("Go to:", menu)

if choice == "Dashboard":
    dashboard_page()
elif choice == "Class Schedule":
    class_schedule_page()
elif choice == "To-Do List":
    todo_list_page()
elif choice == "Calendar":
    gym_events_page()
elif choice == "Protocols":
    study_habits_page()