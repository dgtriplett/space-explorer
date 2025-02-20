import streamlit as st
import pandas as pd
import random
from databricks import sql
from databricks.sdk.core import Config
import os

# Function to execute SQL queries
def sqlQuery(query: str) -> pd.DataFrame:
    cfg = Config()
    with sql.connect(
        server_hostname=cfg.host,
        http_path=f"/sql/1.0/warehouses/{os.getenv('DATABRICKS_WAREHOUSE_ID')}",
        credentials_provider=lambda: cfg.authenticate
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall_arrow().to_pandas()

# Databricks setup
catalog = "drew_triplett"
schema = "space_explorer"
game_table = "galactic_survival_game"
leaderboard_table = "galactic_survival_leaderboard"

# UI Theming
st.set_page_config(page_title="Galactic Survival", layout="centered", page_icon="🚀")

# Custom CSS for Styling
st.markdown("""
    <style>
    body {
        background-color: #0d0d0d;
        color: white;
        font-family: 'Arial', sans-serif;
    }
    .big-title {
        font-size: 36px;
        font-weight: bold;
        text-align: center;
        color: #FFD700;
    }
    .stButton>button {
        background-color: #4682B4;
        color: white;
        font-size: 18px;
        padding: 10px;
        border-radius: 5px;
    }
    .stButton>button:hover {
        background-color: #4169E1;
    }
    </style>
""", unsafe_allow_html=True)

# Game UI Title
st.markdown('<p class="big-title">🚀 Galactic Survival: A Space Explorer\'s Journey \U0001F30C</p>', unsafe_allow_html=True)

# Sidebar Information
st.sidebar.header("Game Information 🪐")
st.sidebar.write("""
    - **Goal**: Survive while exploring planets.
    - **Actions**: Mine, Rest, Travel, Trade.
    - **Challenges**: Asteroid fields, alien attacks, system failures.
""")

# Fetch game state
def get_game_state():
    query = f"SELECT * FROM {catalog}.{schema}.{game_table}"
    df = sqlQuery(query)
    return df.to_dict('records')[0] if not df.empty else None

# Fetch leaderboard
def get_leaderboard():
    query = f"SELECT * FROM {catalog}.{schema}.{leaderboard_table} ORDER BY days_survived DESC LIMIT 5"
    return sqlQuery(query)

# Update game state
def update_game_state(state):
    query = f"""
    MERGE INTO {catalog}.{schema}.{game_table} t
    USING (SELECT 
        '{state["player_name"]}' as player_name,
        {state["credits"]} as credits,
        {state["oxygen"]} as oxygen,
        {state["fuel"]} as fuel,
        {state["health"]} as health,
        {state["distance_traveled"]} as distance_traveled,
        {state["days_survived"]} as days_survived,
        {state["current_planet"]} as current_planet
    ) s
    ON t.player_name = s.player_name
    WHEN MATCHED THEN UPDATE SET
        t.credits = s.credits,
        t.oxygen = s.oxygen,
        t.fuel = s.fuel,
        t.health = s.health,
        t.distance_traveled = s.distance_traveled,
        t.days_survived = s.days_survived,
        t.current_planet = s.current_planet,
        t.last_updated = CURRENT_TIMESTAMP()
    WHEN NOT MATCHED THEN INSERT
        (player_name, credits, oxygen, fuel, health, distance_traveled, days_survived, current_planet, last_updated)
    VALUES
        (s.player_name, s.credits, s.oxygen, s.fuel, s.health, s.distance_traveled, s.days_survived, s.current_planet, CURRENT_TIMESTAMP())
    """
    sqlQuery(query)

# Update leaderboard
def update_leaderboard(state):
    query = f"""
    INSERT INTO {catalog}.{schema}.{leaderboard_table}
    (player_name, days_survived, distance_traveled)
    VALUES ('{state["player_name"]}', {state["days_survived"]}, {state["distance_traveled"]})
    """
    sqlQuery(query)

# Simple game logic
def perform_action(action, state):
    if action == "mine":
        state["credits"] += random.randint(10, 50)
        state["oxygen"] -= random.randint(5, 15)
        state["fuel"] -= random.randint(5, 15)
    elif action == "rest":
        state["health"] += random.randint(10, 30)
        state["oxygen"] -= random.randint(5, 15)
    elif action == "travel":
        state["current_planet"] = random.randint(1, 5)
        state["fuel"] -= random.randint(20, 40)
        state["oxygen"] -= random.randint(10, 30)
        state["distance_traveled"] += random.randint(100, 500)
    elif action == "trade":
        state["credits"] -= random.randint(10, 30)
        state["oxygen"] += random.randint(20, 40)
        state["fuel"] += random.randint(20, 40)
    
    state["days_survived"] += 1
    state["health"] = max(0, min(state["health"], 100))
    state["oxygen"] = max(0, min(state["oxygen"], 100))
    state["fuel"] = max(0, min(state["fuel"], 100))
    
    # Random events
    if random.random() < 0.1:
        event = random.choice(["asteroid", "alien", "malfunction"])
        if event == "asteroid":
            state["health"] -= random.randint(10, 30)
            st.warning("⚠️ Asteroid field encountered! Ship damaged.")
        elif event == "alien":
            state["credits"] -= random.randint(10, 30)
            st.warning("👽 Alien encounter! Some credits were stolen.")
        elif event == "malfunction":
            state["fuel"] -= random.randint(10, 30)
            st.warning("🔧 System malfunction! Fuel leaked.")
    
    return state

# Game UI - Main Section
player_name = st.text_input("Enter your space explorer name:")

if st.button("🚀 Start New Mission"):
    # Initialize game state
    game_state = {
        "player_name": player_name,
        "credits": 100,
        "oxygen": 100,
        "fuel": 100,
        "health": 100,
        "distance_traveled": 0,
        "days_survived": 0,
        "current_planet": 1
    }
    update_game_state(game_state)
    st.success("Mission started! Explore the galaxy!")

# Game Status Display
state = get_game_state()
if state:
    st.markdown("## 🚀 Mission Status")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🛸 Days Survived", state["days_survived"])
    with col2:
        st.metric("🌍 Current Planet", f"Planet {state['current_planet']}")
    with col3:
        st.metric("💳 Credits", f"{state['credits']}")

    st.progress(min(state["health"], 100) / 100)
    st.write(f"🫁 Oxygen: {state['oxygen']} | ⛽ Fuel: {state['fuel']} | ❤️ Health: {state['health']}")

# Custom CSS for button styling
st.markdown("""
    <style>
    .stButton > button {
        width: 100%;
        height: 75px;
        white-space: normal;
        word-wrap: break-word;
    }
    </style>
""", unsafe_allow_html=True)

# Action Buttons
st.markdown("### 🛠 Choose Your Action")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("⛏\nMine\nResources"):
        state = perform_action("mine", state)
        st.success("You mined valuable resources and earned credits!")

with col2:
    if st.button("🛌\nRest"):
        state = perform_action("rest", state)
        st.success("You restored health but consumed oxygen!")

with col3:
    if st.button("🚀\nTravel to\nNew Planet"):
        state = perform_action("travel", state)
        st.success("You traveled to another planet, consuming fuel and oxygen!")

with col4:
    if st.button("🛒\nTrade at\nSpace Station"):
        state = perform_action("trade", state)
        st.success("You traded resources for supplies!")


    # Update game state
    update_game_state(state)

    # Check for game over
    if state["health"] <= 0 or state["oxygen"] <= 0 or state["fuel"] <= 0:
        st.error("Game Over! Your space journey has come to an end.")
        # Update leaderboard
        update_leaderboard(state)

# Leaderboard
st.markdown("## 🏆 Galactic Leaderboard")
leaderboard = get_leaderboard()
if not leaderboard.empty:
    st.dataframe(leaderboard.style.set_properties(**{'background-color': '#0d0d0d', 'color': 'white'}))
else:
    st.write("No leaderboard data yet. Be the first to explore the galaxy!")
