import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="WaterWise — Water Conservation Tracker",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #0077b6, #00b4d8);
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        color: white;
        margin-bottom: 20px;
    }
    .metric-card {
        background: #f0f9ff;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #0077b6;
        margin-bottom: 10px;
    }
    .tip-card {
        background: #fff8e7;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #f4a261;
        margin-bottom: 10px;
    }
    .success-card {
        background: #e8f5e9;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #2e7d32;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- DATA STORAGE (Session) ----------------
if "usage_data" not in st.session_state:
    st.session_state.usage_data = pd.DataFrame(columns=["Date", "Liters", "Activity"])

if "leak_alerts" not in st.session_state:
    st.session_state.leak_alerts = []

# ---------------- HEADER ----------------
st.markdown("""
<div class="main-header">
    <h1>💧 WaterWise</h1>
    <p style="font-size:18px;">Pakistan's Smart Water Conservation Tracker</p>
</div>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR NAVIGATION ----------------
st.sidebar.image("https://img.icons8.com/fluency/96/water.png", width=80)
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to:",
    ["🏠 Home", "📊 Usage Tracker", "🔍 Leak Detection",
     "🌧️ Rainwater Calculator", "🏆 Community Challenges",
     "🏛️ Government Schemes", "📚 Urdu Education"]
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Tip:** Har din paani track karein aur save karein!")

# ================= HOME =================
if page == "🏠 Home":
    st.header("🏠 Welcome to WaterWise")
    st.write("Pakistan mein paani ki kami ek bara masla hai. WaterWise aapki madad karta hai paani bachane mein.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🇵🇰 Pakistan Water Stress", "High", "Critical")
    with col2:
        st.metric("💧 Daily Wastage (avg)", "40%", "-")
    with col3:
        st.metric("🌧️ Rainwater Potential", "Largest", "-")

    st.markdown("---")
    st.subheader("🎯 What Can You Do?")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### 📊 Track\nApna daily paani track karein")
    with c2:
        st.markdown("### 🔍 Detect\nLeakage ka pata lagayein")
    with c3:
        st.markdown("### 🌧️ Harvest\nBarish ka paani bachayein")

    st.markdown("---")
    st.subheader("🚀 Quick Stats")

    total = st.session_state.usage_data["Liters"].sum() if not st.session_state.usage_data.empty else 0
    entries = len(st.session_state.usage_data)

    a, b, c = st.columns(3)
    a.metric("Total Usage Recorded", f"{total:.1f} L")
    b.metric("Entries Logged", entries)
    c.metric("Active Alerts", len(st.session_state.leak_alerts))

# ================= USAGE TRACKER =================
elif page == "📊 Usage Tracker":
    st.header("📊 Daily Water Usage Tracker")

    with st.form("usage_form"):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("Date", datetime.now())
            liters = st.number_input("Water Used (Liters)", min_value=1, value=100)
        with col2:
            activity = st.selectbox(
                "Activity",
                ["Drinking", "Cooking", "Bathing", "Washing", "Cleaning", "Gardening", "Other"]
            )
        submitted = st.form_submit_button("➕ Add Entry")

        if submitted:
            new_row = pd.DataFrame({
                "Date": [date],
                "Liters": [liters],
                "Activity": [activity]
            })
            st.session_state.usage_data = pd.concat(
                [st.session_state.usage_data, new_row], ignore_index=True
            )
            st.success(f"✅ {liters}L ({activity}) added!")

    st.markdown("---")

    if not st.session_state.usage_data.empty:
        df = st.session_state.usage_data.copy()
        df["Date"] = pd.to_datetime(df["Date"])

        # Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Total", f"{df['Liters'].sum():.0f} L")
        col2.metric("Average/Day", f"{df['Liters'].mean():.1f} L")
        col3.metric("Entries", len(df))

        # Chart
        st.subheader("📈 Usage Trend")
        daily = df.groupby("Date")["Liters"].sum().reset_index()
        fig = px.line(daily, x="Date", y="Liters", markers=True,
                      title="Daily Water Consumption")
        fig.update_traces(line_color="#0077b6", line_width=3)
        st.plotly_chart(fig, use_container_width=True)

        # Activity breakdown
        st.subheader("🥧 Usage by Activity")
        act = df.groupby("Activity")["Liters"].sum().reset_index()
        fig2 = px.pie(act, names="Activity", values="Liters", hole=0.4)
        st.plotly_chart(fig2, use_container_width=True)

        # Table
        st.subheader("📋 All Entries")
        st.dataframe(df.sort_values("Date", ascending=False), use_container_width=True)

        if st.button("🗑️ Clear All Data"):
            st.session_state.usage_data = pd.DataFrame(columns=["Date", "Liters", "Activity"])
            st.rerun()
    else:
        st.info("👆 Koi entry add karein shuru karne ke liye.")

# ================= LEAK DETECTION =================
elif page == "🔍 Leak Detection":
    st.header("🔍 Leak Detection System")
    st.write("Meter readings daalein — app check karega ke leak hai ya nahi.")

    with st.form("leak_form"):
        col1, col2 = st.columns(2)
        with col1:
            night_reading_1 = st.number_input("Night Reading (11 PM) — Liter", min_value=0.0, value=1000.0)
        with col2:
            night_reading_2 = st.number_input("Morning Reading (5 AM) — Liter", min_value=0.0, value=1002.0)
        submitted = st.form_submit_button("🔍 Check for Leak")

        if submitted:
            diff = night_reading_2 - night_reading_1
            if diff > 5:
                st.error(f"🚨 **Possible Leak Detected!** Raat mein {diff:.1f} liter paani use hua jab koi use nahi karta.")
                st.session_state.leak_alerts.append({
                    "Time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Difference": diff
                })
            elif diff > 0:
                st.warning(f"⚠️ Thoda unusual hai ({diff:.1f}L). Monitor karein.")
            else:
                st.success("✅ Koi leak nahi mila. Sab theek hai!")

    st.markdown("---")
    st.subheader("📋 Alert History")
    if st.session_state.leak_alerts:
        st.dataframe(pd.DataFrame(st.session_state.leak_alerts), use_container_width=True)
    else:
        st.info("Abhi tak koi alert nahi.")

    st.markdown("---")
    st.subheader("💡 Common Leak Sources")
    st.markdown("""
    - 🚰 **Taps** — Chhoti drip bhi 20L/din waste karti hai
    - 🚽 **Toilet tanks** — Flapper valve leak
    - 🚿 **Showerheads** — O-ring damage
    - 🛢️ **Water tanks** — Cracks
    - 🌱 **Garden pipes** — Underground leaks
    """)

# ================= RAINWATER CALCULATOR =================
elif page == "🌧️ Rainwater Calculator":
    st.header("🌧️ Rainwater Harvesting Calculator")

    st.write("Apni chhat ka area aur shehar daalein — potential calculate karein.")

    city_rainfall = {
        "Karachi": 200, "Lahore": 600, "Islamabad": 1200,
        "Peshawar": 400, "Quetta": 250, "Multan": 180,
        "Faisalabad": 350, "Rawalpindi": 1100
    }

    with st.form("rain_form"):
        col1, col2 = st.columns(2)
        with col1:
            city = st.selectbox("City", list(city_rainfall.keys()))
            area = st.number_input("Roof Area (sq. meters)", min_value=10.0, value=100.0)
        with col2:
            roof_type = st.selectbox("Roof Type", ["Concrete", "Metal", "Tiled"])
            efficiency_map = {"Concrete": 0.85, "Metal": 0.9, "Tiled": 0.75}
        submitted = st.form_submit_button("💧 Calculate")

        if submitted:
            rainfall = city_rainfall[city]
            efficiency = efficiency_map[roof_type]
            # Rainfall (mm) × Area (m²) × efficiency = Liters
            potential = rainfall * area * efficiency

            st.success(f"💧 Aapki chhat se saal mein **{potential:,.0f} liters** barish ka paani collect ho sakta hai!")

            col1, col2, col3 = st.columns(3)
            col1.metric("Annual Rainfall", f"{rainfall} mm")
            col2.metric("Roof Area", f"{area} m²")
            col3.metric("Efficiency", f"{efficiency*100:.0f}%")

            # Visual
            months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                      "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            # Monsoon-heavy distribution
            pattern = [0.03, 0.03, 0.05, 0.05, 0.04, 0.08,
                       0.20, 0.22, 0.12, 0.06, 0.06, 0.06]
            monthly = [potential * p for p in pattern]
            fig = px.bar(x=months, y=monthly, labels={"x": "Month", "y": "Liters"},
                         title="Monthly Rainwater Potential")
            fig.update_traces(marker_color="#00b4d8")
            st.plotly_chart(fig, use_container_width=True)

            st.info(f"💡 **Tip:** Ye paani {potential/200:.0f} logon ki 1 saal ki drinking need cover kar sakta hai (2L/day).")

# ================= COMMUNITY CHALLENGES =================
elif page == "🏆 Community Challenges":
    st.header("🏆 Community Savings Challenge")

    st.write("Apne mohalle ki teams ko compete karao — kaun sabse zyada paani bachata hai!")

    # Sample leaderboard
    leaderboard = pd.DataFrame({
        "Team": ["Green Society", "Blue Block", "Aqua Homes", "Eco Warriors", "Water Savers"],
        "Saved (Liters)": [45000, 38000, 32000, 27000, 21000],
        "Members": [45, 38, 30, 25, 20]
    })

    st.subheader("🥇 Live Leaderboard")
    leaderboard["Per Member"] = leaderboard["Saved (Liters)"] / leaderboard["Members"]

    fig = px.bar(
        leaderboard.sort_values("Saved (Liters)"),
        x="Saved (Liters)", y="Team", orientation="h",
        color="Saved (Liters)", color_continuous_scale="Blues",
        title="Water Saved by Each Team"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(leaderboard, use_container_width=True)

    st.markdown("---")
    st.subheader("➕ Join a Challenge")

    with st.form("challenge_form"):
        name = st.text_input("Your Name")
        team = st.selectbox("Team", leaderboard["Team"].tolist())
        saved = st.number_input("Water You Saved Today (Liters)", min_value=1, value=10)
        if st.form_submit_button("Join"):
            st.success(f"🎉 Shabash {name}! Aap ne {team} ke liye {saved}L save kiye!")

    st.markdown("---")
    st.subheader("🎖️ Badges")
    st.markdown("""
    - 🥉 **Beginner Saver** — 100L saved
    - 🥈 **Water Warrior** — 1,000L saved
    - 🥇 **Aqua Champion** — 10,000L saved
    - 💎 **Water Legend** — 100,000L saved
    """)

# ================= GOVERNMENT SCHEMES =================
elif page == "🏛️ Government Schemes":
    st.header("🏛️ Government Schemes & Subsidies")

    schemes = [
        {
            "name": "Pakistan Water Conservation Program",
            "authority": "Ministry of Water Resources",
            "benefit": "Rainwater harvesting par subsidy",
            "eligibility": "Households with 100+ sq.m roof"
        },
        {
            "name": "Punjab Clean Water Initiative",
            "authority": "Punjab Government",
            "benefit": "Water filter aur tank subsidy",
            "eligibility": "Punjab residents"
        },
        {
            "name": "Sindh Water Sector Improvement",
            "authority": "Sindh Government",
            "benefit": "Irrigation efficiency grants",
            "eligibility": "Farmers"
        },
        {
            "name": "KP Drinking Water Scheme",
            "authority": "KP Government",
            "benefit": "Free water testing + storage",
            "eligibility": "Rural KP households"
        },
    ]

    for s in schemes:
        with st.expander(f"🏛️ {s['name']}"):
            st.write(f"**Authority:** {s['authority']}")
            st.write(f"**Benefit:** {s['benefit']}")
            st.write(f"**Eligibility:** {s['eligibility']}")
            st.button(f"Apply Now — {s['name']}", key=s['name'])

    st.markdown("---")
    st.info("📞 **Helpline:** 1093 (Pakistan Water Info Line)")

# ================= URDU EDUCATION =================
elif page == "📚 Urdu Education":
    st.header("📚 Urdu mein Paani Bachane ki Taleem")

    tips = [
        {
            "title": "🚰 Nal ko band rakhein",
            "content": "Brush karte waqt ya bartan dhote waqt nal band rakhein. Is se 6 liter per minute bachta hai."
        },
        {
            "title": "🚿 Chhota shower lein",
            "content": "5 minute ka shower 40 liter paani use karta hai. 10 minute ka 80 liter. Chhota shower = zyada saving."
        },
        {
            "title": "🚽 Toilet leak check",
            "content": "Toilet tank mein food color daalein. Agar 15 minute mein bowl mein color aa jaye, to leak hai."
        },
        {
            "title": "🌱 Subah ya shaam ko paani dein",
            "content": "Plants ko subah ya shaam ko paani dein — dopahar mein paani evaporation se zaya hota hai."
        },
        {
            "title": "🌧️ Barish ka paani jama karein",
            "content": "Chhat se girne wala paani drum ya tank mein collect karein. Yeh gardening ke liye best hai."
        },
        {
            "title": "🧺 Kapre poore load mein dhoyein",
            "content": "Adhoora load wash karne se paani zaya hota hai. Washing machine poora bhar kar chalayein."
        },
        {
            "title": "🍽️ Bartan bhigone ke baad dhoyein",
            "content": "Bartan ko 10 minute bhigone se saaf karna aasan hota hai aur kam paani lagta hai."
        },
        {
            "title": "🔧 Leak turant theek karein",
            "content": "Ek chhoti drip bhi 20 liter per din = 7,300 liter per saal waste karti hai!"
        },
    ]

    st.subheader("💡 8 Aasan Tips")
    for tip in tips:
        st.markdown(f"""
        <div class="tip-card">
            <h4>{tip['title']}</h4>
            <p>{tip['content']}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🎥 Video / Reading Resources")
    st.markdown("""
    - 📺 [Pakistan Water Crisis Explained](https://www.youtube.com/results?search_query=pakistan+water+crisis+urdu)
    - 📖 [PCRWR Official Website](https://www.pcrwr.gov.pk/)
    - 📱 [UNDP Pakistan Water Projects](https://www.pk.undp.org/)
    """)

# ---------------- FOOTER ----------------
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#666; padding:10px;">
    💧 <b>WaterWise</b> — Save Water, Save Pakistan 🇵🇰<br>
    Made with Streamlit
</div>
""", unsafe_allow_html=True)
