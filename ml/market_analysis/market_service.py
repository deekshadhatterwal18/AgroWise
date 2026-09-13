import os
import pandas as pd


# =========================================================
# CONFIG
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "dataset", "mandi_prices.csv")

# Actual column names from the CSV (Min/Max/Modal have "_x0020_"
# instead of a space — known Agmarknet export quirk)
COL_STATE = "State"
COL_COMMODITY = "Commodity"
COL_MODAL_PRICE = "Modal_x0020_Price"

# The dataset stores prices per QUINTAL (1 quintal = 100 kg).
# Farmers think in per-KG price, so we convert everywhere.
QUINTAL_TO_KG = 100


# =========================================================
# LOAD DATA ONCE (when the app starts, not on every request)
# =========================================================

def _load_dataset():
    """Reads the CSV once. Returns empty DataFrame if file is missing."""

    if not os.path.exists(CSV_PATH):
        print(f"Market dataset not found at {CSV_PATH}")
        return pd.DataFrame()

    df = pd.read_csv(CSV_PATH)

    # Drop rows where price is missing (can't use them for averages)
    df = df.dropna(subset=[COL_MODAL_PRICE])

    # Convert price from ₹/quintal -> ₹/kg, right here at load time,
    # so every function below already works in ₹/kg.
    df[COL_MODAL_PRICE] = (df[COL_MODAL_PRICE] / QUINTAL_TO_KG).round(2)

    return df


market_df = _load_dataset()


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def get_all_commodities():
    """Returns a sorted list of unique crop names for the dropdown."""

    if market_df.empty:
        return []

    return sorted(market_df[COL_COMMODITY].dropna().unique().tolist())


def get_states_for_commodity(commodity):
    """Returns the states where this crop is traded (for the state dropdown)."""

    if market_df.empty:
        return []

    filtered = market_df[market_df[COL_COMMODITY] == commodity]

    return sorted(filtered[COL_STATE].dropna().unique().tolist())


def get_state_price_comparison(commodity):
    """
    For a given crop, returns the average price (₹/kg) in every
    state that trades it — sorted highest first. The frontend uses
    this full list for the bar chart, and highlights whichever
    state the farmer picked in the optional state dropdown.
    """

    if market_df.empty:
        return None

    # Step 1: keep only rows for the selected crop
    filtered = market_df[market_df[COL_COMMODITY] == commodity]

    if filtered.empty:
        return None

    # Step 2: group by state, average the (already-in-kg) price
    state_avg = (
        filtered
        .groupby(COL_STATE)[COL_MODAL_PRICE]
        .mean()
        .round(2)
        .sort_values(ascending=False)
    )

    # Step 3: build the list of {state, price} for the chart
    state_prices = [
        {"state": state, "price": price}
        for state, price in state_avg.items()
    ]

    # Step 4: build the summary numbers (overall avg / highest / lowest)
    overall_avg = round(filtered[COL_MODAL_PRICE].mean(), 2)
    highest = state_prices[0]   # already sorted high -> low
    lowest = state_prices[-1]

    summary = {
        "average_price_kg": overall_avg,
        "highest_state": highest["state"],
        "highest_price_kg": highest["price"],
        "lowest_state": lowest["state"],
        "lowest_price_kg": lowest["price"]
    }

    return {
        "summary": summary,
        "state_prices": state_prices
    }
