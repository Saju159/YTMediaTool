import streamlit as st
import time

# --- Page Configuration ---
st.set_page_config(
    page_title="Nexus | Intelligent Tools",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- State Management ---
# Initialize session state for navigation if it doesn't exist
if "current_page" not in st.session_state:
    st.session_state.current_page = st.query_params.get("page", "home")

def navigate_to(page_name):
    st.session_state.current_page = page_name
    st.query_params["page"] = page_name
    st.rerun()

# --- Custom CSS for Styling ---
st.markdown("""
<style>
    /* Global Styles & Theme Enforcement */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Force Light Theme colors for this design */
    .stApp {
        background-color: #ffffff;
        color: #1f2937;
    }

    h1, h2, h3, h4, h5, h6, p, span, div {
        color: #1f2937;
    }
    
    /* --- HIDE DEFAULT STREAMLIT ELEMENTS (MENU BAR) --- */
    /* Hides the hamburger menu in the top right */
    #MainMenu { visibility: hidden; }
    /* Hides the default Streamlit header bar, including the deploy button */
    header { visibility: hidden; }
    /* Hides the "Made with Streamlit" footer text */
    footer { visibility: hidden; }
    /* ------------------------------------------------ */

    /* Navbar Styling */
    div.stButton > button {
        width: 100%;
        border: none;
        background-color: transparent;
        color: #4b5563;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        color: #2563eb;
        background-color: #f3f4f6;
    }
    div.stButton > button:focus {
        color: #2563eb;
        border-color: transparent;
        box-shadow: none;
    }
    
    /* Active State for Navbar Buttons */
    div.stButton > button:active {
        background-color: #eff6ff;
        color: #2563eb;
    }

    /* Hero Section Gradient */
    .hero-container {
        padding: 4rem 2rem;
        text-align: center;
        background: radial-gradient(ellipse at top right, rgba(219, 234, 254, 0.4), rgba(249, 250, 251, 1), white);
        border-radius: 1rem;
        margin-bottom: 2rem;
    }
    
    /* Card Styling */
    .custom-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 0.75rem;
        border: 1px solid #f3f4f6;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        height: 100%;
        transition: transform 0.2s;
    }
    .custom-card:hover {
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transform: translateY(-2px);
    }
    
    /* Remove default top padding */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 5rem;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #6b7280 !important;
        padding: 2rem;
        border-top: 1px solid #e5e7eb;
        margin-top: 3rem;
    }
    
    /* Override specific Streamlit elements to match theme */
    div[data-testid="stMetricValue"] {
        color: #111827;
    }
</style>
""", unsafe_allow_html=True)

# --- Navbar Component ---
def navbar():
    with st.container():
        col1, col2, col3, col4, col5 = st.columns([1, 4, 1, 1, 1])
        
        with col1:
            st.markdown("### ⚡ Nexus")
            
        # Navigation Buttons
        
        with col3:
            if st.button("Home", key="nav_home"):
                navigate_to("home")
        with col4:
            if st.button("About", key="nav_about"):
                navigate_to("about")
        with col5:
            if st.button("Contact", key="nav_contact"):
                navigate_to("contact")
    st.divider()

# --- Page Components ---

def home_page():
    # Hero Section
    st.markdown("""
    <div class="hero-container">
        <span style="background-color: #eff6ff; color: #1d4ed8; padding: 0.5rem 1rem; border-radius: 9999px; font-size: 0.875rem; font-weight: 500; border: 1px solid #dbeafe;">
            v2.0 Now Available
        </span>
        <h1 style="font-size: 3.5rem; font-weight: 800; color: #111827; margin-top: 1.5rem; margin-bottom: 1rem; line-height: 1.1;">
            Build faster with <br/>
            <span style="background: -webkit-linear-gradient(left, #2563eb, #4f46e5); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                Intelligent Tools
            </span>
        </h1>
        <p style="font-size: 1.25rem; color: #4b5563; max-width: 42rem; margin: 0 auto 2.5rem auto;">
            We provide the infrastructure and components you need to scale your application effectively. Simple, powerful, and built for modern teams.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # CTA Buttons (Centered using columns)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        sc1, sc2 = st.columns(2)
        with sc1:
            if st.button("Get Started →", type="primary", use_container_width=True):
                navigate_to("contact")
        with sc2:
            if st.button("View Services", use_container_width=True):
                st.toast("Redirecting to Services...")
                time.sleep(0.5)
                st.info("Services are just below in the features grid!")

    # Features Grid
    st.write("")
    st.write("")
    st.markdown("<h2 style='text-align: center; margin-bottom: 2rem; color: #111827;'>Everything you need</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="custom-card">
            <div style="font-size: 2rem; margin-bottom: 1rem;">🌍</div>
            <h3 style="font-weight: 700; font-size: 1.25rem; margin-bottom: 0.5rem; color: #111827;">Global Scale</h3>
            <p style="color: #4b5563;">Deploy your application to the edge with a single click. We handle the complexity.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="custom-card">
            <div style="font-size: 2rem; margin-bottom: 1rem;">⚡</div>
            <h3 style="font-weight: 700; font-size: 1.25rem; margin-bottom: 0.5rem; color: #111827;">Lightning Fast</h3>
            <p style="color: #4b5563;">Optimized for speed with automatic image compression and code splitting.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="custom-card">
            <div style="font-size: 2rem; margin-bottom: 1rem;">🛡️</div>
            <h3 style="font-weight: 700; font-size: 1.25rem; margin-bottom: 0.5rem; color: #111827;">Secure by Default</h3>
            <p style="color: #4b5563;">Enterprise-grade security features including DDoS protection and SSL.</p>
        </div>
        """, unsafe_allow_html=True)

def about_page():
    st.markdown("# About Our Mission")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        ### We're here to fix fragmentation.
        
        Founded in 2024, we set out to solve the fragmentation in modern web development. We believe that building great software shouldn't require stitching together dozens of disparate tools.
        
        Our team consists of industry veterans from top tech companies who have seen firsthand the challenges of scaling applications.
        """)
        
        st.write("")
        s1, s2 = st.columns(2)
        s1.metric(label="Active Users", value="10k+")
        s2.metric(label="Uptime", value="99.9%")
        
    with col2:
        st.image("https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=800&q=80", caption="Headquarters in Helsinki, Finland", use_container_width=True)

def contact_page():
    st.markdown("<div style='text-align: center; margin-bottom: 3rem;'><h1>Get in Touch</h1><p>We'd love to hear from you.</p></div>", unsafe_allow_html=True)
    
    c_spacer1, c_main, c_spacer2 = st.columns([1, 2, 1])
    
    with c_main:
        with st.form("contact_form"):
            col_a, col_b = st.columns(2)
            with col_a:
                first_name = st.text_input("First Name", placeholder="John")
            with col_b:
                last_name = st.text_input("Last Name", placeholder="Doe")
                
            email = st.text_input("Email Address", placeholder="john@example.com")
            message = st.text_area("Message", placeholder="How can we help you?")
            
            submitted = st.form_submit_button("Send Message", type="primary")
            
            if submitted:
                if not email or not message:
                    st.error("Please fill out the email and message fields.")
                else:
                    st.success(f"Thanks {first_name}! We've received your message.")

# --- Main App Execution ---

navbar()

# Use session state to determine which page to show
current_page = st.session_state.current_page

if current_page == "home":
    home_page()
elif current_page == "about":
    about_page()
elif current_page == "contact":
    contact_page()
else:
    # Fallback
    home_page()

# Footer
st.markdown("""
<div class="footer">
    <p>© 2024 Nexus Inc. All rights reserved. | Built with Streamlit & Python</p>
</div>
""", unsafe_allow_html=True)