import streamlit as st
import pandas as pd
from datetime import date

# -----------------------
# OPTIONAL PDF IMPORTS
# -----------------------
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# -----------------------
# SIDEBAR NAVIGATION
# -----------------------
st.sidebar.title("🌸 Health Dashboard")
page = st.sidebar.radio("Navigate", ["Tracker", "History", "Report"])

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
    st.info("This report summarizes your symptoms for clinical discussion.")

    if st.button("Generate Report", key="report_btn"):

        try:
            data = pd.read_csv("health_data.csv")

            # -----------------------
            # BASIC STATS
            # -----------------------
            avg = data["Pain"].mean()
            mx = data["Pain"].max()
            recent = data.tail(5)

            # -----------------------
            # METRICS
            # -----------------------
            col1, col2 = st.columns(2)

            with col1:
                st.metric("Average Pain", round(avg, 2))

            with col2:
                st.metric("Maximum Pain", mx)

            # -----------------------
            # CYCLE ANALYSIS
            # -----------------------
            cycle_analysis = data.groupby("Cycle")["Pain"].mean()

            worst_cycle_day = cycle_analysis.idxmax()
            worst_pain_value = cycle_analysis.max()

            st.subheader("📊 Pain Pattern Insight")
            st.write(f"Most painful cycle day: Day {worst_cycle_day}")
            st.write(f"Average pain on that day: {round(worst_pain_value, 2)}")

            # -----------------------
            # PREDICTION
            # -----------------------
            high_pain_days = cycle_analysis[
                cycle_analysis >= cycle_analysis.mean() + 1
            ].index.tolist()

            high_risk_days = cycle_analysis[
                cycle_analysis >= cycle_analysis.mean() + 1.5
            ].index.tolist()

            st.subheader("🔮 Prediction")

            if len(high_pain_days) > 0:
                st.warning(f"Possible high pain days: {high_pain_days}")
            else:
                st.success("No strong recurring pattern detected.")

            # -----------------------
            # AI SUMMARY
            # -----------------------
            pain_level = avg

            if pain_level >= 7:
                severity = "high"
                risk = "significant pain impact"
            elif pain_level >= 4:
                severity = "moderate"
                risk = "recurring discomfort"
            else:
                severity = "mild"
                risk = "manageable pain levels"

            ai_summary = f"""
The patient reports {severity} pain levels with an average score of {round(pain_level,2)}.

Recent symptoms include: {", ".join(recent["Symptoms"].astype(str).head(3))}.

This suggests {risk}.

This summary is generated from self-reported data.
"""

            st.subheader("🧠 AI Summary")
            st.write(ai_summary)

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
        # BUILD PDF
            doc.build(content)
 # DOWNLOAD BUTTON
            with open(pdf_file, "rb") as f:
                st.download_button(label="📥 Download Report",data=f,file_name="health_report.pdf",mime="application/pdf")

            if len(high_risk_days) > 0:
                st.warning(f"Possible flare-up days: {high_risk_days}")
            else:
                st.success("No strong flare-up pattern detected.")

        except Exception as e:
            st.error(f"Error: {e}")