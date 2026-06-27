import sqlite3
import pandas as pd
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, "hmrc_tax_gap.db")

def run_analysis():
    # Connect to your relational SQLite database
    conn = sqlite3.connect(DB_PATH)
    
    print("📊 EXTRACTION & ANALYTICS DASHBOARD")
    print("=" * 60)
    
    # Query 1: Top 5 Highest Loss Tax Categories (Using the latest 2025 publication data)
    print("\n🔥 1. TOP 5 TAX GAP CATEGORIES (2025 Publication Baseline)")
    print("-" * 60)
    query_top_5 = """
        SELECT 
            Tax_Type, 
            Financial_Year, 
            Tax_Gap_Billion
            Source_Publication_Year
        FROM fact_tax_gaps
        WHERE Source_Publication_Year = 2025
        AND Tax_Type NOT LIKE '%Total%'
        AND Tax_Type NOT LIKE '%Liability%'
        ORDER BY Tax_Gap_Billion DESC
        LIMIT 5;
    """
    df_top_5 = pd.read_sql_query(query_top_5, conn)
    print(df_top_5.to_string(index=False))
    
    # Query 2: Variance Analysis - Tracking how HMRC revised historical numbers across publication versions
    print("\n🔄 2. HISTORICAL DATA REVISION VARIANCE (Example: Financial Year 2019-20)")
    print("-" * 60)
    query_variance = """
        SELECT 
            Tax_Type,
            Source_Publication_Year,
            Tax_Gap_Billion
        FROM fact_tax_gaps
        WHERE Financial_Year = '2019-20'
          AND Tax_Type LIKE '%Total%'
        ORDER BY Tax_Type, Source_Publication_Year;
    """
    df_variance = pd.read_sql_query(query_variance, conn)
    if not df_variance.empty:
        print(df_variance.to_string(index=False))
    else:
        print("Note: No explicit 'Total' labels found for 2019-20 rows. Showing a direct slice instead:")
        query_fallback = """
            SELECT Tax_Type, Source_Publication_Year, Tax_Gap_Billion 
            FROM fact_tax_gaps 
            WHERE Financial_Year = '2019-20' 
            LIMIT 6;
        """
        print(pd.read_sql_query(query_fallback, conn).to_string(index=False))

    # Query 3: Overall Trend Summary by Component over time
    print("\n📈 3. MACRO VS VAT DETAIL RECORD VOLUMES IN DB")
    print("-" * 60)
    query_counts = """
        SELECT 
            SUBSTR(Tax_Type, 1, INSTR(Tax_Type, ' - ') - 1) AS Category_Group,
            COUNT(*) as Total_Records,
            ROUND(AVG(Tax_Gap_Billion), 2) as Avg_Gap_Billion
        FROM fact_tax_gaps
        GROUP BY Category_Group;
    """
    df_counts = pd.read_sql_query(query_counts, conn)
    print(df_counts.to_string(index=False))

    conn.close()

if __name__ == "__main__":
    if os.path.exists(DB_PATH):
        run_analysis()
    else:
        print(f"❌ Error: Database not found at {DB_PATH}. Please run tax_gap_etl.py first!")