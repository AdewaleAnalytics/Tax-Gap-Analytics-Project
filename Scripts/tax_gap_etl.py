import pandas as pd
import os
import sqlite3

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. Configuration & Source Paths
files = {
    2022: os.path.join(SCRIPT_DIR, "Measuring_tax_gap_tables_2022.xlsx"),
    2023: os.path.join(SCRIPT_DIR, "Measuring_tax_gap_online_tables_2023.xlsx"),
    2025: os.path.join(SCRIPT_DIR, "Measuring_tax_gap_online_tables_2025.xlsx")
}

target_sheets = {
    "Table 1.3": "Macro Tax Summary",
    "Table 2.1": "VAT Detail",
}

all_melted_dfs = []

print("🚀 STEP 1: EXTRACT & TRANSFORM PIPELINE\n")

for year, file_path in files.items():
    if not os.path.exists(file_path):
        print(f"⚠️ File missing: {os.path.basename(file_path)}")
        continue
        
    print(f"🔄 Processing {year} publication...")
    
    for sheet, component_name in target_sheets.items():
        try:
            raw_df = pd.read_excel(file_path, sheet_name=sheet)
            
            header_row_idx = None
            for idx, row in raw_df.iterrows():
                row_strings = [str(cell).lower() for cell in row.values]
                if any('type' in s or 'tax' in s or 'vat' in s for s in row_strings):
                    header_row_idx = idx
                    break
            
            if header_row_idx is None:
                header_row_idx = 4
                
            df = pd.read_excel(file_path, sheet_name=sheet, skiprows=header_row_idx + 1)
            df.columns = df.columns.astype(str).str.strip()
            
            if len(df.columns) == 0:
                continue
                
            first_col = df.columns[0]
            df = df.rename(columns={first_col: "Raw_Tax_Type"})
            
            # Forward fill Excel structural merged blocks
            df["Raw_Tax_Type"] = df["Raw_Tax_Type"].astype(str).str.strip()
            df.loc[df["Raw_Tax_Type"].str.lower() == 'nan', "Raw_Tax_Type"] = None
            df.loc[df["Raw_Tax_Type"] == '', "Raw_Tax_Type"] = None
            df["Raw_Tax_Type"] = df["Raw_Tax_Type"].ffill()
            
            df = df.dropna(subset=["Raw_Tax_Type"])
            df = df[~df["Raw_Tax_Type"].str.contains(r'^Notes|^Source|📊|^\[\d\]', case=False, na=False)]
            
            year_cols = [c for c in df.columns if '-' in c and any(char.isdigit() for char in c)]
            if not year_cols:
                continue
                
            df_filtered = df[["Raw_Tax_Type"] + year_cols].copy()
            
            for col in year_cols:
                df_filtered[col] = pd.to_numeric(df_filtered[col], errors='coerce')
                
            df_filtered["Sub_Row_ID"] = df_filtered.groupby("Raw_Tax_Type").cumcount() + 1
            
            df_melted = df_filtered.melt(
                id_vars=["Raw_Tax_Type", "Sub_Row_ID"], 
                value_vars=year_cols, 
                var_name="Financial_Year", 
                value_name="Tax_Gap_Billion"
            )
            
            df_melted = df_melted.dropna(subset=["Tax_Gap_Billion"])
            df_melted["Component_Context"] = component_name
            df_melted["Source_Publication_Year"] = year
            
            all_melted_dfs.append(df_melted)
            
        except Exception as e:
            print(f"  ⚠️ Skipping sheet {sheet} in {year}: {e}")

if not all_melted_dfs:
    print("❌ Process halted: No data extracted.")
    exit()

# Final Dataframe Consolidation
master_tax_gap_df = pd.concat(all_melted_dfs, ignore_index=True)
master_tax_gap_df["Tax_Type"] = (
    master_tax_gap_df["Component_Context"] + " - " + 
    master_tax_gap_df["Raw_Tax_Type"] + " (Breakdown " + 
    master_tax_gap_df["Sub_Row_ID"].astype(str) + ")"
)
master_tax_gap_df = master_tax_gap_df.drop(columns=["Component_Context", "Raw_Tax_Type", "Sub_Row_ID"])
master_tax_gap_df = master_tax_gap_df.sort_values(by=["Tax_Type", "Financial_Year", "Source_Publication_Year"])

print("\n" + "="*50)
print("🔍 STEP 2: DATA QUALITY VALIDATION LAYER")
print("="*50)

validation_passed = True

# Check 1: Row Count Sanity Check
total_rows = len(master_tax_gap_df)
print(f"📋 Check 1: Volumetric Analysis... Total Staged Rows: {total_rows}")
if total_rows < 1000:
    print("  ❌ WARNING: Row count lower than expected bounds!")
    validation_passed = False
else:
    print("  ✅ Passed: Row count falls within expected variance.")

# Check 2: Null Value Integrity Check
null_counts = master_tax_gap_df.isnull().sum().sum()
print(f"📋 Check 2: Missing Data Integrity Scan... Found Null Cells: {null_counts}")
if null_counts > 0:
    print("  ❌ WARNING: Critical missing values found in key columns!")
    validation_passed = False
else:
    print("  ✅ Passed: Zero null values found in final target records.")

# Check 3: Data Bounds (Negative Value Check)
negative_values = (master_tax_gap_df["Tax_Gap_Billion"] < 0).sum()
print(f"📋 Check 3: Value Boundary Scan... Negative Values Found: {negative_values}")
if negative_values > 0:
    print("  ❌ WARNING: Negative tax gap amounts identified!")
    validation_passed = False
else:
    print("  ✅ Passed: All tax values are non-negative.")

if validation_passed:
    print("\n🟢 DATA QUALITY VERDICT: PASSED. Proceeding to target load.")
else:
    print("\n🔴 DATA QUALITY VERDICT: FAILED. Please review staged data anomalies.")

print("\n" + "="*50)
print("💾 STEP 3: DATABASE INGESTION LAYER")
print("="*50)

# Connect to a local SQLite database (it creates it automatically if it doesn't exist)
db_path = os.path.join(SCRIPT_DIR, "hmrc_tax_gap.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Drop old table if running again to ensure clean schema sync
    cursor.execute("DROP TABLE IF EXISTS fact_tax_gaps;")
    
    # Write dataframe smoothly to SQL
    master_tax_gap_df.to_sql("fact_tax_gaps", conn, if_exists="replace", index=False)
    conn.commit()
    print(f"✅ Success: Written records into table 'fact_tax_gaps' inside:")
    print(f"   📁 {db_path}")
    
    # Verification Test directly inside SQL engine
    cursor.execute("SELECT COUNT(*), AVG(Tax_Gap_Billion) FROM fact_tax_gaps;")
    sql_stats = cursor.fetchone()
    print(f"\n📊 Verified SQL Table Stats:")
    print(f"   🔹 Total SQL Logged Rows: {sql_stats[0]}")
    print(f"   🔹 Calculated Global Average Gap: £{sql_stats[1]:.2f} Billion")
    
except Exception as e:
    print(f"❌ Database load execution aborted: {e}")
finally:
    conn.close()
    print("\n🔒 Database pipeline connection securely closed.")