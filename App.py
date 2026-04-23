import pandas as pd

# Load dataset once
df = pd.read_csv("Docs/Medsearch.csv")

# Preprocessing (same as your notebook)
df = df[df["is_discontinued"] == False]
df = df[df["primary_strength"].notna()]

df["primary_ingredient"] = df["primary_ingredient"].str.strip().str.lower()
df["primary_strength"] = df["primary_strength"].str.strip().str.lower()
df["dosage_form"] = df["dosage_form"].str.strip().str.lower()
df["brand_name"] = df["brand_name"].str.strip()

df.reset_index(drop=True, inplace=True)


def recommend_alternatives(brand_name, top_n=10):
    brand_name = brand_name.strip()

    if brand_name not in df["brand_name"].values:
        return None

    input_drug = df[df["brand_name"] == brand_name].iloc[0]

    ingredient = input_drug["primary_ingredient"]
    strength = input_drug["primary_strength"]
    dosage = input_drug["dosage_form"]
    input_price = input_drug["price_inr"]

    alternatives = df[
        (df["primary_ingredient"] == ingredient) &
        (df["primary_strength"] == strength) &
        (df["dosage_form"] == dosage) &
        (df["brand_name"] != brand_name)
    ].copy()

    if alternatives.empty:
        return None

    alternatives = alternatives.sort_values(by="price_inr")

    alternatives["savings_inr"] = input_price - alternatives["price_inr"]
    alternatives["savings_percent"] = (
        (alternatives["savings_inr"] / input_price) * 100
    ).round(2)

    return alternatives.head(top_n)
    //This demonstartes first 5 elements
