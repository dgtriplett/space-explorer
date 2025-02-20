# Galactic Survival: A Space Explorer's Journey

## Overview

Galactic Survival is an interactive space exploration game built as a Databricks App using Streamlit. This game demonstrates the power of Databricks SQL, Unity Catalog, and serverless computing in creating a data-driven application.

## Features

- Real-time resource management (credits, oxygen, fuel, health)
- Dynamic planet exploration
- Random events (asteroid fields, alien encounters, system malfunctions)
- Persistent game state using Databricks SQL
- Global leaderboard

## Prerequisites

- Databricks workspace with Unity Catalog enabled
- Databricks SQL warehouse
- Python 3.7+
- Required Python packages (see `requirements.txt`)

## Setup

1. Clone this repository
2. Install required packages:
   ```
   pip install -r requirements.txt
   ```
3. Set up the following environment variables:
   - `DATABRICKS_HOST`
   - `DATABRICKS_TOKEN`
   - `DATABRICKS_WAREHOUSE_ID`

4. Create the necessary tables in your Databricks SQL warehouse:
   ```sql
   CREATE TABLE drew_triplett.space_explorer.galactic_survival_game (
       player_name STRING,
       credits INT,
       oxygen INT,
       fuel INT,
       health INT,
       distance_traveled INT,
       days_survived INT,
       current_planet INT,
       last_updated TIMESTAMP
   ) USING DELTA;

   CREATE TABLE drew_triplett.space_explorer.galactic_survival_leaderboard (
       player_name STRING,
       days_survived INT,
       distance_traveled INT
   ) USING DELTA;
   ```

## Running the App

To run the Streamlit app locally:

```
streamlit run galactic_survival.py
```

To deploy as a Databricks App, follow the Databricks documentation for app deployment.

## Game Rules

- Start with 100 credits, oxygen, fuel, and health
- Choose actions: Mine, Rest, Travel, or Trade
- Random events may occur after each action
- Game ends when health, oxygen, or fuel reaches 0
- Try to survive as long as possible and travel the farthest!

## Code Structure

- `sqlQuery()`: Function to execute SQL queries using Databricks SQL connector
- `get_game_state()`, `update_game_state()`: Functions to manage game state
- `get_leaderboard()`, `update_leaderboard()`: Functions to manage leaderboard
- `perform_action()`: Main game logic for different actions and random events
- Streamlit UI code for game interface and interactions

## Customization

You can customize the game by modifying:
- Probabilities and values in the `perform_action()` function
- UI elements and styling in the Streamlit code
- Table structures and queries for more complex game mechanics

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.
