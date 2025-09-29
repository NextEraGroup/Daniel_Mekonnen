import streamlit as st
import sqlite3
from datetime import datetime

# =========================
# CONFIG
# =========================
DB_FILE = "elv_agent.db"
APP_TITLE = "🚀 ELV Consulting Agent Pro"
APP_VERSION = "Ultimate Premium v1.1"

# =========================
# DATABASE
# =========================
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Create users table
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        created_at TEXT
    )""")

    # Create feedback table
    c.execute("""CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT,
        rating INTEGER,
        comment TEXT,
        date TEXT
    )""")

    # Ensure "plan" column exists in users
    c.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in c.fetchall()]
    if "plan" not in columns:
        c.execute("ALTER TABLE users ADD COLUMN plan TEXT DEFAULT 'free'")

    conn.commit()
    conn.close()


def add_user(name, email):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "INSERT OR IGNORE INTO users (name, email, plan, created_at) VALUES (?, ?, 'free', ?)",
        (name, email, datetime.today().strftime("%Y-%m-%d")),
    )
    conn.commit()
    conn.close()


def get_user(email):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = c.fetchone()
    conn.close()
    return user


def add_feedback(user_email, rating, comment):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "INSERT INTO feedback (user_email, rating, comment, date) VALUES (?, ?, ?, ?)",
        (user_email, rating, comment, datetime.today().strftime("%Y-%m-%d")),
    )
    conn.commit()
    conn.close()


# =========================
# STYLING
# =========================
def inject_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }
        .hero {
            text-align: center;
            padding: 3rem 1rem;
            background: linear-gradient(135deg, #2563EB, #1E40AF);
            color: white;
            border-radius: 20px;
            margin-bottom: 2rem;
        }
        .card {
            background: rgba(255,255,255,0.7);
            backdrop-filter: blur(12px);
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 8px 24px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }
        .card:hover { transform: translateY(-5px); }
        .pricing {
            display: flex; gap: 1.5rem; justify-content: center; margin: 2rem 0;
        }
        .plan {
            flex: 1; padding: 2rem; border-radius: 16px;
            border: 2px solid #e5e7eb; text-align: center;
        }
        .plan h3 { margin-bottom: 1rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )


# =========================
# PAGES
# =========================
def login_page():
    st.title("🔐 Login / Sign Up")

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        email = st.text_input("📧 Email", key="login_email")
        if st.button("Login"):
            user = get_user(email)
            if user:
                st.session_state["user"] = user
                st.success(f"Welcome back, {user[1]}!")
                st.rerun()
            else:
                st.error("User not found. Please sign up.")

    with tab2:
        name = st.text_input("👤 Full Name", key="signup_name")
        email = st.text_input("📧 Email", key="signup_email")
        if st.button("Sign Up"):
            if get_user(email):
                st.error("Email already exists. Please log in.")
            else:
                add_user(name, email)
                st.session_state["user"] = get_user(email)
                st.success("Account created successfully!")
                st.rerun()


def home_page():
    inject_css()
    st.markdown(
        f"""
        <div class="hero">
            <h1>{APP_TITLE}</h1>
            <p>AI-Powered ELV System Design & Compliance Platform</p>
            <span>Edition: {APP_VERSION}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("## ✨ Why Choose Us?")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("#### 🤖 AI Automation\nSmart compliance & design checks")
    with col2:
        st.markdown("#### 📊 Analytics\nAdvanced performance insights")
    with col3:
        st.markdown("#### 🚀 Enterprise Ready\nScale with confidence")

    st.markdown("---")
    st.markdown("## 🚀 Quick Start")
    st.info("Access free tools or upgrade for premium services.")


def tasks_page():
    st.title("🛠️ Task Directory")

    free_tasks = ["📑 Compliance Checker", "📊 Basic Analytics", "📁 Report Generator"]
    pro_tasks = ["🤖 AI Risk Assessment", "🚀 System Optimizer", "🏢 Enterprise Dashboard"]

    st.subheader("Free Tools")
    for t in free_tasks:
        st.success(t)

    st.subheader("Premium Tools (Pro/Enterprise)")
    for t in pro_tasks:
        st.warning(t + " 🔒")


def pricing_page():
    inject_css()
    st.markdown("<h2 style='text-align:center;'>💎 Choose Your Plan</h2>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="pricing">
            <div class="plan">
                <h3>Free</h3>
                <p>$0 / forever</p>
                <ul><li>5–10 free tools</li><li>Basic AI checks</li></ul>
            </div>
            <div class="plan" style="border-color:#2563EB;">
                <h3>Pro</h3>
                <p>$99 / month</p>
                <ul><li>100+ tools</li><li>Advanced AI compliance</li><li>Priority support</li></ul>
            </div>
            <div class="plan" style="border-color:#9333EA;">
                <h3>Enterprise</h3>
                <p>$299 / month</p>
                <ul><li>Unlimited tools</li><li>Dedicated support</li><li>Custom integrations</li></ul>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def feedback_page():
    st.title("💬 Customer Feedback")
    user = st.session_state.get("user")

    if user:
        rating = st.slider("Rate your experience (1-5)", 1, 5, 5)
        comment = st.text_area("Leave your feedback")
        if st.button("Submit Feedback"):
            add_feedback(user[2], rating, comment)
            st.success("Thank you for your feedback! 🌟")
    else:
        st.info("Please login to submit feedback.")

    st.markdown("### 📢 Recent Feedback")
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT user_email, rating, comment, date FROM feedback ORDER BY id DESC LIMIT 5")
    rows = c.fetchall()
    conn.close()

    for r in rows:
        st.markdown(f"**{r[0]}** rated ⭐ {r[1]}/5  \n_{r[2]}_  \n📅 {r[3]}")


def about_page():
    inject_css()
    st.markdown(
        """
        <div class="card">
            <h2>👨‍💻 About the Developer</h2>
            <p><b>Daniel M.</b> – ELV Systems Consultant with 20 years of expertise in 
            Smart BAS, ICT, Security & Safety Systems, AV, Data Centers, and emerging 
            technologies like IoT and AI.</p>
            <p>Founder of <b>ELV Consulting Agent Pro</b>, turning decades of 
            experience into a digital platform for clients worldwide.</p>
            <p>🌍 Based in Ethiopia • Helping clients globally</p>
            <p><a href="https://www.linkedin.com/in/daniel-mekonnen-6845972a" target="_blank">🔗 LinkedIn</a> 
            | <a href="https://x.com/DanielM62021892" target="_blank">✖ X (Twitter)</a></p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================
# MAIN APP
# =========================
def main():
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    init_db()

    if "user" not in st.session_state:
        login_page()
        return

    menu = ["🏠 Home", "🛠️ Tasks", "💎 Pricing", "💬 Feedback", "👨‍💻 About", "🚪 Logout"]
    choice = st.sidebar.radio("Navigation", menu)

    if choice == "🏠 Home":
        home_page()
    elif choice == "🛠️ Tasks":
        tasks_page()
    elif choice == "💎 Pricing":
        pricing_page()
    elif choice == "💬 Feedback":
        feedback_page()
    elif choice == "👨‍💻 About":
        about_page()
    elif choice == "🚪 Logout":
        st.session_state.clear()
        st.rerun()


if __name__ == "__main__":
    main()
