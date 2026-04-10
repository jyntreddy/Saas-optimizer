"""SaaS Score - Gamification dashboard with achievements and referrals"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import sys
sys.path.append('..')
from utils.api import make_request
from utils.session import require_auth

require_auth()

st.title("🏆 Your SaaS Score")
st.markdown("Track your optimization journey and unlock achievements")

# Get score
score_data = make_request("GET", "/gamification/score")

if score_data:
    # Main score display
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        score = score_data.get('score', 0)
        level = score_data.get('level', 'Novice')
        
        # Score gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': f"Level: {level}"},
            delta={'reference': 800},
            gauge={
                'axis': {'range': [None, 1000]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 250], 'color': "lightgray"},
                    {'range': [250, 500], 'color': "gray"},
                    {'range': [500, 750], 'color': "lightblue"},
                    {'range': [750, 1000], 'color': "royalblue"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 900
                }
            }
        ))
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.metric("Total Savings", f"${score_data.get('total_savings', 0):.2f}")
        st.metric("Subscriptions", score_data.get('subscriptions_tracked', 0))
    
    with col3:
        st.metric("Streak", f"{score_data.get('streak_days', 0)} days")
        percentile = score_data.get('rank_percentile', 0)
        if percentile:
            st.metric("Rank", f"Top {percentile:.0f}%")

# Level progression
st.subheader("📈 Level Progression")

levels = {
    "Novice": 0,
    "Explorer": 100,
    "Optimizer": 250,
    "Expert": 500,
    "Master": 750,
    "Legend": 1000
}

current_score = score_data.get('score', 0) if score_data else 0
current_level = score_data.get('level', 'Novice') if score_data else 'Novice'

# Find next level
next_level = None
for level_name, threshold in levels.items():
    if threshold > current_score:
        next_level = level_name
        next_threshold = threshold
        break

if next_level:
    progress_pct = (current_score / next_threshold) * 100
    st.progress(progress_pct / 100)
    st.write(f"**{progress_pct:.0f}%** to {next_level} ({next_threshold - current_score} points needed)")
else:
    st.success("🎉 Maximum level reached!")

# Achievements
st.subheader("🎖️ Achievements")

achievements = make_request("GET", "/gamification/achievements")
unlocked = make_request("GET", "/gamification/achievements/unlocked")

unlocked_ids = {ua['achievement']['id'] for ua in unlocked} if unlocked else set()

if achievements:
    # Group by tier
    tiers = {}
    for ach in achievements:
        tier = ach.get('tier', 'common')
        if tier not in tiers:
            tiers[tier] = []
        tiers[tier].append(ach)
    
    for tier_name in ['legendary', 'epic', 'rare', 'common']:
        if tier_name in tiers:
            st.write(f"**{tier_name.upper()}**")
            
            cols = st.columns(3)
            for idx, ach in enumerate(tiers[tier_name]):
                with cols[idx % 3]:
                    is_unlocked = ach['id'] in unlocked_ids
                    
                    with st.container():
                        if is_unlocked:
                            st.success(f"{ach.get('icon', '🏆')} **{ach['name']}**")
                        else:
                            st.info(f"🔒 **{ach['name']}**")
                        
                        st.caption(ach.get('description', ''))
                        st.write(f"{ach.get('points', 0)} points")

# Referral program
st.subheader("🎁 Referral Program")

col1, col2 = st.columns(2)

with col1:
    if st.button("Generate Referral Link"):
        result = make_request("POST", "/gamification/referral/create")
        
        if result:
            st.success("✅ Referral link created!")
            st.code(f"https://saas-optimizer.com{result['referral_url']}", language=None)
            st.info("Share this link to earn 20 points per signup!")

with col2:
    st.info("""
    **Earn Points:**
    - 🔗 Each click: 1 point
    - 📝 Each signup: 20 points  
    - 💰 Conversion: 50 points
    
    **Rewards:**
    - 5 referrals: Premium badge
    - 10 referrals: Free month
    - 25 referrals: Lifetime free!
    """)

# Savings report
st.subheader("📊 Share Your Wins")

col1, col2 = st.columns(2)

with col1:
    period = st.selectbox("Report Period", ["Monthly", "Quarterly", "Yearly"])
    days_map = {"Monthly": 30, "Quarterly": 90, "Yearly": 365}
    
    if st.button("Generate Shareable Report"):
        result = make_request(
            "POST",
            f"/gamification/reports/generate",
            params={"period_days": days_map[period]}
        )
        
        if result:
            st.success(f"✅ Report generated! Saved ${result['total_saved']:.2f}")
            st.code(f"https://saas-optimizer.com{result['share_url']}", language=None)
            
            st.balloons()

with col2:
    st.image("https://via.placeholder.com/300x200?text=Savings+Report", use_container_width=True)
    st.caption("Share your savings on social media!")

# Leaderboard
st.subheader("🏅 Leaderboard")

st.info("Coming soon: See how you rank against other optimizers!")

# Tips for earning points
with st.expander("💡 How to Earn Points"):
    st.markdown("""
    - **Track subscriptions**: 10 points each
    - **Savings**: 1 point per $10 saved
    - **Win negotiation**: 50 points
    - **Daily login streak**: 5 points/day
    - **Referral**: 20 points per signup
    - **Complete profile**: 25 points
    - **Link bank account**: 30 points
    - **Find duplicate**: 15 points
    - **Cancel unused**: 20 points
    """)
