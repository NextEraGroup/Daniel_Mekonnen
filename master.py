# app.py
"""
ELV Consulting Agent - Autonomous Service Skeleton
- Single-file Streamlit app scaffold for an AI-driven ELV SaaS.
- Key features:
  * Task discovery and modular task execution (tasks/task_x.py)
  * Lightweight user/project DB (SQLite)
  * File upload intake for design files
  * Job queue + background worker (threaded placeholder)
  * AI Chatbot hook (ai_query)
  * Subscription / feature gating placeholders (payments)
  * Clear TODO markers for integrating LLM, vector DB, payment gateway, and background worker system
"""

import streamlit as st
from datetime import datetime
import importlib
import os
import sqlite3
import uuid
import threading
import time
import json
from pathlib import Path
from typing import Dict, Any, Optional

# ---------------------------
# Config & Constants
# ---------------------------
APP_TITLE = "🤖 ELV Consulting Agent (Autonomous)"
DB_PATH = "elv_agent.db"
TASKS_DIR = "tasks"
UPLOAD_DIR = "uploads"
JOB_POLL_INTERVAL = 1.0  # seconds (only for demo worker)

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(TASKS_DIR, exist_ok=True)

# ---------------------------
# Streamlit page setup
# ---------------------------
st.set_page_config(page_title=APP_TITLE, layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
.header {
  background: linear-gradient(90deg,#2C3E50,#34495E);
  color: white;
  padding: 18px;
  border-radius: 8px;
  text-align:center;
}
.card {
  padding: 12px; border-radius: 8px; border: 1px solid #eee; margin-bottom:10px;
}
.small-muted { color: #7f8c8d; font-size:0.9rem }
</style>
""", unsafe_allow_html=True)

st.markdown(f'<div class="header"><h1>{APP_TITLE}</h1><div class="small-muted">90% AI • 10% Human — scalable ELV consulting platform</div></div>', unsafe_allow_html=True)
st.divider()

# ---------------------------
# --- Lightweight DB layer (SQLite)
# ---------------------------
def get_db_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_conn()
    cur = conn.cursor()
    # users, projects, jobs
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE,
        name TEXT,
        subscription_level TEXT,
        created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS projects (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        name TEXT,
        metadata TEXT,
        created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS jobs (
        id TEXT PRIMARY KEY,
        project_id TEXT,
        task_key TEXT,
        status TEXT,
        payload TEXT,
        result TEXT,
        created_at TEXT,
        updated_at TEXT
    );
    """)
    conn.commit()
    return conn

db = init_db()

# ---------------------------
# Auth / User utilities (very lightweight placeholder)
# ---------------------------
def create_user(email: str, name: str = "User") -> Dict[str, Any]:
    uid = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    cur = db.cursor()
    cur.execute("INSERT INTO users (id,email,name,subscription_level,created_at) VALUES (?,?,?,?,?)",
                (uid, email, name, "free", now))
    db.commit()
    return {"id": uid, "email": email, "name": name, "subscription_level": "free"}

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    cur = db.cursor()
    cur.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = cur.fetchone()
    return dict(row) if row else None

def current_user():
    # session-based quick auth for demo
    if "user_email" not in st.session_state:
        return None
    return get_user_by_email(st.session_state["user_email"])

# ---------------------------
# Job queue / worker (placeholder, thread-based)
# For production: replace with Celery / RQ / Cloud Tasks and worker processes.
# ---------------------------
_job_lock = threading.Lock()

def enqueue_job(project_id: str, task_key: str, payload: dict) -> Dict[str, Any]:
    job_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    cur = db.cursor()
    cur.execute("INSERT INTO jobs (id,project_id,task_key,status,payload,created_at,updated_at) VALUES (?,?,?,?,?,?,?)",
                (job_id, project_id, task_key, "queued", json.dumps(payload), now, now))
    db.commit()
    # Signal worker (the demo worker poll will pick it up)
    return {"id": job_id, "status": "queued"}

def get_job(job_id: str):
    cur = db.cursor()
    cur.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
    r = cur.fetchone()
    return dict(r) if r else None

def update_job_status(job_id: str, status: str, result: Optional[dict] = None):
    now = datetime.utcnow().isoformat()
    cur = db.cursor()
    cur.execute("UPDATE jobs SET status = ?, updated_at = ?, result = ? WHERE id = ?",
                (status, now, json.dumps(result) if result else None, job_id))
    db.commit()

def _demo_worker_loop(stop_event: threading.Event):
    """
    Demo worker: polls the jobs table and processes queued jobs one-by-one.
    Replace with real workers in production.
    """
    while not stop_event.is_set():
        try:
            cur = db.cursor()
            cur.execute("SELECT * FROM jobs WHERE status = 'queued' ORDER BY created_at LIMIT 1")
            row = cur.fetchone()
            if row:
                job = dict(row)
                job_id = job["id"]
                update_job_status(job_id, "running")
                # Simulated processing: import task module and call `run_task(payload)`
                try:
                    task_module_name = job["task_key"]  # expects module path saved as task_key
                    payload = json.loads(job["payload"]) if job["payload"] else {}
                    # Safe import attempt
                    task_module = importlib.import_module(task_module_name)
                    if hasattr(task_module, "run_task"):
                        result = task_module.run_task(payload)  # synchronous; may take time
                    elif hasattr(task_module, "run"):
                        # fallback to run()
                        result = task_module.run(payload)  # many mini-apps use run()
                    else:
                        result = {"error": "task module missing run_task / run"}
                    update_job_status(job_id, "done", result)
                except Exception as e:
                    update_job_status(job_id, "failed", {"error": str(e)})
            else:
                time.sleep(JOB_POLL_INTERVAL)
        except Exception:
            time.sleep(JOB_POLL_INTERVAL)

# start demo worker thread (only if not already started)
if "worker_thread" not in st.session_state:
    st.session_state["worker_stop_event"] = threading.Event()
    worker_thread = threading.Thread(target=_demo_worker_loop, args=(st.session_state["worker_stop_event"],), daemon=True)
    worker_thread.start()
    st.session_state["worker_thread"] = worker_thread

# ---------------------------
# Task discovery (modular tasks)
# ---------------------------
def discover_tasks() -> Dict[str, Dict[str, Any]]:
    tasks = {}
    if not os.path.exists(TASKS_DIR):
        return tasks
    for f in sorted(os.listdir(TASKS_DIR)):
        if f.startswith("task_") and f.endswith(".py"):
            task_id = f.replace(".py", "")
            module_name = f"{TASKS_DIR}.{task_id}"
            display_name = task_id.replace("_", " ").title()
            tasks[module_name] = {
                "name": display_name,
                "module": module_name,
                "path": os.path.join(TASKS_DIR, f),
                "description": f"Auto-discovered task from {f}"
            }
    return tasks

# ---------------------------
# AI integration hook (plug your LLM here)
# ---------------------------
def ai_query(prompt: str, context: Optional[str] = None) -> str:
    """
    Replace this with a call to your LLM of choice (OpenAI, local LLM, etc).
    - Use `context` to pass vector-search results or project-specific data.
    - Add safety / prompt-engineering specific to ELV standards.
    """
    # TODO: integrate OpenAI / Anthropic / local LLM & your API key handling
    # Example (pseudocode):
    # from openai import OpenAI
    # client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    # response = client.responses.create(model="gpt-4o-mini", input=final_prompt)
    # return response.output_text
    # For skeleton, echo back:
    response = f"[AI DEMO] Received prompt: {prompt[:300]}{'...' if len(prompt)>300 else ''}"
    if context:
        response += f"\n\n[Context preview] {context[:800]}"
    return response

# ---------------------------
# Utility: simple payment gating placeholder
# ---------------------------
def user_has_feature(user: Dict[str, Any], feature_key: str) -> bool:
    # Implement a real subscription check with Stripe billing
    if not user:
        return False
    sub = user.get("subscription_level", "free")
    if sub == "enterprise":
        return True
    if feature_key == "automated_jobs" and sub in ("pro", "enterprise"):
        return True
    return False

def mock_upgrade_user(email: str, level: str = "pro"):
    cur = db.cursor()
    cur.execute("UPDATE users SET subscription_level = ? WHERE email = ?", (level, email))
    db.commit()

# ---------------------------
# UI: Sidebar Auth & Navigation
# ---------------------------
st.sidebar.title("Account & Navigation")

if "user_email" not in st.session_state:
    st.session_state["user_email"] = None

auth_action = st.sidebar.selectbox("Signin / Actions", ["Sign in", "Create account", "Switch user (dev)"])
if auth_action == "Sign in":
    email = st.sidebar.text_input("Email", value=st.session_state.get("user_email") or "")
    if st.sidebar.button("Sign in"):
        user = get_user_by_email(email)
        if user:
            st.session_state["user_email"] = email
            st.sidebar.success(f"Signed in as {user['name']} ({user['subscription_level']})")
        else:
            st.sidebar.error("No account found. Create one from 'Create account'.")
elif auth_action == "Create account":
    new_email = st.sidebar.text_input("Email (new)", key="create_email")
    new_name = st.sidebar.text_input("Full name", key="create_name")
    if st.sidebar.button("Create Account"):
        if get_user_by_email(new_email):
            st.sidebar.error("Account already exists.")
        else:
            create_user(new_email, new_name or "User")
            st.sidebar.success("Account created. Sign in now.")
elif auth_action == "Switch user (dev)":
    # quick dev helper: list users
    cur = db.cursor()
    cur.execute("SELECT email, name, subscription_level FROM users ORDER BY created_at DESC LIMIT 10")
    rows = cur.fetchall()
    emails = [r["email"] for r in rows]
    picked = st.sidebar.selectbox("Pick user (dev)", [""] + emails)
    if picked and st.sidebar.button("Switch"):
        st.session_state["user_email"] = picked
        st.sidebar.success(f"Switched to {picked}")

st.sidebar.markdown("---")
menu = st.sidebar.radio("Main", ["Home", "Task Directory", "AI Chatbot", "Projects & Uploads", "Jobs", "Admin"])

# ---------------------------
# Home
# ---------------------------
if menu == "Home":
    st.subheader("Welcome")
    user = current_user()
    if user:
        st.info(f"Signed in as {user['name']} — subscription: {user['subscription_level']}")
    else:
        st.warning("You are not signed in. Create an account to run automated jobs and save projects.")
    st.markdown("""
    **Capabilities included in this skeleton**
    - Modular tasks discovered from /tasks/ (drop-in mini-apps)  
    - Submit a project & upload drawings -> enqueue automated compliance job  
    - Lightweight job queue + demo worker (replace with Celery/RQ)  
    - AI Chatbot (ai_query) to answer ELV questions programmatically  
    - Subscription gating placeholders (free / pro / enterprise)
    """)

# ---------------------------
# Task Directory (users can run tasks immediately or enqueue)
# ---------------------------
elif menu == "Task Directory":
    st.subheader("📋 Task Directory")
    tasks = discover_tasks()
    if not tasks:
        st.warning("No tasks available. Add files like tasks/task_example.py")
        st.info("Example task API: define run_task(payload) -> dict or run(payload)")
    else:
        for module_name, info in tasks.items():
            st.write(f"**{info['name']}** — {info['description']}")
            col1, col2, col3 = st.columns([2,1,1])
            with col1:
                st.caption(f"module: {module_name}")
            with col2:
                if st.button(f"Run now: {info['name']}", key=f"run_{module_name}"):
                    # immediate run (blocking) — fine for quick tasks
                    try:
                        module = importlib.import_module(module_name)
                        payload = {"demo": True}
                        if hasattr(module, "run_task"):
                            r = module.run_task(payload)
                        elif hasattr(module, "run"):
                            r = module.run(payload)
                        else:
                            raise RuntimeError("Task module missing run_task/run")
                        st.success("Task completed. See result below.")
                        st.json(r)
                    except Exception as e:
                        st.exception(e)
            with col3:
                if st.button(f"Enqueue: {info['name']}", key=f"enqueue_{module_name}"):
                    user = current_user()
                    if not user:
                        st.warning("Sign in to enqueue automated jobs.")
                    elif not user_has_feature(user, "automated_jobs"):
                        st.warning("Automated jobs are a paid feature. Upgrade to Pro/Enterprise.")
                    else:
                        # create or pick a project
                        project_id = str(uuid.uuid4())
                        now = datetime.utcnow().isoformat()
                        cur = db.cursor()
                        cur.execute("INSERT INTO projects (id,user_id,name,metadata,created_at) VALUES (?,?,?,?,?)",
                                    (project_id, user["id"], f"Auto Project {now}", json.dumps({}), now))
                        db.commit()
                        job = enqueue_job(project_id, module_name, {"submitted_by": user["email"]})
                        st.success(f"Enqueued job {job['id']} — it will be processed by worker.")

# ---------------------------
# Projects & Uploads
# ---------------------------
elif menu == "Projects & Uploads":
    st.subheader("Projects & File Uploads")
    user = current_user()
    if not user:
        st.warning("Sign in to create projects and upload files.")
    else:
        st.markdown("### Create / Select Project")
        cur = db.cursor()
        cur.execute("SELECT * FROM projects WHERE user_id = ?", (user["id"],))
        projects = cur.fetchall()
        project_options = {p["id"]: p["name"] for p in projects}
        new_name = st.text_input("New project name")
        if st.button("Create Project"):
            pid = str(uuid.uuid4())
            now = datetime.utcnow().isoformat()
            cur.execute("INSERT INTO projects (id,user_id,name,metadata,created_at) VALUES (?,?,?,?,?)",
                        (pid, user["id"], new_name or f"Project {now}", json.dumps({}), now))
            db.commit()
            st.success("Project created.")

        selected_project = st.selectbox("Select Project", [""] + list(project_options.values()))
        st.markdown("---")
        st.markdown("### Upload design files (DWG, DXF, PDF, XLSX)")
        uploaded = st.file_uploader("Upload files", accept_multiple_files=True)
        if uploaded and st.button("Save uploads"):
            # create uploads under project
            for f in uploaded:
                safe_name = f"{uuid.uuid4()}_{f.name}"
                path = os.path.join(UPLOAD_DIR, safe_name)
                with open(path, "wb") as fh:
                    fh.write(f.read())
                st.success(f"Saved {f.name} -> {path}")
            st.info("Files saved. Use Task Directory to run automatic checks against these files.")

# ---------------------------
# AI Chatbot
# ---------------------------
elif menu == "AI Chatbot":
    st.subheader("AI Chatbot (Plug your LLM)")
    prompt = st.text_area("Ask the ELV Agent (include context: project ID, system, standards)", height=200)
    if st.button("Ask") and prompt.strip():
        # Optionally, you can run vector-search here to build `context`
        context = None  # TODO: run vector DB search based on uploaded documents
        answer = ai_query(prompt, context=context)
        st.markdown("**AI Response**")
        st.write(answer)

# ---------------------------
# Jobs (monitor queue)
# ---------------------------
elif menu == "Jobs":
    st.subheader("Jobs & Queue")
    user = current_user()
    cur = db.cursor()
    if user:
        cur.execute("SELECT * FROM jobs j JOIN projects p ON j.project_id = p.id WHERE p.user_id = ? ORDER BY j.created_at DESC LIMIT 50", (user["id"],))
    else:
        cur.execute("SELECT * FROM jobs ORDER BY created_at DESC LIMIT 50")
    rows = cur.fetchall()
    if not rows:
        st.info("No jobs yet.")
    else:
        for r in rows:
            job = dict(r)
            with st.expander(f"Job {job['id']} — {job['task_key']} — status: {job['status']}"):
                st.write("Project:", job.get("project_id"))
                st.write("Created:", job.get("created_at"))
                st.write("Updated:", job.get("updated_at"))
                st.write("Payload:")
                st.json(json.loads(job["payload"]) if job["payload"] else {})
                st.write("Result:")
                if job["result"]:
                    try:
                        st.json(json.loads(job["result"]))
                    except Exception:
                        st.text(job["result"])
                else:
                    st.info("No result yet.")

# ---------------------------
# Admin (dev tools)
# ---------------------------
elif menu == "Admin":
    st.subheader("Admin / Developer Tools")
    st.markdown("**Quick actions**")
    user = current_user()
    if st.button("Print DB summary"):
        cur = db.cursor()
        cur.execute("SELECT COUNT(*) as c FROM users"); st.write("Users:", cur.fetchone()["c"])
        cur.execute("SELECT COUNT(*) as c FROM projects"); st.write("Projects:", cur.fetchone()["c"])
        cur.execute("SELECT COUNT(*) as c FROM jobs"); st.write("Jobs:", cur.fetchone()["c"])
    if st.button("Create mock pro user"):
        create_user(f"pro_{uuid.uuid4().hex[:6]}@example.com", "Pro User")
        st.success("Created mock user (free by default). Use 'Switch user (dev)' to switch.")
    if st.button("Upgrade current user to Pro (mock)"):
        if not user:
            st.warning("Sign in first.")
        else:
            mock_upgrade_user(user["email"], "pro")
            st.success("Upgraded (mock) — reload to see subscription.")
    st.markdown("---")
    st.markdown("**Tasks discovered**")
    st.json(discover_tasks())

# ---------------------------
# Footer
# ---------------------------
st.markdown("---")
st.caption(f"ELV Consulting Agent • skeleton • {datetime.utcnow().date().isoformat()} • Replace demo components with production services (LLM, vector DB, payments, worker system)")

# ---------------------------
# Clean up: stop worker when session ends (best-effort)
# ---------------------------
def _stop_worker():
    if "worker_stop_event" in st.session_state:
        st.session_state["worker_stop_event"].set()
if st.button("Stop demo worker (dev only)"):
    _stop_worker()
    st.success("Worker stop signal sent. (In production use process manager)")
