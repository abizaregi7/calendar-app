import streamlit as st
import json
import os
import hashlib
from datetime import date
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

# =============================
# UI STYLE (LINEAR / NOTION)
# =============================
st.markdown("""
<style>
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
.panel {
    background: #ffffff;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.06);
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
# CALENDAR EVENTS
# =============================
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
# HANDLE EVENT CLICK
# =============================
if calendar_state and calendar_state.get("eventClick"):
    st.session_state.selected_id = calendar_state["eventClick"]["event"]["id"]

# =============================
# MODAL-LIKE DETAIL PANEL
# =============================
if st.session_state.selected_id:
    project_data = next(
        p for p in data["projects"]
        if p["id"] == st.session_state.selected_id
    )

    st.markdown("---")
    with st.container():
        st.markdown('<div class="panel">', unsafe_allow_html=True)

        st.markdown(f"### {project_data['project']}")
        st.caption(f"{project_data['client']} • {project_data['deadline']}")

        new_client = st.text_input("Client", project_data["client"])
        new_project = st.text_input("Project", project_data["project"])
        new_detail = st.text_area("Detail", project_data["detail"])
        new_deadline = st.date_input(
            "Deadline",
            date.fromisoformat(project_data["deadline"])
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

        st.markdown('</div>', unsafe_allow_html=True)
