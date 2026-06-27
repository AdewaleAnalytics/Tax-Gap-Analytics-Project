import pandas as pd
import os
from sqlalchemy import create_engine

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(SCRIPT_DIR, "clean_tax_gap_master.csv")

# ----------------------------------------------------
# 1. CONNECT TO MICROSOFT SQL SERVER (TARGETED DATABASE)
# ----------------------------------------------------
# Pointing to localhost\SQLEXPRESS and the new dedicated database container
connection_string = (
    "mssql+pyodbc://localhost\\SQLEXPRESS/HMRC_Tax_Gap_Framework"
    "?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
)

print("🖥️ Connecting to SQL Server Instance (SQLEXPRESS)...")
engine = create_engine(connection_string)

try:
    with engine.connect() as conn:
        print("✅ Connection Successful! Target database 'HMRC_Tax_Gap_Framework' found.\n")
except Exception as e:
    print(f"❌ Connection Failed: {e}")
    print("\n💡 Tip: Make sure you created the database 'HMRC_Tax_Gap_Framework' in SSMS first.")
    exit()

if not os.path.exists(CSV_PATH):
    print(f"❌ Error: {CSV_PATH} not found. Please run your ETL script first!")
    exit()

print("🛠️ Transforming Master Dataset into Star Schema Dimensions...")
df_master = pd.read_csv(CSV_PATH)

# ---- Create Dimension 1: Tax Metadata ----
unique_tax_types = df_master["Tax_Type"].unique()
dim_tax_data = []
for idx, full_name in enumerate(unique_tax_types, start=1):
    component = "Macro Tax Summary" if "Macro Tax Summary" in full_name else "VAT Detail"
    core_name = full_name.replace("Macro Tax Summary - ", "").replace("VAT Detail - ", "")
    
    dim_tax_data.append({
        "Tax_Type_Key": idx,
        "Full_Tax_Label": full_name,
        "Reporting_Component": component,
        "Core_Tax_Stream": core_name
    })
dim_tax = pd.DataFrame(dim_tax_data)

# ---- Create Dimension 2: Financial Calendar ----
unique_years = df_master["Financial_Year"].unique()
dim_calendar_data = []
for year in unique_years:
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

# ---- Create Central Fact Table ----
label_to_key = dict(zip(dim_tax["Full_Tax_Label"], dim_tax["Tax_Type_Key"]))
fact_tax_gaps_star = df_master.copy()
fact_tax_gaps_star["Tax_Type_Key"] = fact_tax_gaps_star["Tax_Type"].map(label_to_key)
fact_tax_gaps_star = fact_tax_gaps_star.drop(columns=["Tax_Type"])
fact_tax_gaps_star = fact_tax_gaps_star[[
    "Tax_Type_Key", "Financial_Year", "Source_Publication_Year", "Tax_Gap_Billion"
]]

# ----------------------------------------------------
# 2. LOAD PHASE: PUSH TO CHOSEN SSMS ARCHIVE
# ----------------------------------------------------
print("\n🚀 Loading Star Schema Dimensions to SSMS Data Warehouse...")

try:
    # Overwrite/Create the explicit tables on the server
    dim_tax.to_sql("dim_tax_metadata", engine, if_exists="replace", index=False)
    print("   🔹 Table [dim_tax_metadata] loaded successfully.")
    
    dim_calendar.to_sql("dim_financial_calendar", engine, if_exists="replace", index=False)
    print("   🔹 Table [dim_financial_calendar] loaded successfully.")
    
    fact_tax_gaps_star.to_sql("fact_tax_gaps", engine, if_exists="replace", index=False)
    print("   🔹 Fact Table [fact_tax_gaps] loaded successfully.")
    
    print("\n🎉 RELATIONAL INGESTION COMPLETE!")
    print("Go back to SSMS, right-click 'HMRC_Tax_Gap_Framework' -> 'Refresh', and look under Tables!")

except Exception as e:
    print(f"❌ Critical error during SQL database write operations: {e}")