# Enterprise BFSI Customer 360 — Tableau Integration Guide

This guide provides step-by-step instructions for connecting Tableau Desktop (or Tableau Server / Tableau Cloud) to the Customer 360 Data Warehouse, configuring the Star Schema data model, and building certified BFSI analytical worksheets.

---

## 1. Connecting Tableau to the Data Warehouse

### Option A: PostgreSQL Direct Connection (Docker / Production)
1. Open **Tableau Desktop** → **Connect** → **To a Server** → **PostgreSQL**.
2. Enter connection details:
   - **Server**: `localhost` (or your cloud server hostname)
   - **Port**: `5432`
   - **Database**: `bfsi_enterprise_dw`
   - **Username**: `edw_user`
   - **Password**: (from `.env` file)
   - **Require SSL**: Preferred
3. Click **Sign In**.

### Option B: REST API / Web Data Connector (WDC)
1. Use the **Web Data Connector** to pull live data from the Customer 360 API:
   - URL: `http://localhost:8000/api/c360/customers?limit=500`
   - Format: JSON
2. Use the built-in JSON connector to flatten nested records.

### Option C: CSV/Excel Flat Export
1. Download exports from the BI Integration Hub at `http://localhost:8000/`
2. Navigate to **Power BI & Tableau** → Click **Download Tableau Data Extract**.
3. Open the downloaded `.csv` in Tableau.

---

## 2. Data Model Configuration (Star Schema)

### Step 1: Add Tables
In Tableau's **Data Source** tab, drag the following tables from the left panel:
- `dim_customer` (Customer Dimension)
- `dim_date` (Date Dimension)
- `dim_product` (Product Dimension)
- `dim_channel` (Channel Dimension)
- `dim_branch` (Branch Dimension)
- `fact_transactions` (Transactions Fact)
- `fact_daily_account_snapshot` (Account Snapshots)
- `fact_loan_performance` (Loan Performance)
- `fact_customer_interactions` (CRM Interactions)
- `c360_customer_mart` (Customer 360 Serving Mart)

### Step 2: Define Relationships
In Tableau's **Relationship** view, create the following joins:

| Dimension Table | Fact / Mart Table | Join Key | Join Type |
|---|---|---|---|
| `dim_customer` | `fact_transactions` | `customer_key` | Inner |
| `dim_customer` | `fact_daily_account_snapshot` | `customer_key` | Inner |
| `dim_customer` | `fact_loan_performance` | `customer_key` | Inner |
| `dim_customer` | `fact_customer_interactions` | `customer_key` | Inner |
| `dim_customer` | `c360_customer_mart` | `customer_key` | Inner |
| `dim_date` | `fact_transactions` | `date_key` | Inner |
| `dim_date` | `fact_daily_account_snapshot` | `date_key` | Inner |
| `dim_date` | `fact_loan_performance` | `date_key` | Inner |
| `dim_product` | `fact_transactions` | `product_key` | Inner |
| `dim_channel` | `fact_transactions` | `channel_key` | Inner |

### Step 3: Set Data Types & Hierarchies
- Set `date_key` as a **Date** type (YYYYMMDD integer → Date)
- Create a **Date Hierarchy**: Year → Quarter → Month → Week → Day
- Create a **Product Hierarchy**: Product Category → Product Sub Type → Product Name
- Create a **Geography Hierarchy**: State → City → Branch Name
- Mark `customer_key`, `product_key`, `channel_key` as **Dimensions** (not measures)

---

## 3. Certified Tableau Calculated Fields

Create the following calculated fields in Tableau for BFSI analytics:

### 1. Total Assets Under Management (AUM)
```
// Total AUM across deposits and loan exposure
[Total Deposit Balance] + [Total Loan Outstanding]
```

### 2. Non-Performing Loan (NPL) Classification
```
// Classify loans as NPL (90+ days past due) or Performing
IF [Overdue Days] >= 90 THEN "NPL"
ELSE "Performing"
END
```

### 3. Delinquency Aging Bucket
```
// Days Past Due (DPD) aging classification
IF [Overdue Days] = 0 THEN "Current"
ELSEIF [Overdue Days] < 30 THEN "1-29 DPD (Early Warning)"
ELSEIF [Overdue Days] < 60 THEN "30-59 DPD (Special Mention)"
ELSEIF [Overdue Days] < 90 THEN "60-89 DPD (Substandard)"
ELSE "90+ DPD (Default / NPL)"
END
```

### 4. Credit Card Utilization %
```
// Net credit utilization ratio
IF [Total Credit Limit] > 0 THEN
    [Total Credit Outstanding] / [Total Credit Limit] * 100
ELSE 0
END
```

### 5. Customer Risk Category
```
// Risk tier based on composite risk score
IF [Composite Risk Score] >= 50 THEN "Critical Risk"
ELSEIF [Composite Risk Score] >= 35 THEN "High Risk"
ELSEIF [Composite Risk Score] >= 20 THEN "Medium Risk"
ELSE "Low Risk"
END
```

### 6. Cross-Sell Penetration Flag
```
// Identifies multi-product customers for cross-sell analysis
IF [Total Products Held] >= 2 THEN "Multi-Product"
ELSE "Single Product"
END
```

### 7. Churn Risk Indicator
```
// Early warning churn signal
IF [Engagement Status] = "DECLINING" OR [Engagement Status] = "DORMANT" THEN "At Risk"
ELSEIF [Avg Sentiment Score] < -0.1 THEN "Negative Sentiment"
ELSEIF [Txn Count 30d] = 0 THEN "Inactive"
ELSE "Healthy"
END
```

---

## 4. Recommended Tableau Worksheets & Dashboards

### Dashboard 1: Executive Banking Overview
| Worksheet | Chart Type | Metrics |
|---|---|---|
| Portfolio KPI Bar | KPI / BANs | Total Customers, Total AUM, NPL Ratio, Cross-Sell % |
| Monthly Transaction Volume | Dual-Axis Bar+Line | Debit/Credit Volume, Transaction Count Trend |
| Customer Segment Distribution | Treemap | Customer count by Segment, colored by Risk |
| Risk Heatmap | Highlight Table | Segment × Risk Tier with AUM intensity |

### Dashboard 2: Loan Portfolio & NPL Tracker
| Worksheet | Chart Type | Metrics |
|---|---|---|
| Delinquency Aging Waterfall | Stacked Bar | Loan counts by DPD Bucket |
| NPL Exposure Treemap | Treemap | Outstanding balance by segment for NPL loans |
| Loss Provision Trend | Area Chart | Monthly loan loss provisions |
| Top Delinquent Customers | Table | Top 20 by overdue amount |

### Dashboard 3: Customer 360 Profile Drill-Down
| Worksheet | Chart Type | Metrics |
|---|---|---|
| Customer Search | Parameter + Filter | Dynamic customer lookup |
| Financial Snapshot | KPI BANs | Deposits, Loans, Credit Limit, LTV |
| Transaction Timeline | Gantt/Timeline | Recent transactions with merchant categories |
| Sentiment Analysis | Bullet Graph | CRM sentiment scores with benchmarks |

### Dashboard 4: Channel & Digital Adoption
| Worksheet | Chart Type | Metrics |
|---|---|---|
| Channel Distribution | Donut/Pie | Transaction volume by channel |
| Digital vs Physical | Side-by-side Bar | Mobile+Web vs ATM+Branch |
| Channel Trend | Line Chart | Monthly channel adoption rates |

---

## 5. Tableau Server / Cloud Publishing

### Publishing to Tableau Server
1. In Tableau Desktop, click **Server** → **Publish Workbook**.
2. Select your Tableau Server or Tableau Cloud site.
3. Set **Project**: `BFSI Analytics`
4. **Data Source**: Choose **Embedded** or **Published Separately**
5. **Permissions**: Set appropriate access for Relationship Managers, Risk Officers, and C-Suite.

### Scheduling Extracts
1. If using **Extract** mode, schedule daily refreshes:
   - Full Extract: Run nightly at 2:00 AM
   - Incremental: Every 4 hours based on `transaction_timestamp`
2. Configure alerts for extract failures.

### Embedding in Web Applications
Use the Tableau JavaScript API to embed dashboards:
```html
<script src="https://your-server/javascripts/api/tableau-2.min.js"></script>
<div id="tableauViz"></div>
<script>
  var viz = new tableau.Viz(
    document.getElementById('tableauViz'),
    'https://your-server/views/BFSI_Customer360/ExecutiveOverview',
    { hideTabs: true, hideToolbar: false }
  );
</script>
```

---

## 6. Best Practices

1. **Use Extracts for Complex Calculations**: Tableau Extracts (.hyper) provide faster query performance for calculated fields.
2. **Leverage Level of Detail (LOD) Expressions**: Use `FIXED`, `INCLUDE`, and `EXCLUDE` for multi-grain analysis.
3. **Apply Context Filters**: For large datasets, use context filters to improve query performance.
4. **Use Parameters for Dynamic Analysis**: Allow users to switch between metrics, time periods, and segments.
5. **Implement Row-Level Security (RLS)**: Use user filters to restrict data access by role.
6. **Color Coding**: Use consistent color schemes aligned with risk tiers and business segments.

---

## 📜 License
This project is licensed under the MIT License.
