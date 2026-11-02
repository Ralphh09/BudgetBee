import json
import os
import re
import secrets
import hashlib
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="BudgetBee", page_icon="🐝", layout="centered")

# ── Constants ────────────────────────────────────────────────────────────────
GREEN, HONEY, RED = "#0F5C4A", "#E8A33D", "#C8443B"
IMG_TYPES = ["png", "jpg", "jpeg"]
MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]
CATEGORIES = ["Food & Drinks", "Transport", "Stationeries", "Event", "Utilities",
              "Rent", "Healthcare", "Entertainment", "Others"]
EARN_SOURCES = ["Salary", "Freelance / Side job", "Business", "Allowance",
                "Gift", "Investment", "Refund", "Others"]
CURRENCIES = ["GHS", "USD", "EUR", "GBP", "NGN", "JPY", "CAD", "AUD", "CHF", "CNY",
              "INR", "ZAR", "KES", "EGP", "MAD", "XOF", "XAF", "TZS", "UGX", "RWF",
              "IRR", "IQD", "JOD", "KWD", "LBP", "LYD", "OMR", "QAR", "SAR", "SYP", "TND"]

# Keep the key out of the code: put EXCHANGE_API_KEY in .streamlit/secrets.toml
# or set it as an environment variable.
try:
    API_KEY = st.secrets["EXCHANGE_API_KEY"]
except Exception:
    API_KEY = os.environ.get("EXCHANGE_API_KEY", "")

# ── Style ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;800&display=swap');
html, body, [data-testid="stAppViewContainer"], button, input, textarea {
    font-family: 'Manrope', sans-serif;
}
[data-testid="stAppViewContainer"] { background: #F5F8F6; }
[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"] { background: #FFFFFF; border-right: 1px solid #DDE5E1; }
[data-testid="stSidebar"] [data-testid="stImage"] img { border-radius: 50%; }
h1, h2, h3 { color: #0F5C4A; font-weight: 800; letter-spacing: -0.01em; }
[data-testid="stMetric"], [data-testid="stForm"] {
    background: #FFFFFF; border: 1px solid #DDE5E1; border-radius: 12px; padding: 14px 16px;
}
[data-testid="stMetricLabel"] { color: #5B6B66; }
.stButton > button, [data-testid="stFormSubmitButton"] > button {
    border-radius: 8px; font-weight: 600; border: 1px solid #0F5C4A;
}
[data-testid="stFormSubmitButton"] > button { background: #0F5C4A; color: #fff; }
.note { padding: 10px 14px; border-radius: 8px; margin: 8px 0; border-left: 4px solid; background: #fff; }
.note.warn { border-color: #E8A33D; }
.note.bad  { border-color: #C8443B; }
.bar  { background: #E3EAE7; height: 10px; border-radius: 5px; margin: 4px 0 14px; }
.fill { height: 10px; border-radius: 5px; }
.goal { background: #fff; border: 1px solid #DDE5E1; border-radius: 12px; padding: 14px 16px; }

[data-testid="stAppViewContainer"] {
    background-color: #F3F7F4;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='56' height='100' viewBox='0 0 56 100'%3E%3Cpath d='M28 66L0 50L0 16L28 0L56 16L56 50L28 66L28 100' fill='none' stroke='%230F5C4A' stroke-opacity='.07' stroke-width='2'/%3E%3Cpath d='M28 0L28 34L0 50L0 84L28 100L56 84L56 50L28 34' fill='none' stroke='%230F5C4A' stroke-opacity='.07' stroke-width='2'/%3E%3C/svg%3E");
}
.hero {
    background-image:
        url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='56' height='100' viewBox='0 0 56 100'%3E%3Cpath d='M28 66L0 50L0 16L28 0L56 16L56 50L28 66L28 100' fill='none' stroke='%23ffffff' stroke-opacity='.14' stroke-width='2'/%3E%3Cpath d='M28 0L28 34L0 50L0 84L28 100L56 84L56 50L28 34' fill='none' stroke='%23ffffff' stroke-opacity='.14' stroke-width='2'/%3E%3C/svg%3E"),
        linear-gradient(120deg, #0F5C4A 0%, #13806A 65%, #E8A33D 170%);
    border-radius: 18px; padding: 26px 28px; margin-bottom: 18px;
    display: flex; justify-content: space-between; align-items: center;
    box-shadow: 0 8px 24px rgba(15, 92, 74, .25);
}
.hero, .hero * { color: #FFFFFF !important; }
.hero .hello { opacity: .85; font-size: 14px; }
.hero .ttl { font-size: 32px; font-weight: 800; line-height: 1.15; }
.hero .bee { font-size: 54px; margin-right: 18px; }
.hero .chip { background: rgba(255,255,255,.16); border: 1px solid rgba(255,255,255,.35);
              border-radius: 14px; padding: 10px 16px; text-align: right; font-size: 13px; }
.hero .chip b { font-size: 20px; }
[data-testid="stMetric"] { border-top: 4px solid #E8A33D; box-shadow: 0 4px 14px rgba(15,92,74,.08); }
[data-testid="stMetricValue"] { color: #0F5C4A; font-weight: 800; }
[data-testid="stHorizontalBlock"] > div:nth-child(2) [data-testid="stMetric"] { border-top-color: #0F5C4A; }
[data-testid="stHorizontalBlock"] > div:nth-child(3) [data-testid="stMetric"] { border-top-color: #C8443B; }
[data-testid="stFormSubmitButton"] > button { background: linear-gradient(120deg, #0F5C4A, #13806A); }
[data-testid="stSidebar"] .stRadio label { padding: 6px 10px; border-radius: 8px; }
[data-testid="stSidebar"] .stRadio label:hover { background: #EAF3EF; }
.stTabs [aria-selected="true"] { color: #0F5C4A; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ──────────────────────────────────────────────────────────────────
def load(path, default):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return default


def save(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


def ufile(name):
    folder = f"data/{st.session_state.username}"
    os.makedirs(folder, exist_ok=True)
    return f"{folder}/{name}"


def save_image(upload, kind):
    """Save an uploaded image under the user's folder and return its path."""
    folder = ufile(kind)
    os.makedirs(folder, exist_ok=True)
    ext = upload.name.rsplit(".", 1)[-1].lower()
    path = f"{folder}/{datetime.now():%Y%m%d%H%M%S}_{secrets.token_hex(3)}.{ext}"
    with open(path, "wb") as f:
        f.write(upload.getbuffer())
    return path


def hash_pw(pw, salt=None):
    salt = salt or secrets.token_hex(8)
    digest = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt.encode(), 100_000).hex()
    return f"sha${salt}${digest}"


def check_pw(pw, stored):
    if not stored.startswith("sha$"):          # old plain-text accounts still work
        return pw == stored
    return secrets.compare_digest(hash_pw(pw, stored.split("$")[1]), stored)


def note(kind, text):
    st.markdown(f"<div class='note {kind}'>{text}</div>", unsafe_allow_html=True)


def bar(pct, color):
    st.markdown(f"<div class='bar'><div class='fill' style='background:{color};"
                f"width:{pct:.0f}%'></div></div>", unsafe_allow_html=True)


def tidy(fig):
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                      font_family="Manrope", margin=dict(l=0, r=0, t=30, b=0))
    return fig


def by_category(records):
    if not records:
        return pd.DataFrame(columns=["category", "amount"])
    return pd.DataFrame(records).groupby("category")["amount"].sum().reset_index()


def flash_and_rerun(msg):
    st.session_state.flash = msg
    st.rerun()


@st.cache_data(ttl=3600)
def fetch_rates(base):
    if not API_KEY:
        return None, "Add EXCHANGE_API_KEY to .streamlit/secrets.toml or your environment."
    try:
        r = requests.get(f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{base}", timeout=10)
        data = r.json()
        if r.status_code == 200 and data.get("result") == "success":
            return data["conversion_rates"], None
        return None, f"The rates service returned an error (status {r.status_code})."
    except Exception as e:
        return None, f"Could not reach the rates service: {e}"


# ── Session + login ──────────────────────────────────────────────────────────
st.session_state.setdefault("logged_in", False)
st.session_state.setdefault("username", "")


def login_page():
    st.markdown("""
    <div class='hero'>
      <div style='display:flex;align-items:center'>
        <div class='bee'>🐝</div>
        <div><div class='ttl'>BudgetBee</div><div class='hello'>Track what you earn, save and spend.</div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Log in", "Sign up"])

    with tab1:
        u = st.text_input("Username", key="login_user")
        p = st.text_input("Password", type="password", key="login_pass")
        if st.button("Log in", use_container_width=True):
            users = load("users.json", {})
            if u in users and check_pw(p, users[u]):
                if not users[u].startswith("sha$"):      # upgrade old accounts
                    users[u] = hash_pw(p)
                    save("users.json", users)
                st.session_state.logged_in, st.session_state.username = True, u
                st.rerun()
            st.error("Wrong username or password.")

    with tab2:
        nu = st.text_input("Username", key="signup_user", help="3-30 letters, numbers, _ or -")
        np1 = st.text_input("Password", type="password", key="signup_pass")
        np2 = st.text_input("Confirm password", type="password", key="signup_pass2")
        if st.button("Create account", use_container_width=True):
            users = load("users.json", {})
            if not re.fullmatch(r"[A-Za-z0-9_-]{3,30}", nu):
                st.error("Username must be 3-30 letters, numbers, _ or -.")
            elif len(np1) < 6:
                st.error("Password must be at least 6 characters.")
            elif np1 != np2:
                st.error("Passwords do not match.")
            elif nu in users:
                st.error("That username is taken.")
            else:
                users[nu] = hash_pw(np1)
                save("users.json", users)
                st.success("Account created. You can log in now.")


if not st.session_state.logged_in:
    login_page()
    st.stop()

# ── Data ─────────────────────────────────────────────────────────────────────
user = st.session_state.username
profile = load(ufile("profile.json"), {})
earnings = load(ufile("earnings.json"), [])
savings = load(ufile("savings.json"), [])
expenses = load(ufile("expense.json"), [])
limits = load(ufile("budget_limits.json"), {})
goals = load(ufile("savings_goals.json"), [])

earn_total = sum(r["amount"] for r in earnings)
save_total = sum(r["amount"] for r in savings)
exp_total = sum(r["amount"] for r in expenses)
pool = earn_total - save_total
balance = pool - exp_total

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    if profile.get("avatar") and os.path.exists(profile["avatar"]):
        st.image(profile["avatar"], width=90)
    st.markdown(f"**{user}**")
    with st.expander("Profile photo"):
        pic = st.file_uploader("Photo", type=IMG_TYPES, key="avatar_up", label_visibility="collapsed")
        if pic and st.button("Save photo"):
            profile["avatar"] = save_image(pic, "profile")
            save(ufile("profile.json"), profile)
            st.rerun()
    icons = {"Earnings": "💰", "Savings": "🏦", "Expenses": "🧾", "Charts": "📈",
             "Monthly breakdown": "📅", "Budget limits": "🚦", "Savings goals": "🎯",
             "Conversion rates": "💱", "Financial summary": "📊"}
    page = st.radio("Go to", list(icons), format_func=lambda p: f"{icons[p]}  {p}",
                    label_visibility="collapsed")
    st.divider()
    if st.button("Log out", use_container_width=True):
        st.session_state.logged_in, st.session_state.username = False, ""
        st.rerun()

# ── Header, flash message, alerts ────────────────────────────────────────────
if os.path.exists("assets/banner.png"):          # optional: drop a banner at assets/banner.png
    st.image("assets/banner.png", use_container_width=True)
st.markdown(f"""
<div class='hero'>
  <div style='display:flex;align-items:center'>
    <div class='bee'>🐝</div>
    <div><div class='hello'>Hello, {user}</div><div class='ttl'>{page}</div></div>
  </div>
  <div class='chip'>Balance<br><b>GHS {balance:,.2f}</b></div>
</div>
""", unsafe_allow_html=True)

if "flash" in st.session_state:
    st.toast(st.session_state.pop("flash"), icon="✅")

if limits and expenses:
    spent_by_cat = by_category(expenses).set_index("category")["amount"].to_dict()
    for cat, lim in limits.items():
        spent = spent_by_cat.get(cat, 0)
        pct = spent / lim * 100 if lim > 0 else 0
        if pct >= 100:
            note("bad", f"<b>{cat}</b>: budget exceeded. GHS {spent:.2f} of GHS {lim:.2f}")
        elif pct >= 80:
            note("warn", f"<b>{cat}</b>: {pct:.0f}% used. GHS {spent:.2f} of GHS {lim:.2f}")

if balance < 0:
    note("bad", f"Negative balance: GHS {balance:.2f}")
elif balance < 100:
    note("warn", f"Low balance: GHS {balance:.2f} remaining")

# ── Pages ────────────────────────────────────────────────────────────────────
if page == "Earnings":
    c1, c2 = st.columns(2)
    c1.metric("Total earnings", f"GHS {earn_total:,.2f}")
    c2.metric("Entries", len(earnings))

    with st.form("earnings_form", clear_on_submit=True):
        name = st.text_input("Description (optional)")
        source = st.selectbox("What did you earn from?", EARN_SOURCES)
        other_source = st.text_input("If you chose Others, say what")
        col_a, col_b = st.columns([2, 1])
        amount = col_a.number_input("Amount", min_value=0.0)
        currency = col_b.selectbox("Currency", CURRENCIES, index=0)
        month = st.selectbox("Month", MONTHS, index=datetime.now().month - 1)
        date = st.date_input("Date", value=datetime.now())

        if st.form_submit_button("Record earnings", use_container_width=True):
            if amount <= 0:
                st.error("Enter an amount greater than 0.")
            else:
                rate, err = 1.0, None
                if currency != "GHS":
                    rates, err = fetch_rates(currency)
                    if not err:
                        rate = rates.get("GHS")
                        if rate is None:
                            err = "No GHS rate found for " + currency + "."

                if err:
                    st.error(err)
                else:
                    ghs = amount * rate
                    final_source = (other_source.strip()
                                    if source == "Others" and other_source.strip()
                                    else source)
                    earnings.append({
                        "name": name,
                        "source": final_source,
                        "amount": ghs,                 # always in GHS, so totals still work
                        "original_amount": amount,
                        "currency": currency,
                        "month": month,
                        "date": date.strftime("%d %b %Y"),
                    })
                    save(ufile("earnings.json"), earnings)
                    flash_and_rerun(f"{amount:,.2f} {currency} recorded (GHS {ghs:,.2f})")

    if earnings:
        st.subheader("Earnings log")
        df = pd.DataFrame(earnings)
        df = df.assign(_d=pd.to_datetime(df["date"], format="%d %b %Y")).sort_values("_d", ascending=False)
        df = df.drop(columns="_d").rename(columns={"amount": "amount (GHS)"})
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.subheader("By source")
        src = pd.DataFrame(earnings)
        if "source" not in src:
            src["source"] = "Not set"
        src["source"] = src["source"].fillna("Not set")
        by_src = src.groupby("source")["amount"].sum().reset_index().sort_values("amount", ascending=False)
        st.dataframe(by_src.rename(columns={"source": "Source", "amount": "Amount (GHS)"}),
                     use_container_width=True, hide_index=True)
    else:
        st.info("No earnings yet. Record your first one above.")

elif page == "Savings":
    c1, c2 = st.columns(2)
    c1.metric("Total saved", f"GHS {save_total:,.2f}")
    c2.metric("Entries", len(savings))

    with st.form("savings_form", clear_on_submit=True):
        amount = st.number_input("Amount (GHS)", min_value=0.0)
        reason = st.text_input("What are you saving for?")
        date = st.date_input("Date", value=datetime.now())
        if st.form_submit_button("Record savings", use_container_width=True):
            if amount <= 0:
                st.error("Enter an amount greater than 0.")
            else:
                savings.append({"amount": amount, "Reason": reason, "date": date.strftime("%d %b %Y")})
                save(ufile("savings.json"), savings)
                flash_and_rerun(f"GHS {amount:.2f} saved")

    if savings:
        st.subheader("Savings log")
        st.dataframe(pd.DataFrame(savings), use_container_width=True, hide_index=True)
    else:
        st.info("No savings yet. Record your first one above.")

elif page == "Expenses":
    c1, c2 = st.columns(2)
    c1.metric("Total expenses", f"GHS {exp_total:,.2f}")
    c2.metric("Remaining balance", f"GHS {balance:,.2f}")

    with st.form("expense_form", clear_on_submit=True):
        amount = st.number_input("Amount (GHS)", min_value=0.0)
        date = st.date_input("Date", datetime.now())
        cat = st.selectbox("Category", CATEGORIES)
        receipt = st.file_uploader("Receipt photo (optional)", type=IMG_TYPES)
        if st.form_submit_button("Record expense", use_container_width=True):
            if amount <= 0:
                st.error("Enter an amount greater than 0.")
            elif amount > balance:
                st.error("Not enough funds. Your balance is GHS " f"{balance:.2f}.")
            else:
                spent = by_category(expenses).set_index("category")["amount"].get(cat, 0) if expenses else 0
                over = cat in limits and limits[cat] > 0 and spent + amount > limits[cat]
                expenses.append({"amount": amount, "date": date.strftime("%d %b %Y"), "category": cat,
                                 "receipt": save_image(receipt, "receipts") if receipt else None})
                save(ufile("expense.json"), expenses)
                flash_and_rerun(f"GHS {amount:.2f} recorded under {cat}"
                                + (" (over budget)" if over else ""))

    if expenses:
        st.subheader("Expenses log")
        df = pd.DataFrame(expenses)
        df["receipt"] = df["receipt"].notna() if "receipt" in df else False
        st.dataframe(df.rename(columns={"receipt": "has receipt"}), use_container_width=True, hide_index=True)

        st.subheader("By category")
        cs = by_category(expenses).sort_values("amount", ascending=False)
        st.dataframe(cs.rename(columns={"category": "Category", "amount": "Amount (GHS)"}),
                     use_container_width=True, hide_index=True)

        receipts = [r for r in expenses if r.get("receipt") and os.path.exists(r["receipt"])]
        if receipts:
            with st.expander(f"Receipts ({len(receipts)})"):
                cols = st.columns(3)
                for i, r in enumerate(receipts):
                    cols[i % 3].image(r["receipt"], use_container_width=True,
                                      caption=f"{r['category']} · GHS {r['amount']:.2f} · {r['date']}")
    else:
        st.info("No expenses yet.")

elif page == "Financial summary":
    c1, c2, c3 = st.columns(3)
    c1.metric("Earnings", f"GHS {earn_total:,.2f}")
    c2.metric("Savings", f"GHS {save_total:,.2f}")
    c3.metric("Expenses", f"GHS {exp_total:,.2f}")
    c1, c2, c3 = st.columns(3)
    c1.metric("Available pool", f"GHS {pool:,.2f}")
    c2.metric("Balance", f"GHS {balance:,.2f}")
    c3.metric("Savings rate", f"{(save_total / earn_total * 100) if earn_total else 0:.1f}%")
    st.metric("Expense rate", f"{(exp_total / earn_total * 100) if earn_total else 0:.1f}% of earnings")

elif page == "Charts":
    if not (earnings or savings or expenses):
        st.info("Add some records to see charts.")
    st.subheader("Earnings, savings and expenses")
    fig = go.Figure([go.Bar(name="Earnings", x=["Total"], y=[earn_total], marker_color=GREEN),
                     go.Bar(name="Savings", x=["Total"], y=[save_total], marker_color=HONEY),
                     go.Bar(name="Expenses", x=["Total"], y=[exp_total], marker_color=RED)])
    fig.update_layout(barmode="group")
    st.plotly_chart(tidy(fig), use_container_width=True)

    if expenses:
        st.subheader("Expenses by category")
        st.plotly_chart(tidy(px.pie(by_category(expenses), values="amount", names="category",
                                    color_discrete_sequence=px.colors.qualitative.Set3)),
                        use_container_width=True)
    for title, recs, color in [("Earnings over time", earnings, GREEN), ("Savings over time", savings, HONEY)]:
        if recs:
            st.subheader(title)
            d = pd.DataFrame(recs)
            d["date"] = pd.to_datetime(d["date"], format="%d %b %Y")
            st.plotly_chart(tidy(px.line(d.sort_values("date"), x="date", y="amount",
                                         color_discrete_sequence=[color])), use_container_width=True)

elif page == "Monthly breakdown":
    month = st.selectbox("Month", MONTHS, index=datetime.now().month - 1)
    abbr = month[:3].upper()
    m_earn = sum(r["amount"] for r in earnings if r.get("month") == month)
    m_sav = sum(r["amount"] for r in savings if abbr in r.get("date", "").upper())
    m_exp_recs = [r for r in expenses if abbr in r.get("date", "").upper()]
    m_exp = sum(r["amount"] for r in m_exp_recs)

    c1, c2 = st.columns(2)
    c1.metric("Earnings", f"GHS {m_earn:,.2f}")
    c2.metric("Savings", f"GHS {m_sav:,.2f}")
    c1, c2 = st.columns(2)
    c1.metric("Expenses", f"GHS {m_exp:,.2f}")
    c2.metric("Balance", f"GHS {m_earn - m_exp:,.2f}")

    if m_exp_recs:
        cs = by_category(m_exp_recs).sort_values("amount", ascending=False)
        st.plotly_chart(tidy(px.bar(cs, x="category", y="amount", color="category",
                                    color_discrete_sequence=px.colors.qualitative.Set3)),
                        use_container_width=True)
    else:
        st.info(f"No expenses recorded for {month}.")

elif page == "Budget limits":
    st.caption("Set a monthly spending limit per category. Use 0 for no limit.")
    with st.form("budget_form"):
        new = {c: st.number_input(f"{c} (GHS)", min_value=0.0, value=float(limits.get(c, 0.0)),
                                  key=f"budget_{c}") for c in CATEGORIES}
        if st.form_submit_button("Save limits", use_container_width=True):
            save(ufile("budget_limits.json"), new)
            flash_and_rerun("Budget limits saved")

    if limits and expenses:
        st.subheader("Status")
        spent_by_cat = by_category(expenses).set_index("category")["amount"].to_dict()
        for cat, lim in limits.items():
            if lim > 0:
                spent = spent_by_cat.get(cat, 0)
                pct = min(spent / lim * 100, 100)
                st.write(f"**{cat}**  ·  GHS {spent:.2f} of GHS {lim:.2f}")
                bar(pct, RED if pct >= 100 else HONEY if pct >= 80 else GREEN)

elif page == "Savings goals":
    with st.form("goal_form", clear_on_submit=True):
        name = st.text_input("Goal name (e.g. New laptop, Vacation)")
        target = st.number_input("Target amount (GHS)", min_value=0.0)
        date = st.date_input("Target date", value=datetime.now())
        photo = st.file_uploader("Goal photo (optional)", type=IMG_TYPES)
        if st.form_submit_button("Add goal", use_container_width=True):
            if name.strip() and target > 0:
                goals.append({"name": name, "target": target, "saved": 0,
                              "date": date.strftime("%d %b %Y"),
                              "image": save_image(photo, "goals") if photo else None})
                save(ufile("savings_goals.json"), goals)
                flash_and_rerun(f"Goal '{name}' added")
            else:
                st.error("Enter a name and a target above 0.")

    if not goals:
        st.info("No goals yet. Add one above.")
    for i, g in enumerate(goals):
        pct = min(g["saved"] / g["target"] * 100, 100) if g["target"] > 0 else 0
        color = GREEN if pct >= 100 else HONEY if pct >= 50 else "#5B9BD5"
        img_col, body_col = st.columns([1, 3])
        with img_col:
            if g.get("image") and os.path.exists(g["image"]):
                st.image(g["image"], use_container_width=True)
            else:
                st.markdown("<div style='font-size:48px;text-align:center'>🎯</div>", unsafe_allow_html=True)
        with body_col:
            st.markdown(f"**{g['name']}**  ·  due {g['date']}")
            st.caption(f"GHS {g['saved']:.2f} of GHS {g['target']:.2f}  ·  "
                       f"GHS {max(g['target'] - g['saved'], 0):.2f} to go")
            bar(pct, color)
        a, b, c = st.columns([3, 1, 1])
        add = a.number_input(f"Add to {g['name']}", min_value=0.0, key=f"goal_add_{i}",
                             label_visibility="collapsed")
        if b.button("Add", key=f"goal_btn_{i}", use_container_width=True):
            goals[i]["saved"] += add
            save(ufile("savings_goals.json"), goals)
            st.rerun()
        if c.button("Delete", key=f"goal_del_{i}", use_container_width=True):
            goals.pop(i)
            save(ufile("savings_goals.json"), goals)
            st.rerun()
        st.divider()

elif page == "Conversion rates":
    col1, col2 = st.columns(2)
    from_cur = col1.selectbox("From", CURRENCIES, index=0)
    to_cur = col2.selectbox("To", CURRENCIES, index=1)
    amount = st.number_input("Amount", min_value=0.0, value=1.0)

    if st.button("Convert", use_container_width=True):
        if from_cur == to_cur:
            st.warning("Choose two different currencies.")
        else:
            rates, err = fetch_rates(from_cur)
            if err:
                st.error(err)
            elif to_cur not in rates:
                st.error(f"No rate found for {to_cur}.")
            else:
                st.success(f"{amount:,.2f} {from_cur} = {amount * rates[to_cur]:,.2f} {to_cur}")
                st.caption(f"1 {from_cur} = {rates[to_cur]:.4f} {to_cur}")

# ── Clear data ───────────────────────────────────────────────────────────────
st.divider()
with st.expander("Danger zone"):
    sure = st.checkbox("I understand this deletes my earnings, savings and expenses")
    if st.button("Clear my data", disabled=not sure):
        for f in ("earnings.json", "savings.json", "expense.json"):
            save(ufile(f), [])
        flash_and_rerun("Data cleared")