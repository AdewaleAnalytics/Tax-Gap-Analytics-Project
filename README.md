# Tax Gap Analytics & Variance Project

A comprehensive, end-to-end data analytics and business intelligence solution engineered to monitor, calculate, and profile the structural tax gap across multiple fiscal publication cycles. This project processes multi-year dimensional data to isolate macro performance trends, track percentage variations across core tax streams, and deliver dynamic, executive-ready performance visual metrics.

![Executive Summary Workspace](images/exe.png)

***

## 💼 Project Case Study

### 📌 Situation
In public finance and macroeconomic auditing, manually tracking multi-year compliance shortfalls and structural revenue losses across shifting fiscal calendar boundaries introduces severe data calculation and context bottlenecks. This project addresses the complexities of analyzing multi-billion-currency tax gap figures across a matrix of distinct publication cycles (2022–2025). Without centralized model automation, identifying which specific core streams (such as VAT or Corporation Tax) are driving the largest absolute variations happens reactively, obscuring critical long-term structural revenue losses.

### 🎯 Task
My objective was to design, optimize, and deploy a robust relational reporting model and an executive-facing business intelligence application. The project required ingesting multi-stream transactional structures from a database, resolving complex evaluation context mismatches between dimensional calendars and fact metrics, and surfacing real-time, evidence-based revenue insights using dynamic KPI formatting indicators.

### ⚙️ Action
I engineered a unified corporate analytics workspace split across three primary design layers:

* **Data Integration & Architecture (Power Query / M):** Built specialized column-level filtering states directly within the database ingestion phase to cleanly partition structural year cycles. Implemented type-safe casting wrappers to reconcile data boundaries and prevent runtime processing failures.
* **Context-Aware Modeling (DAX):** Developed advanced time-intelligence calculations that decouple calendar filter spaces. By utilizing targeted evaluation functions (`REMOVEFILTERS`, `COALESCE`, and explicit state isolation), I neutralized the "All Years Combined" visual bug, allowing standalone card components to execute strict, isolated year-over-year comparisons.
* **Dynamic SVG UI Engineering:** Programmed inline XML vector calculations (`data:image/svg+xml`) that evaluate active percentage deltas on the fly. The engine dynamically injects color-coded hex keys (`%23D62828` for red/upward revenue risk and `%232A9D8F` for green/downward risk) to embed responsive trend arrows directly inside the primary metric rows.

### 📊 Result

* **Stabilized Metric Engine:** Successfully deployed a fully optimized DAX schema that guarantees 100% calculation accuracy, maintaining complete structural stability whether data is sliced by specific years or viewed unfiltered.
* **Executive Intelligence Hub:** Formatted an interactive visualization suite featuring macro variance matrices and synchronized KPI cards that isolate current performance metrics directly against historical base periods.
* **Strategic Financial Visibility:** The project instantly surfaces high-value compliance drivers, transforming raw transactional reporting lines into a clear roadmap for legislative review and revenue intervention.

***

## 🎛️ Database Ingestion & Relational Architecture Disclosure

### 🔒 Data Governance & Structural Management
The baseline data layer for this project is integrated from an enterprise database structure utilizing a dedicated `dim_financial_calendar` table. Because database-driven calendars frequently extend into future operating cycles, executing standard time-intelligence functions can skew standalone visual calculations. To achieve bulletproof accuracy across this structural landscape, the model incorporates explicit design constraints:

* **Type-Safe Validation:** Wraps calendar evaluation fields inside explicit casting layers (`VALUE`, `LEFT`, `INT`) to eliminate implicit database text-to-number conflicts during calculations.
* **Context Isolation:** Leverages decoupled filter parameters to completely clear out empty future reporting windows, forcing the visual components to evaluate calculations against actual data rows.
* **Context-Driven Fallbacks:** Implements fallback logic to guarantee that if a dashboard user clears all page slicers, the visual cards gracefully default to the most recent completed reporting cycle (2023) rather than crashing or blanking out.

***

## 📁 Repository Architecture

* `data_model/`: Relational database connections, dimensional mappings, and schema definitions linking tax facts to calendar streams.
* `dax_measures/`: Central repository of core DAX calculations including isolated year gaps, percentage variations, and dynamic asset scripts.
* `Tax_Gap_Analytics.pbix`: The interactive production Power BI workbook featuring executive viewports and custom visual layouts.

***

## 🛠️ Analytical Analytics & DAX Pipeline Breakdown

The project model relies on a highly synchronized suite of custom business logic calculations to track multi-year variances reliably:

### Total Tax Gap (Billions)
Aggregates raw transactional reporting parameters and standardizes the scaling factor, converting baseline figures into clean, readable billions formatting:

Total Tax Gap (Billions) = DIVIDE(SUM('fact_tax_gaps'[Tax_Gap_Billion]), 1000, 0)

Prior Year Tax Gap
Dynamically extracts the active calendar year context, overrides the current visual filter using safe casting, and looks back exactly one fiscal period to capture the precise comparative baseline:

Code snippet
Prior Year Tax Gap = 
VAR SelectedYear = COALESCE(SELECTEDVALUE('dim_financial_calendar'[Calendar_Year_Start]), 2023)
RETURN
    CALCULATE(
        [Total Tax Gap (Billions)],
        REMOVEFILTERS('dim_financial_calendar'),
        VALUE('dim_financial_calendar'[Calendar_Year_Start]) = VALUE(SelectedYear) - 1
    )
YoY Tax Gap Change (%)
Computes the strict algebraic difference between isolated fiscal years, completely bypassing external cross-filtering distortion to deliver accurate rate metrics:

Code snippet
YoY Tax Gap Change (%) = 
VAR SelectedYear = COALESCE(SELECTEDVALUE('dim_financial_calendar'[Calendar_Year_Start]), 2023)
VAR CurrentYearGap = CALCULATE([Total Tax Gap (Billions)], REMOVEFILTERS('dim_financial_calendar'), VALUE('dim_financial_calendar'[Calendar_Year_Start]) = VALUE(SelectedYear))
VAR PriorYearGap = [Prior Year Tax Gap]
RETURN
    DIVIDE(CurrentYearGap - PriorYearGap, PriorYearGap, 0)
💻 Dynamic Visual Assets (SVG UI Integration)
To deliver a premium consumer-grade user experience, visual trend indicators are rendered programmatically based on active performance outcomes using a custom vector-injection script:

YoY Tax Gap Icon URL
Evaluates the directional trajectory of the gap metric. If uncollected revenue expands (positive variance), it injects a high-visibility hazard red vector asset; if the gap contracts (negative variance), it switches instantly to a stabilization green asset:

Code snippet
YoY Tax Gap Icon URL = 
IF(
    [YoY Tax Gap Change (%)] >= 0,
    "data:image/svg+xml;utf8,<svg xmlns='[http://www.w3.org/2000/svg](http://www.w3.org/2000/svg)' viewBox='0 0 24 24' fill='none' stroke='%23D62828' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'><polyline points='23 6 13.5 15.5 8.5 10.5 1 18'></polyline><polyline points='17 6 23 6 23 12'></polyline></svg>",
    "data:image/svg+xml;utf8,<svg xmlns='[http://www.w3.org/2000/svg](http://www.w3.org/2000/svg)' viewBox='0 0 24 24' fill='none' stroke='%232A9D8F' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'><polyline points='23 18 13.5 8.5 8.5 13.5 1 6'></polyline><polyline points='17 18 23 18 23 12'></polyline></svg>"
)
📊 Business Intelligence & Executive Outcomes
The analytical backend feeds an enterprise-ready dashboard that empowers financial policy and risk management teams to drive strategic interventions based on explicit data:

Executive Performance Profile: Houses synchronized metric rows tracking overall shortfalls, absolute deltas, and percentage variances with native callout text formatting.

Core Stream Structural Analysis: Employs advanced comparative matrices that cross-examine individual tax streams (such as VAT sectors or Corporate structures) over multiple years, detailing specific growth rates.

Targeted Key Insights: Surfaces high-impact narrative observations automatically:

Key Insight: The total tax gap across selected streams expanded by +20.7% (£6.3B) from 2022 to 2025, driven heavily by a combined £2.8B surge in VAT – Retail & Wholesale and Corporation Tax – Large Businesses.

⚖️ Licensing & Data Attribution
Data Source: This project utilizes official public sector estimation datasets published by His Majesty's Revenue and Customs (HMRC), licensed under the Open Government Licence v3.0.

Endorsement Disclaimer: This repository serves entirely as an independent data analysis portfolio project. It is not endorsed, approved, sponsored, or affiliated with HMRC, the government, or any public sector authority.

Third-Party Material Notice: All operational database structures, analytical metrics, visual layouts, and vector assets are custom configurations engineered uniquely for this portfolio analysis. Care has been taken to ensure no restricted or excluded third-party copyright materials are included in the asset model.
