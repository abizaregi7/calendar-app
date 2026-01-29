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
st.set_page_config(page_title="Project Calendar", layout="wide")
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
# CSS — CLEAN + CARD + WRAP
# =============================
st.markdown("""
<style>
/* Calendar wrap fix */
.fc-daygrid-event,
.fc-daygrid-event-harness,
.fc-event-title-container,
.fc-event-title {
    white-space: normal !important;
    overflow-wrap: anywhere !important;
    word-break: break-word !important;
    line-height: 1.35 !important;
    font-size: 0.8rem;
}
.fc-daygrid-event-dot { display: none !important; }

/* Weekly cards */
.week-day {
    margin-top: 24px;
}
.project-card {
    background: #ffffff;
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 10px;
    border-left: 6px solid var(--accent);
    box-shadow: 0 4px 14px rgba(0,0,0,0.05);
}
.project-title {
    font-weight: 600;
    font-size: 0.95rem;
}
.project-client {
    font-size: 0.75rem;
    color: #666;
}
.project-detail {
    font-size: 0.85rem;
    margin-top: 6px;
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

if st.sidebar.button("Save Project", use_container_width=True):
    if client and project:
        data["projects"].append({
            "id": hashlib.md5(f"{client}{project}{deadline}".encode()).hexdigest(),
            "client": client,
            "project": project,
            "detail": detail,
            "deadline": deadline.strftime("%Y-%m-%d"),
            "color": client_color(client)
        })
        save_data(data)
        st.rerun()
    else:
        st.sidebar.error("Client & Project wajib diisi")

# =============================
# WEEKLY VIEW (LIST + CARD)
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

for i in range(7):
    day = start_week + timedelta(days=i)
    st.markdown(f"### {day.strftime('%A, %d %B %Y')}", help="Weekly execution focus")

    if day in weekly_projects:
        for p in weekly_projects[day]:
            st.markdown(
                f"""
                <div class="project-card" style="--accent:{p['color']}">
                    <div class="project-title">{p['project']}</div>
                    <div class="project-client">{p['client']}</div>
                    <div class="project-detail">{p['detail']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.caption("No project")

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
    options={
        "initialView": "dayGridMonth",
        "height": "750px"
    }
)

# =============================
# EVENT CLICK
# =============================
if calendar_state and calendar_state.get("eventClick"):
    st.session_state.selected_id = calendar_state["eventClick"]["event"]["id"]

# =============================
# DETAIL PANEL (EDIT / DELETE)
# =============================
if st.session_state.selected_id:
    project_data = next(
        p for p in data["projects"]
        if p["id"] == st.session_state.selected_id
    )

    st.markdown("---")
    st.markdown("### ✏️ Project Detail")

    new_client = st.text_input("Client", project_data["client"])
    new_project = st.text_input("Project", project_data["project"])
    new_detail = st.text_area("Detail", project_data["detail"])
    new_deadline = st.date_input(
        "Deadline",
        parse_date(project_data["deadline"])
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("💾 Update", use_container_width=True):
            project_data.update({
                "client": new_client,
                "project": new_project,
                "detail": new_detail,
                "deadline": new_deadline.strftime("%Y-%m-%d"),
                "color": client_color(new_client)
            })
            save_data(data)
            st.session_state.selected_id = None
            st.rerun()

    with col2:
        if st.button("🗑 Delete", use_container_width=True):
            data["projects"] = [
                p for p in data["projects"]
                if p["id"] != project_data["id"]
            ]
            save_data(data)
            st.session_state.selected_id = None
            st.rerun()

    with col3:
        if st.button("✖ Close", use_container_width=True):
            st.session_state.selected_id = None
            st.rerun()

