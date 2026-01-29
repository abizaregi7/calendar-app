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
    font-size:0.85rem;
}

.kanban-card {
    background:#ffffff;
    border-radius:8px;
    padding:10px 12px;
    margin-bottom:8px;
    box-shadow:0 2px 8px rgba(0,0,0,0.05);
    font-size:0.8rem;
}
</style>
""", unsafe_allow_html=True)

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

if st.sidebar.button("Save Project", use_container_width=True):
    if client and project:
        data["projects"].append({
            "id": hashlib.md5(f"{client}{project}{deadline}".encode()).hexdigest(),
            "client": client,
            "project": project,
            "detail": detail,
            "deadline": deadline.strftime("%Y-%m-%d"),
            "color": client_color(client),
            "status": "todo"
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

weekly_projects = defaultdict(list)
for p in data["projects"]:
    d = parse_date(p["deadline"])
    if start_week <= d <= end_week:
        weekly_projects[d].append(p)

for day in sorted(weekly_projects.keys()):
    st.markdown(f"### {day.strftime('%A, %d %B %Y')}")
    for p in weekly_projects[day]:
        st.markdown(
            f"""
            <div class="project-card" style="--accent:{p['color']}">
                <strong>{p['project']}</strong><br>
                <small>{p['client']}</small><br>
                {p['detail']}
            </div>
            """,
            unsafe_allow_html=True
        )

# =============================
# KANBAN BOARD (DRAG & DROP)
# =============================
st.markdown("---")
st.markdown("## 🧩 Kanban Board")

todo_items = [
    {"id": p["id"], "label": f"{p['project']} ({p['client']})"}
    for p in data["projects"] if p["status"] == "todo"
]

done_items = [
    {"id": p["id"], "label": f"{p['project']} ({p['client']})"}
    for p in data["projects"] if p["status"] == "done"
]

kanban = sort_items(
    {
        "Todo": todo_items,
        "Done": done_items
    },
    direction="horizontal",
    key="kanban"
)

# =============================
# UPDATE STATUS
# =============================
id_map = {p["id"]: p for p in data["projects"]}

for item in kanban["Todo"]:
    id_map[item["id"]]["status"] = "todo"

for item in kanban["Done"]:
    id_map[item["id"]]["status"] = "done"

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

calendar(events=events, options={"initialView": "dayGridMonth", "height": "750px"})
