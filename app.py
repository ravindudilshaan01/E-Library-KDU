"""
Kothalawala Library Management System
Theme  : Ivory & Forest Green
Layout : Icon Sidebar (200px)
"""

import streamlit as st
from library_backend import LibraryManager, Book
from datetime import datetime, timedelta
import traceback
import pandas as pd


# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Kothalawala E-Library",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
if "lib" not in st.session_state:
    try:
        st.session_state.lib   = LibraryManager()
        st.session_state.db_ok = True
    except Exception as e:
        st.session_state.db_ok    = False
        st.session_state.db_error = str(e)

for k, v in {
    "page":           "Dashboard",
    "confirm_add":    False,
    "confirm_borrow": False,
    "confirm_return": False,
    "pending_book":   None,
    "pending_borrow": None,
    "add_ok":         None,
    "borrow_ok":      None,
    "return_ok":      None,
    "ret_isbn":       "",
    "ret_name":       "",
}.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────
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
# UI HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def stat_row(items):
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
# SIDEBAR NAV
# ─────────────────────────────────────────────────────────────────────────────

def sidebar_nav():
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

        pages = [
            ("Home",      "🏠", "Dashboard"),
            ("Inventory",      "📦", "Inventory"),
            ("Add Books",      "➕", "Add Books"),
            ("Search & Borrow","🔍", "Search & Borrow"),
            ("Returns & Fees", "↩️",  "Returns & Fees"),
        ]

        for label, icon, key in pages:
            active = st.session_state.page == key
            if st.button(
                f"{icon}  {label}",
                key="nav_" + key,
                help=key,
                type="primary" if active else "secondary",
                use_container_width=True,
            ):
                st.session_state.page           = key
                st.session_state.confirm_add    = False
                st.session_state.confirm_borrow = False
                st.session_state.confirm_return = False
                st.rerun()

        st.markdown(
            f'<div style="position:fixed;bottom:16px;left:0;width:200px;text-align:center;'
            f'font-size:9px;color:rgba(116,198,157,0.25);font-family:Inter,sans-serif;">'
            f'{datetime.now().year}</div>',
            unsafe_allow_html=True
        )


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    if not st.session_state.get("db_ok", False):
        st.error("Database connection failed: " + st.session_state.get("db_error", "Unknown"))
        st.info("Ensure serviceAccountKey.json is present and Firestore is enabled.")
        return

    sidebar_nav()
    lib  = st.session_state.lib
    page = st.session_state.page

    if   page == "Dashboard":       page_dashboard(lib)
    elif page == "Inventory":       page_inventory(lib)
    elif page == "Add Books":       page_add_books(lib)
    elif page == "Search & Borrow": page_search(lib)
    elif page == "Returns & Fees":  page_returns(lib)


# ─────────────────────────────────────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────

def page_dashboard(lib):
    st.markdown(f"""
    <div style="display:flex;align-items:flex-end;justify-content:space-between;
        margin-bottom:28px;padding-bottom:18px;border-bottom:1px solid #DAF0E5;">
      <div>
        <div style="font-family:'Sora',sans-serif;font-size:26px;color:#1A3D2E;">
                    Library Home
        </div>
        <div style="font-size:13px;color:#7BA892;margin-top:5px;">
                    Good {"morning" if datetime.now().hour < 12 else "afternoon"} — monitor circulation, stock, and returns in one place.
        </div>
      </div>
      <div style="font-size:12px;color:#A8C4B6;font-family:'Inter',sans-serif;">
        {datetime.now().strftime("%A, %d %B %Y")}
      </div>
    </div>
    """, unsafe_allow_html=True)

    try:
        inv = lib.get_inventory()
        trans = lib.get_transaction_history()
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
        if st.button("Open Full Inventory", use_container_width=True, type="primary"):
            st.session_state.page = "Inventory"
            st.rerun()

    st.markdown(f"""
    <div style="text-align:center;color:#C4D9CC;font-size:11px;
        padding:32px 0 4px;font-family:'Inter',sans-serif;">
      Kothalawala E-Library · Powered by Firebase & Streamlit · {datetime.now().year}
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# INVENTORY  (REQ 5)
# ─────────────────────────────────────────────────────────────────────────────

def page_inventory(lib):
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
        f1, f2, f3 = st.columns([3, 2, 1])
        with f1:
            search = st.text_input("s", placeholder="Filter by title or author…", label_visibility="collapsed")
        with f2:
            status_f = st.selectbox("f", ["All Books", "Available", "Out of Stock"], label_visibility="collapsed")
        with f3:
            df_export = pd.DataFrame([{"Title": b["title"], "Author": b["author"], "ISBN": b["isbn"],
                "Available Quantity": b["available_quantity"], "Daily Late Fee (Rs)": b["late_return_fee"]} for b in inv])
            st.download_button("Export CSV", data=df_export.to_csv(index=False),
                file_name=f"inventory_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv", use_container_width=True)
        card_close()

        filtered = [b for b in inv if
            (not search or search.lower() in b["title"].lower() or search.lower() in b["author"].lower()) and
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
        for i, b in enumerate(filtered):
            qty = b["available_quantity"]
            bg  = "#FFFFFF" if i % 2 == 0 else "#F9FCF9"
            badge = ('<span style="background:#FEF2F2;color:#991B1B;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600;">Out of Stock</span>' if qty == 0
                else f'<span style="background:#FFFBEB;color:#92400E;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600;">Low ({qty})</span>' if qty <= 2
                else f'<span style="background:#ECFDF5;color:#065F46;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600;">In Stock ({qty})</span>')
            qty_color = "#065F46" if qty > 2 else ("#92400E" if qty > 0 else "#991B1B")
            st.markdown(f"""
            <div style="background:{bg};padding:12px 22px;display:flex;border-bottom:1px solid #EBF5EF;align-items:center;">
              <span style="flex:3;font-size:13.5px;color:#1A3D2E;font-weight:500;font-family:'Inter',sans-serif;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;padding-right:12px;">{b['title']}</span>
              <span style="flex:2;font-size:13px;color:#6B9080;font-family:'Inter',sans-serif;">{b['author']}</span>
              <span style="flex:2;font-size:12px;color:#8BB09C;font-family:'DM Mono',monospace;">{b['isbn']}</span>
              <span style="flex:1;font-size:14px;font-weight:600;color:{qty_color};text-align:center;font-family:'Sora',sans-serif;">{qty}</span>
              <span style="flex:1.5;font-size:13px;color:#6B9080;text-align:center;font-family:'Inter',sans-serif;">Rs. {b['late_return_fee']:.2f}</span>
              <span style="flex:1.5;text-align:right;">{badge}</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)
        card_close()
    except Exception:
        st.error("Error loading inventory.")
        with st.expander("Details"): st.code(traceback.format_exc())


# ─────────────────────────────────────────────────────────────────────────────
# ADD BOOKS  (REQ 1)
# ─────────────────────────────────────────────────────────────────────────────

def page_add_books(lib):
    page_heading(
        "Add New Books",
        "Create new catalogue records with a modern inline form",
    )

    # ── Success screen ────────────────────────────────────────────────────────
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
            isbn = st.text_input("ISBN *", placeholder="e.g. 978-0-7432-7356-5")

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
    if submitted:
        if not title.strip() or not author.strip() or not isbn.strip():
            st.error("Please fill in all required fields: Title, Author, and ISBN.")
            return
        try:
            ok = lib.add_book(
                Book(
                    title=title.strip(),
                    author=author.strip(),
                    isbn=isbn.strip(),
                    late_return_fee=fee,
                    available_quantity=int(qty),
                )
            )
            if ok:
                st.session_state.add_ok = title.strip()
                st.rerun()
            st.error("Failed to save. Please try again.")
        except Exception as e:
            st.error(str(e))


# ─────────────────────────────────────────────────────────────────────────────
# SEARCH & BORROW  (REQ 2 & 3)
# ─────────────────────────────────────────────────────────────────────────────

def page_search(lib):
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


# ─────────────────────────────────────────────────────────────────────────────
# RETURNS & FEES  (REQ 4)
# ─────────────────────────────────────────────────────────────────────────────

def page_returns(lib):
    page_heading("Returns & Late Fee Calculator",
        "Process book returns · Late fee calculated automatically if return exceeds 2 weeks")

    step_bar(3 if (st.session_state.confirm_return or st.session_state.return_ok) else 1)
    st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)

    if st.session_state.return_ok:
        rr = st.session_state.return_ok
        _, cc, _ = st.columns([1, 2, 1])
        with cc:
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
                success_box("Book Returned On Time",
                    f'Returned by <strong>{rr["name"]}</strong>.<br>Within the 14-day loan period — no late fees.')
                st.balloons()
            st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
            if st.button("Process Another Return", type="primary", use_container_width=True):
                st.session_state.return_ok = None; st.rerun()
        return

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
                        fee = lib.return_book(st.session_state.ret_isbn, st.session_state.ret_name)
                        st.session_state.confirm_return = False
                        if fee is not None:
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
        if borrow_date and return_date:
            db = (return_date - borrow_date).days
            dl = max(0, db - 14)
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
            if dl > 0 and isbn.strip():
                try:
                    bk = lib.get_book_by_isbn(isbn.strip())
                    if bk:
                        total = dl * bk["late_return_fee"]
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
        if st.button("Process Return →", type="primary", use_container_width=True):
            if not isbn.strip() or not bname.strip():
                st.error("Please enter both the Book ISBN and Borrower Name.")
            else:
                st.session_state.confirm_return = True
                st.session_state.ret_isbn = isbn.strip()
                st.session_state.ret_name = bname.strip()
                st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()