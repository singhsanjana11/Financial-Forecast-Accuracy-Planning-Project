import pandas as pd

print("🔄 Reading cleaned_superstore_data.xlsx ...")
df = pd.read_excel("cleaned_superstore_data.xlsx", sheet_name="Sheet1")

# Rename columns to exactly what pipeline.py expects
df = df.rename(columns={
    "order date": "Order Date",
    "sales": "Sales"
})

# Save with the exact filename pipeline.py is looking for
df.to_csv("cleaned_superstore_data.xlsx - Sheet1.csv", index=False)

print("✅ Successfully created 'cleaned_superstore_data.xlsx - Sheet1.csv'")
print(f"   → Rows: {len(df):,}")
print(f"   → Columns: {df.columns.tolist()}")
print("\nYou can now run the pipeline in the next step.")