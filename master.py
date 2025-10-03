# master.py
import streamlit as st
from datetime import datetime
from pathlib import Path
import importlib
import os

# ---------------------------
# Config
# ---------------------------
APP_TITLE = "🤖 ELV Consulting Agent"
APP_ICON = "🤖"
AUTHOR = "Daniel M."
YEAR = datetime.today().year

st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="wide", initial_sidebar_state="expanded")

# ---------------------------
# Global Styling
# ---------------------------
st.markdown("""
<style>
/* Container */
.main > div.block-container { padding-left:4rem; padding-right:4rem; }

/* Hero */
.hero { padding:60px 0; text-align:center; }
.hero h1 { font-size:46px; font-weight:700; margin-bottom:12px; color:#0f172a; }
.hero p { font-size:18px; color:#475569; max-width:900px; margin:auto; line-height:1.6; }

/* Card */
.card { background:#fff; padding:20px; border-radius:14px; box-shadow:0 4px 14px rgba(0,0,0,0.05); border:1px solid #e5e7eb; margin-bottom:12px; }
.card h3 { margin-top:0; color:#1e293b; font-size:18px; }
.card .desc { font-size:14px; color:#64748b; }

/* Grid */
.grid { display:grid; grid-template-columns:repeat(auto-fit, minmax(280px,1fr)); gap:18px; margin-top:18px; }

/* Footer */
.footer { text-align:center; font-size:13px; color:#94a3b8; padding:20px 0; }
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Sidebar
# ---------------------------
st.sidebar.title("🧭 Navigation")
menu = st.sidebar.radio("Navigate", ["🏠 Home", "📋 Task Directory", "🚀 About", "📞 Contact"])
st.sidebar.markdown("---")
st.sidebar.markdown("**Connect**")
st.sidebar.markdown("[LinkedIn](https://www.linkedin.com/in/daniel-mekonnen-6845972a) | [X](https://x.com/DanielM62021892) | [Email](mailto:elv.ethiopia@gmail.com)")
st.sidebar.markdown(f"<div style='font-size:12px; color:#94a3b8'>Last updated {datetime.today().strftime('%B %d, %Y')}</div>", unsafe_allow_html=True)

# ---------------------------
# HOME
# ---------------------------
if menu == "🏠 Home":
    st.markdown('<div class="hero">', unsafe_allow_html=True)
    st.markdown(f"<h1>{APP_TITLE}</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p>Your **AI-driven digital partner** for ELV System Compliance, Design Review, and Automation.<br>"
        "Transforming 20+ years of field expertise into a **digital brain** that works for you 24/7.</p>",
        unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.success("Start exploring the **Task Directory** to see the impact of automation on your daily ELV workflows.")

    st.markdown("### 🌟 Why ELV Consulting Agent?")
    st.markdown("""
    - ✅ Automates **repetitive ELV consulting tasks** (reports, checklists, audits).  
    - ✅ Cuts review & documentation time by **70%+** compared to manual Excel sheets.  
    - ✅ Modular design — new AI-driven services can be added daily.  
    - ✅ Provides **instant compliance insight** aligned with global standards (TIA, NFPA, IEC, ICAO).  
    """)

# ---------------------------
# TASK DIRECTORY
# ---------------------------
elif menu == "📋 Task Directory":
    st.header("📋 Task Directory")
    st.markdown("The Agent organizes tasks into **major categories**, each with multiple sub-tools. Each sub-task will run as its own micro-app (`tasks/task_n.py`).")

    # Define tasks by category
    TASKS = {
        "Label Extractors": [
            ("SCN Label Extractor – Type 1", "Upload DWG/DXF/PDF → auto-extract structured cabling labels."),
            ("SCN Label Extractor – Type 2", "Enhanced SCN extraction with host zone & device sorting."),
            ("FAS Label Extractor", "Extract Fire Alarm devices & generate T&C-ready reports."),
            ("PA Label Extractor", "Extract Public Address speakers/zones from drawings."),
        ],
        "BOQ Generators": [
            ("SCN BOQ Generator", "Generate structured cabling BOQ with materials & quantities."),
            ("FAS BOQ Generator", "Fire Alarm BOQ including panels, detectors, modules."),
            ("PA BOQ Generator", "Public Address system BOQ with amplifiers, speakers."),
            ("CCTV & ACS BOQ Generator", "Security BOQ for cameras, access readers, controllers."),
        ],
        "Design Review Checklists": [
            ("SCN Review", "Verify against TIA-568, contract docs & ER."),
            ("FAS Review", "Check compliance with NFPA, ICAO, project specs."),
            ("CCTV Review", "Coverage validation, redundancy & storage compliance."),
            ("ACS Review", "Door control, reader integration & redundancy checks."),
            ("BMS Review", "Cross-system integration, energy & automation logic."),
        ],
        "Construction Follow-up": [
            ("Site Instructions (SI)", "Record & track instructions."),
            ("Engineering Instructions (EI)", "Formalize engineering changes."),
            ("RFIs", "Submit, log & track Requests for Information."),
            ("NCRs", "Non-Compliance Reports for quality assurance."),
            ("Snag & Outstanding Lists", "Generate & monitor open issues."),
            ("MoM", "Automated Minutes of Meeting template."),
        ],
        "Handover (HO) Docs": [
            ("As-built Drawings", "Checklist for DWG, Master List & Legends."),
            ("OMM & OMT", "Operation & Maintenance Manuals/Training."),
            ("T&C Checklist", "Testing & Commissioning compliance forms."),
            ("Spare & Tools List", "Automated spare/tools compliance tracker."),
        ],
        "MAS Approvals": [
            ("Communication Systems Approval", "Guide for MAS communication submissions."),
            ("Safety & Security Approvals", "Approval guide for FAS, CCTV, ACS."),
            ("BMS Approvals", "System-specific approval documentation."),
            ("Specialized Airport Systems", "ICAO-compliant MAS guides."),
        ],
        "Reports": [
            ("Daily Reports", "Quick site reporting templates."),
            ("Weekly Reports", "Automated weekly progress summaries."),
            ("Monthly Reports", "High-level project overviews."),
            ("HSE Reports", "Health & Safety compliance documentation."),
        ],
        "Standards Reference": [
            ("FAS Standards", "NFPA 72 mapping to project design."),
            ("SCN Standards", "TIA-568-E cabling compliance checks."),
            ("CCTV Standards", "ONVIF, IEC, ICAO compliance references."),
            ("ACS Standards", "Access Control integration guidelines."),
            ("BAS Standards", "Automation best practices, ISO 16484."),
        ]
    }

    # Render tasks
    for category, tasks in TASKS.items():
        st.subheader(f"📂 {category}")
        cols = st.columns(2)
        for i, (title, desc) in enumerate(tasks):
            with cols[i % 2]:
                st.markdown(f"""
                <div class="card">
                    <h3>{title}</h3>
                    <div class="desc">{desc}</div>
                    <div class="desc"><i>Status: 🚧 Under Development</i></div>
                </div>
                """, unsafe_allow_html=True)

# ---------------------------
# ABOUT
# ---------------------------
elif menu == "🚀 About":
    st.header("🚀 About")
    st.markdown(f"""
**Vision**  
To build an **AI-driven ELV Consulting Agent** that automates complex engineering tasks, boosts efficiency, and transforms 20+ years of expertise into a **scalable digital service**.

**Who I Am**  
With a deep-rooted passion for technology and a 20-year journey in Extra Low Voltage (ELV) Engineering, I’ve mastered Smart BAS, Smart Communication, Smart Security & Safety, Sound Reinforcement, SCS, PON, PA, A/V, Data Centers, CCTV, VACS, FA, and EVAC.  
My expertise ensures **intelligent spaces**, seamless connectivity, and **robust security & safety**.  

Driven by emerging technologies (IoT, AI, Blockchain, Big Data), I continuously push boundaries to **shape the future of ELV**.

**Why This Agent?**  
- To **make a lasting impact** on the ELV industry.  
- To **save engineers time** with automation.  
- To **monetize expertise** as AI-driven digital services.  
""")

# ---------------------------
# CONTACT
# ---------------------------
elif menu == "📞 Contact":
    st.header("📞 Contact the Expert")
    st.markdown("Get in touch to explore collaboration or request a service.")
    st.markdown("- 📧 Email: [elv.ethiopia@gmail.com](mailto:elv.ethiopia@gmail.com)")
    st.markdown("- 🔗 LinkedIn: [Daniel Mekonnen](https://www.linkedin.com/in/daniel-mekonnen-6845972a)")
    st.markdown("- 🐦 X: [@DanielM62021892](https://x.com/DanielM62021892)")

# ---------------------------
# Footer
# ---------------------------
st.markdown("---")
st.markdown(f"<div class='footer'>{APP_TITLE} © {YEAR} | Built with ❤️ using Streamlit</div>", unsafe_allow_html=True)
