import streamlit as st
import json
import os
import hashlib
from datetime import datetime
from streamlit_calendar import calendar

DATA_FILE = "data.json"

# -----------------------------
# Utility Functions
# -----------------------------
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"projects": []}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def client_color(client_name):
    hash_object = hashlib.md5(client_name.encode())
    hex_color = "#" + hash_object.hexdigest()[:6]
    return hex_color

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="Project Management Calendar",
    layout="wide"
)

st.title("📅 Project Management Calendar")

# -----------------------------
# Load Data
# -----------------------------
data = load_data()

# -----------------------------
# Sidebar Input
# -----------------------------
st.sidebar.header("➕ Tambah Project")

client = st.sidebar.text_input("Nama Klien")
project_name = st.sidebar.text_input("Nama Project")
detail = st.sidebar.text_area("Detail Project")
deadline = st.sidebar.date_input("Deadline")

if st.sidebar.button("Simpan Project"):
    if client and project_name:
        new_project = {
            "client": client,
            "project": project_name,
            "detail": detail,
            "deadline": deadline.strftime("%Y-%m-%d"),
            "color": client_color(client)
        }
        data["projects"].append(new_project)
        save_data(data)
        st.sidebar.success("Project berhasil ditambahkan!")
        st.rerun()
    else:
        st.sidebar.error("Nama klien dan project wajib diisi.")

# -----------------------------
# Prepare Calendar Events
# -----------------------------
events = []
for p in data["projects"]:
    events.append({
        "title": f"{p['project']} ({p['client']})",
        "start": p["deadline"],
        "end": p["deadline"],
        "color": p["color"],
        "extendedProps": {
            "detail": p["detail"]
        }
    })

calendar_options = {
    "initialView": "dayGridMonth",
    "height": "800px",
    "headerToolbar": {
        "left": "prev,next today",
        "center": "title",
        "right": "dayGridMonth,timeGridWeek,timeGridDay"
    }
}

# -----------------------------
# Render Calendar
# -----------------------------
calendar(events=events, options=calendar_options)

