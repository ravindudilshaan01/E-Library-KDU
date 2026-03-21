"""
Kothalawala Library Management System
Clean Professional UI — Top nav bar, white cards, no sidebar
"""

import streamlit as st
from library_backend import LibraryManager, Book
from datetime import datetime, timedelta
import traceback
import pandas as pd


# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────

if "lib" not in st.session_state:
    try:
        st.session_state.lib    = LibraryManager()
        st.session_state.db_ok  = True
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
# PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Kothalawala E-Library",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
#MainMenu, footer, header   { visibility: hidden; }

/* Page background */
.main { background: #F3F4F6 !important; }
.main .block-container {
    padding: 24px 36px 48px !important;
    max-width: 1200px !important;
}

/* Hide sidebar completely */
[data-testid="stSidebar"]        { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }

/* ── Nav buttons ── */
.nav-wrap .stButton > button {
    border-radius: 8px !important;
    font-size: 13.5px !important;
    font-weight: 600 !important;
    padding: 9px 14px !important;
    width: 100% !important;
    transition: all 0.15s !important;
}

/* ── All other buttons ── */
.stButton > button {
    border-radius: 7px !important;
    font-size: 13.5px !important;
    font-weight: 600 !important;
    transition: all 0.15s !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 3px 10px rgba(0,0,0,0.12) !important;
}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input {
    border-radius: 7px !important;
    border: 1.5px solid #D1D5DB !important;
    background: #fff !important;
    font-size: 14px !important;
    padding: 9px 12px !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
    border-color: #2563EB !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.1) !important;
    outline: none !important;
}
.stTextInput label, .stNumberInput label,
.stSelectbox label, .stDateInput label {
    font-size: 13px !important;
    font-weight: 600 !important;
    color: #374151 !important;
}
.stSelectbox > div > div {
    border-radius: 7px !important;
    border: 1.5px solid #D1D5DB !important;
}
.stDateInput > div > div > input {
    border-radius: 7px !important;
    border: 1.5px solid #D1D5DB !important;
}

/* ── Dataframe ── */
.stDataFrame { border-radius: 8px !important; overflow: hidden !important; }

/* ── Alerts ── */
.stAlert { border-radius: 7px !important; font-size: 13.5px !important; }

/* ── Download button ── */
.stDownloadButton > button {
    border-radius: 7px !important;
    font-weight: 600 !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    border-radius: 8px !important;
    border: 1.5px solid #E5E7EB !important;
    background: #fff !important;
}

/* ── Form ── */
[data-testid="stForm"] {
    border: none !important;
    padding: 0 !important;
    background: transparent !important;
}

hr { border-color: #E5E7EB !important; margin: 14px 0 !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SHARED UI HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def stat_row(items):
    """items = list of (label, value, sublabel, color)"""
    cols = st.columns(len(items))
    for col, (lbl, val, sub, color) in zip(cols, items):
        with col:
            st.markdown(f"""
            <div style="background:#fff;border-radius:8px;padding:18px 16px 14px;
                box-shadow:0 1px 3px rgba(0,0,0,0.08);position:relative;overflow:hidden;">
              <div style="position:absolute;top:0;left:0;right:0;height:3px;
                  background:{color};border-radius:8px 8px 0 0;"></div>
              <div style="font-size:10px;font-weight:700;color:{color};
                  letter-spacing:1.2px;text-transform:uppercase;margin-bottom:7px;">{lbl}</div>
              <div style="font-size:26px;font-weight:700;color:#111827;line-height:1;">{val}</div>
              <div style="font-size:12px;color:#6B7280;margin-top:4px;">{sub}</div>
            </div>
            """, unsafe_allow_html=True)


def card_open(padding="24px"):
    st.markdown(
        f'<div style="background:#fff;border-radius:8px;padding:{padding};'
        'box-shadow:0 1px 3px rgba(0,0,0,0.08);margin-bottom:16px;">',
        unsafe_allow_html=True
    )

def card_close():
    st.markdown('</div>', unsafe_allow_html=True)


def page_heading(title, subtitle="", req=None):
    req_tag = ""
    if req:
        req_tag = (f' <span style="font-size:10px;font-weight:700;background:#EFF6FF;'
                   f'color:#1D4ED8;padding:2px 8px;border-radius:4px;'
                   f'letter-spacing:0.5px;vertical-align:middle;margin-left:8px;">{req}</span>')
    st.markdown(f"""
    <div style="margin-bottom:20px;padding-bottom:14px;border-bottom:1px solid #E5E7EB;">
      <div style="font-size:22px;font-weight:700;color:#111827;">{title}{req_tag}</div>
      {"" if not subtitle else f'<div style="font-size:13px;color:#6B7280;margin-top:4px;">{subtitle}</div>'}
    </div>
    """, unsafe_allow_html=True)


def info_bar(text):
    st.markdown(f"""
    <div style="background:#EFF6FF;border-left:3px solid #2563EB;border-radius:0 6px 6px 0;
        padding:9px 14px;margin-bottom:18px;font-size:13px;color:#1E3A5F;">{text}</div>
    """, unsafe_allow_html=True)


def section_title(text):
    st.markdown(f"""
    <div style="font-size:11px;font-weight:700;color:#9CA3AF;letter-spacing:1.2px;
        text-transform:uppercase;margin:18px 0 10px;">{text}</div>
    """, unsafe_allow_html=True)


def success_box(title, body):
    st.markdown(f"""
    <div style="background:#F0FDF4;border:1.5px solid #86EFAC;border-radius:8px;
        padding:26px;text-align:center;margin-bottom:16px;">
      <div style="font-size:19px;font-weight:700;color:#166534;margin-bottom:7px;">{title}</div>
      <div style="font-size:13.5px;color:#15803D;line-height:1.6;">{body}</div>
    </div>
    """, unsafe_allow_html=True)


def confirm_box(title, body, details=None, border="#2563EB"):
    det = ""
    if details:
        rows = ""
        for k, v in details.items():
            rows += (f'<div style="display:flex;justify-content:space-between;'
                     f'padding:6px 0;border-bottom:1px solid #F3F4F6;">'
                     f'<span style="font-size:13px;color:#6B7280;">{k}</span>'
                     f'<span style="font-size:13px;font-weight:600;color:#111827;">{v}</span>'
                     f'</div>')
        det = (f'<div style="background:#F9FAFB;border-radius:6px;'
               f'padding:12px 14px;text-align:left;margin:12px 0 14px;">{rows}</div>')
    st.markdown(f"""
    <div style="background:#fff;border-radius:8px;padding:26px;
        box-shadow:0 1px 4px rgba(0,0,0,0.08);border:2px solid {border};
        max-width:440px;margin:0 auto 20px;text-align:center;">
      <div style="font-size:19px;font-weight:700;color:#111827;margin-bottom:8px;">{title}</div>
      <div style="font-size:13px;color:#6B7280;line-height:1.6;">{body}</div>
      {det}
    </div>
    """, unsafe_allow_html=True)


def avail_badge(qty):
    if qty == 0:
        return '<span style="background:#FEF2F2;color:#991B1B;padding:2px 9px;border-radius:4px;font-size:11.5px;font-weight:600;">Out of Stock</span>'
    elif qty <= 2:
        return f'<span style="background:#FFFBEB;color:#92400E;padding:2px 9px;border-radius:4px;font-size:11.5px;font-weight:600;">Low — {qty} left</span>'
    return f'<span style="background:#F0FDF4;color:#065F46;padding:2px 9px;border-radius:4px;font-size:11.5px;font-weight:600;">Available — {qty}</span>'


def step_bar(active):
    steps = ["Enter Details", "Review Fee", "Confirm Return"]
    cols  = st.columns(3)
    for i, (col, lbl) in enumerate(zip(cols, steps), 1):
        with col:
            if i < active:
                bg, fg = "#10B981", "#fff"
            elif i == active:
                bg, fg = "#2563EB", "#fff"
            else:
                bg, fg = "#F3F4F6", "#9CA3AF"
            st.markdown(f"""
            <div style="background:{bg};border-radius:6px;padding:10px;
                text-align:center;font-size:12.5px;font-weight:600;color:{fg};">
              <span style="display:inline-block;width:18px;height:18px;border-radius:50%;
                  background:rgba(255,255,255,0.25);font-size:10px;line-height:18px;
                  margin-right:5px;">{i}</span>{lbl}
            </div>
            """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TOP NAV BAR
# ─────────────────────────────────────────────────────────────────────────────

def top_nav():
    # Branding strip
    st.markdown("""
    <div style="display:flex;align-items:center;justify-content:space-between;
        margin-bottom:16px;">
      <div>
        <span style="font-size:20px;font-weight:700;color:#111827;">
          Kothalawala E-Library
        </span>
        <span style="font-size:12px;color:#9CA3AF;margin-left:10px;">
          Management System
        </span>
      </div>
      <div style="font-size:12px;color:#9CA3AF;">
        """ + datetime.now().strftime("%A, %d %B %Y") + """
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Nav buttons
    pages = [
        ("Dashboard",       "Dashboard"),
        ("Inventory",       "Inventory"),
        ("Add Books",       "Add Books"),
        ("Search & Borrow", "Search & Borrow"),
        ("Returns & Fees",  "Returns & Fees"),
    ]

    # White pill container
    st.markdown('<div class="nav-wrap">', unsafe_allow_html=True)
    cols = st.columns(len(pages))
    for col, (label, key) in zip(cols, pages):
        with col:
            active = st.session_state.page == key
            if st.button(
                label,
                key="nav_" + key,
                use_container_width=True,
                type="primary" if active else "secondary",
            ):
                st.session_state.page           = key
                st.session_state.confirm_add    = False
                st.session_state.confirm_borrow = False
                st.session_state.confirm_return = False
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom:24px;'></div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    if not st.session_state.get("db_ok", False):
        st.error("Database connection failed: " + st.session_state.get("db_error", "Unknown"))
        st.info("Make sure serviceAccountKey.json is present and Firestore is enabled.")
        return

    lib = st.session_state.lib

    top_nav()

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
    page_heading("Dashboard", "Overview of library activity")

    try:
        inv   = lib.get_inventory()
        trans = lib.get_transaction_history()
        tt    = len(inv)
        tc    = sum(b["available_quantity"] for b in inv)
        bw    = len([t for t in trans if not t.get("return_date")])
        fe    = sum(t.get("late_fee", 0) for t in trans if t.get("late_fee", 0) > 0)
    except:
        inv = []; tt = tc = bw = 0; fe = 0.0

    st.markdown("<div style='margin-bottom:6px;'></div>", unsafe_allow_html=True)
    stat_row([
        ("Book Titles",    tt,                    "In catalogue",      "#2563EB"),
        ("Available",      tc,                    "Copies on shelf",   "#10B981"),
        ("On Loan",        bw,                    "Currently borrowed","#F59E0B"),
        ("Fees Collected", f"Rs. {int(fe)}",       "Late return fees",  "#EF4444"),
    ])

    st.markdown("<br>", unsafe_allow_html=True)

    # Quick actions
    section_title("Quick Actions")
    qa = st.columns(4)
    actions = [
        ("Search Books",  "Find and borrow a book",     "#2563EB", "Search & Borrow"),
        ("Add Book",      "Add a new title",             "#10B981", "Add Books"),
        ("Inventory",     "View the full report",        "#F59E0B", "Inventory"),
        ("Returns",       "Process a return",            "#EF4444", "Returns & Fees"),
    ]
    for col, (lbl, sub, color, dest) in zip(qa, actions):
        with col:
            st.markdown(f"""
            <div style="background:#fff;border-radius:8px;padding:18px 16px;
                box-shadow:0 1px 3px rgba(0,0,0,0.08);border-top:3px solid {color};
                margin-bottom:10px;">
              <div style="font-size:14px;font-weight:700;color:#111827;margin-bottom:3px;">{lbl}</div>
              <div style="font-size:12px;color:#9CA3AF;">{sub}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Open", key="qa_" + dest, use_container_width=True):
                st.session_state.page = dest
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Recent inventory table
    if inv:
        section_title("Library Collection")
        card_open()
        df = pd.DataFrame([{
            "Title":     b["title"],
            "Author":    b["author"],
            "ISBN":      b["isbn"],
            "Available": b["available_quantity"],
            "Late Fee":  f"Rs. {b['late_return_fee']:.2f}/day",
        } for b in inv[:10]])
        st.dataframe(df, use_container_width=True, hide_index=True)
        if len(inv) > 10:
            c1, c2, c3 = st.columns([3, 1, 3])
            with c2:
                if st.button("View All", use_container_width=True, type="primary"):
                    st.session_state.page = "Inventory"
                    st.rerun()
        card_close()
    else:
        st.info("No books in the library yet. Go to Add Books to get started.")

    st.markdown(f"""
    <div style="text-align:center;color:#D1D5DB;font-size:11px;padding:24px 0 4px;">
      Kothalawala E-Library · Powered by Firebase and Streamlit · {datetime.now().year}
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# INVENTORY  (REQ 5)
# ─────────────────────────────────────────────────────────────────────────────

def page_inventory(lib):
    page_heading(
        "Inventory Dashboard",
        "Title · Author · Available Quantity · Daily Late Return Fee",
        req="REQ 5"
    )

    try:
        inv   = lib.get_inventory()
        trans = lib.get_transaction_history()
        tt    = len(inv)
        tc    = sum(b["available_quantity"] for b in inv)
        bw    = len([t for t in trans if not t.get("return_date")])
        fe    = sum(t.get("late_fee", 0) for t in trans if t.get("late_fee", 0) > 0)

        stat_row([
            ("Book Titles",    tt,                    "In catalogue",      "#2563EB"),
            ("Available",      tc,                    "Copies on shelf",   "#10B981"),
            ("On Loan",        bw,                    "Currently borrowed","#F59E0B"),
            ("Fees Collected", f"Rs. {int(fe)}",       "Late return fees",  "#EF4444"),
        ])

        st.markdown("<br>", unsafe_allow_html=True)

        if not inv:
            st.info("No books yet. Add some to get started.")
            return

        # Filter bar inside a card
        card_open("16px 20px")
        f1, f2, f3 = st.columns([3, 2, 1])
        with f1:
            search = st.text_input("s", placeholder="Filter by title or author...",
                                   label_visibility="collapsed")
        with f2:
            status_f = st.selectbox("f", ["All Books", "Available", "Out of Stock"],
                                    label_visibility="collapsed")
        with f3:
            st.download_button(
                "Export CSV",
                data=pd.DataFrame([{
                    "Title":  b["title"], "Author": b["author"], "ISBN": b["isbn"],
                    "Available Quantity":  b["available_quantity"],
                    "Daily Late Fee (Rs)": b["late_return_fee"],
                } for b in inv]).to_csv(index=False),
                file_name=f"inventory_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv", use_container_width=True
            )
        card_close()

        # Apply filters
        filtered = []
        for b in inv:
            qty = b["available_quantity"]
            if search:
                q = search.lower()
                if q not in b["title"].lower() and q not in b["author"].lower():
                    continue
            if status_f == "Available"    and qty == 0: continue
            if status_f == "Out of Stock" and qty > 0:  continue
            filtered.append(b)

        if not filtered:
            st.info("No books match the current filter.")
            return

        # Table as the inventory report
        card_open()
        section_title("Inventory Report — REQ 5")
        rows = []
        for b in filtered:
            qty = b["available_quantity"]
            rows.append({
                "Title":                  b["title"],
                "Author":                 b["author"],
                "ISBN":                   b["isbn"],
                "Available Quantity":     qty,
                "Daily Late Fee (Rs/day)":f"Rs. {b['late_return_fee']:.2f}",
                "Status": ("Out of Stock" if qty == 0
                           else f"Low ({qty})"  if qty <= 2
                           else f"Available ({qty})"),
            })
        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
            hide_index=True,
            height=min(56 + len(rows) * 36, 500),
            column_config={
                "Available Quantity": st.column_config.NumberColumn(format="%d copies")
            }
        )
        card_close()

    except Exception as e:
        st.error("Error loading inventory.")
        with st.expander("Details"): st.code(traceback.format_exc())


# ─────────────────────────────────────────────────────────────────────────────
# ADD BOOKS  (REQ 1)
# ─────────────────────────────────────────────────────────────────────────────

def page_add_books(lib):
    page_heading(
        "Add New Books",
        "Title · Author · ISBN · Late Return Fee · Quantity of Copies",
        req="REQ 1"
    )

    # ── Confirm state ──
    if st.session_state.confirm_add and st.session_state.pending_book:
        bk = st.session_state.pending_book
        _, cc, _ = st.columns([1, 2, 1])
        with cc:
            confirm_box(
                "Confirm Adding Book",
                "Please review all details before saving.",
                details={
                    "Title":           bk["title"],
                    "Author":          bk["author"],
                    "ISBN":            bk["isbn"],
                    "Quantity":        f"{bk['qty']} copies",
                    "Late Return Fee": f"Rs. {bk['fee']:.2f} per day",
                }
            )
            b1, b2 = st.columns(2)
            with b1:
                if st.button("Confirm & Save", type="primary", use_container_width=True):
                    try:
                        nb = Book(
                            title=bk["title"], author=bk["author"],
                            isbn=bk["isbn"], late_return_fee=bk["fee"],
                            available_quantity=bk["qty"]
                        )
                        if lib.add_book(nb):
                            st.session_state.confirm_add  = False
                            st.session_state.pending_book = None
                            st.session_state.add_ok       = bk["title"]
                            st.rerun()
                        else:
                            st.error("Failed to save. Please try again.")
                    except Exception as e:
                        st.error(str(e))
            with b2:
                if st.button("Go Back & Edit", use_container_width=True):
                    st.session_state.confirm_add = False
                    st.rerun()
        return

    # ── Success state ──
    if st.session_state.add_ok:
        _, cc, _ = st.columns([1, 2, 1])
        with cc:
            success_box(
                "Book Added Successfully",
                f'<strong>"{st.session_state.add_ok}"</strong> '
                f'has been added to the library catalogue.'
            )
            st.balloons()
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Add Another Book", type="primary", use_container_width=True):
                st.session_state.add_ok = None
                st.rerun()
        return

    # ── Form ──
    info_bar("<strong>Requirement 1</strong> — Enter: Title &middot; Author &middot; "
             "ISBN &middot; Late Return Fee (Rs/day) &middot; Quantity of Copies")

    _, center, _ = st.columns([1, 2, 1])
    with center:
        card_open()
        section_title("Book Information")
        with st.form("add_form", clear_on_submit=False):
            title  = st.text_input("Book Title *",  placeholder="e.g. The Great Gatsby")
            author = st.text_input("Author *",       placeholder="e.g. F. Scott Fitzgerald")
            isbn   = st.text_input("ISBN *",          placeholder="e.g. 978-0-7432-7356-5")
            st.markdown("<hr>", unsafe_allow_html=True)
            section_title("Pricing & Stock")
            c1, c2 = st.columns(2)
            with c1:
                fee = st.number_input(
                    "Late Return Fee (Rs./day) *",
                    min_value=0.0, max_value=1000.0, value=10.0, step=5.0, format="%.2f"
                )
            with c2:
                qty = st.number_input(
                    "Number of Copies *",
                    min_value=1, max_value=1000, value=1
                )
            submitted = st.form_submit_button(
                "Review & Confirm", use_container_width=True, type="primary"
            )
        card_close()

    if submitted:
        if not title.strip() or not author.strip() or not isbn.strip():
            st.error("Please fill in all required fields: Title, Author, and ISBN.")
        else:
            st.session_state.pending_book = {
                "title": title.strip(), "author": author.strip(),
                "isbn":  isbn.strip(),  "fee": fee, "qty": int(qty)
            }
            st.session_state.confirm_add = True
            st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# SEARCH & BORROW  (REQ 2 & 3)
# ─────────────────────────────────────────────────────────────────────────────

def page_search(lib):
    page_heading(
        "Search & Borrow",
        "Search availability by title or author · Borrowing reduces available quantity by 1",
        req="REQ 2 & 3"
    )

    # ── Confirm borrow ──
    if st.session_state.confirm_borrow and st.session_state.pending_borrow:
        pb  = st.session_state.pending_borrow
        due = (datetime.now() + timedelta(days=14)).strftime("%d %B %Y")
        _, cc, _ = st.columns([1, 2, 1])
        with cc:
            confirm_box(
                "Confirm Borrow",
                f'Borrow <strong>"{pb["title"]}"</strong> for '
                f'<strong>{pb["name"]}</strong>?<br>'
                f'Available quantity will reduce by 1.<br>'
                f'Due date: <strong>{due}</strong>'
            )
            b1, b2 = st.columns(2)
            with b1:
                if st.button("Confirm Borrow", type="primary", use_container_width=True):
                    try:
                        if lib.borrow_book(pb["isbn"], pb["name"]):
                            st.session_state.confirm_borrow = False
                            st.session_state.borrow_ok      = pb
                            st.session_state.pending_borrow = None
                            st.rerun()
                        else:
                            st.error("Borrow failed — book may no longer be available.")
                    except Exception as e:
                        st.error(str(e))
            with b2:
                if st.button("Cancel", use_container_width=True):
                    st.session_state.confirm_borrow = False
                    st.rerun()
        return

    # ── Borrow success ──
    if st.session_state.borrow_ok:
        bs  = st.session_state.borrow_ok
        due = (datetime.now() + timedelta(days=14)).strftime("%d %B %Y")
        _, cc, _ = st.columns([1, 2, 1])
        with cc:
            success_box(
                "Book Borrowed Successfully",
                f'<strong>{bs["name"]}</strong> has borrowed '
                f'<strong>"{bs["title"]}"</strong>.<br>'
                f'Available quantity reduced by 1. Due: <strong>{due}</strong>'
            )
            st.balloons()
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Search Again", type="primary", use_container_width=True):
                st.session_state.borrow_ok = None
                st.rerun()
        return

    # ── Search bar ──
    info_bar("<strong>Req 2</strong> — Search by Title or Author &nbsp;·&nbsp; "
             "<strong>Req 3</strong> — Borrowing reduces available quantity by 1")

    s1, s2, s3 = st.columns([5, 1.5, 1])
    with s1:
        query = st.text_input("q", placeholder="Enter book title or author name...",
                              label_visibility="collapsed")
    with s2:
        by = st.selectbox("by", ["By Title", "By Author"], label_visibility="collapsed")
    with s3:
        go = st.button("Search", type="primary", use_container_width=True)

    search_by = "title" if "Title" in by else "author"

    if not (go or query):
        st.markdown("""
        <div style="text-align:center;padding:56px 20px;color:#9CA3AF;">
          <div style="font-size:15px;font-weight:500;">Enter a title or author name above to search.</div>
          <div style="font-size:13px;margin-top:5px;">Use the dropdown to switch between title and author search.</div>
        </div>
        """, unsafe_allow_html=True)
        return

    if not query.strip():
        st.warning("Please enter a search term.")
        return

    try:
        results = lib.search_book(query.strip(), search_by=search_by)

        if not results:
            st.info(f"No books found for '{query}'. Try a different keyword.")
            return

        st.markdown(f"<div style='font-size:13px;color:#6B7280;margin-bottom:14px;'>"
                    f"Found <strong>{len(results)}</strong> result(s) for "
                    f"<em>\"{query}\"</em></div>", unsafe_allow_html=True)

        for book in results:
            qty = book["available_quantity"]
            card_open("18px 22px")

            c1, c2, c3 = st.columns([3, 2, 2])

            with c1:
                st.markdown(f"""
                <div style="font-size:16px;font-weight:700;color:#111827;margin-bottom:3px;">
                  {book['title']}
                </div>
                <div style="font-size:13px;color:#6B7280;margin-bottom:4px;">
                  {book['author']}
                </div>
                <div style="font-size:12px;color:#9CA3AF;">
                  ISBN: {book['isbn']}
                </div>
                """, unsafe_allow_html=True)

            with c2:
                st.markdown(f"""
                <div style="padding-top:4px;">
                  {avail_badge(qty)}
                  <div style="font-size:12px;color:#9CA3AF;margin-top:6px;">
                    Late fee: Rs. {book['late_return_fee']:.2f} / day
                  </div>
                </div>
                """, unsafe_allow_html=True)

            with c3:
                if qty > 0:
                    name = st.text_input(
                        "Name", key=f"n_{book['isbn']}",
                        placeholder="Borrower name",
                        label_visibility="collapsed"
                    )
                    if st.button("Borrow", key=f"b_{book['isbn']}",
                                 type="primary", use_container_width=True):
                        if not name.strip():
                            st.warning("Enter the borrower's name.")
                        else:
                            st.session_state.pending_borrow = {
                                "isbn":   book["isbn"],
                                "title":  book["title"],
                                "author": book["author"],
                                "name":   name.strip()
                            }
                            st.session_state.confirm_borrow = True
                            st.rerun()
                else:
                    st.markdown(
                        '<div style="padding-top:8px;font-size:13px;'
                        'font-weight:500;color:#DC2626;">No copies available</div>',
                        unsafe_allow_html=True
                    )

            card_close()

    except Exception as e:
        st.error("An error occurred during search.")
        with st.expander("Details"): st.code(traceback.format_exc())


# ─────────────────────────────────────────────────────────────────────────────
# RETURNS & FEES  (REQ 4)
# ─────────────────────────────────────────────────────────────────────────────

def page_returns(lib):
    page_heading(
        "Returns & Late Fee Calculator",
        "Process book returns · Late fee calculated automatically if return exceeds 2 weeks",
        req="REQ 4"
    )

    step_bar(3 if (st.session_state.confirm_return
                   or st.session_state.return_ok) else 1)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Result ──
    if st.session_state.return_ok:
        rr = st.session_state.return_ok
        _, cc, _ = st.columns([1, 2, 1])
        with cc:
            if rr["fee"] > 0:
                st.markdown(f"""
                <div style="background:#fff;border-radius:8px;padding:26px;
                    box-shadow:0 1px 4px rgba(0,0,0,0.08);border:2px solid #F59E0B;
                    text-align:center;max-width:440px;margin:0 auto 20px;">
                  <div style="font-size:19px;font-weight:700;color:#92400E;margin-bottom:8px;">
                    Book Returned — Late Fee Due
                  </div>
                  <div style="font-size:13px;color:#78350F;margin-bottom:16px;">
                    Returned by <strong>{rr['name']}</strong>
                  </div>
                  <div style="background:#FFFBEB;border-left:3px solid #F59E0B;
                      border-radius:0 6px 6px 0;padding:16px 18px;text-align:left;">
                    <div style="font-size:11px;font-weight:700;color:#92400E;
                        letter-spacing:1px;margin-bottom:5px;">LATE RETURN FEE</div>
                    <div style="font-size:28px;font-weight:700;color:#92400E;">
                      Rs. {rr['fee']:.2f}
                    </div>
                    <div style="font-size:12px;color:#92400E;margin-top:5px;">
                      Please collect this amount at the counter.
                    </div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                success_box(
                    "Book Returned On Time",
                    f'Returned by <strong>{rr["name"]}</strong>.<br>'
                    f'Within the 14-day loan period — no late fees.'
                )
                st.balloons()
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Process Another Return", type="primary", use_container_width=True):
                st.session_state.return_ok = None
                st.rerun()
        return

    # ── Confirm ──
    if st.session_state.confirm_return:
        _, cc, _ = st.columns([1, 2, 1])
        with cc:
            confirm_box(
                "Confirm Return",
                f'Processing return for '
                f'<strong>{st.session_state.ret_name}</strong><br>'
                f'ISBN: <code>{st.session_state.ret_isbn}</code>'
            )
            b1, b2 = st.columns(2)
            with b1:
                if st.button("Confirm Return", type="primary", use_container_width=True):
                    try:
                        fee = lib.return_book(
                            st.session_state.ret_isbn,
                            st.session_state.ret_name
                        )
                        st.session_state.confirm_return = False
                        if fee is not None:
                            st.session_state.return_ok = {
                                "name": st.session_state.ret_name, "fee": fee
                            }
                        else:
                            st.error("No active borrow record found for this ISBN and name.")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
            with b2:
                if st.button("Cancel", use_container_width=True):
                    st.session_state.confirm_return = False
                    st.rerun()
        return

    # ── Form + live preview ──
    info_bar("<strong>Req 4</strong> — Late fee = "
             "<strong>(days overdue) × (daily late fee)</strong> "
             "&nbsp;·&nbsp; Loan period = 14 days (2 weeks)")

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
            borrow_date = st.date_input("Date Borrowed",
                                        value=datetime.now() - timedelta(days=20))
        with d2:
            return_date = st.date_input("Date Returning", value=datetime.now())
        card_close()

    with right:
        card_open()
        st.markdown("""
        <div style="font-size:11px;font-weight:700;color:#9CA3AF;
            letter-spacing:1.2px;text-transform:uppercase;margin-bottom:16px;">
          Fee Preview
          <span style="background:#EFF6FF;color:#1D4ED8;padding:2px 7px;
              border-radius:4px;font-size:10px;font-weight:700;margin-left:8px;
              letter-spacing:0.5px;vertical-align:middle;">REQ 4</span>
        </div>
        """, unsafe_allow_html=True)

        if borrow_date and return_date:
            db = (return_date - borrow_date).days
            dl = max(0, db - 14)
            lc = "#DC2626" if dl > 0 else "#10B981"

            # Three counters
            cc1, cc2, cc3 = st.columns(3)
            for col, val, label, bg, border in [
                (cc1, db, "DAYS BORROWED", "#F9FAFB", "#E5E7EB"),
                (cc2, 14, "DAY LIMIT",     "#EFF6FF", "#BFDBFE"),
                (cc3, dl, "DAYS LATE",     "#F9FAFB", "#E5E7EB"),
            ]:
                with col:
                    color = lc if label == "DAYS LATE" else ("#1D4ED8" if label == "DAY LIMIT" else "#111827")
                    st.markdown(f"""
                    <div style="background:{bg};border-radius:6px;padding:12px 8px;
                        text-align:center;border:1px solid {border};margin-bottom:14px;">
                      <div style="font-size:24px;font-weight:700;color:{color};line-height:1;">{val}</div>
                      <div style="font-size:9px;font-weight:700;color:#9CA3AF;
                          letter-spacing:1px;margin-top:4px;">{label}</div>
                    </div>
                    """, unsafe_allow_html=True)

            # Fee box
            if dl > 0 and isbn.strip():
                try:
                    bk = lib.get_book_by_isbn(isbn.strip())
                    if bk:
                        total = dl * bk["late_return_fee"]
                        st.markdown(f"""
                        <div style="background:#FFFBEB;border-left:3px solid #F59E0B;
                            border-radius:0 6px 6px 0;padding:16px;">
                          <div style="font-size:11px;font-weight:700;color:#92400E;
                              letter-spacing:1px;margin-bottom:5px;">LATE RETURN FEE</div>
                          <div style="font-size:12px;color:#78350F;margin-bottom:7px;">
                            {dl} days × Rs. {bk['late_return_fee']:.2f} per day
                          </div>
                          <div style="font-size:26px;font-weight:700;color:#92400E;">
                            Rs. {total:.2f}
                          </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.info("Enter a valid ISBN to calculate the fee.")
                except:
                    st.info("Enter a valid ISBN to calculate the fee.")
            elif dl > 0:
                st.warning("Enter the ISBN above to calculate the exact fee.")
            else:
                st.markdown("""
                <div style="background:#F0FDF4;border-left:3px solid #10B981;
                    border-radius:0 6px 6px 0;padding:16px;">
                  <div style="font-size:11px;font-weight:700;color:#166534;
                      letter-spacing:1px;margin-bottom:5px;">ON TIME</div>
                  <div style="font-size:12px;color:#15803D;margin-bottom:7px;">
                    Within the 14-day loan period.
                  </div>
                  <div style="font-size:26px;font-weight:700;color:#166534;">No Late Fee</div>
                </div>
                """, unsafe_allow_html=True)

        card_close()

    st.markdown("<br>", unsafe_allow_html=True)
    _, bc, _ = st.columns([2, 1, 2])
    with bc:
        if st.button("Process Return", type="primary", use_container_width=True):
            if not isbn.strip() or not bname.strip():
                st.error("Please enter both the Book ISBN and Borrower Name.")
            else:
                st.session_state.confirm_return = True
                st.session_state.ret_isbn       = isbn.strip()
                st.session_state.ret_name       = bname.strip()
                st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()