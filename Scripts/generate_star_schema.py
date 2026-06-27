import pandas as pd
import sqlite3
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(SCRIPT_DIR, "clean_tax_gap_master.csv")
DB_PATH = os.path.join(SCRIPT_DIR, "hmrc_tax_gap.db")

def build_star_schema():
    if not os.path.exists(CSV_PATH):
        print(f"❌ Error: {CSV_PATH} not found. Please run your ETL script first!")
        return

    print("🛠️ Generating Power BI Star Schema Relational Tables...\n")
    df_master = pd.read_csv(CSV_PATH)

    # ----------------------------------------------------
    # 1. DIMENSION 1: Tax Metadata (dim_tax_metadata)
    # ----------------------------------------------------
    print("🔹 Structuring 'dim_tax_metadata'...")
    # Extract unique tax types
    unique_tax_types = df_master["Tax_Type"].unique()
    
    dim_tax_data = []
    for idx, full_name in enumerate(unique_tax_types, start=1):
        # Parse component context out of the string prefix we created earlier
        component = "Unknown"
        if "Macro Tax Summary" in full_name:
            component = "Macro Tax Summary"
        elif "VAT Detail" in full_name:
            component = "VAT Detail"
            
        # Clean the core name up
        core_name = full_name.replace("Macro Tax Summary - ", "").replace("VAT Detail - ", "")
        
        dim_tax_data.append({
            "Tax_Type_Key": idx,
            "Full_Tax_Label": full_name,
            "Reporting_Component": component,
            "Core_Tax_Stream": core_name
        })
        
    dim_tax = pd.DataFrame(dim_tax_data)

    # ----------------------------------------------------
    # 2. DIMENSION 2: Financial Calendar (dim_financial_calendar)
    # ----------------------------------------------------
    print("🔹 Structuring 'dim_financial_calendar'...")
    unique_years = df_master["Financial_Year"].unique()
    
    dim_calendar_data = []
    for year in unique_years:
        # Extract start and end year integers from string formatting like '2023-24'
        try:
            start_yr = int(year.split('-')[0])
            end_yr = start_yr + 1
        except:
            start_yr, end_yr = None, None
            
        dim_calendar_data.append({
            "Financial_Year": year,
            "Calendar_Year_Start": start_yr,
            "Calendar_Year_End": end_yr
        })
        
    dim_calendar = pd.DataFrame(dim_calendar_data)

    # ----------------------------------------------------
    # 3. CENTRAL FACT TABLE: Fact Tax Gaps (fact_tax_gaps_star)
    # ----------------------------------------------------
    print("🔹 Mapping Foreign Keys to Central Fact Table...")
    # Map the text labels back to their numeric surrogate primary keys
    label_to_key = dict(zip(dim_tax["Full_Tax_Label"], dim_tax["Tax_Type_Key"]))
    
    fact_tax_gaps_star = df_master.copy()
    fact_tax_gaps_star["Tax_Type_Key"] = fact_tax_gaps_star["Tax_Type"].map(label_to_key)
    
    # Drop the massive redundant text columns from the fact table
    fact_tax_gaps_star = fact_tax_gaps_star.drop(columns=["Tax_Type"])
    
    # Reorder columns for a clean DW standard structure
    fact_tax_gaps_star = fact_tax_gaps_star[[
        "Tax_Type_Key", "Financial_Year", "Source_Publication_Year", "Tax_Gap_Billion"
    ]]

    # ----------------------------------------------------
    # 4. LOAD PHASE: Commit directly into SQLite Engine
    # ----------------------------------------------------
    print("\n💾 Loading Star Schema Tables into SQLite Environment...")
    conn = sqlite3.connect(DB_PATH)
    
    try:
        dim_tax.to_sql("dim_tax_metadata", conn, if_exists="replace", index=False)
        dim_calendar.to_sql("dim_financial_calendar", conn, if_exists="replace", index=False)
        fact_tax_gaps_star.to_sql("fact_tax_gaps", conn, if_exists="replace", index=False)
        conn.commit()
        
        print("🎉 SUCCESS! Star schema tables configured successfully inside:")
        print(f"   📁 {DB_PATH}\n")
        print("📋 Created Tables:")
        print("   ✅ dim_tax_metadata       (Lookup Dimension)")
        print("   ✅ dim_financial_calendar  (Time Dimension)")
        print("   ✅ fact_tax_gaps          (Central Metrics Fact Table)")
        
    except Exception as e:
        print(f"❌ Error during relational execution: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    build_star_schema()