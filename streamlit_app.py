import streamlit as st
import json
import os
import hashlib
from streamlit_calendar import calendar

# =============================
# CONFIG
# =============================
st.set_page_config(
    page_title="Project Calendar",
    layout="wide"
)

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

# =============================
# CLEAN UI (LINEAR / NOTION STYLE)
# =============================
st.markdown("""
<style>
body {
    background-color: #fafafa;
}
.fc {
    font-size: 13px;
}
.fc-event-title {
    white-space: normal !important;
    overflow-wrap: anywhere !important;
    word-break: break-word;
    line-height: 1.35;
    font-size: 0.8rem;
}
.fc-daygrid-event {
    border-radius: 6px;
    padding: 2px 4px;
}
.fc-daygrid-event-dot {
    display: none;
}
.sidebar-content {
    background-color: #ffffff;
}
</style>
""", unsafe_allow_html=True)

# =============================
# TITLE
# =============================
st.markdown("## 📅 Project Management Calendar")
st.caption("Minimal, clear, and focused — like Linear & Notion")

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
        st.sidebar.error("Client & Project required")

# =============================
# CALENDAR EVENTS
# =============================
events = []
for p in data["projects"]:
    events.append({
        "id": p["id"],
        "title": f"{p['client']} | {p['project']} - {p['detail']}",
        "start": p["deadline"],
        "end": p["deadline"],
        "color": p["color"]
    })

calendar_options = {
    "initialView": "dayGridMonth",
    "height": "800px",
    "headerToolbar": {
        "left": "prev,next today",
        "center": "title",
        "right": "dayGridMonth,timeGridWeek"
    }
}

# =============================
# RENDER CALENDAR
# =============================
calendar_state = calendar(
    events=events,
    options=calendar_options
)

# =============================
# EVENT CLICK → MODAL
# =============================
if calendar_state and calendar_state.get("eventClick"):
    event_id = calendar_state["eventClick"]["event"]["id"]
    project_data = next(p for p in data["projects"] if p["id"] == event_id)

    with st.dialog("📌 Project Detail"):
        st.markdown(f"### {project_data['project']}")
        st.markdown(f"**Client:** {project_data['client']}")
        st.markdown(f"**Deadline:** {project_data['deadline']}")
        st.markdown("---")

        new_client = st.text_input("Client", project_data["client"])
        new_project = st.text_input("Project Name", project_data["project"])
        new_detail = st.text_area("Detail", project_data["detail"])
        new_deadline = st.date_input(
            "Deadline",
            value=st.session_state.get(
                "edit_deadline",
                st.date_input("", label_visibility="collapsed")
            )
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("💾 Update", use_container_width=True):
                project_data["client"] = new_client
                project_data["project"] = new_project
                project_data["detail"] = new_detail
                project_data["deadline"] = new_deadline.strftime("%Y-%m-%d")
                project_data["color"] = client_color(new_client)
                save_data(data)
                st.rerun()

        with col2:
            if st.button("🗑 Delete", use_container_width=True):
                data["projects"] = [
                    p for p in data["projects"] if p["id"] != event_id
                ]
                save_data(data)
                st.rerun()


