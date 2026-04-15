import streamlit as st
import pandas as pd
from datetime import date
import io
import requests
import base64
from datetime import datetime
import json



# -----------------------
# OPTIONAL PDF IMPORTS
# -----------------------
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def get_access_token(consumer_key, consumer_secret):
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    response = requests.get(url, auth=(consumer_key, consumer_secret))

    st.write("STATUS CODE:", response.status_code)
    st.write("RESPONSE TEXT:", response.text)

    try:
        return response.json().get("access_token")
    except:
        return None

import requests
import base64
from datetime import datetime

def get_access_token(consumer_key, consumer_secret):
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=(consumer_key, consumer_secret))
    return response.json().get("access_token")


def stk_push(phone, amount, consumer_key, consumer_secret):

    import requests, base64
    from datetime import datetime

    token_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    r = requests.get(token_url, auth=(consumer_key, consumer_secret))
    access_token = r.json().get("access_token")

    shortcode = "174379"
    passkey = "bfb279f9aa9bdbcf6b7f0f399d1a7c9c"

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    password = base64.b64encode(
        (shortcode + passkey + timestamp).encode()
    ).decode()

    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": shortcode,
        "PhoneNumber": phone,
        "CallBackURL": "https://webhook.site/test",
        "AccountReference": "Test",
        "TransactionDesc": "Test"
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

    response = requests.post(url, json=payload, headers=headers)

    return response.json()
# -----------------------
# SUBSCRIPTION SYSTEM
# -----------------------
if "subscribed" not in st.session_state:
    st.session_state.subscribed = False

if "report_count" not in st.session_state:
    st.session_state.report_count = 0

TRIAL_LIMIT = 2

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = None

if "subscribed" not in st.session_state:
    st.session_state.subscribed = False

if "report_count" not in st.session_state:
    st.session_state.report_count = 0
# -----------------------
# SIMPLE LOGIN SYSTEM
# -----------------------
def load_users():
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f)
def signup():
    st.title("📝 Sign Up")

    new_user = st.text_input("Create Username")
    new_pass = st.text_input("Create Password", type="password")

    if st.button("Sign Up"):
        users = load_users()

        if new_user in users:
            st.error("User already exists")
        else:
            users[new_user] = { "password": new_pass,"subscribed": False}
            save_users(users)
            st.success("Account created! Please login.")       
def login():
    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        users = load_users()

        if username in users and users[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.subscribed = users[username]["subscribed"]
        else:
            st.error("Invalid credentials")

def logout():
    st.session_state.logged_in = False
if not st.session_state.logged_in:
    option = st.radio("Choose Option", ["Login", "Sign Up"])

    if option == "Login":
        login()
    else:
        signup()

    st.stop()

# -----------------------
# SIDEBAR NAVIGATION
# -----------------------
st.sidebar.subheader("💎 Subscription")

if st.session_state.subscribed:
    st.sidebar.success("Premium Active 💎")
else:
    st.sidebar.warning("Free Plan")
phone = st.text_input("Enter MPesa number (2547...)")

if st.button("Pay KES 200 via MPesa"):
    if phone:
        result = stk_push(
            phone=phone,
            amount=200,
            consumer_key="ATiwKlvLGuJi3H6cGbeenxnJJNygm891ebNWH3EZS9nrcyzd",
            consumer_secret="C2v1yuS4DckRizJgfgOMN2DLGgeYGkaZ5znMsQgvSSBqgGERvongukaoJHLJuUQI")

        st.write(result)
    else:
        st.warning("Enter phone number first")

        # simulate payment success
        users = load_users()
        users[st.session_state.username]["subscribed"] = True
        save_users(users)

        st.session_state.subscribed = True

        st.sidebar.success("✅ Payment successful! Premium activated 💎")
        
st.sidebar.title("🌸 Health Dashboard")
page = st.sidebar.radio("Navigate", ["Tracker", "History", "Report"])
if st.sidebar.button("Logout"):
    logout()

# -----------------------
# MAIN TITLE
# -----------------------
st.markdown(
    "<h1 style='text-align: center;'>🌸 Women's Health Companion</h1>",
    unsafe_allow_html=True
)

st.markdown("### Track symptoms, understand patterns, and prepare for doctor visits")

# -----------------------
# CONDITION SELECTOR
# -----------------------
condition = st.selectbox(
    "Select Condition Focus",
    ["General", "Endometriosis", "PCOS"]
)

st.write("Track your symptoms and generate reports for your doctor.")

# =========================================================
# TRACKER PAGE
# =========================================================
if page == "Tracker":

    st.header("📝 Daily Symptom Entry")

    col1, col2 = st.columns(2)

    with col1:
        entry_date = st.date_input("Date", value=date.today())
        pain_level = st.slider("Pain Level (0-10)", 0, 10, 5)
        cycle_day = st.number_input("Cycle Day", 1, 35, 1)

    with col2:
        symptoms = st.text_area("Symptoms")
        triggers = st.text_input("Triggers")

    if st.button("💾 Save Entry", key="save_btn"):

        new_data = pd.DataFrame({
            "Date": [entry_date],
            "Pain": [pain_level],
            "Symptoms": [symptoms],
            "Cycle": [cycle_day],
            "Triggers": [triggers]
        })

        try:
            old = pd.read_csv("health_data.csv")
            updated = pd.concat([old, new_data], ignore_index=True)
        except FileNotFoundError:
            updated = new_data

        updated.to_csv("health_data.csv", index=False)
        st.success("Saved successfully!")

# =========================================================
# HISTORY PAGE
# =========================================================
elif page == "History":

    st.header("📊 Your Health History")

    try:
        data = pd.read_csv("health_data.csv")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Avg Pain", round(data["Pain"].mean(), 2))

        with col2:
            st.metric("Max Pain", int(data["Pain"].max()))

        with col3:
            st.metric("Entries", len(data))

        st.dataframe(data)
        st.line_chart(data["Pain"])

    except FileNotFoundError:
        st.info("No data yet. Start adding entries.")

# =========================================================
# REPORT PAGE
# =========================================================
elif page == "Report":

    st.header("📄 Doctor Report")

    # 🔒 Check trial limit BEFORE generating report
    if not st.session_state.subscribed and st.session_state.report_count >= TRIAL_LIMIT:
        st.warning("🔒 Free trial ended. Please upgrade to continue using reports.")
        st.stop()
        
user = st.session_state.username
users = load_users()

if not users[user]["subscribed"]:
    st.warning("🔒 You need to pay to access reports")
    st.stop()
if st.button("Generate Report", key="report_btn"):

    st.session_state.report_count += 1
    st.success(f"Reports used: {st.session_state.report_count}/{TRIAL_LIMIT}")

    try:
        data = pd.read_csv("health_data.csv")

        avg = data["Pain"].mean()
        mx = data["Pain"].max()
        recent = data.tail(5)

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Average Pain", round(avg, 2))

        with col2:
            st.metric("Maximum Pain", mx)

        cycle_analysis = data.groupby("Cycle")["Pain"].mean()

        worst_cycle_day = cycle_analysis.idxmax()
        worst_pain_value = cycle_analysis.max()

        st.subheader("📊 Pain Pattern Insight")
        st.write(f"Most painful cycle day: Day {worst_cycle_day}")
        st.write(f"Average pain on that day: {round(worst_pain_value, 2)}")

        high_pain_days = cycle_analysis[
            cycle_analysis >= cycle_analysis.mean() + 1
        ].index.tolist()

        st.subheader("🔮 Prediction")

        if len(high_pain_days) > 0:
            st.warning(f"Possible high pain days: {high_pain_days}")
        else:
            st.success("No strong pattern detected.")

        pain_level = avg

        if pain_level >= 7:
            severity = "high"
            risk = "significant impact"
        elif pain_level >= 4:
            severity = "moderate"
            risk = "recurring discomfort"
        else:
            severity = "mild"
            risk = "manageable levels"

        ai_summary = f"""
The patient reports {severity} pain levels with an average score of {round(pain_level,2)}.

Recent symptoms: {", ".join(recent["Symptoms"].astype(str).head(3))}.

This suggests {risk}.
"""

        st.subheader("🧠 AI Summary")
        st.write(ai_summary)

        # -----------------------
        # TEXT DOWNLOAD REPORT
        # -----------------------
        report_text = f"""
WOMEN'S HEALTH REPORT

Average Pain: {round(avg,2)}
Maximum Pain: {mx}

Most painful cycle day: {worst_cycle_day}
Pain level: {round(worst_pain_value,2)}
"""

        buffer = io.BytesIO()
        buffer.write(report_text.encode("utf-8"))
        buffer.seek(0)

        st.download_button(
            label="📥 Download Report",
            data=buffer,
            file_name="health_report.txt",
            mime="text/plain"
        )

        # -----------------------
        # QUESTIONS
        # -----------------------
        st.subheader("❓ Suggested Questions")

        if condition == "Endometriosis":
            questions = [
                "Could this be endometriosis?",
                "Should I get a laparoscopy?",
                "Why is pain worse during periods?",
                "What treatments exist?"
            ]

        elif condition == "PCOS":
            questions = [
                "Do my symptoms match PCOS?",
                "Should I check hormones?",
                "Do I need an ultrasound?",
                "How can I manage cycles?"
            ]

        else:
            questions = [
                "What could be causing my symptoms?",
                "What tests should I do?",
                "Should I see a specialist?",
                "How can I manage pain?"
            ]

        for q in questions:
            st.write("-", q)

        # -----------------------
        # FLARE-UP ALERT
        # -----------------------
        st.subheader("🚨 Flare-Up Risk")

        if len(high_pain_days) > 0:
            st.warning(f"Possible flare-up days: {high_pain_days}")
        else:
            st.success("No strong flare-up pattern detected.")

        # -----------------------
        # PDF GENERATION
        # -----------------------
        pdf_file = "report.pdf"

        doc = SimpleDocTemplate(pdf_file)
        styles = getSampleStyleSheet()

        content = []

        content.append(Paragraph("Women's Health Report", styles["Title"]))
        content.append(Spacer(1, 12))

        content.append(Paragraph(f"Average Pain: {round(avg,2)}", styles["Normal"]))
        content.append(Paragraph(f"Maximum Pain: {mx}", styles["Normal"]))

        content.append(Spacer(1, 12))

        content.append(Paragraph("Recent Symptoms:", styles["Heading2"]))
        for s in recent["Symptoms"]:
            content.append(Paragraph(str(s), styles["Normal"]))

        content.append(Spacer(1, 12))

        content.append(Paragraph("Suggested Questions:", styles["Heading2"]))
        for q in questions:
            content.append(Paragraph(q, styles["Normal"]))

        doc.build(content)

        with open(pdf_file, "rb") as f:
            st.download_button(
                label="📥 Download PDF",
                data=f,
                file_name="health_report.pdf",
                mime="application/pdf"
            )

    except Exception as e:
        st.error(f"Error: {e}")

    