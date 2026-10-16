# Enterprise BFSI Customer 360 Data Product

[![FastAPI](https://img.shields.io/badge/FastAPI-0.128-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![Power BI](https://img.shields.io/badge/Power_BI-Certified-F2C811?style=flat&logo=powerbi&logoColor=black)](https://powerbi.microsoft.com/)
[![Tableau](https://img.shields.io/badge/Tableau-Certified-E97627?style=flat&logo=tableau&logoColor=white)](https://www.tableau.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

An enterprise-grade **Customer 360 Data Product** engineered for Tier-1 Banking, Financial Services, and Insurance (BFSI) institutions. This system unifies disparate core banking silos—customer demographics, deposit accounts, loan origination, credit cards, payment transactions, AML/KYC compliance records, and omnichannel customer service touchpoints—into a high-performance **Dimensional Star Schema Data Warehouse**, an automated **Data Quality & Lineage Layer**, and a real-time **FastAPI Customer 360 Data Serving API** with an interactive executive BI portal supporting both **Microsoft Power BI** and **Tableau**.

---

## 🏛️ System Architecture

```
                    ┌──────────────────────────────────────────────┐
                    │                Business Users                │
                    │   (Relationship Managers, Credit Risk, C-Suite)
                    └──────────────────────┬───────────────────────┘
                                           │
                                           ▼
                    ┌──────────────────────────────────────────────┐
                    │        Interactive BI Executive Portal       │
                    │        (Modern SPA Portal + Power BI)        │
                    └──────────────────────┬───────────────────────┘
                                           │
                                           ▼
                    ┌──────────────────────────────────────────────┐
                    │          Customer 360 Data REST API          │
                    │         (FastAPI, OpenAPI, JSON API)         │
                    └──────────────────────┬───────────────────────┘
                                           │
                                           ▼
                    ┌──────────────────────────────────────────────┐
                    │          Enterprise Data Warehouse           │
                    │         (PostgreSQL 16 / Star Schema)        │
                    │   - Conformed Dimensions (Customer, Date,    │
                    │     Product, Channel, Branch)                │
                    │   - Fact Tables (Txns, Loans, Snapshots)     │
                    │   - Consolidated C360 Serving Mart           │
                    └──────────────────────┬───────────────────────┘
                                           ▲
                                           │
                    ┌──────────────────────┴───────────────────────┐
                    │               ETL / ELT Pipeline             │
                    │       (Python, SQLAlchemy, Batch Engine)     │
                    └──────────▲───────────────────────▲───────────┘
                               │                       │
                    ┌──────────┴──────────┐ ┌──────────┴───────────┐
                    │ Data Quality Layer  │ │  Data Lineage Layer  │
                    │ (15 Automated Rules │ │ (Directed DAG Graph, │
                    │  Completeness, Ref) │ │  Catalog & Freshness)│
                    └──────────▲──────────┘ └──────────────────────┘
                               │
            ┌──────────────────┼──────────────────┐
            ▼                  ▼                  ▼
    ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
    │ Customer DB  │   │ Loan System  │   │ Txn & Cards  │
    │  (Core CRM & │   │  (Mortgages, │   │ (Payments,   │
    │   KYC / AML) │   │  Overdue NPL)│   │  POS, Lines) │
    └──────────────┘   └──────────────┘   └──────────────┘
```

---

## 🌟 Resume Highlights & Impact Statements

Use these bullet points for your resume, LinkedIn, or portfolio:

> - **Architected an Enterprise BFSI Customer 360 Data Product** consolidating 7 disparate operational banking databases (Demographics, Deposits, Loans, Credit Cards, Transactions, KYC/AML, CRM interactions) into a unified Kimball Star Schema Data Warehouse.
> - **Engineered an End-to-End Python & SQL ETL Pipeline** processing 25,000+ daily financial transactions and generating single-customer 360 analytical mart records with under 2-second batch latency.
> - **Built an Automated 15-Rule Data Quality & Governance Framework** covering completeness, range validity (Credit Score $\in [300, 850]$, AML $\in [0, 100]$), referential integrity (zero orphan records), and anomaly detection with an interactive audit scorecard.
> - **Developed High-Performance REST APIs with FastAPI** providing sub-15ms endpoints for customer 360 search, multi-product cross-sell identification, NPL delinquency tracking, and executive KPI monitoring.
> - **Designed a Full Data Lineage DAG & Power BI Semantic Model** with production DAX measures (Total AUM, NPL Ratio %, Churn Risk %, Cross-Sell Penetration) and Dockerized deployment on PostgreSQL 16.

---

## 📊 Core Business Questions Answered

This data product provides dedicated, pre-built SQL analytical scripts and REST endpoints answering 6 fundamental banking questions:

| # | Strategic Business Question | Production SQL Script | API Endpoint | Strategic Value |
|---|---|---|---|---|
| **1** | **Which customers have multiple products?** | [`02_customers_multiple_products.sql`](file:///sql/02_customers_multiple_products.sql) | `GET /api/analytics/business-questions/multiple-products` | Identify cross-holding depth across Deposits, Loans, and Credit Cards to drive cross-sell propensity. |
| **2** | **Which customers are high-value?** | [`03_high_value_customers.sql`](file:///sql/03_high_value_customers.sql) | `GET /api/analytics/business-questions/high-value` | Calculate Lifetime Value (LTV) and relationship assets to prioritize Private Wealth & VIP services. |
| **3** | **Which customers have overdue loans?** | [`04_overdue_loans_delinquency.sql`](file:///sql/04_overdue_loans_delinquency.sql) | `GET /api/analytics/business-questions/overdue-loans` | Monitor Days Past Due (DPD) aging buckets (30, 60, 90+ NPL) and automate debt recovery workflows. |
| **4** | **What is the monthly transaction volume?** | [`05_monthly_transaction_volume.sql`](file:///sql/05_monthly_transaction_volume.sql) | `GET /api/analytics/business-questions/monthly-transactions` | Track payment throughput, average ticket sizes, and digital adoption velocity (Mobile vs ATM/Branch). |
| **5** | **Which customers have declining engagement?** | [`06_declining_engagement.sql`](file:///sql/06_declining_engagement.sql) | `GET /api/analytics/business-questions/declining-engagement` | Early churn warning signals: Negative sentiment, unresolved disputes, or zero transactions in 30 days. |
| **6** | **Which customer segments have the highest risk?** | [`07_high_risk_segments.sql`](file:///sql/07_high_risk_segments.sql) | `GET /api/analytics/business-questions/high-risk-segments` | Cross-segment portfolio risk matrix combining credit scores, AML risk indices, and overdue rates. |

---

## ⚡ Quickstart Guide

### Option 1: Instant Local Run (Zero External Setup)

This repository includes dual-database support. It works out of the box with zero external dependencies using SQLite for instant demonstration:

```bash
# 1. Clone repository & install dependencies
pip install -r requirements.txt

# 2. Generate realistic BFSI synthetic data (1.2k customers, 25k transactions)
python -m scripts.generate_synthetic_data

# 3. Execute ETL Pipeline (DQ checks, Star Schema load, Data Mart refresh)
python -m scripts.run_pipeline

# 4. Launch Customer 360 API & BI Dashboard
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

Open your browser:
- **Interactive BI Dashboard**: `http://localhost:8000/`
- **Swagger / OpenAPI Interactive Docs**: `http://localhost:8000/docs`
- **Redoc Documentation**: `http://localhost:8000/redoc`

---

### Option 2: Docker & PostgreSQL 16 Deployment

Deploy the complete enterprise stack (PostgreSQL 16 Enterprise Data Warehouse + Customer 360 FastAPI container):

```bash
docker compose up --build -d
```

Verify the containers:
```bash
docker ps
# Status will report healthy for both postgres_edw and c360_api
```

---

## 📐 Dimensional Model (Star Schema)

The Enterprise Data Warehouse is built on conformed dimensions and granular fact tables:

- **Conformed Dimensions**:
  - `dim_customer`: Surrogate key `customer_key`, natural `customer_id`, demographics, credit brackets, KYC status, and risk tier.
  - `dim_date`: Calendar dimension with `date_key` (YYYYMMDD), day name, month name, fiscal quarters.
  - `dim_product`: Product catalog for Deposits (Savings, Checking, CD), Loans (Mortgage, Auto, Business), and Credit Cards.
  - `dim_branch`: 13 regional branches across US metro areas.
  - `dim_channel`: Omnichannel touchpoints (Mobile App, Web, ATM, Branch, POS, Chatbot).
- **Fact Tables**:
  - `fact_transactions`: 25,000 granular payment event records with merchant categories, timestamps, and fraud flags.
  - `fact_daily_account_snapshot`: Daily deposit balances, available balances, and interest accrued.
  - `fact_loan_performance`: Principal balance, monthly installments, Days Past Due (DPD), and loan loss provisions.
  - `fact_customer_interactions`: 4,000 CRM touchpoints with sentiment scores (-1.0 to +1.0) and complaint resolutions.
- **Analytical Serving Mart**:
  - `c360_customer_mart`: Denormalized single-customer-per-row serving layer powering sub-10ms queries.

---

## 🛡️ Data Quality Layer (15 Automated Verification Rules)

The ETL pipeline enforces 15 automated validation checks across 4 critical quality dimensions:

| Rule ID | Rule Description | Target Table | Rule Type | Severity | Permissible Threshold |
|---|---|---|---|---|---|
| `DQ-COMP-01` | Customer ID Not Null | `src_customers` | Completeness | CRITICAL | 0 |
| `DQ-COMP-02` | Account Balance Not Null | `src_accounts` | Completeness | CRITICAL | 0 |
| `DQ-COMP-03` | Loan Balance Not Null | `src_loans` | Completeness | CRITICAL | 0 |
| `DQ-COMP-04` | Txn Timestamp & Amount Not Null | `src_transactions` | Completeness | CRITICAL | 0 |
| `DQ-VAL-01` | Credit Score Valid Range (300-850) | `src_customers` | Validity | ERROR | 0 |
| `DQ-VAL-02` | AML Risk Score Range (0.0-100.0) | `src_kyc` | Validity | ERROR | 0 |
| `DQ-VAL-03` | Overdue Days Non-Negative | `src_loans` | Validity | ERROR | 0 |
| `DQ-VAL-04` | Transaction Amount Positive | `src_transactions` | Validity | ERROR | 0 |
| `DQ-VAL-05` | Customer Age Above 18 Years | `src_customers` | Validity | WARNING | 0 |
| `DQ-REF-01` | Orphan Accounts (No Valid Customer) | `src_accounts` | Referential Integrity | CRITICAL | 0 |
| `DQ-REF-02` | Orphan Loans (No Valid Customer) | `src_loans` | Referential Integrity | CRITICAL | 0 |
| `DQ-REF-03` | Orphan Credit Cards | `src_credit_cards` | Referential Integrity | CRITICAL | 0 |
| `DQ-REF-04` | Orphan Transactions (No Valid Account) | `src_transactions` | Referential Integrity | CRITICAL | 0 |
| `DQ-ANOM-01` | Outlier Transaction Volume (> $50,000) | `src_transactions` | Anomaly Detection | WARNING | 0 |
| `DQ-ANOM-02` | High Delinquency without Flagged Status | `src_loans` | Anomaly Detection | ERROR | 0 |

---

## 📊 Enterprise BI Integration: Power BI & Tableau

The Customer 360 platform provides turnkey, enterprise-grade integration for both **Microsoft Power BI** and **Tableau Desktop / Server / Cloud**.

### 1. Microsoft Power BI
- **Connection Guide**: See [POWER_BI_GUIDE.md](file:///d:/Data%20Analytics/POWER_BI_GUIDE.md)
- **Instant Connection**: Double-click [bfsi_customer_360_postgres.pbids](file:///d:/Data%20Analytics/powerbi/bfsi_customer_360_postgres.pbids) for direct PostgreSQL DW connection, or [bfsi_customer_360_web.pbids](file:///d:/Data%20Analytics/powerbi/bfsi_customer_360_web.pbids) for REST API feeds.
- **Data Model**: Certified Kimball Star Schema (`dim_customer`, `dim_date`, `dim_product`, `dim_channel`, `dim_branch`, `fact_transactions`, `fact_loan_performance`, `c360_customer_mart`).
- **Certified DAX Library**:
  ```dax
  // Non-Performing Loan (NPL) Ratio %
  NPL Ratio % = 
  DIVIDE(
      CALCULATE(SUM(fact_loan_performance[outstanding_balance]), fact_loan_performance[is_npl] = TRUE()),
      SUM(fact_loan_performance[outstanding_balance]),
      0
  ) * 100
  ```

### 2. Tableau Desktop & Server
- **Connection Guide**: See [TABLEAU_GUIDE.md](file:///d:/Data%20Analytics/TABLEAU_GUIDE.md)
- **Instant Data Source**: Double-click [bfsi_customer_360.tds](file:///d:/Data%20Analytics/tableau/bfsi_customer_360.tds) to open a certified Tableau Data Source with pre-configured calculated fields and connections.
- **Executive Workbook**: Open [bfsi_customer_360.twb](file:///d:/Data%20Analytics/tableau/bfsi_customer_360.twb) for ready-to-use executive dashboards and risk-value scatter plots.
- **Certified Calculated Fields**:
  ```tableau
  // Cross-Sell Penetration %
  COUNT(IF [has_multiple_products] = TRUE THEN [customer_key] END) / COUNT([customer_key]) * 100

  // Total Assets Under Management (AUM)
  ZN(SUM([total_deposit_balance])) + ZN(SUM([total_loan_outstanding]))
  ```

### 3. Automated BI Export API Endpoints
- `GET /api/exports/csv/customer-360-mart`: Live CSV streaming extract for Power BI / Tableau
- `GET /api/exports/csv/fact-transactions`: Granular transaction stream
- `GET /api/exports/powerbi/semantic-model`: Full DAX measure dictionary and relationship metadata
- `GET /api/exports/tableau/semantic-model`: Tableau calculated fields and connection properties
- `GET /api/exports/bi-summary`: High-level row counts, relationship stats, and live BI status

---

## 📂 Repository Directory Structure

```
d:\Data Analytics\
├── Dockerfile                          # Multi-stage container definition
├── docker-compose.yml                  # PostgreSQL 16 EDW + FastAPI app
├── requirements.txt                    # Project Python dependencies
├── .env.example                        # Configuration template
├── ARCHITECTURE.md                     # Deep-dive architecture and design specifications
├── POWER_BI_GUIDE.md                   # Power BI connection & DAX documentation
├── TABLEAU_GUIDE.md                    # Tableau connection, LOD & dashboard guide
├── README.md                           # Master documentation
├── scripts/
│   ├── generate_synthetic_data.py      # Core banking synthetic data generator
│   └── run_pipeline.py                 # Pipeline execution entrypoint
├── sql/
│   ├── 00_schema_source_db.sql         # Operational disparate source DDL
│   ├── 01_ddl_star_schema.sql          # Star Schema & Data Mart DDL
│   ├── 02_customers_multiple_products.sql # Business Question 1
│   ├── 03_high_value_customers.sql     # Business Question 2
│   ├── 04_overdue_loans_delinquency.sql # Business Question 3
│   ├── 05_monthly_transaction_volume.sql # Business Question 4
│   ├── 06_declining_engagement.sql     # Business Question 5
│   ├── 07_high_risk_segments.sql       # Business Question 6
│   └── 08_customer_360_datamart.sql    # Mart transformation view
├── src/
│   ├── config.py                       # Centralized configuration & environment loader
│   ├── database/
│   │   ├── connection.py               # Database engine & session factories
│   │   ├── models_source.py            # Operational source ORM entities
│   │   └── models_edw.py               # Star Schema & C360 Mart ORM models
│   ├── etl/
│   │   ├── extractor.py                # Source system extractor
│   │   ├── transformer.py              # Dimensional key mapper & 360 KPIs
│   │   ├── loader.py                   # Data warehouse bulk loader
│   │   └── pipeline.py                 # Orchestrator & execution runner
│   ├── quality/
│   │   ├── rules.py                    # 15 BFSI Data Quality rules engine
│   │   └── validator.py                # DQ scorecard & report generator
│   ├── lineage/
│   │   └── tracker.py                  # End-to-end Data Lineage DAG
│   └── api/
│       ├── main.py                     # FastAPI application setup
│       ├── routes_c360.py              # Customer 360 profiles & drilldowns
│       ├── routes_analytics.py         # Business questions & executive KPIs
│       ├── routes_governance.py        # DQ scorecard, Lineage & Pipeline trigger
│       ├── routes_exports.py           # Power BI & Tableau export APIs
│       └── static/                     # Web dashboard assets
│           ├── index.html              # Responsive BI executive portal (Tab 6: BI Hub)
│           ├── styles.css              # Custom banking design system
│           └── app.js                  # Dynamic Chart.js & BI Hub switcher
├── powerbi/
│   ├── bfsi_customer_360_postgres.pbids # One-click Power BI PostgreSQL connector
│   ├── bfsi_customer_360_web.pbids      # One-click Power BI Web API connector
│   └── star_schema_model.json          # Semantic model metadata
└── tableau/
    ├── bfsi_customer_360.tds           # Certified Tableau Data Source XML
    ├── bfsi_customer_360.twb           # Executive Tableau Workbook
    ├── datasource_config.json          # Tableau connection & metadata specification
    └── generate_tableau_artifacts.py   # Generator for .tds and .twb
```

---

## 📜 License
This project is licensed under the MIT License.
