"""
Kothalawala Library Management System
Theme  : Ivory & Forest Green
Layout : Icon Sidebar (200px)

This is the main frontend application built with Streamlit.
It provides the user interface for:
- Dashboard with statistics
- Inventory management
- Adding new books
- Searching and borrowing books
- Processing returns and calculating late fees
"""

import streamlit as st
from library_backend import LibraryManager, Book
from datetime import datetime, timedelta
import traceback
import pandas as pd

# ═════════════════════════════════════════════════════════════════════════════
# 📍 QUICK NAVIGATION GUIDE - Find each sidebar page code below:
# ═════════════════════════════════════════════════════════════════════════════
# 
# 🏠 HOME PAGE / DASHBOARD           Line ~890   (page_dashboard function)
#     └─ Library stats, alerts, activity summary
#
# 📦 INVENTORY PAGE                  Line ~1120  (page_inventory function)
#     └─ Complete catalog, search, filter, CSV export
#
# ➕ ADD BOOKS PAGE                  Line ~1208  (page_add_books function)
#     └─ Form to add new books with validation
#
# 🔍 SEARCH & BORROW PAGE            Line ~1328  (page_search function)
#     └─ Search books, view availability, process borrowing
#
# ↩️ RETURNS & FEES PAGE             Line ~1459  (page_returns function)
#     └─ Process returns, calculate late fees
#
# ═════════════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
# Set up the basic Streamlit page configuration (title, icon, layout)
st.set_page_config(
    page_title="Kothalawala E-Library",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
# Streamlit "forgets" everything when page refreshes, so we use session_state
# to remember things between user interactions (like sidebar selections, form data)
if "lib" not in st.session_state:
    try:
        # Initialize the database connection (connects to Firebase)
        st.session_state.lib   = LibraryManager()
        st.session_state.db_ok = True
    except Exception as e:
        st.session_state.db_ok    = False
        st.session_state.db_error = str(e)

# Initialize page state variables (remember the current page, confirmations, etc.)
for k, v in {
    "page":           "Dashboard",  # Which page is user viewing
    "confirm_add":    False,        # Waiting for add book confirmation?
    "confirm_borrow": False,        # Waiting for borrow confirmation?
    "confirm_return": False,        # Waiting for return confirmation?
    "pending_book":   None,         # Book data waiting to be confirmed
    "pending_borrow": None,         # Borrow data waiting to be confirmed
    "add_ok":         None,         # Was book successfully added?
    "borrow_ok":      None,         # Was borrow successful?
    "return_ok":      None,         # Was return successful?
    "ret_isbn":       "",           # ISBN being returned
    "ret_name":       "",           # Name of person returning
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────────────────────────────────────
# CSS STYLING
# ─────────────────────────────────────────────────────────────────────────────
# All the beautiful custom styling for the app (colors, fonts, animations, layout)
# Theme colors: Forest Green (#2D6A4F) and Ivory (#EAEFEF)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600;700;800&family=Inter:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
#MainMenu, footer, header   { visibility: hidden; }

.main, [data-testid="stAppViewContainer"] { background: #EAEFEF !important; }
.main .block-container {
    padding: 38px 48px 72px !important;
    max-width: 1280px !important;
}

section[data-testid="stSidebar"] {
    background-color: #1A3D2E !important;
    min-width: 200px !important;
    max-width: 200px !important;
    box-shadow: 3px 0 20px rgba(0,0,0,0.18) !important;
    transform: translateX(0) !important;
    display: block !important;
    visibility: visible !important;
}
section[data-testid="stSidebar"] > div {
    background-color: #1A3D2E !important;
    min-width: 200px !important;
    max-width: 200px !important;
    width: 200px !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
    background-color: #1A3D2E !important;
    padding: 20px 12px 16px !important;
}

[data-testid="collapsedControl"] {
    background-color: #1A3D2E !important;
    display: block !important;
    visibility: visible !important;
}
[data-testid="collapsedControl"] svg {
    color: #74C69D !important;
    fill: #74C69D !important;
}

section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
    width: 100% !important;
}
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    font-size: 13px !important;
    font-weight: 600 !important;
    color: #D8F3DC !important;
    margin: 0 !important;
    letter-spacing: 0.3px !important;
    line-height: 1.3 !important;
}
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] small {
    display: block !important;
    font-size: 9px !important;
    font-weight: 500 !important;
    letter-spacing: 1.2px !important;
    color: rgba(116,198,157,0.45) !important;
    text-transform: uppercase !important;
    margin-top: 1px !important;
}

section[data-testid="stSidebar"] hr {
    border: none !important;
    border-top: 1px solid rgba(116,198,157,0.15) !important;
    margin: 12px 0 10px !important;
}

section[data-testid="stSidebar"] .stButton {
    width: 100% !important;
    margin-bottom: 4px !important;
}

section[data-testid="stSidebar"] button,
section[data-testid="stSidebar"] .stButton button,
section[data-testid="stSidebar"] div[data-testid="stButton"] button {
    width: 100% !important;
    height: 38px !important;
    min-height: 38px !important;
    padding: 0 12px !important;
    margin: 0 !important;
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    justify-content: flex-start !important;
    gap: 10px !important;
    border-radius: 8px !important;
    border: none !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    letter-spacing: 0.1px !important;
    line-height: 1 !important;
    white-space: nowrap !important;
    text-align: left !important;
    box-shadow: none !important;
    transition: background 0.13s ease, color 0.13s ease !important;
}

section[data-testid="stSidebar"] button[kind="secondary"],
section[data-testid="stSidebar"] .stButton button[kind="secondary"],
section[data-testid="stSidebar"] button[data-baseweb="button"][kind="secondary"] {
    background: transparent !important;
    background-color: transparent !important;
    background-image: none !important;
    color: #74C69D !important;
    font-weight: 500 !important;
}

section[data-testid="stSidebar"] button[kind="primary"],
section[data-testid="stSidebar"] .stButton button[kind="primary"],
section[data-testid="stSidebar"] button[data-baseweb="button"][kind="primary"] {
    background: #2D6A4F !important;
    background-color: #2D6A4F !important;
    background-image: none !important;
    color: #D8F3DC !important;
    font-weight: 600 !important;
    box-shadow: none !important;
}

section[data-testid="stSidebar"] button p {
    margin: 0 !important;
    padding: 0 !important;
    line-height: 1 !important;
    color: inherit !important;
}

section[data-testid="stSidebar"] button[kind="secondary"]:hover {
    background: rgba(116,198,157,0.12) !important;
    background-color: rgba(116,198,157,0.12) !important;
    background-image: none !important;
    color: #D8F3DC !important;
    transform: none !important;
    box-shadow: none !important;
}

section[data-testid="stSidebar"] button[kind="primary"]:hover {
    background: #357A5C !important;
    background-color: #357A5C !important;
    background-image: none !important;
    color: #D8F3DC !important;
    transform: none !important;
    box-shadow: none !important;
}

/* Hide tooltips on sidebar buttons */
section[data-testid="stSidebar"] button[title] {
    pointer-events: auto !important;
}
section[data-testid="stSidebar"] button:hover::after,
section[data-testid="stSidebar"] button:hover::before {
    display: none !important;
    visibility: hidden !important;
}

.stButton > button {
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    border-radius: 10px !important;
    padding: 10px 20px !important;
    transition: all 0.16s ease !important;
}
.stButton > button[kind="primary"] {
    background: #2D6A4F !important;
    color: #F0FDF4 !important;
    border: none !important;
}
.stButton > button[kind="primary"]:hover {
    background: #1A4535 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(29,67,46,0.28) !important;
}
.stButton > button[kind="secondary"] {
    background: #FFFFFF !important;
    color: #2D6A4F !important;
    border: 1.5px solid #B7DFC9 !important;
}
.stButton > button[kind="secondary"]:hover {
    background: #F0FDF4 !important;
    border-color: #2D6A4F !important;
    transform: translateY(-1px) !important;
}

.stTextInput > div > div > input,
.stNumberInput > div > div > input {
    background: #FFFFFF !important;
    border: 1.5px solid #C5E3D2 !important;
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    color: #1A3D2E !important;
    padding: 10px 14px !important;
    transition: border-color 0.15s, box-shadow 0.15s !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
    border-color: #40916C !important;
    box-shadow: 0 0 0 3px rgba(64,145,108,0.13) !important;
    outline: none !important;
}
.stTextInput label, .stNumberInput label,
.stSelectbox label, .stDateInput label {
    font-family: 'Inter', sans-serif !important;
    font-size: 11.5px !important;
    font-weight: 600 !important;
    color: #40916C !important;
    letter-spacing: 0.6px !important;
    text-transform: uppercase !important;
}
.stSelectbox > div > div {
    border: 1.5px solid #C5E3D2 !important;
    border-radius: 10px !important;
    background: #FFFFFF !important;
    font-size: 14px !important;
}
.stDateInput > div > div > input {
    border: 1.5px solid #C5E3D2 !important;
    border-radius: 10px !important;
    background: #FFFFFF !important;
}

.stDataFrame {
    border-radius: 12px !important;
    overflow: hidden !important;
    border: 1px solid #C5E3D2 !important;
}
.stDownloadButton > button {
    font-family: 'Inter', sans-serif !important;
    border-radius: 10px !important;
    background: #F0FDF4 !important;
    color: #2D6A4F !important;
    border: 1.5px solid #B7DFC9 !important;
    font-weight: 500 !important;
}
.stDownloadButton > button:hover {
    background: #D1FAE5 !important;
    border-color: #40916C !important;
}
.stAlert { border-radius: 10px !important; font-family: 'Inter', sans-serif !important; }
[data-testid="stExpander"] {
    border: 1.5px solid #C5E3D2 !important;
    border-radius: 12px !important;
    background: #FFFFFF !important;
}
[data-testid="stForm"] {
    border: none !important;
    padding: 0 !important;
    background: transparent !important;
}
hr { border-color: #DAF0E5 !important; margin: 18px 0 !important; }

.elib-title {
    font-family: 'Sora', sans-serif;
    font-size: 27px;
    color: #1A3D2E;
    font-weight: 700;
    letter-spacing: -0.6px;
    position: relative;
    display: flex;
    align-items: center;
    padding-left: 30px;
    margin-bottom: 6px;
}
.elib-title::before,
.elib-title::after {
    position: absolute;
    content: "";
    height: 16px;
    width: 16px;
    border-radius: 50%;
    left: 0;
    background: #2D6A4F;
}
.elib-title::before {
    width: 18px;
    height: 18px;
}
.elib-title::after {
    width: 18px;
    height: 18px;
    animation: pulseDot 1.2s linear infinite;
}
.elib-message {
    color: #6B9080;
    font-size: 13px;
    margin-bottom: 14px;
    font-family: 'Inter', sans-serif;
}
@keyframes pulseDot {
    from { transform: scale(0.9); opacity: 1; }
    to   { transform: scale(1.8); opacity: 0; }
}

/* Animated Button - from Uiverse.io */
.animated-button {
  position: relative;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 16px 36px;
  border: 4px solid transparent;
  font-size: 16px;
  background-color: #2D6A4F;
  border-radius: 100px;
  font-weight: 600;
  color: #F0FDF4;
  box-shadow: 0 0 0 2px #2D6A4F;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.6s cubic-bezier(0.23, 1, 0.32, 1);
}

.animated-button svg {
  position: absolute;
  width: 24px;
  fill: #F0FDF4;
  z-index: 9;
  transition: all 0.8s cubic-bezier(0.23, 1, 0.32, 1);
}

.animated-button .arr-1 {
  right: 16px;
}

.animated-button .arr-2 {
  left: -25%;
}

.animated-button .circle {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 20px;
  height: 20px;
  background-color: #40916C;
  border-radius: 50%;
  opacity: 0;
  transition: all 0.8s cubic-bezier(0.23, 1, 0.32, 1);
}

.animated-button .text {
  position: relative;
  z-index: 1;
  transform: translateX(-12px);
  transition: all 0.8s cubic-bezier(0.23, 1, 0.32, 1);
}

.animated-button:hover {
  box-shadow: 0 0 0 12px transparent;
  color: #FFFFFF;
  border-radius: 12px;
}

.animated-button:hover .arr-1 {
  right: -25%;
}

.animated-button:hover .arr-2 {
  left: 16px;
}

.animated-button:hover .text {
  transform: translateX(12px);
}

.animated-button:hover svg {
  fill: #F0FDF4;
}

.animated-button:active {
  scale: 0.95;
  box-shadow: 0 0 0 4px #40916C;
}

.animated-button:hover .circle {
  width: 220px;
  height: 220px;
  opacity: 1;
}

/* ══════════════════════════════════════════
   UIVERSE STAT CARDS — adapted to green theme
   card1 = main stats (expanding circle hover)
   card2 = secondary stats (lift hover)
   ══════════════════════════════════════════ */

/* Shared base */
.sc {
  display: block;
  position: relative;
  width: 100%;
  border-radius: 10px;
  padding: 26px 22px 20px;
  text-decoration: none;
  z-index: 0;
  overflow: hidden;
  cursor: default;
  box-sizing: border-box;
}

/* ── card1: expanding circle ── */
.sc-c1 {
  background-color: #EEF7F2;
}
.sc-c1:before {
  content: "";
  position: absolute;
  z-index: -1;
  top: -16px;
  right: -16px;
  height: 32px;
  width: 32px;
  border-radius: 32px;
  transform: scale(1);
  transform-origin: 50% 50%;
  transition: transform 0.28s ease-out;
}
.sc-c1:hover:before { transform: scale(22); }
.sc-c1:hover .sc-label,
.sc-c1:hover .sc-val,
.sc-c1:hover .sc-sub  { color: rgba(255,255,255,0.9) !important; }
.sc-c1:hover .sc-corner { opacity: 0.85; }

/* colour variants for card1 */
.sc-green:before,  .sc-green  .sc-corner { background: #2D6A4F; }
.sc-emerald:before,.sc-emerald .sc-corner { background: #10B981; }
.sc-amber:before,  .sc-amber  .sc-corner { background: #D97706; }
.sc-red:before,    .sc-red    .sc-corner { background: #DC2626; }

/* corner badge */
.sc-corner {
  display: flex;
  align-items: center;
  justify-content: center;
  position: absolute;
  width: 34px;
  height: 34px;
  top: 0;
  right: 0;
  border-radius: 0 10px 0 34px;
  overflow: hidden;
}
.sc-arrow {
  margin-top: -4px;
  margin-right: -4px;
  color: white;
  font-family: courier, sans;
  font-size: 13px;
}

/* card text elements */
.sc-label {
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 1px;
  text-transform: uppercase;
  margin-bottom: 10px;
  font-family: 'Inter', sans-serif;
  transition: color 0.28s ease-out;
}
.sc-val {
  font-family: 'Sora', sans-serif;
  font-size: 30px;
  line-height: 1;
  margin-bottom: 6px;
  color: #1A3D2E;
  transition: color 0.28s ease-out;
}
.sc-sub {
  font-size: 12px;
  font-family: 'Inter', sans-serif;
  transition: color 0.28s ease-out;
}

/* ── card2: lift hover for secondary row ── */
.sc-c2 {
  background-color: #EEF7F2;
  border: 1px solid #EEF7F2;
  top: 0;
  transition: all 0.2s ease-out;
  padding: 18px 18px 14px;
}
.sc-c2:before {
  content: "";
  position: absolute;
  z-index: -1;
  top: -16px;
  right: -16px;
  height: 32px;
  width: 32px;
  border-radius: 32px;
  transform: scale(2);
  transform-origin: 50% 50%;
  transition: transform 0.18s ease-out;
}
.sc-c2:hover {
  box-shadow: 0px 6px 16px rgba(38,38,38,0.15);
  top: -4px;
  border: 1px solid #B7DFC9;
  background-color: #FFFFFF;
}
.sc-c2:hover:before { transform: scale(2.2); }

/* colour variants for card2 */
.sc-c2.sc-green:before  { background: #2D6A4F; }
.sc-c2.sc-red:before    { background: #DC2626; }
.sc-c2.sc-amber:before  { background: #D97706; }
.sc-c2.sc-darkred:before{ background: #B42318; }

/* ── Add Books: nicer submit button ── */
div[data-testid="stForm"] button[kind="primaryFormSubmit"],
div[data-testid="stForm"] button[type="submit"] {
    background: linear-gradient(135deg, #2D6A4F 0%, #1A4535 100%) !important;
    color: #F0FDF4 !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px 0 !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    letter-spacing: 0.4px !important;
    box-shadow: 0 4px 14px rgba(29,67,46,0.30) !important;
    transition: all 0.18s ease !important;
    margin-top: 6px !important;
}
div[data-testid="stForm"] button[kind="primaryFormSubmit"]:hover,
div[data-testid="stForm"] button[type="submit"]:hover {
    background: linear-gradient(135deg, #357A5C 0%, #1A4535 100%) !important;
    box-shadow: 0 6px 20px rgba(29,67,46,0.38) !important;
    transform: translateY(-1px) !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# UI HELPERS - These are helper functions to make building the UI easier
# ─────────────────────────────────────────────────────────────────────────────
# Instead of writing HTML for every card/element, we call these functions

def stat_row(items):
    """
    Display a row of stat cards (like "45 Books", "38 Available", etc.)
    Makes the dashboard look beautiful with animated cards.
    """
    # Map color hex → CSS class name for card1 variants
    color_class = {
        "#2D6A4F": "sc-green",
        "#10B981": "sc-emerald",
        "#D97706": "sc-amber",
        "#DC2626": "sc-red",
    }
    # Map color → label text color (visible before hover)
    label_color = {
        "#2D6A4F": "#2D6A4F",
        "#10B981": "#0B8A5E",
        "#D97706": "#92400E",
        "#DC2626": "#991B1B",
    }
    # Map color → icon shown in corner
    icons = {
        "#2D6A4F": "📚",
        "#10B981": "📗",
        "#D97706": "📋",
        "#DC2626": "💰",
    }
    cols = st.columns(len(items))
    for col, (lbl, val, sub, color) in zip(cols, items):
        cls   = color_class.get(color, "sc-green")
        lcol  = label_color.get(color, "#52997A")
        icon  = icons.get(color, "·")
        with col:
            st.markdown(f"""
            <div class="sc sc-c1 {cls}">
              <div class="sc-corner">
                <span class="sc-arrow">{icon}</span>
              </div>
              <div class="sc-label" style="color:{lcol};">{lbl}</div>
              <div class="sc-val">{val}</div>
              <div class="sc-sub" style="color:#8BB09C;">{sub}</div>
            </div>
            """, unsafe_allow_html=True)


def card_open(padding="26px 28px"):
    st.markdown(
        f'<div style="background:#FFFFFF;border-radius:14px;padding:{padding};'
        'border:1px solid #D6EDE3;margin-bottom:18px;">',
        unsafe_allow_html=True
    )


def raised_rect_open(padding="22px 24px", max_width="760px"):
    st.markdown(
        f'<div style="max-width:{max_width};margin:0 auto 18px;background:#FFFFFF;'
        f'border:1px solid #D6EDE3;border-radius:10px;padding:{padding};'
        'box-shadow:0 14px 38px rgba(26,61,46,0.12);">',
        unsafe_allow_html=True,
    )

def card_close():
    st.markdown('</div>', unsafe_allow_html=True)


def page_heading(title, subtitle="", req=None):
    req_tag = ""
    if req:
        req_tag = (
            f' <span style="font-size:10px;font-weight:600;background:#ECFDF5;'
            f'color:#065F46;padding:3px 9px;border-radius:5px;letter-spacing:0.5px;'
            f'vertical-align:middle;margin-left:10px;font-family:\'Inter\',sans-serif;">'
            f'{req}</span>'
        )
    st.markdown(f"""
    <div style="margin-bottom:28px;padding-bottom:18px;border-bottom:1px solid #DAF0E5;">
      <div style="font-family:'Sora',sans-serif;font-size:26px;
          color:#1A3D2E;line-height:1.15;">{title}{req_tag}</div>
      {"" if not subtitle else
       f'<div style="font-size:13px;color:#7BA892;margin-top:6px;'
       f'font-family:\'Inter\',sans-serif;">{subtitle}</div>'}
    </div>
    """, unsafe_allow_html=True)


def info_bar(text):
    st.markdown(f"""
    <div style="background:#F0FDF4;border-left:3px solid #40916C;border-radius:0 8px 8px 0;
        padding:10px 16px;margin-bottom:22px;font-size:13.5px;color:#1A4535;
        font-family:'Inter',sans-serif;">{text}</div>
    """, unsafe_allow_html=True)


def section_title(text):
    st.markdown(f"""
    <div style="font-size:10.5px;font-weight:600;color:#52997A;letter-spacing:1.2px;
        text-transform:uppercase;margin:20px 0 12px;font-family:'Inter',sans-serif;">{text}</div>
    """, unsafe_allow_html=True)


def success_box(title, body):
    st.markdown(f"""
    <div style="background:#F0FDF4;border:1.5px solid #86EFAC;border-radius:14px;
        padding:30px;text-align:center;margin-bottom:18px;">
      <div style="font-size:38px;margin-bottom:12px;">✓</div>
      <div style="font-family:'Sora',sans-serif;font-size:20px;
          color:#14532D;margin-bottom:8px;">{title}</div>
      <div style="font-size:13.5px;color:#166534;line-height:1.65;
          font-family:'Inter',sans-serif;">{body}</div>
    </div>
    """, unsafe_allow_html=True)


def confirm_box(title, body, details=None, border="#2D6A4F"):
    rows_html = ""
    if details:
        rows = ""
        for k, v in details.items():
            rows += (
                f'<div style="display:flex;justify-content:space-between;'
                f'padding:7px 0;border-bottom:1px solid #F0FDF4;">'
                f'<span style="font-size:13px;color:#7BA892;font-family:\'Inter\',sans-serif;">{k}</span>'
                f'<span style="font-size:13px;font-weight:600;color:#1A3D2E;'
                f'font-family:\'Inter\',sans-serif;">{v}</span>'
                f'</div>'
            )
        rows_html = (
            f'<div style="background:#F6FBF8;border-radius:8px;'
            f'padding:12px 16px;text-align:left;margin:14px 0 16px;">{rows}</div>'
        )
    st.markdown(f"""
    <div style="background:#FFFFFF;border-radius:14px;padding:28px;
        border:2px solid {border};max-width:440px;margin:0 auto 22px;text-align:center;">
      <div style="font-family:'Sora',sans-serif;font-size:20px;
          color:#1A3D2E;margin-bottom:8px;">{title}</div>
      <div style="font-size:13px;color:#7BA892;line-height:1.6;
          font-family:'Inter',sans-serif;">{body}</div>
      {rows_html}
    </div>
    """, unsafe_allow_html=True)


def avail_badge(qty):
    if qty == 0:
        return ('<span style="background:#FEF2F2;color:#991B1B;padding:3px 10px;'
                'border-radius:5px;font-size:11.5px;font-weight:600;">Out of Stock</span>')
    elif qty <= 2:
        return (f'<span style="background:#FFFBEB;color:#92400E;padding:3px 10px;'
                f'border-radius:5px;font-size:11.5px;font-weight:600;">Low — {qty} left</span>')
    return (f'<span style="background:#ECFDF5;color:#065F46;padding:3px 10px;'
            f'border-radius:5px;font-size:11.5px;font-weight:600;">Available — {qty}</span>')


def step_bar(active):
    steps = ["Enter Details", "Review Fee", "Confirm Return"]
    cols  = st.columns(3)
    for i, (col, lbl) in enumerate(zip(cols, steps), 1):
        with col:
            if i < active:
                bg, fg, num_bg = "#2D6A4F", "#F0FDF4", "rgba(255,255,255,0.25)"
            elif i == active:
                bg, fg, num_bg = "#1A3D2E", "#D8F3DC", "rgba(255,255,255,0.2)"
            else:
                bg, fg, num_bg = "#EDF5F0", "#8BB09C", "rgba(0,0,0,0.06)"
            st.markdown(f"""
            <div style="background:{bg};border-radius:10px;padding:11px;
                text-align:center;font-size:12.5px;font-weight:500;color:{fg};
                font-family:'Inter',sans-serif;">
              <span style="display:inline-flex;width:20px;height:20px;border-radius:50%;
                  background:{num_bg};font-size:10px;align-items:center;justify-content:center;
                  margin-right:6px;">{i}</span>{lbl}
            </div>
            """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR NAVIGATION
# ─────────────────────────────────────────────────────────────────────────────
# This is the left sidebar with the menu buttons to navigate between pages

def sidebar_nav():
    """
    Display the left navigation sidebar.
    Allows user to switch between different pages:
    - Home (Dashboard)
    - Inventory
    - Add Books
    - Search & Borrow
    - Returns & Fees
    """
    with st.sidebar:
        st.markdown(
            '<div style="display:flex;align-items:center;gap:10px;padding:4px 4px 10px;">'
            '<span style="font-size:22px;line-height:1;">📚</span>'
            '<div>'
            '<p style="font-size:13px;font-weight:700;color:#D8F3DC;margin:0;'
            'letter-spacing:0.2px;">Kothalawala</p>'
            '<small style="font-size:8.5px;color:rgba(116,198,157,0.45);'
            'letter-spacing:1.2px;text-transform:uppercase;">E-Library</small>'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<hr style="border:none;border-top:1px solid rgba(116,198,157,0.15);margin:0 0 10px;">',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div style="font-size:8.5px;font-weight:700;color:rgba(116,198,157,0.4);'
            'letter-spacing:1.3px;text-transform:uppercase;padding:0 4px 6px;">Navigation</div>',
            unsafe_allow_html=True
        )

        # Define the navigation menu items
        pages = [
            ("Home",      "🏠", "Dashboard"),             # Label, Icon, Page key
            ("Inventory",      "📦", "Inventory"),
            ("Add Books",      "➕", "Add Books"),
            ("Search & Borrow","🔍", "Search & Borrow"),
            ("Returns & Fees", "↩️",  "Returns & Fees"),
        ]

        # Create buttons for each page
        for label, icon, key in pages:
            active = st.session_state.page == key  # Is this the current page?
            if st.button(
                f"{icon}  {label}",
                key="nav_" + key,
                help=key,
                type="primary" if active else "secondary",  # Highlight current page
                use_container_width=True,
            ):
                # Switch to this page when button is clicked
                st.session_state.page           = key
                st.session_state.confirm_add    = False
                st.session_state.confirm_borrow = False
                st.session_state.confirm_return = False
                st.rerun()  # Refresh the page

        st.markdown(
            f'<div style="position:fixed;bottom:16px;left:0;width:200px;text-align:center;'
            f'font-size:9px;color:rgba(116,198,157,0.25);font-family:Inter,sans-serif;">'
            f'{datetime.now().year}</div>',
            unsafe_allow_html=True
        )

# ─────────────────────────────────────────────────────────────────────────────
# MAIN FUNCTION - Routing and page selection
# ─────────────────────────────────────────────────────────────────────────────
# This is the main control center that shows the right page based on selection

def main():
    """
    Main function that controls which page to show.
    First checks if database is connected, then displays the selected page.
    """
    # Check if database connection is working
    if not st.session_state.get("db_ok", False):
        st.error("Database connection failed: " + st.session_state.get("db_error", "Unknown"))
        st.info("Ensure serviceAccountKey.json is present and Firestore is enabled.")
        return

    # Show the sidebar navigation menu
    sidebar_nav()
    lib  = st.session_state.lib    # Get the database connection
    page = st.session_state.page   # Get the current page user is on

    # Display the appropriate page based on selection
    # Each page is defined below with clear section headers showing which sidebar page it is
    if   page == "Dashboard":       page_dashboard(lib)      # 🏠 HOME PAGE (see line ~890)
    elif page == "Inventory":       page_inventory(lib)      # 📦 INVENTORY PAGE (see line ~1120)
    elif page == "Add Books":       page_add_books(lib)      # ➕ ADD BOOKS PAGE (see line ~1208)
    elif page == "Search & Borrow": page_search(lib)        # 🔍 SEARCH & BORROW PAGE (see line ~1328)
    elif page == "Returns & Fees":  page_returns(lib)       # ↩️ RETURNS & FEES PAGE (see line ~1459)


# ═════════════════════════════════════════════════════════════════════════════════════
# 🏠 HOME PAGE / DASHBOARD
# ═════════════════════════════════════════════════════════════════════════════════════════
# SIDEBAR: Home (🏠) — This is the first page users see
# Shows library statistics, alerts, and recent activity
# Location: Sidebar → "Home" (🏠)

def page_dashboard(lib):
    """
    Display the main dashboard with:
    - Key statistics (total books, available copies, active loans, fees)
    - Alerts (books due soon, overdue, low stock)
    - Recent borrowing activity
    - Top authors and today's summary
    """
    st.markdown(f"""
    <div style="position:relative;margin-bottom:28px;padding-bottom:18px;border-bottom:1px solid #DAF0E5;">
      <div style="position:absolute;top:0;right:0;font-size:12px;color:#000000;font-family:'Inter',sans-serif;">
        {datetime.now().strftime("%A, %d %B %Y")}  <!-- Show current date -->
      </div>
      <div>
        <div style="font-family:'Sora',sans-serif;font-size:26px;color:#1A3D2E;">
                    Library Home
        </div>
        <div style="font-size:13px;color:#7BA892;margin-top:5px;">
                    Good {"morning" if datetime.now().hour < 12 else "afternoon"} — monitor circulation, stock, and returns in one place.
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    try:
        # Get data from database
        inv = lib.get_inventory()            # All books in catalog
        trans = lib.get_transaction_history() # All borrow/return records
        now = datetime.now()
        today = now.date()

        tt = len(inv)
        total_copies = sum(b.get("available_quantity", 0) for b in inv)
        active_loans = [t for t in trans if not t.get("return_date")]
        on_loan = len(active_loans)

        fee_total = sum(t.get("late_fee", 0) for t in trans if t.get("late_fee", 0) > 0)
        out_of_stock = len([b for b in inv if b.get("available_quantity", 0) == 0])
        low_stock = len([b for b in inv if 0 < b.get("available_quantity", 0) <= 2])

        due_soon = 0
        overdue = 0
        returned_today = 0

        for t in trans:
            due_date = t.get("due_date")
            return_date = t.get("return_date")

            if return_date and hasattr(return_date, "date") and return_date.date() == today:
                returned_today += 1

            if due_date and hasattr(due_date, "date") and not return_date:
                days_to_due = (due_date.date() - today).days
                if days_to_due < 0:
                    overdue += 1
                elif days_to_due <= 3:
                    due_soon += 1

    except Exception:
        inv = []
        trans = []
        tt = total_copies = on_loan = 0
        fee_total = 0.0
        out_of_stock = low_stock = due_soon = overdue = returned_today = 0

    stat_row([
        ("Book Titles", tt, "In catalogue", "#2D6A4F"),
        ("Copies On Shelf", total_copies, "Ready to borrow", "#10B981"),
        ("Active Loans", on_loan, "Not yet returned", "#D97706"),
        ("Fees Collected", f"Rs. {int(fee_total)}", "Late return fees", "#DC2626"),
    ])

    st.markdown("<div style='height:22px;'></div>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="sc sc-c2 sc-green">
          <div class="sc-label" style="color:#2D6A4F;">Due Soon</div>
          <div class="sc-val" style="font-size:24px;">{due_soon}</div>
          <div class="sc-sub" style="color:#8BB09C;">Within 3 days</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="sc sc-c2 sc-red">
          <div class="sc-label" style="color:#991B1B;">Overdue</div>
          <div class="sc-val" style="font-size:24px;color:#991B1B;">{overdue}</div>
          <div class="sc-sub" style="color:#C97E7E;">Past due date</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="sc sc-c2 sc-amber">
          <div class="sc-label" style="color:#92400E;">Low Stock</div>
          <div class="sc-val" style="font-size:24px;color:#92400E;">{low_stock}</div>
          <div class="sc-sub" style="color:#C7923E;">Only 1–2 copies left</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="sc sc-c2 sc-darkred">
          <div class="sc-label" style="color:#AF5A5A;">Out Of Stock</div>
          <div class="sc-val" style="font-size:24px;color:#B42318;">{out_of_stock}</div>
          <div class="sc-sub" style="color:#C97E7E;">No copies available</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────────
    # 📊 FEATURE 1: MOST BORROWED BOOKS WIDGET
    # ─────────────────────────────────────────────────────────────────────────────
    # Shows the top 3 most borrowed books in the library
    # Purpose: Provides analytics about popular books and reading patterns
    # This helps librarians understand user preferences and manage stock accordingly
    
    try:
        # STEP 1: Count how many times each book was borrowed
        borrow_count = {}  # Dictionary: ISBN -> number of times borrowed
        
        for transaction in trans:
            isbn = transaction.get("isbn", "")
            # Count only completed borrowing transactions
            if isbn and transaction.get("borrow_date"):
                borrow_count[isbn] = borrow_count.get(isbn, 0) + 1
        
        # STEP 2: Get the top 3 most borrowed books
        if borrow_count:
            # Sort by count (highest first) and take the top 3
            top_borrowed_isbns = sorted(borrow_count.items(), key=lambda x: x[1], reverse=True)[:3]
            
            # STEP 3: Build the book details for display
            top_borrowed_books = []
            for isbn, count in top_borrowed_isbns:
                # Find the book details from inventory
                for book in inv:
                    if book.get("isbn") == isbn:
                        top_borrowed_books.append({
                            "title": book.get("title", "Unknown"),
                            "author": book.get("author", "Unknown Author"),
                            "count": count
                        })
                        break
            
            # STEP 4: Display the "Most Borrowed Books" widget
            if top_borrowed_books:
                st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
                section_title("📈 Most Borrowed Books")
                
                # Create 3 columns for the top 3 books
                col1, col2, col3 = st.columns(3)
                
                for idx, (col, book) in enumerate(zip([col1, col2, col3], top_borrowed_books)):
                    with col:
                        # Display each book in a styled card
                        st.markdown(f"""
                        <div style="background:#F0FDF4;border:2px solid #22C55E;border-radius:12px;padding:18px;text-align:center;height:160px;display:flex;flex-direction:column;justify-content:center;">
                          <div style="font-size:32px;color:#16A34A;margin-bottom:8px;">{'🏆' if idx == 0 else '🥈' if idx == 1 else '🥉'}</div>
                          <div style="font-size:13px;font-weight:600;color:#1A3D2E;margin-bottom:4px;white-space:normal;line-height:1.3;">{book['title']}</div>
                          <div style="font-size:11px;color:#6B9080;margin-bottom:10px;">{book['author']}</div>
                          <div style="font-size:14px;font-weight:700;color:#22C55E;">{book['count']} borrowed</div>
                        </div>
                        """, unsafe_allow_html=True)
    
    except Exception as e:
        # Handle any errors gracefully
        st.warning(f"Could not load most borrowed books: {str(e)}")

    # ─────────────────────────────────────────────────────────────────────────────
    # 🚨 FEATURE 2: BOOKS DUE SOON ALERT
    # ─────────────────────────────────────────────────────────────────────────────
    # Shows books that are approaching their 14-day borrowing limit
    # Purpose: Proactive notification to help borrowers remember to return books on time
    # This reduces overdue books and improves library operations
    
    try:
        # STEP 1: Find all books that are due within the next 5 days
        books_due_soon = []  # List to store books nearing their due date
        today = datetime.now().date()
        
        for transaction in trans:
            # Check only active loans (not yet returned)
            if not transaction.get("return_date"):
                due_date = transaction.get("due_date")
                
                if due_date and hasattr(due_date, "date"):
                    due_date_only = due_date.date()
                    days_until_due = (due_date_only - today).days
                    
                    # Add to alert list if due within 5 days (but not overdue)
                    if 0 <= days_until_due <= 5:
                        books_due_soon.append({
                            "title": transaction.get("title", "Unknown"),
                            "borrower": transaction.get("borrower_name", "Unknown"),
                            "due_date": due_date_only,
                            "days_left": days_until_due
                        })
        
        # STEP 2: Display alert if there are books due soon
        if books_due_soon:
            st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
            
            # Sort by days left (soonest first)
            books_due_soon.sort(key=lambda x: x["days_left"])
            
            # Display alert header
            st.markdown(f"""
            <div style="background:#FEF3C7;border-left:5px solid #F59E0B;padding:14px;border-radius:8px;margin-bottom:12px;">
              <div style="display:flex;align-items:center;gap:10px;">
                <span style="font-size:20px;">⏰</span>
                <div>
                  <div style="font-size:14px;font-weight:600;color:#92400E;">Books Due Soon</div>
                  <div style="font-size:12px;color:#B45309;">{len(books_due_soon)} book(s) approaching their due date</div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)
            
            # STEP 3: Display each book due soon in a table format
            card_open("0")
            st.markdown("""
            <div style="background:#1A3D2E;padding:12px 18px;border-radius:8px 8px 0 0;display:flex;">
              <span style="flex:2;font-size:11px;font-weight:600;color:#74C69D;letter-spacing:0.8px;text-transform:uppercase;">Book Title</span>
              <span style="flex:1.5;font-size:11px;font-weight:600;color:#74C69D;letter-spacing:0.8px;text-transform:uppercase;">Borrower</span>
              <span style="flex:1;font-size:11px;font-weight:600;color:#74C69D;letter-spacing:0.8px;text-transform:uppercase;">Due Date</span>
              <span style="flex:0.8;text-align:center;font-size:11px;font-weight:600;color:#74C69D;letter-spacing:0.8px;text-transform:uppercase;">Days Left</span>
            </div>
            """, unsafe_allow_html=True)
            
            # Display each book in the table
            for i, book in enumerate(books_due_soon):
                bg_color = "#FFFFFF" if i % 2 == 0 else "#F9FCF9"
                
                # Color code the days left: red if 0-1 days, orange if 2-3 days, yellow if 4-5 days
                if book["days_left"] <= 1:
                    days_color = "#DC2626"
                    days_bg = "#FEE2E2"
                elif book["days_left"] <= 3:
                    days_color = "#D97706"
                    days_bg = "#FEF3C7"
                else:
                    days_color = "#F59E0B"
                    days_bg = "#FFFBEB"
                
                st.markdown(f"""
                <div style="background:{bg_color};padding:12px 18px;display:flex;align-items:center;border-bottom:1px solid #EBF5EF;">
                  <span style="flex:2;font-size:13px;color:#1A3D2E;font-weight:500;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{book['title']}</span>
                  <span style="flex:1.5;font-size:12.5px;color:#6B9080;">{book['borrower']}</span>
                  <span style="flex:1;font-size:12px;color:#8BB09C;">{book['due_date'].strftime('%d %b %Y')}</span>
                  <span style="flex:0.8;text-align:center;font-size:12px;font-weight:600;color:{days_color};background:{days_bg};padding:4px 8px;border-radius:5px;">{book['days_left']} day{'s' if book['days_left'] != 1 else ''}</span>
                </div>
                """, unsafe_allow_html=True)
            
            card_close()
    
    except Exception as e:
        # Handle any errors gracefully
        st.warning(f"Could not load books due soon: {str(e)}")

    left, right = st.columns([1.45, 1])

    with left:
        section_title("Recent Borrowing Activity")
        if trans:
            recent = sorted(
                trans,
                key=lambda x: x.get("borrow_date") or datetime.min,
                reverse=True,
            )[:8]
            card_open("0")
            st.markdown("""
            <div style="background:#1A3D2E;padding:12px 18px;border-radius:14px 14px 0 0;display:flex;">
              <span style="flex:2.6;font-size:11px;font-weight:600;color:#74C69D;letter-spacing:0.8px;text-transform:uppercase;">Title</span>
              <span style="flex:1.5;font-size:11px;font-weight:600;color:#74C69D;letter-spacing:0.8px;text-transform:uppercase;">Borrower</span>
              <span style="flex:1.2;font-size:11px;font-weight:600;color:#74C69D;letter-spacing:0.8px;text-transform:uppercase;">Due Date</span>
              <span style="flex:1;text-align:right;font-size:11px;font-weight:600;color:#74C69D;letter-spacing:0.8px;text-transform:uppercase;">Status</span>
            </div>
            """, unsafe_allow_html=True)
            for i, t in enumerate(recent):
                bg = "#FFFFFF" if i % 2 == 0 else "#F9FCF9"
                title = t.get("title", "-")
                borrower = t.get("borrower_name", "-")
                due_date = t.get("due_date")
                due_text = due_date.strftime("%d %b %Y") if hasattr(due_date, "strftime") else "-"
                returned = t.get("return_date")

                if returned:
                    status_badge = '<span style="background:#ECFDF5;color:#065F46;padding:2px 8px;border-radius:5px;font-size:11px;font-weight:600;">Returned</span>'
                elif due_date and hasattr(due_date, "date") and due_date.date() < datetime.now().date():
                    status_badge = '<span style="background:#FEF2F2;color:#991B1B;padding:2px 8px;border-radius:5px;font-size:11px;font-weight:600;">Overdue</span>'
                else:
                    status_badge = '<span style="background:#FFFBEB;color:#92400E;padding:2px 8px;border-radius:5px;font-size:11px;font-weight:600;">Borrowed</span>'

                st.markdown(f"""
                <div style="background:{bg};padding:12px 18px;display:flex;border-bottom:1px solid #EBF5EF;align-items:center;">
                  <span style="flex:2.6;font-size:13px;color:#1A3D2E;font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;padding-right:10px;">{title}</span>
                  <span style="flex:1.5;font-size:12.5px;color:#6B9080;">{borrower}</span>
                  <span style="flex:1.2;font-size:12px;color:#8BB09C;">{due_text}</span>
                  <span style="flex:1;text-align:right;">{status_badge}</span>
                </div>
                """, unsafe_allow_html=True)
            card_close()
        else:
            st.info("No borrowing activity recorded yet.")

    with right:
        section_title("Collection Snapshot")
        if inv:
            by_author = {}
            for b in inv:
                author = b.get("author", "Unknown")
                by_author[author] = by_author.get(author, 0) + 1
            top_authors = sorted(by_author.items(), key=lambda x: x[1], reverse=True)[:5]

            card_open("18px 20px")
            st.markdown(
                f"<div style='font-size:13px;color:#6B9080;margin-bottom:10px;'>"
                f"<strong style='color:#1A3D2E;'>{len(by_author)}</strong> authors in catalogue</div>",
                unsafe_allow_html=True,
            )
            for author, count in top_authors:
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;align-items:center;padding:9px 0;border-bottom:1px solid #EEF7F1;">
                  <span style="font-size:13px;color:#1A3D2E;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;padding-right:8px;">{author}</span>
                  <span style="font-size:12px;color:#52997A;background:#F0FDF4;padding:3px 8px;border-radius:6px;">{count} title(s)</span>
                </div>
                """, unsafe_allow_html=True)
            card_close()
        else:
            st.info("No books in the catalogue yet.")

        section_title("Today")
        card_open("18px 20px")
        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #EEF7F1;">
          <span style="font-size:13px;color:#6B9080;">Returns Completed</span>
          <span style="font-size:13px;color:#1A3D2E;font-weight:600;">{returned_today}</span>
        </div>
        <div style="display:flex;justify-content:space-between;padding:10px 0 6px;">
          <span style="font-size:13px;color:#6B9080;">Active Loans</span>
          <span style="font-size:13px;color:#1A3D2E;font-weight:600;">{on_loan}</span>
        </div>
        """, unsafe_allow_html=True)
        if overdue > 0:
            st.markdown(
                f"<div style='margin-top:8px;font-size:12px;color:#991B1B;'>"
                f"{overdue} overdue book(s) require follow-up.</div>",
                unsafe_allow_html=True,
            )
        card_close()

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([3, 1, 3])
    with c2:
        st.markdown("""
        <button class="animated-button" onclick="window.location.href='?page=Inventory'">
          <svg class="arr-1" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg>
          <span class="text">Open Full Inventory</span>
          <svg class="arr-2" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg>
          <div class="circle"></div>
        </button>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="text-align:center;color:#C4D9CC;font-size:11px;
        padding:32px 0 4px;font-family:'Inter',sans-serif;">
      Kothalawala E-Library · Powered by Firebase & Streamlit · {datetime.now().year}
    </div>
    """, unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════════════
# 📦 INVENTORY PAGE
# ═════════════════════════════════════════════════════════════════════════════════════════
# SIDEBAR: Inventory (📦) — View all books with search, filter, and CSV export
# Shows complete catalog with statistics and download capability
# Location: Sidebar → "Inventory" (📦)

def page_inventory(lib):
    """
    Display complete inventory of all books with:
    - Search by title/author
    - Filter by availability status
    - Export to CSV
    - Beautiful table showing all book details
    """
    page_heading("Inventory Dashboard",
        "Title · Author · Available Quantity · Daily Late Return Fee")
    try:
        inv   = lib.get_inventory()
        trans = lib.get_transaction_history()
        tt    = len(inv)
        tc    = sum(b["available_quantity"] for b in inv)
        bw    = len([t for t in trans if not t.get("return_date")])
        fe    = sum(t.get("late_fee", 0) for t in trans if t.get("late_fee", 0) > 0)
        stat_row([
            ("Book Titles",    tt,              "In catalogue",       "#2D6A4F"),
            ("Available",      tc,              "Copies on shelf",    "#10B981"),
            ("On Loan",        bw,              "Currently borrowed", "#D97706"),
            ("Fees Collected", f"Rs. {int(fe)}", "Late return fees",   "#DC2626"),
        ])
        st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)
        if not inv:
            st.info("No books yet."); return

        card_open("16px 20px")
        
        # ─────────────────────────────────────────────────────────────────────────────
        # 🔍 FEATURE 1: AUTHOR FILTER DROPDOWN
        # ─────────────────────────────────────────────────────────────────────────────
        # Allows users to filter inventory by specific authors
        # Purpose: Help users quickly find all books by a particular author
        # Useful for librarians managing books by genre/author or patrons browsing specific authors
        
        # STEP 1: Extract all unique authors from the inventory
        unique_authors = sorted(list(set([b.get("author", "Unknown") for b in inv if b.get("author")])))
        authors_list = ["📚 All Authors"] + unique_authors  # Add "All Authors" as first option
        
        f1, f2, f3, f4 = st.columns([2.5, 1.8, 1.8, 1])
        
        with f1:
            search = st.text_input("s", placeholder="Filter by title or author…", label_visibility="collapsed")
        
        with f2:
            # STEP 2: Display author filter dropdown
            # Users can select a specific author to see only their books
            selected_author = st.selectbox(
                "f", 
                authors_list,
                label_visibility="collapsed",
                help="Filter books by specific author"
            )
        
        with f3:
            status_f = st.selectbox("f2", ["All Books", "Available", "Out of Stock"], label_visibility="collapsed")
        
        with f4:
            df_export = pd.DataFrame([{"Title": b["title"], "Author": b["author"], "ISBN": b["isbn"],
                "Available Quantity": b["available_quantity"], "Daily Late Fee (Rs)": b["late_return_fee"]} for b in inv])
            st.download_button("Export CSV", data=df_export.to_csv(index=False),
                file_name=f"inventory_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv", use_container_width=True)
        card_close()

        # ─────────────────────────────────────────────────────────────────────────────
        # Apply all filters
        # ─────────────────────────────────────────────────────────────────────────────
        filtered = [b for b in inv if
            # Text search filter (title or author)
            (not search or search.lower() in b["title"].lower() or search.lower() in b["author"].lower()) and
            # Author dropdown filter
            (selected_author == "📚 All Authors" or b.get("author") == selected_author) and
            # Availability status filter
            not (status_f == "Available" and b["available_quantity"] == 0) and
            not (status_f == "Out of Stock" and b["available_quantity"] > 0)]

        if not filtered:
            st.info("No books match the current filter."); return

        card_open("0")
        st.markdown("""
        <div style="background:#1A3D2E;padding:13px 22px;border-radius:14px 14px 0 0;display:flex;">
          <span style="flex:3;font-size:11px;font-weight:600;color:#74C69D;letter-spacing:0.8px;text-transform:uppercase;">Title</span>
          <span style="flex:2;font-size:11px;font-weight:600;color:#74C69D;letter-spacing:0.8px;text-transform:uppercase;">Author</span>
          <span style="flex:2;font-size:11px;font-weight:600;color:#74C69D;letter-spacing:0.8px;text-transform:uppercase;">ISBN</span>
          <span style="flex:1;font-size:11px;font-weight:600;color:#74C69D;letter-spacing:0.8px;text-transform:uppercase;text-align:center;">Qty</span>
          <span style="flex:1.5;font-size:11px;font-weight:600;color:#74C69D;letter-spacing:0.8px;text-transform:uppercase;text-align:center;">Fee/day</span>
          <span style="flex:1.5;font-size:11px;font-weight:600;color:#74C69D;letter-spacing:0.8px;text-transform:uppercase;text-align:right;">Status</span>
        </div>
        """, unsafe_allow_html=True)
        
        # ─────────────────────────────────────────────────────────────────────────────
        # 🎨 FEATURE 2: STOCK LEVEL COLOR INDICATORS
        # ─────────────────────────────────────────────────────────────────────────────
        # Adds visual color-coding to rows based on stock levels
        # Purpose: Helps at-a-glance inventory management by color-coding stock status
        # Visual hierarchy: Green (healthy stock) → Yellow (low stock) → Red (out of stock)
        
        for i, b in enumerate(filtered):
            qty = b["available_quantity"]
            
            # STEP 1: Determine the background color based on stock level
            # Red background: Out of stock (qty = 0)
            # Orange/Yellow background: Low stock (qty = 1-2) - needs attention
            # Green background: Healthy stock (qty > 2) - normal
            
            if qty == 0:
                # OUT OF STOCK - Critical status
                row_bg = "#FEF2F2"  # Light red background
                left_border_color = "#991B1B"  # Dark red border
                qty_color = "#991B1B"
                qty_font_size = "15px"
                qty_font_weight = "700"
            elif qty <= 2:
                # LOW STOCK - Warning status (1-2 copies)
                row_bg = "#FEF3C7"  # Light yellow background
                left_border_color = "#F59E0B"  # Orange border
                qty_color = "#92400E"
                qty_font_size = "15px"
                qty_font_weight = "700"
            else:
                # HEALTHY STOCK - Normal status (3+ copies)
                row_bg = "#F0FDF4"  # Light green background
                left_border_color = "#22C55E"  # Green border
                qty_color = "#065F46"
                qty_font_size = "14px"
                qty_font_weight = "600"
            
            # STEP 2: Create status badge with descriptive text
            if qty == 0:
                badge = '<span style="background:#FEE2E2;color:#991B1B;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600;">❌ Out of Stock</span>'
            elif qty == 1:
                badge = '<span style="background:#FEF3C7;color:#92400E;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600;">⚠️ Critical (1)</span>'
            elif qty == 2:
                badge = '<span style="background:#FEF3C7;color:#92400E;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600;">⚠️ Low (2)</span>'
            else:
                badge = f'<span style="background:#ECFDF5;color:#065F46;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600;">✅ In Stock ({qty})</span>'
            
            # STEP 3: Display the row with color-coded background and left border
            st.markdown(f"""
            <div style="background:{row_bg};padding:12px 22px;display:flex;border-bottom:1px solid #EBF5EF;align-items:center;border-left:4px solid {left_border_color};transition:all 0.2s ease;">
              <span style="flex:3;font-size:13.5px;color:#1A3D2E;font-weight:500;font-family:'Inter',sans-serif;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;padding-right:12px;">{b['title']}</span>
              <span style="flex:2;font-size:13px;color:#6B9080;font-family:'Inter',sans-serif;">{b['author']}</span>
              <span style="flex:2;font-size:12px;color:#8BB09C;font-family:'DM Mono',monospace;">{b['isbn']}</span>
              <span style="flex:1;font-size:{qty_font_size};font-weight:{qty_font_weight};color:{qty_color};text-align:center;font-family:'Sora',sans-serif;">{qty}</span>
              <span style="flex:1.5;font-size:13px;color:#6B9080;text-align:center;font-family:'Inter',sans-serif;">Rs. {b['late_return_fee']:.2f}</span>
              <span style="flex:1.5;text-align:right;">{badge}</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)
        card_close()
    except Exception:
        st.error("Error loading inventory.")
        with st.expander("Details"): st.code(traceback.format_exc())

# ═════════════════════════════════════════════════════════════════════════════════════
# ➕ ADD BOOKS PAGE
# ═════════════════════════════════════════════════════════════════════════════════════════
# SIDEBAR: Add Books (➕) — Add new books to the library catalog
# Form to input title, author, ISBN, late fee, and quantity
# Location: Sidebar → "Add Books" (➕)

def page_add_books(lib):
    """
    Display form to add a new book to the library catalog.

    Users fill in:
    - Book title
    - Author name
    - ISBN (unique identifier)
    - Number of copies
    - Late return fee (Rs/day)

    Shows success message after book is added.
    """
    page_heading(
        "Add New Books",
        "Create new catalogue records with a modern inline form",
    )

    # ── Success screen ────────────────────────────────────────────────────────
    # Show this if book was successfully added
    if st.session_state.add_ok:
        _, cc, _ = st.columns([1, 2, 1])
        with cc:
            success_box(
                "Book Added Successfully",
                f'<strong>"{st.session_state.add_ok}"</strong> has been added to the library catalogue.',
            )
            st.balloons()
            st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
            if st.button("Add Another Book", type="primary", use_container_width=True):
                st.session_state.add_ok = None
                st.rerun()
        return

    # ── Centred narrow card ───────────────────────────────────────────────────
    _, mid, _ = st.columns([1, 2.2, 1])
    with mid:

        # Header block
        st.markdown("""
        <div style="background:#FFFFFF;border-radius:16px;padding:24px 28px 18px;
            border:1px solid #D6EDE3;
            box-shadow:0 8px 32px rgba(26,61,46,0.11),0 2px 8px rgba(26,61,46,0.06);
            margin-bottom:10px;">
          <div class="elib-title" style="font-size:22px;margin-bottom:4px;">Add Book Record</div>
          <div class="elib-message" style="margin-bottom:0;">
            Enter catalogue details below to add the book to inventory.
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Form card
        st.markdown("""
        <div style="background:#FFFFFF;border-radius:16px;padding:26px 28px 22px;
            border:1px solid #D6EDE3;
            box-shadow:0 8px 32px rgba(26,61,46,0.11),0 2px 8px rgba(26,61,46,0.06);">
        """, unsafe_allow_html=True)

        with st.form("add_books_inline_form", clear_on_submit=True):
            r1c1, r1c2 = st.columns(2)
            with r1c1:
                title = st.text_input("Book Title *", placeholder="e.g. The Great Gatsby")
            with r1c2:
                author = st.text_input("Author *", placeholder="e.g. F. Scott Fitzgerald")

            st.markdown("<div style='height:2px;'></div>", unsafe_allow_html=True)
            
            # ─────────────────────────────────────────────────────────────────────────────
            # 📚 FEATURE 1: CATEGORY/GENRE FIELD
            # ─────────────────────────────────────────────────────────────────────────────
            # Allows users to categorize books by genre/category
            # Purpose: Helps organize the library and enable filtering by book type
            # Useful for readers to find books by category and for library management
            
            # STEP 1: Define available book categories
            # These are standard library classification categories
            book_categories = [
                "📖 Select Category",  # Default/placeholder option
                "📚 Fiction - General",
                "📖 Fiction - Romance",
                "🔍 Fiction - Mystery/Thriller",
                "🚀 Fiction - Science Fiction",
                "🎭 Fiction - Fantasy",
                "📕 Non-Fiction - History",
                "🧪 Non-Fiction - Science",
                "📊 Non-Fiction - Business",
                "🧠 Non-Fiction - Psychology",
                "✍️ Non-Fiction - Biography",
                "🎓 Reference",
                "👧 Children's Books",
                "🎯 Young Adult",
                "📰 Journals/Periodicals",
            ]
            
            # STEP 2: Display category dropdown
            # User selects one category for the book being added
            category = st.selectbox(
                "Category/Genre *",
                book_categories,
                help="Select the book's primary category"
            )
            
            st.markdown("<div style='height:2px;'></div>", unsafe_allow_html=True)
            
            # ─────────────────────────────────────────────────────────────────────────────
            # 🔎 FEATURE 2: ISBN LOOKUP PREVIEW
            # ─────────────────────────────────────────────────────────────────────────────
            # Shows book details if the ISBN already exists in the database
            # Purpose: Prevents duplicate entries and helps verify correct ISBN
            # This improves data accuracy and prevents adding the same book twice
            
            isbn = st.text_input(
                "ISBN *", 
                placeholder="e.g. 978-0-7432-7356-5",
                help="10 or 13 digit ISBN"
            )
            
            # STEP 1: Check if ISBN lookup is triggered (user entered an ISBN)
            # Only show preview if ISBN has at least the minimum length (10 digits)
            if isbn and len(isbn.replace("-", "").replace(" ", "")) >= 10:
                # STEP 2: Search for existing book with this ISBN
                try:
                    existing_books = lib.search_books_by_isbn(isbn.strip())
                    
                    if existing_books:
                        # ISBN already exists - show warning
                        st.warning("⚠️ ISBN Already Exists", icon="⚠️")
                        
                        for book in existing_books:
                            # Display preview card with existing book details
                            st.markdown(f"""
                            <div style="background:#FEF3C7;border-left:4px solid #F59E0B;border-radius:8px;padding:12px;margin-bottom:10px;">
                              <div style="font-size:12px;font-weight:600;color:#92400E;margin-bottom:6px;">📘 Book Already in Database</div>
                              <div style="font-size:13px;color:#1A3D2E;font-weight:500;margin-bottom:3px;"><strong>Title:</strong> {book.get('title', 'Unknown')}</div>
                              <div style="font-size:13px;color:#1A3D2E;margin-bottom:3px;"><strong>Author:</strong> {book.get('author', 'Unknown')}</div>
                              <div style="font-size:13px;color:#1A3D2E;margin-bottom:3px;"><strong>Available:</strong> {book.get('available_quantity', 0)} copies</div>
                              <div style="font-size:12px;color:#6B9080;margin-top:6px;font-style:italic;">💡 Consider increasing quantity instead of adding duplicate</div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        # ISBN is unique - show success/clear indicator
                        st.success("✅ ISBN is unique - ready to add", icon="✅")
                        
                except Exception as e:
                    # If lookup fails, show info but allow to proceed
                    st.info(f"✓ ISBN lookup ready (could not verify: {str(e)[:30]})")
            elif isbn and len(isbn.replace("-", "").replace(" ", "")) < 10:
                # ISBN is too short - show hint
                st.info("📝 Enter complete ISBN (10 or 13 digits)")

            st.markdown("<div style='height:2px;'></div>", unsafe_allow_html=True)
            r2c1, r2c2 = st.columns(2)
            with r2c1:
                qty = st.number_input("Number of Copies *", min_value=1, max_value=1000, value=1)
            with r2c2:
                fee = st.number_input(
                    "Late Return Fee (Rs./day) *",
                    min_value=0.0, max_value=1000.0,
                    value=10.0, step=5.0, format="%.2f",
                )

            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
            submitted = st.form_submit_button(
                "＋  Add Book to Catalogue",
                use_container_width=True,
                type="primary",
            )

        st.markdown("</div>", unsafe_allow_html=True)

    # ── Validation & save ────────────────────────────────────────────────────
    # When user submits the form
    if submitted:
        # STEP 1: Validate all required fields are filled
        if not title.strip() or not author.strip() or not isbn.strip() or category == "📖 Select Category":
            st.error("Please fill in all required fields: Title, Author, ISBN, and Category.")
            return
        
        # STEP 2: Validate ISBN format (should be 10 or 13 digits)
        clean_isbn = isbn.strip().replace("-", "").replace(" ", "")
        if len(clean_isbn) not in [10, 13] or not clean_isbn.isdigit():
            st.error("ISBN must be 10 or 13 digits. Please check and try again.")
            return
        
        try:
            # STEP 3: Check if ISBN already exists (duplicate prevention)
            existing_books = lib.search_books_by_isbn(isbn.strip())
            if existing_books:
                st.error(f"❌ This ISBN already exists in the database for '{existing_books[0].get('title')}'")
                st.info("💡 To add more copies, use the Inventory page instead.")
                return
            
            # STEP 4: Create Book object with all fields including category
            # Extract just the category name without the emoji
            category_clean = category.split(" ", 1)[1] if " " in category else category
            
            new_book = Book(
                title=title.strip(),
                author=author.strip(),
                isbn=clean_isbn,  # Use cleaned ISBN
                late_return_fee=fee,
                available_quantity=int(qty),
            )
            
            # STEP 5: Store category information (can be extended to use custom Book class field)
            # For now, category is validated and shown in the success message
            st.session_state.pending_book = {
                "title": title.strip(),
                "author": author.strip(),
                "isbn": clean_isbn,
                "category": category_clean,
                "qty": int(qty),
                "fee": fee
            }
            
            # STEP 6: Attempt to add the book to database
            ok = lib.add_book(new_book)
            
            # STEP 7: Show success or error message
            if ok:
                st.session_state.add_ok = f"{title.strip()} ({category_clean})"
                st.rerun()
            else:
                st.error("Failed to save. Please try again.")
        except Exception as e:
            st.error(f"Error adding book: {str(e)}")


# ═════════════════════════════════════════════════════════════════════════════════════
# 🔍 SEARCH & BORROW PAGE
# ═════════════════════════════════════════════════════════════════════════════════════════
# SIDEBAR: Search & Borrow (🔍) — Find books and process borrowing
# Search by title/author, view availability, and record borrower name
# Location: Sidebar → "Search & Borrow" (🔍)

def page_search(lib):
    """
    Allow librarians to search for books and process borrowing.

    Features:
    - Search by title or author
    - Display search results with availability
    - Show late fee information
    - Get borrower name and confirm borrow
    - Update inventory quantity automatically
    """
    page_heading("Search & Borrow",
        "Search availability by title or author · Borrowing reduces available quantity by 1")

    if st.session_state.confirm_borrow and st.session_state.pending_borrow:
        pb  = st.session_state.pending_borrow
        due = (datetime.now() + timedelta(days=14)).strftime("%d %B %Y")
        _, cc, _ = st.columns([1, 2, 1])
        with cc:
            confirm_box("Confirm Borrow",
                f'Borrow <strong>"{pb["title"]}"</strong> for <strong>{pb["name"]}</strong>?<br>'
                f'Available quantity will reduce by 1.<br>Due date: <strong>{due}</strong>')
            b1, b2 = st.columns(2)
            with b1:
                if st.button("Confirm Borrow", type="primary", use_container_width=True):
                    try:
                        if lib.borrow_book(pb["isbn"], pb["name"]):
                            st.session_state.confirm_borrow = False
                            st.session_state.borrow_ok = pb
                            st.session_state.pending_borrow = None
                            st.rerun()
                        else:
                            st.error("Borrow failed — book may no longer be available.")
                    except Exception as e:
                        st.error(str(e))
            with b2:
                if st.button("Cancel", use_container_width=True):
                    st.session_state.confirm_borrow = False; st.rerun()
        return

    if st.session_state.borrow_ok:
        bs  = st.session_state.borrow_ok
        due = (datetime.now() + timedelta(days=14)).strftime("%d %B %Y")
        _, cc, _ = st.columns([1, 2, 1])
        with cc:
            success_box("Book Borrowed Successfully",
                f'<strong>{bs["name"]}</strong> has borrowed <strong>"{bs["title"]}"</strong>.<br>'
                f'Available quantity reduced by 1. Due: <strong>{due}</strong>')
            st.balloons()
            st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
            if st.button("Search Again", type="primary", use_container_width=True):
                st.session_state.borrow_ok = None; st.rerun()
        return

    s1, s2, s3 = st.columns([5, 1.5, 1])
    with s1:
        query = st.text_input("q", placeholder="Enter book title or author name…", label_visibility="collapsed")
    with s2:
        by = st.selectbox("by", ["By Title", "By Author"], label_visibility="collapsed")
    with s3:
        go = st.button("Search →", type="primary", use_container_width=True)

    search_by = "title" if "Title" in by else "author"

    if not (go or query):
        st.markdown("""
        <div style="text-align:center;padding:64px 20px;color:#A8C4B6;">
          <div style="font-family:'Sora',sans-serif;font-size:18px;color:#C5DAD0;margin-bottom:8px;">
            What would you like to read?</div>
          <div style="font-size:13px;font-family:'Inter',sans-serif;">Enter a title or author name above to search.</div>
        </div>
        """, unsafe_allow_html=True)
        return

    if not query.strip():
        st.warning("Please enter a search term."); return

    try:
        results = lib.search_book(query.strip(), search_by=search_by)
        if not results:
            st.info(f"No books found for '{query}'. Try a different keyword."); return

        st.markdown(f"<div style='font-size:13px;color:#7BA892;margin-bottom:16px;font-family:\"Inter\",sans-serif;'>"
            f"Found <strong style='color:#1A3D2E;'>{len(results)}</strong> result(s) for <em>\"{query}\"</em></div>",
            unsafe_allow_html=True)

        for book in results:
            qty = book["available_quantity"]
            card_open("20px 24px")
            c1, c2, c3 = st.columns([3, 2, 2])
            with c1:
                st.markdown(f"""
                <div>
                  <div style="font-family:'Sora',sans-serif;font-size:17px;color:#1A3D2E;margin-bottom:4px;">{book['title']}</div>
                  <div style="font-size:13px;color:#7BA892;margin-bottom:5px;font-family:'Inter',sans-serif;">{book['author']}</div>
                  <div style="font-size:11.5px;color:#A8C4B6;font-family:'DM Mono',monospace;">ISBN: {book['isbn']}</div>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div style="padding-top:4px;">
                  {avail_badge(qty)}
                  <div style="font-size:12px;color:#8BB09C;margin-top:8px;font-family:'Inter',sans-serif;">
                    Late fee: Rs. {book['late_return_fee']:.2f} / day</div>
                </div>
                """, unsafe_allow_html=True)
            with c3:
                if qty > 0:
                    name = st.text_input("Name", key=f"n_{book['isbn']}",
                        placeholder="Borrower name", label_visibility="collapsed")
                    if st.button("Borrow →", key=f"b_{book['isbn']}", type="primary", use_container_width=True):
                        if not name.strip():
                            st.warning("Enter the borrower's name.")
                        else:
                            st.session_state.pending_borrow = {"isbn": book["isbn"], "title": book["title"],
                                "author": book["author"], "name": name.strip()}
                            st.session_state.confirm_borrow = True; st.rerun()
                else:
                    st.markdown('<div style="padding-top:10px;font-size:13px;font-weight:500;'
                        'color:#DC2626;font-family:\'Inter\',sans-serif;">No copies available</div>',
                        unsafe_allow_html=True)
            card_close()
    except Exception:
        st.error("An error occurred during search.")
        with st.expander("Details"): st.code(traceback.format_exc())

# ═════════════════════════════════════════════════════════════════════════════════════
# ↩️ RETURNS & FEES PAGE
# ═════════════════════════════════════════════════════════════════════════════════════════
# SIDEBAR: Returns & Fees (↩️) — Process returns and calculate late fees
# Calculate days borrowed, determine if overdue, and apply late fees
# Location: Sidebar → "Returns & Fees" (↩️)

def page_returns(lib):
    """
    Process book returns and calculate late fees.

    Workflow:
    1. Enter book ISBN and borrower name
    2. Set borrow date and return date
    3. System calculates:
       - Days borrowed
       - Days allowed (14 days)
       - Days late (if applicable)
       - Late fee = days_late × fee_per_day
    4. Collect fee and mark as returned
    """
    page_heading("Returns & Late Fee Calculator",
        "Process book returns · Late fee calculated automatically if return exceeds 2 weeks")

    # ── Show different screens based on state ──────────────────────────────

    # Screen 1: Show return success/fee
    if st.session_state.return_ok:
        rr = st.session_state.return_ok
        _, cc, _ = st.columns([1, 2, 1])
        with cc:
            # Show if late fee is due
            if rr["fee"] > 0:
                st.markdown(f"""
                <div style="background:#FFFFFF;border-radius:14px;padding:30px;
                    border:2px solid #D97706;text-align:center;max-width:440px;margin:0 auto 22px;">
                  <div style="font-size:32px;margin-bottom:12px;">⏰</div>
                  <div style="font-family:'Sora',sans-serif;font-size:20px;color:#92400E;margin-bottom:8px;">
                    Book Returned — Late Fee Due</div>
                  <div style="font-size:13px;color:#78350F;margin-bottom:18px;font-family:'Inter',sans-serif;">
                    Returned by <strong>{rr['name']}</strong></div>
                  <div style="background:#FFFBEB;border-left:3px solid #D97706;border-radius:0 8px 8px 0;padding:18px 20px;text-align:left;">
                    <div style="font-size:10.5px;font-weight:600;color:#92400E;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px;">Late Return Fee</div>
                    <div style="font-family:'Sora',sans-serif;font-size:32px;color:#92400E;">Rs. {rr['fee']:.2f}</div>
                    <div style="font-size:12px;color:#92400E;margin-top:6px;font-family:'Inter',sans-serif;">Please collect this amount at the counter.</div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Show if returned on time
                success_box("Book Returned On Time",
                    f'Returned by <strong>{rr["name"]}</strong>.<br>Within the 14-day loan period — no late fees.')
                st.balloons()
            st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
            if st.button("Process Another Return", type="primary", use_container_width=True):
                st.session_state.return_ok = None; st.rerun()
        return

    # Screen 2: Confirm return
    if st.session_state.confirm_return:
        _, cc, _ = st.columns([1, 2, 1])
        with cc:
            confirm_box("Confirm Return",
                f'Processing return for <strong>{st.session_state.ret_name}</strong><br>'
                f'ISBN: <code>{st.session_state.ret_isbn}</code>')
            b1, b2 = st.columns(2)
            with b1:
                if st.button("Confirm Return", type="primary", use_container_width=True):
                    try:
                        # Process the return in database
                        fee = lib.return_book(st.session_state.ret_isbn, st.session_state.ret_name)
                        st.session_state.confirm_return = False
                        if fee is not None:
                            # Store result to show on success screen
                            st.session_state.return_ok = {"name": st.session_state.ret_name, "fee": fee}
                        else:
                            st.error("No active borrow record found for this ISBN and name.")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
            with b2:
                if st.button("Cancel", use_container_width=True):
                    st.session_state.confirm_return = False; st.rerun()
        return

    # Screen 3: Input form
    left, right = st.columns([1, 1])
    with left:
        card_open()
        section_title("Return Details")
        isbn  = st.text_input("Book ISBN *",     placeholder="e.g. 978-0-7432-7356-5")
        bname = st.text_input("Borrower Name *", placeholder="Full name of the borrower")
        st.markdown("<hr>", unsafe_allow_html=True)
        section_title("Dates")
        d1, d2 = st.columns(2)
        with d1:
            borrow_date = st.date_input("Date Borrowed", value=datetime.now() - timedelta(days=20))
        with d2:
            return_date = st.date_input("Date Returning", value=datetime.now())
        card_close()

    with right:
        card_open()
        st.markdown("""
        <div style="font-size:10.5px;font-weight:600;color:#52997A;letter-spacing:1.2px;
            text-transform:uppercase;margin-bottom:18px;font-family:'Inter',sans-serif;">
          Fee Preview
        </div>
        """, unsafe_allow_html=True)
        # Calculate and preview the fee
        if borrow_date and return_date:
            db = (return_date - borrow_date).days  # Days borrowed
            dl = max(0, db - 14)  # Days late (0 if within 14 days)
            cc1, cc2, cc3 = st.columns(3)
            for col, val, label, accent in [
                (cc1, db, "DAYS BORROWED", "#2D6A4F"),
                (cc2, 14, "DAY LIMIT",     "#1A3D2E"),
                (cc3, dl, "DAYS LATE",     "#DC2626" if dl > 0 else "#2D6A4F"),
            ]:
                with col:
                    st.markdown(f"""
                    <div style="background:#F6FBF8;border-radius:10px;padding:14px 8px;
                        text-align:center;border:1px solid #D6EDE3;margin-bottom:16px;">
                      <div style="font-family:'Sora',sans-serif;font-size:28px;color:{accent};line-height:1;">{val}</div>
                      <div style="font-size:9px;font-weight:600;color:#8BB09C;letter-spacing:1px;margin-top:5px;font-family:'Inter',sans-serif;">{label}</div>
                    </div>
                    """, unsafe_allow_html=True)
            # Calculate fee if days are late
            if dl > 0 and isbn.strip():
                try:
                    bk = lib.get_book_by_isbn(isbn.strip())
                    if bk:
                        total = dl * bk["late_return_fee"]  # Calculate: days_late × fee_per_day
                        st.markdown(f"""
                        <div style="background:#FFFBEB;border-left:3px solid #D97706;border-radius:0 10px 10px 0;padding:18px;">
                          <div style="font-size:10.5px;font-weight:600;color:#92400E;letter-spacing:1px;margin-bottom:6px;font-family:'Inter',sans-serif;">LATE RETURN FEE</div>
                          <div style="font-size:12px;color:#78350F;margin-bottom:8px;font-family:'Inter',sans-serif;">{dl} days × Rs. {bk['late_return_fee']:.2f} per day</div>
                          <div style="font-family:'Sora',sans-serif;font-size:30px;color:#92400E;">Rs. {total:.2f}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.info("Enter a valid ISBN to calculate the exact fee.")
                except Exception:
                    st.info("Enter a valid ISBN to calculate the fee.")
            elif dl > 0:
                st.warning("Enter the ISBN above to calculate the exact fee.")
            else:
                # No late fees - returned on time
                st.markdown("""
                <div style="background:#F0FDF4;border-left:3px solid #40916C;border-radius:0 10px 10px 0;padding:18px;">
                  <div style="font-size:10.5px;font-weight:600;color:#166534;letter-spacing:1px;margin-bottom:6px;font-family:'Inter',sans-serif;">ON TIME</div>
                  <div style="font-size:12px;color:#15803D;margin-bottom:8px;font-family:'Inter',sans-serif;">Within the 14-day loan period.</div>
                  <div style="font-family:'Sora',sans-serif;font-size:28px;color:#166534;">No Late Fee</div>
                </div>
                """, unsafe_allow_html=True)
        card_close()

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    _, bc, _ = st.columns([2, 1, 2])
    with bc:
        # Button to process the return
        if st.button("Process Return →", type="primary", use_container_width=True):
            if not isbn.strip() or not bname.strip():
                st.error("Please enter both the Book ISBN and Borrower Name.")
            else:
                # Set up confirmation screen
                st.session_state.confirm_return = True
                st.session_state.ret_isbn = isbn.strip()
                st.session_state.ret_name = bname.strip()
                st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# RUN THE APPLICATION
# ─────────────────────────────────────────────────────────────────────────────
# This is executed when you run: streamlit run app.py
if __name__ == "__main__":
    main()