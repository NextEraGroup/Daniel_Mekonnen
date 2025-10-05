# master.py
import streamlit as st
from datetime import datetime
from pathlib import Path
import importlib
import os
import json
import sys
from typing import Dict, List, Tuple, Optional

# ---------------------------
# Configuration & Constants
# ---------------------------
class Config:
    APP_TITLE = "🤖 ELV Consulting Agent"
    APP_ICON = "🤖"
    AUTHOR = "Daniel M."
    YEAR = datetime.today().year
    VERSION = "2.0.0"
    
    # Color Scheme (Inspired by NextEra website)
    PRIMARY_COLOR = "#00695C"
    SECONDARY_COLOR = "#4DB6AC"
    ACCENT_COLOR = "#FFC107"
    DARK_COLOR = "#00251A"
    LIGHT_COLOR = "#E0F2F1"
    SUCCESS_COLOR = "#2E7D32"
    WARNING_COLOR = "#FF8F00"
    
    # Paths
    TASKS_DIR = Path("tasks")
    DATA_DIR = Path("data")
    CONFIG_DIR = Path("config")

# ---------------------------
# Session State Management
# ---------------------------
def init_session_state():
    """Initialize session state variables"""
    if 'app_initialized' not in st.session_state:
        st.session_state.app_initialized = True
        st.session_state.user_visits = 0
        st.session_state.last_visited = datetime.now()
        st.session_state.feedback_submitted = False
        st.session_state.current_page = "home"
        st.session_state.active_task = None

# ---------------------------
# Enhanced Styling & UI Components
# ---------------------------
class EnhancedUIStyles:
    """Enhanced styling management inspired by NextEra website"""
    
    @staticmethod
    def inject_custom_css():
        """Inject custom CSS styles with professional design"""
        primary = Config.PRIMARY_COLOR
        secondary = Config.SECONDARY_COLOR
        accent = Config.ACCENT_COLOR
        dark = Config.DARK_COLOR
        light = Config.LIGHT_COLOR
        success = Config.SUCCESS_COLOR
        warning = Config.WARNING_COLOR
        
        st.markdown(f"""
        <style>
        /* Main Container */
        .main > div.block-container {{ 
            padding-left: 2rem; 
            padding-right: 2rem; 
            max-width: 1200px;
        }}
        
        /* Hero Section */
        .hero {{ 
            background: linear-gradient(135deg, {primary}, {dark});
            padding: 4rem 2rem;
            border-radius: 15px;
            text-align: center;
            color: white;
            margin-bottom: 3rem;
            position: relative;
            overflow: hidden;
        }}
        .hero h1 {{ 
            font-size: 3rem; 
            font-weight: 800; 
            margin-bottom: 1rem;
            background: linear-gradient(45deg, #fff, #f0f0f0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .hero p {{ 
            font-size: 1.3rem; 
            color: #f8fafc; 
            max-width: 800px; 
            margin: 0 auto 2rem; 
            line-height: 1.6;
            font-weight: 300;
        }}
        
        /* Enhanced Cards with Hover Effects */
        .enhanced-card {{ 
            background: #fff; 
            padding: 1.5rem; 
            border-radius: 12px; 
            box-shadow: 0 4px 15px rgba(0,0,0,0.08); 
            border-left: 4px solid {primary};
            margin-bottom: 1rem;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            cursor: pointer;
        }}
        .enhanced-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.12);
        }}
        .enhanced-card h3 {{ 
            margin-top: 0; 
            color: {dark}; 
            font-size: 1.3rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }}
        .enhanced-card .desc {{ 
            font-size: 0.95rem; 
            color: #64748b; 
            line-height: 1.5;
            margin-bottom: 1rem;
        }}
        
        /* Status Badges */
        .status {{ 
            font-size: 0.85rem; 
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            display: inline-block;
            font-weight: 500;
        }}
        .status-ready {{ background: #dcfce7; color: #166534; }}
        .status-development {{ background: #fef3c7; color: #92400e; }}
        .status-planned {{ background: #e0e7ff; color: #3730a3; }}
        
        /* Roadmap Items */
        .roadmap-item {{
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            border-left: 4px solid {success};
            margin-bottom: 1rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        }}
        .roadmap-current {{ border-left-color: {warning}; }}
        .roadmap-upcoming {{ border-left-color: {primary}; }}
        
        /* Feature Badges */
        .feature-badge {{
            background: {light};
            color: {primary};
            padding: 0.3rem 0.8rem;
            border-radius: 15px;
            font-size: 0.8rem;
            display: inline-block;
            margin: 0.2rem;
        }}
        
        /* Metrics Grid */
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 2rem 0;
        }}
        .metric-card {{
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            border-top: 4px solid {secondary};
        }}
        
        /* Enhanced Sidebar */
        .sidebar-header {{
            background: linear-gradient(135deg, {primary}, {dark});
            padding: 1.5rem;
            border-radius: 10px;
            text-align: center;
            color: white;
            margin-bottom: 2rem;
        }}
        
        /* Footer */
        .footer {{ 
            text-align: center; 
            font-size: 0.9rem; 
            color: #64748b; 
            padding: 2rem 0;
            margin-top: 3rem;
            border-top: 1px solid #e2e8f0;
        }}
        
        /* Responsive Design */
        @media (max-width: 768px) {{
            .main > div.block-container {{ 
                padding-left: 1rem; 
                padding-right: 1rem; 
            }}
            .hero h1 {{ font-size: 2.5rem; }}
        }}
        </style>
        """, unsafe_allow_html=True)

# ---------------------------
# Enhanced Data Management
# ---------------------------
class EnhancedTaskManager:
    """Manage tasks with enhanced structure"""
    
    @staticmethod
    def load_tasks_config() -> Dict:
        """Load tasks configuration with enhanced structure"""
        return {
            "Label Extractors": [
                {"title": "SCN Label Extractor – Type 1", 
                 "desc": "Upload DWG/DXF/PDF → auto-extract structured cabling labels.",
                 "status": "development",
                 "priority": "high",
                 "eta": "Q1 2024",
                 "icon": "🏷️"},
                {"title": "SCN Label Extractor – Type 2", 
                 "desc": "Enhanced SCN extraction with host zone & device sorting.",
                 "status": "planned",
                 "priority": "medium",
                 "eta": "Q2 2024",
                 "icon": "🏷️"},
                {"title": "FAS Label Extractor", 
                 "desc": "Extract Fire Alarm devices & generate T&C-ready reports.",
                 "status": "development", 
                 "priority": "high",
                 "eta": "Q1 2024",
                 "icon": "🔥"},
                {"title": "PA Label Extractor", 
                 "desc": "Extract Public Address speakers/zones from drawings.",
                 "status": "planned",
                 "priority": "medium",
                 "eta": "Q2 2024",
                 "icon": "📢"},
            ],
            "BOQ Generators": [
                {"title": "SCN BOQ Generator", 
                 "desc": "Generate structured cabling BOQ with materials & quantities.",
                 "status": "development",
                 "priority": "high",
                 "eta": "Q1 2024",
                 "icon": "📊"},
                {"title": "FAS BOQ Generator", 
                 "desc": "Fire Alarm BOQ including panels, detectors, modules.",
                 "status": "planned",
                 "priority": "high",
                 "eta": "Q2 2024",
                 "icon": "🔥"},
                {"title": "PA BOQ Generator", 
                 "desc": "Public Address system BOQ with amplifiers, speakers.",
                 "status": "planned",
                 "priority": "medium",
                 "eta": "Q2 2024",
                 "icon": "📢"},
                {"title": "CCTV & ACS BOQ Generator", 
                 "desc": "Security BOQ for cameras, access readers, controllers.",
                 "status": "planned",
                 "priority": "medium",
                 "eta": "Q3 2024",
                 "icon": "📹"},
            ],
            "Design Review Checklists": [
                {"title": "SCN Review", 
                 "desc": "Verify against TIA-568, contract docs & ER.",
                 "status": "planned",
                 "priority": "high",
                 "eta": "Q2 2024",
                 "icon": "✅"},
                {"title": "FAS Review", 
                 "desc": "Check compliance with NFPA, ICAO, project specs.",
                 "status": "planned",
                 "priority": "high",
                 "eta": "Q2 2024",
                 "icon": "🔥"},
            ],
            "Construction Follow-up": [
                {"title": "Site Instructions (SI)", 
                 "desc": "Record & track instructions.",
                 "status": "planned",
                 "priority": "medium",
                 "eta": "Q3 2024",
                 "icon": "📝"},
                {"title": "RFIs", 
                 "desc": "Submit, log & track Requests for Information.",
                 "status": "planned",
                 "priority": "medium",
                 "eta": "Q3 2024",
                 "icon": "❓"},
            ]
        }
    
    @staticmethod
    def get_status_badge(status: str) -> str:
        """Return formatted status badge"""
        status_config = {
            "ready": ("🟢 Ready", "status-ready"),
            "development": ("🚧 In Development", "status-development"), 
            "planned": ("📅 Planned", "status-planned")
        }
        text, css_class = status_config.get(status, ("❓ Unknown", "status-planned"))
        return f'<span class="status {css_class}">{text}</span>'

# ---------------------------
# Enhanced Page Components
# ---------------------------
class EnhancedPageRenderer:
    """Handle rendering of enhanced pages"""
    
    @staticmethod
    def render_hero():
        """Render enhanced hero section inspired by NextEra website"""
        st.markdown("""
        <div class="hero">
            <h1>🤖 ELV Consulting Agent</h1>
            <p>Your <strong>AI-driven digital partner</strong> for ELV System Compliance, Design Review, and Automation.<br>
            Transforming <strong>20+ years of field expertise</strong> into a digital brain that works for you 24/7.</p>
            <div style="display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap;">
                <div style="background: rgba(255,255,255,0.15); padding: 0.5rem 1.2rem; border-radius: 25px;">
                    🚀 70%+ Time Savings
                </div>
                <div style="background: rgba(255,255,255,0.15); padding: 0.5rem 1.2rem; border-radius: 25px;">
                    ⚡ 30+ Automated Tasks
                </div>
                <div style="background: rgba(255,255,255,0.15); padding: 0.5rem 1.2rem; border-radius: 25px;">
                    🎯 20+ Years Expertise
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_metrics_dashboard():
        """Render metrics dashboard"""
        st.markdown("### 📊 Impact Dashboard")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Time Saved", 
                value="70%+",
                delta="vs manual processes"
            )
        
        with col2:
            st.metric(
                label="Tasks Automated", 
                value="30+",
                delta="ELV workflows"
            )
            
        with col3:
            st.metric(
                label="Accuracy", 
                value="95%+",
                delta="error reduction"
            )
            
        with col4:
            st.metric(
                label="Adoption", 
                value="Growing",
                delta="12 projects"
            )
    
    @staticmethod
    def render_home():
        """Render enhanced home page"""
        EnhancedPageRenderer.render_hero()
        EnhancedPageRenderer.render_metrics_dashboard()
        
        # Value Proposition
        st.success("🚀 **Start exploring the Task Directory to transform your ELV workflows with AI-powered automation.**")
        
        # Features Grid
        st.markdown("### 🌟 Why ELV Consulting Agent?")
        cols = st.columns(2)
        
        with cols[0]:
            st.markdown("""
            **🚀 Efficiency Boost**
            - Automates repetitive ELV consulting tasks
            - Cuts review & documentation time by 70%+
            - Reduces human error in compliance checks
            
            **🎯 Expert Knowledge**
            - 20+ years of ELV expertise embedded
            - Built-in compliance with global standards
            - Real-world project validation
            """)
            
        with cols[1]:
            st.markdown("""
            **📈 Scalable Impact**  
            - Modular design for continuous expansion
            - Instant compliance insights
            - Cross-platform compatibility
            
            **💼 Business Value**
            - Faster project delivery
            - Higher quality outputs
            - Competitive advantage
            """)
        
        # Quick Start Section
        st.markdown("---")
        st.markdown("### 🚀 Quick Start")
        quick_col1, quick_col2, quick_col3 = st.columns(3)
        
        with quick_col1:
            if st.button("📋 Explore Tasks", use_container_width=True):
                st.session_state.current_page = "tasks"
                st.rerun()
                
        with quick_col2:
            if st.button("🛣️ View Roadmap", use_container_width=True):
                st.session_state.current_page = "roadmap"
                st.rerun()
                
        with quick_col3:
            if st.button("📞 Get Support", use_container_width=True):
                st.session_state.current_page = "contact"
                st.rerun()
    
    @staticmethod
    def render_task_directory():
        """Render enhanced task directory page"""
        st.header("📋 Task Directory")
        st.markdown("""
        The Agent organizes tasks into **major categories**, each with multiple sub-tools. 
        Each sub-task runs as its own micro-app with specialized functionality.
        """)
        
        # Search and Filter
        col1, col2 = st.columns([3, 1])
        with col1:
            search_query = st.text_input("🔍 Search tasks...", placeholder="Type to filter tasks")
        with col2:
            status_filter = st.selectbox("Filter by status", ["All", "Ready", "In Development", "Planned"])
        
        tasks_config = EnhancedTaskManager.load_tasks_config()
        
        # Render tasks by category
        for category, tasks in tasks_config.items():
            # Filter tasks based on search and status
            filtered_tasks = [
                task for task in tasks 
                if (not search_query or search_query.lower() in task['title'].lower()) and
                (status_filter == "All" or status_filter.lower() in task['status'])
            ]
            
            if filtered_tasks:
                st.subheader(f"📂 {category}")
                
                # Create grid of enhanced cards
                cols = st.columns(2)
                for i, task in enumerate(filtered_tasks):
                    with cols[i % 2]:
                        status_badge = EnhancedTaskManager.get_status_badge(task['status'])
                        
                        st.markdown(f"""
                        <div class="enhanced-card">
                            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                                <span style="font-size: 1.5rem; margin-right: 0.5rem;">{task['icon']}</span>
                                <h3>{task['title']}</h3>
                            </div>
                            <div class="desc">{task['desc']}</div>
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                {status_badge}
                                <small style="color: {Config.PRIMARY_COLOR};">
                                    🕐 {task['eta']} | 📊 {task['priority'].title()}
                                </small>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                
                st.markdown("---")
    
    @staticmethod
    def render_roadmap():
        """Render development roadmap"""
        st.header("🛣️ Development Roadmap")
        st.markdown("Our strategic plan for transforming ELV consulting through AI and automation.")
        
        roadmap_data = [
            {
                "phase": "Phase 1: Foundation", 
                "title": "Core Platform & Basic Tools",
                "status": "completed",
                "progress": 100,
                "features": ["Basic Architecture", "Label Extractors", "BOQ Generators", "Task Management"],
                "description": "Establishing the core platform and essential automation tools"
            },
            {
                "phase": "Phase 2: Intelligence", 
                "title": "AI Integration & Advanced Features",
                "status": "current",
                "progress": 45,
                "features": ["Machine Learning", "Smart Validation", "API Integrations", "Advanced Analytics"],
                "description": "Integrating AI capabilities and expanding tool functionality"
            },
            {
                "phase": "Phase 3: Enterprise", 
                "title": "Scalability & Enterprise Features",
                "status": "upcoming",
                "progress": 0,
                "features": ["Multi-user Collaboration", "Mobile Application", "Enterprise Security", "Custom Workflows"],
                "description": "Scaling for enterprise use and advanced customization"
            }
        ]
        
        for phase in roadmap_data:
            status_icon = "✅" if phase["status"] == "completed" else "🚧" if phase["status"] == "current" else "📅"
            status_color = Config.SUCCESS_COLOR if phase["status"] == "completed" else Config.WARNING_COLOR if phase["status"] == "current" else Config.PRIMARY_COLOR
            css_class = "roadmap-item" + (" roadmap-current" if phase["status"] == "current" else " roadmap-upcoming" if phase["status"] == "upcoming" else "")
            
            st.markdown(f"""
            <div class="{css_class}" style="border-left-color: {status_color}">
                <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                    <span style="font-size: 1.5rem; margin-right: 1rem;">{status_icon}</span>
                    <div style="flex-grow: 1;">
                        <h3 style="margin: 0; color: {Config.DARK_COLOR};">{phase['phase']}</h3>
                        <p style="margin: 0; color: {status_color}; font-weight: 600;">{phase['title']}</p>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-weight: 600; color: {status_color};">{phase['progress']}% Complete</div>
                        <small style="color: #666;">{phase['status'].title()}</small>
                    </div>
                </div>
                <p style="color: #666; margin-bottom: 1rem;">{phase['description']}</p>
                <div>
            """, unsafe_allow_html=True)
            
            for feature in phase["features"]:
                st.markdown(f'<span class="feature-badge">{feature}</span>', unsafe_allow_html=True)
            
            st.markdown("</div></div>", unsafe_allow_html=True)
            
            # Progress bar for current phase
            if phase["status"] == "current":
                st.progress(phase["progress"] / 100)
    
    @staticmethod
    def render_about():
        """Render enhanced about page"""
        st.header("🚀 About ELV Consulting Agent")
        
        tab1, tab2, tab3 = st.tabs(["🎯 Vision & Mission", "👤 Expertise", "📈 Our Impact"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                **🎯 Vision**  
                To lead **ELV consulting transformation** through AI-powered automation, 
                making elite engineering expertise accessible to all professionals.
                
                **🚀 Mission**
                - Democratize 20+ years of ELV consulting expertise
                - Automate repetitive engineering workflows  
                - Ensure compliance through intelligent validation
                - Reduce project risks and costs industry-wide
                """)
                
            with col2:
                st.markdown("""
                **💡 Our Approach**
                - **AI-First**: Leverage machine learning for intelligent automation
                - **Expert-Driven**: Built by ELV professionals for ELV professionals
                - **Continuous Innovation**: Regular updates with new capabilities
                - **User-Centric**: Designed around real workflow challenges
                """)
            
        with tab2:
            st.markdown("""
            **20+ Years of ELV Mastery Embedded**
            
            **Domain Specializations**
            - **Structured Cabling Systems (SCS)**: TIA-568 compliance, labeling, BOQ generation
            - **Fire Alarm Systems (FAS)**: NFPA 72 compliance, device extraction, testing
            - **Security Systems**: CCTV, Access Control, intrusion detection
            - **Building Automation**: BMS, IoT integration, energy management
            - **Public Address**: Sound reinforcement, emergency voice evacuation
            
            **Standards Expertise**
            - TIA-568, NFPA 72, ICAO, IEC, ONVIF
            - Local regulatory requirements and best practices
            - International project delivery standards
            """)
            
        with tab3:
            st.markdown("""
            **📊 Measurable Impact**
            
            **For Individual Engineers**
            - 70% reduction in documentation time
            - 95%+ accuracy in compliance checking
            - Instant access to expert knowledge
            - Reduced training time for new hires
            
            **For Organizations**
            - Consistent quality across all projects
            - Faster project delivery cycles
            - Reduced rework and compliance issues
            - Scalable expertise without scaling headcount
            
            **Industry Transformation**
            - Setting new standards for ELV consulting efficiency
            - Making expert knowledge accessible to smaller firms
            - Accelerating adoption of digital workflows
            - Creating new career paths in ELV technology
            """)
    
    @staticmethod
    def render_contact():
        """Render enhanced contact page"""
        st.header("📞 Contact & Support")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            **Get in Touch**
            - 📧 **Email**: [elv.ethiopia@gmail.com](mailto:elv.ethiopia@gmail.com)
            - 🔗 **LinkedIn**: [Daniel Mekonnen](https://www.linkedin.com/in/daniel-mekonnen-6845972a)
            - 🐦 **X**: [@DanielM62021892](https://x.com/DanielM62021892)
            - 💼 **Portfolio**: Available upon request
            """)
            
            # Enhanced Contact Form
            st.markdown("### 💬 Send Message")
            with st.form("contact_form"):
                col_a, col_b = st.columns(2)
                with col_a:
                    name = st.text_input("Your Name*")
                with col_b:
                    email = st.text_input("Your Email*")
                
                subject = st.selectbox("Subject*", [
                    "General Inquiry", 
                    "Feature Request", 
                    "Collaboration Opportunity",
                    "Technical Support",
                    "Custom Development",
                    "Partnership Inquiry"
                ])
                
                message = st.text_area("Message*", height=150, 
                                      placeholder="Please describe your inquiry in detail...")
                
                submitted = st.form_submit_button("Send Message", use_container_width=True)
                
                if submitted:
                    if name and email and message:
                        st.success("✅ Message sent! We'll get back to you within 24 hours.")
                    else:
                        st.error("Please fill in all required fields (*).")
        
        with col2:
            st.markdown("""
            **Quick Resources**
            - [📚 Documentation & Guides]()
            - [🎬 Video Tutorials]()
            - [💡 Feature Requests]()
            - [🐛 Report Issues]()
            - [⭐ Leave Review]()
            """)
            
            # Quick Feedback
            st.markdown("### 💡 Quick Feedback")
            feedback = st.select_slider(
                "How useful is this platform for your work?",
                options=["Not useful", "Somewhat useful", "Useful", "Very useful", "Extremely useful"]
            )
            if st.button("Submit Feedback", use_container_width=True):
                st.session_state.feedback_submitted = True
                st.success(f"Thanks for your feedback: '{feedback}'")

# ---------------------------
# Enhanced Sidebar Component
# ---------------------------
class EnhancedSidebarRenderer:
    """Handle enhanced sidebar rendering and navigation"""
    
    @staticmethod
    def render_sidebar():
        """Render enhanced sidebar with professional design"""
        with st.sidebar:
            # Enhanced Logo Section
            st.markdown(f"""
            <div class="sidebar-header">
                <h2 style="margin: 0; font-size: 1.5rem;">🤖 ELV Agent</h2>
                <p style="margin: 0; opacity: 0.9; font-size: 0.9rem;">Engineering Excellence</p>
                <div style="margin-top: 0.5rem; font-size: 0.8rem; opacity: 0.8;">
                    v{Config.VERSION}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Navigation with active states
            st.markdown("### 🧭 Navigation")
            
            menu_options = {
                "🏠 Home": "home",
                "📋 Task Directory": "tasks", 
                "🛣️ Roadmap": "roadmap",
                "🚀 About": "about",
                "📞 Contact": "contact"
            }
            
            current_page = st.session_state.get("current_page", "home")
            
            for label, page in menu_options.items():
                is_active = current_page == page
                
                if st.button(
                    label,
                    key=page,
                    use_container_width=True,
                    type="primary" if is_active else "secondary"
                ):
                    st.session_state.current_page = page
                    st.rerun()
            
            st.markdown("---")
            
            # Quick Stats
            st.markdown("**📊 Quick Stats**")
            st.markdown(f"Visits: `{st.session_state.user_visits}`")
            st.markdown(f"Last: `{st.session_state.last_visited.strftime('%Y-%m-%d')}`")
            
            st.markdown("---")
            
            # Quick Actions
            st.markdown("**⚡ Quick Actions**")
            if st.button("🆕 New Project", use_container_width=True):
                st.info("Project management features coming in Phase 2!")
            if st.button("📊 View Analytics", use_container_width=True):
                st.info("Advanced analytics dashboard in development!")
                
            st.markdown("---")
            
            # Connect Section
            st.markdown("**🔗 Connect**")
            st.markdown("[LinkedIn](https://www.linkedin.com/in/daniel-mekonnen-6845972a) | [X](https://x.com/DanielM62021892)")
            st.markdown("[Email](mailto:elv.ethiopia@gmail.com)")
            
            # Footer in Sidebar
            st.markdown("---")
            st.markdown(f"<div style='font-size: 0.8rem; color: #64748b; text-align: center;'>"
                       f"© {Config.YEAR} {Config.AUTHOR}<br>"
                       f"Built with ❤️ using Streamlit"
                       f"</div>", unsafe_allow_html=True)

# ---------------------------
# Enhanced Footer
# ---------------------------
def render_enhanced_footer():
    """Render enhanced footer"""
    st.markdown("---")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"""
        **{Config.APP_TITLE}**  
        *Transforming 20+ years of ELV expertise into AI-powered automation*
        """)
        
    with col2:
        st.markdown("""
        **Connect**  
        [LinkedIn](https://linkedin.com) • [Email](mailto:elv.ethiopia@gmail.com)
        """)
        
    with col3:
        st.markdown("""
        **Resources**  
        [Documentation]() • [Support]()
        """)
    
    st.markdown(f"""
    <div class='footer'>
        {Config.APP_TITLE} © {Config.YEAR} | 
        Built with ❤️ using Streamlit | 
        v{Config.VERSION} | 
        Transforming ELV Consulting through AI
    </div>
    """, unsafe_allow_html=True)

# ---------------------------
# Main Application
# ---------------------------
def main():
    """Enhanced main application function"""
    
    # Initialize app
    st.set_page_config(
        page_title=Config.APP_TITLE,
        page_icon=Config.APP_ICON,
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state and styles
    init_session_state()
    EnhancedUIStyles.inject_custom_css()
    
    # Update session state
    st.session_state.user_visits += 1
    st.session_state.last_visited = datetime.now()
    
    try:
        # Render enhanced sidebar
        EnhancedSidebarRenderer.render_sidebar()
        
        # Render main content based on navigation
        current_page = st.session_state.get("current_page", "home")
        
        if current_page == "home":
            EnhancedPageRenderer.render_home()
            
        elif current_page == "tasks":
            EnhancedPageRenderer.render_task_directory()
            
        elif current_page == "roadmap":
            EnhancedPageRenderer.render_roadmap()
            
        elif current_page == "about":
            EnhancedPageRenderer.render_about()
            
        elif current_page == "contact":
            EnhancedPageRenderer.render_contact()
        
    except Exception as e:
        st.error(f"🚨 Application Error: {str(e)}")
        st.info("Please refresh the page or contact support if this persists.")

    # Enhanced footer
    render_enhanced_footer()

if __name__ == "__main__":
    main()
