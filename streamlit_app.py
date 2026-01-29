import streamlit as st
import json
import os
import hashlib
from datetime import date, datetime, timedelta
from collections import defaultdict
from streamlit_calendar import calendar

# =============================
# CONFIG
# =============================
st.set_page_config(page_title="Project Manager", layout="wide")
DATA_FILE = "data.json"

# =============================
# UTILS
# =============================
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"projects": []}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def client_color(client):
    return "#" + hashlib.md5(client.encode()).hexdigest()[:6]

def parse_date(d):
    return datetime.strptime(d, "%Y-%m-%d").date()

# =============================
# CSS — CLEAN UI
# =============================
st.markdown("""
<style>
.project-card {
    background:#fff;
    border-radius:10px;
    padding:12px 14px;
    margin-bottom:10px;
    border-left:6px solid var(--accent);
    box-shadow:0 4px 14px rgba(0,0,0,0.05);
    font-size:0.85rem;
}
.kanban-col {
    background:#f7f7f7;
    border-radius:12px;
    padding:16px;
}
.kanban-title {
    font-weight:600;
    margin-bottom:12px;
}
</style>
""", unsafe_allow_html=True)

# =============================
# STATE
# =============================
if "selected_id" not in st.session_state:
    st.session_state.selected_id = None

# =============================
# LOAD DATA
# =============================
data = load_data()

# =============================
# SIDEBAR — ADD PROJECT
# =============================
st.sidebar.markdown("### ➕ New Project")

client = st.sidebar.text_input("Client")
project = st.sidebar.text_input("Project Name")
detail = st.sidebar.text_area("Project Detail")
deadline = st.sidebar.date_input("Deadline")

status = st.sidebar.radio(
    "Status",
    ["todo", "done"],
    format_func=lambda x: "To-Do" if x == "todo" else "Done",
    index=0
)

if st.sidebar.button("Save Project", use_container_width=True):
    if client and project:
        data["projects"].append({
            "id": hashlib.md5(f"{client}{project}{deadline}".encode()).hexdigest(),
            "client": client,
            "project": project,
            "detail": detail,
            "deadline": deadline.strftime("%Y-%m-%d"),
            "color": client_color(client),
            "status": status
        })
        save_data(data)
        st.rerun()

# =============================
# WEEKLY VIEW (FILTERED)
# =============================
st.markdown("## 🗓 Weekly View")

today = date.today()
start_week = today - timedelta(days=today.weekday())
end_week = start_week + timedelta(days=6)

weekly = defaultdict(list)
for p in data["projects"]:
    d = parse_date(p["deadline"])
    if start_week <= d <= end_week:
        weekly[d].append(p)

for day in sorted(weekly.keys()):
    st.markdown(f"### {day.strftime('%A, %d %B %Y')}")
    for p in weekly[day]:
        st.markdown(
            f"""
            <div class="project-card" style="--accent:{p['color']}">
                <strong>{p['project']}</strong><br>
                <small>{p['client']} • {p['status'].upper()}</small><br>
                {p['detail']}
            </div>
            """,
            unsafe_allow_html=True
        )

# =============================
# KANBAN (STABLE VERSION)
# =============================
st.markdown("---")
st.markdown("## 🧩 Kanban Board")

todo_col, done_col = st.columns(2)

with todo_col:
    st.markdown("### 🟦 To-Do")
    for p in [x for x in data["projects"] if x["status"] == "todo"]:
        with st.container():
            st.markdown(
                f"""
                <div class="project-card" style="--accent:{p['color']}">
                    <strong>{p['project']}</strong><br>
                    <small>{p['client']}</small>
                </div>
                """,
                unsafe_allow_html=True
            )
            if st.button("➡ Mark as Done", key=f"done-{p['id']}"):
                p["status"] = "done"
                save_data(data)
                st.rerun()

with done_col:
    st.markdown("### ✅ Done")
    for p in [x for x in data["projects"] if x["status"] == "done"]:
        with st.container():
            st.markdown(
                f"""
                <div class="project-card" style="--accent:{p['color']}">
                    <strong>{p['project']}</strong><br>
                    <small>{p['client']}</small>
                </div>
                """,
                unsafe_allow_html=True
            )
            if st.button("⬅ Move to To-Do", key=f"todo-{p['id']}"):
                p["status"] = "todo"
                save_data(data)
                st.rerun()

# =============================
# MONTHLY CALENDAR
# =============================
st.markdown("---")
st.markdown("## 📅 Monthly Calendar")

events = []
for p in data["projects"]:
    events.append({
        "id": p["id"],
        "title": f"{p['client']} | {p['project']} - {p['detail']}",
        "start": p["deadline"],
        "color": p["color"]
    })

calendar_state = calendar(
    events=events,
    options={"initialView": "dayGridMonth", "height": "750px"}
)

# =============================
# EDIT / DELETE
# =============================
if calendar_state and calendar_state.get("eventClick"):
    st.session_state.selected_id = calendar_state["eventClick"]["event"]["id"]

if st.session_state.selected_id:
    p = next(x for x in data["projects"] if x["id"] == st.session_state.selected_id)

    st.markdown("---")
    st.markdown("### ✏️ Edit Project")

    new_client = st.text_input("Client", p["client"])
    new_project = st.text_input("Project", p["project"])
    new_detail = st.text_area("Detail", p["detail"])
    new_deadline = st.date_input("Deadline", parse_date(p["deadline"]))

    if st.button("💾 Update"):
        p.update({
            "client": new_client,
            "project": new_project,
            "detail": new_detail,
            "deadline": new_deadline.strftime("%Y-%m-%d"),
            "color": client_color(new_client)
        })
        save_data(data)
        st.session_state.selected_id = None
        st.rerun()

    if st.button("🗑 Delete"):
        data["projects"] = [x for x in data["projects"] if x["id"] != p["id"]]
        save_data(data)
        st.session_state.selected_id = None
        st.rerun()
