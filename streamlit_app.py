import streamlit as st
import json
import os
import hashlib
from datetime import date, datetime, timedelta
from collections import defaultdict
from streamlit_calendar import calendar
from streamlit_sortables import sort_items

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
.fc-daygrid-event,
.fc-daygrid-event-harness,
.fc-event-title-container,
.fc-event-title {
    white-space: normal !important;
    overflow-wrap: anywhere !important;
    word-break: break-word !important;
    font-size: 0.8rem;
}
.fc-daygrid-event-dot { display:none!important; }

.project-card {
    background:#fff;
    border-radius:10px;
    padding:12px 14px;
    margin-bottom:10px;
    border-left:6px solid var(--accent);
    box-shadow:0 4px 14px rgba(0,0,0,0.05);
}

.kanban-col {
    background:#f9f9f9;
    border-radius:10px;
    padding:12px;
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
id_map = {p["id"]: p for p in data["projects"]}

# =============================
# SIDEBAR — ADD PROJECT
# =============================
st.sidebar.markdown("### ➕ New Project")

client = st.sidebar.text_input("Client")
project = st.sidebar.text_input("Project Name")
detail = st.sidebar.text_area("Project Detail")
deadline = st.sidebar.date_input("Deadline")

# 🔥 STATUS BUTTON (NEW)
status = st.sidebar.radio(
    "Status",
    ["todo", "done"],
    index=0,
    format_func=lambda x: "To-Do" if x == "todo" else "Done"
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
    else:
        st.sidebar.error("Client & Project wajib diisi")

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
# KANBAN BOARD
# =============================
st.markdown("---")
st.markdown("## 🧩 Kanban Board")

todo_items = [
    f"{p['id']}|{p['project']} ({p['client']})"
    for p in data["projects"] if p["status"] == "todo"
]

done_items = [
    f"{p['id']}|{p['project']} ({p['client']})"
    for p in data["projects"] if p["status"] == "done"
]

kanban = sort_items(
    {
        "todo": todo_items,
        "done": done_items
    },
    direction="horizontal",
    key="kanban"
)

for item in kanban["todo"]:
    pid = item.split("|")[0]
    id_map[pid]["status"] = "To-Do"

for item in kanban["done"]:
    pid = item.split("|")[0]
    id_map[pid]["status"] = "Done"

save_data(data)

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
    options={"initialView": "dayGridMonth", "height": "500px"}
)

# =============================
# EDIT / DELETE PANEL
# =============================
if calendar_state and calendar_state.get("eventClick"):
    st.session_state.selected_id = calendar_state["eventClick"]["event"]["id"]

if st.session_state.selected_id:
    p = id_map[st.session_state.selected_id]

    st.markdown("---")
    st.markdown("### ✏️ Edit Project")

    new_client = st.text_input("Client", p["client"])
    new_project = st.text_input("Project", p["project"])
    new_detail = st.text_area("Detail", p["detail"])
    new_deadline = st.date_input("Deadline", parse_date(p["deadline"]))

    new_status = st.radio(
        "Status",
        ["todo", "done"],
        index=0 if p["status"] == "todo" else 1,
        format_func=lambda x: "To-Do" if x == "todo" else "Done"
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("💾 Update", use_container_width=True):
            p.update({
                "client": new_client,
                "project": new_project,
                "detail": new_detail,
                "deadline": new_deadline.strftime("%Y-%m-%d"),
                "color": client_color(new_client),
                "status": new_status
            })
            save_data(data)
            st.session_state.selected_id = None
            st.rerun()

    with col2:
        if st.button("🗑 Delete", use_container_width=True):
            data["projects"] = [x for x in data["projects"] if x["id"] != p["id"]]
            save_data(data)
            st.session_state.selected_id = None
            st.rerun()

    with col3:
        if st.button("✖ Close", use_container_width=True):
            st.session_state.selected_id = None
            st.rerun()
