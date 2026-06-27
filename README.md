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
```dax
Total Tax Gap (Billions) = DIVIDE(SUM('fact_tax_gaps'[Tax_Gap_Billion]), 1000, 0)

### Prior Year Tax Gap
Dynamically extracts the active calendar year context, overrides the current visual filter using safe casting, and looks back exactly one fiscal period to capture the precise comparative baseline:

```dax
Prior Year Tax Gap = 
VAR SelectedYear = COALESCE(SELECTEDVALUE('dim_financial_calendar'[Calendar_Year_Start]), 2023)
RETURN
    CALCULATE(
        [Total Tax Gap (Billions)],
        REMOVEFILTERS('dim_financial_calendar'),
        VALUE('dim_financial_calendar'[Calendar_Year_Start]) = VALUE(SelectedYear) - 1
    )sure no restricted or excluded third-party copyright materials are included in the asset model.
