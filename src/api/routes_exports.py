"""
BI Export Routes — Power BI & Tableau Data Integration Endpoints
Provides export endpoints for data extracts, semantic model metadata,
DAX measures, Tableau calculated fields, and relationship definitions.
"""
import csv
import io
import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, case

from src.database.connection import get_warehouse_db
from src.database.models_edw import (
    C360CustomerMart,
    FactTransaction,
    FactLoanPerformance,
    FactDailyAccountSnapshot,
    DimCustomer,
    DimDate,
    DimProduct,
    DimChannel,
)

router = APIRouter(prefix="/api/exports", tags=["BI Exports — Power BI & Tableau"])


# ============================================================================
# 1. CSV Data Extracts (for Power BI Import & Tableau)
# ============================================================================
@router.get("/csv/customer-360-mart")
def export_c360_mart_csv(
    limit: int = Query(5000, ge=1, le=50000),
    db: Session = Depends(get_warehouse_db),
):
    """
    Export the full Customer 360 Serving Mart as CSV for Power BI Import or Tableau Extract.
    """
    rows = (
        db.query(C360CustomerMart)
        .order_by(C360CustomerMart.customer_key)
        .limit(limit)
        .all()
    )

    columns = [
        "customer_key", "customer_id", "full_name", "email", "phone",
        "city", "state", "age", "age_bracket", "annual_income", "income_bracket",
        "customer_segment", "credit_score", "kyc_status", "aml_risk_score",
        "risk_tier", "composite_risk_score",
        "deposit_accounts_count", "active_loans_count", "credit_cards_count",
        "total_products_held", "has_multiple_products",
        "total_deposit_balance", "total_loan_outstanding", "total_credit_limit",
        "total_credit_outstanding", "credit_utilization_pct",
        "total_overdue_amount", "max_overdue_days", "has_overdue_loan",
        "total_relationship_value", "ltv_score",
        "is_high_value", "is_high_risk",
        "txn_volume_30d", "txn_count_30d",
        "avg_sentiment_score", "unresolved_complaints_count",
        "interactions_count_90d", "engagement_status",
    ]

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(columns)

    for row in rows:
        writer.writerow([getattr(row, col, "") for col in columns])

    output.seek(0)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="bfsi_c360_mart_{timestamp}.csv"'
        },
    )


@router.get("/csv/fact-transactions")
def export_transactions_csv(
    limit: int = Query(10000, ge=1, le=100000),
    db: Session = Depends(get_warehouse_db),
):
    """
    Export fact_transactions with dimension attributes denormalized for BI tool import.
    """
    rows = (
        db.query(
            FactTransaction.fact_txn_key,
            FactTransaction.transaction_id,
            DimCustomer.customer_id,
            DimCustomer.full_name,
            DimCustomer.customer_segment,
            DimDate.full_date,
            DimDate.month_name,
            DimDate.year,
            DimDate.quarter,
            FactTransaction.transaction_type,
            FactTransaction.amount,
            FactTransaction.merchant_category,
            FactTransaction.status,
            FactTransaction.is_fraud_flag,
        )
        .join(DimCustomer, FactTransaction.customer_key == DimCustomer.customer_key)
        .join(DimDate, FactTransaction.date_key == DimDate.date_key)
        .order_by(FactTransaction.fact_txn_key)
        .limit(limit)
        .all()
    )

    columns = [
        "fact_txn_key", "transaction_id", "customer_id", "full_name",
        "customer_segment", "full_date", "month_name", "year", "quarter",
        "transaction_type", "amount", "merchant_category",
        "status", "is_fraud_flag",
    ]

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(columns)
    for row in rows:
        writer.writerow(list(row))

    output.seek(0)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="bfsi_transactions_{timestamp}.csv"'
        },
    )


@router.get("/csv/loan-performance")
def export_loan_performance_csv(
    limit: int = Query(5000, ge=1, le=50000),
    db: Session = Depends(get_warehouse_db),
):
    """
    Export fact_loan_performance with customer dimension denormalized.
    """
    rows = (
        db.query(
            FactLoanPerformance.loan_fact_key,
            FactLoanPerformance.loan_id,
            DimCustomer.customer_id,
            DimCustomer.full_name,
            DimCustomer.customer_segment,
            DimCustomer.credit_score,
            FactLoanPerformance.principal_amount,
            FactLoanPerformance.outstanding_balance,
            FactLoanPerformance.monthly_installment,
            FactLoanPerformance.overdue_days,
            FactLoanPerformance.overdue_amount,
            FactLoanPerformance.delinquency_status,
            FactLoanPerformance.is_npl,
            FactLoanPerformance.loan_loss_provision,
        )
        .join(DimCustomer, FactLoanPerformance.customer_key == DimCustomer.customer_key)
        .order_by(desc(FactLoanPerformance.overdue_days))
        .limit(limit)
        .all()
    )

    columns = [
        "loan_fact_key", "loan_id", "customer_id", "full_name",
        "customer_segment", "credit_score",
        "principal_amount", "outstanding_balance", "monthly_installment",
        "overdue_days", "overdue_amount", "delinquency_status",
        "is_npl", "loan_loss_provision",
    ]

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(columns)
    for row in rows:
        writer.writerow(list(row))

    output.seek(0)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="bfsi_loan_performance_{timestamp}.csv"'
        },
    )


# ============================================================================
# 2. Power BI Semantic Model & DAX Measures Library
# ============================================================================
@router.get("/powerbi/semantic-model")
def get_powerbi_semantic_model():
    """
    Return the full Power BI semantic model definition (star schema entities,
    relationships, and DAX measure library) as structured JSON for .pbit import.
    """
    return {
        "model_name": "BFSI_Customer_360_Semantic_Model",
        "model_version": "2.0",
        "platform": "Power BI",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "entities": [
            {
                "name": "dim_customer",
                "type": "Dimension",
                "primary_key": "customer_key",
                "attributes": [
                    "customer_id", "full_name", "email", "phone", "city", "state",
                    "age", "age_bracket", "annual_income", "income_bracket",
                    "customer_segment", "credit_score", "kyc_status", "risk_tier",
                ],
            },
            {
                "name": "dim_date",
                "type": "Dimension",
                "primary_key": "date_key",
                "attributes": [
                    "full_date", "day_name", "month", "month_name",
                    "quarter", "year", "fiscal_quarter",
                ],
            },
            {
                "name": "dim_product",
                "type": "Dimension",
                "primary_key": "product_key",
                "attributes": [
                    "product_id", "product_category", "product_sub_type",
                    "product_name", "standard_interest_rate",
                ],
            },
            {
                "name": "dim_channel",
                "type": "Dimension",
                "primary_key": "channel_key",
                "attributes": ["channel_code", "channel_name", "channel_type"],
            },
            {
                "name": "dim_branch",
                "type": "Dimension",
                "primary_key": "branch_key",
                "attributes": ["branch_code", "branch_name", "city", "state"],
            },
            {
                "name": "fact_transactions",
                "type": "Fact",
                "foreign_keys": [
                    "customer_key", "date_key", "product_key", "channel_key",
                ],
                "measures": ["amount", "fee_amount", "is_fraud_flag"],
            },
            {
                "name": "fact_loan_performance",
                "type": "Fact",
                "foreign_keys": ["customer_key", "date_key", "product_key"],
                "measures": [
                    "principal_amount", "outstanding_balance", "overdue_days",
                    "overdue_amount", "loan_loss_provision",
                ],
            },
            {
                "name": "fact_daily_account_snapshot",
                "type": "Fact",
                "foreign_keys": ["customer_key", "date_key"],
                "measures": [
                    "current_balance", "available_balance", "interest_accrued",
                ],
            },
            {
                "name": "fact_customer_interactions",
                "type": "Fact",
                "foreign_keys": ["customer_key", "date_key"],
                "measures": ["sentiment_score"],
            },
            {
                "name": "c360_customer_mart",
                "type": "ServingMart",
                "primary_key": "customer_key",
                "measures": [
                    "total_deposit_balance", "total_loan_outstanding",
                    "total_credit_limit", "total_products_held",
                    "ltv_score", "composite_risk_score", "txn_volume_30d",
                ],
            },
        ],
        "relationships": [
            {"from_table": "dim_customer", "from_column": "customer_key", "to_table": "fact_transactions", "to_column": "customer_key", "cardinality": "1:*", "cross_filter": "Single"},
            {"from_table": "dim_customer", "from_column": "customer_key", "to_table": "fact_daily_account_snapshot", "to_column": "customer_key", "cardinality": "1:*", "cross_filter": "Single"},
            {"from_table": "dim_customer", "from_column": "customer_key", "to_table": "fact_loan_performance", "to_column": "customer_key", "cardinality": "1:*", "cross_filter": "Single"},
            {"from_table": "dim_customer", "from_column": "customer_key", "to_table": "fact_customer_interactions", "to_column": "customer_key", "cardinality": "1:*", "cross_filter": "Single"},
            {"from_table": "dim_customer", "from_column": "customer_key", "to_table": "c360_customer_mart", "to_column": "customer_key", "cardinality": "1:*", "cross_filter": "Single"},
            {"from_table": "dim_date", "from_column": "date_key", "to_table": "fact_transactions", "to_column": "date_key", "cardinality": "1:*", "cross_filter": "Single"},
            {"from_table": "dim_date", "from_column": "date_key", "to_table": "fact_daily_account_snapshot", "to_column": "date_key", "cardinality": "1:*", "cross_filter": "Single"},
            {"from_table": "dim_date", "from_column": "date_key", "to_table": "fact_loan_performance", "to_column": "date_key", "cardinality": "1:*", "cross_filter": "Single"},
            {"from_table": "dim_product", "from_column": "product_key", "to_table": "fact_transactions", "to_column": "product_key", "cardinality": "1:*", "cross_filter": "Single"},
            {"from_table": "dim_channel", "from_column": "channel_key", "to_table": "fact_transactions", "to_column": "channel_key", "cardinality": "1:*", "cross_filter": "Single"},
        ],
        "dax_measures": [
            {
                "name": "Cross-Sell Ratio %",
                "expression": 'DIVIDE(CALCULATE(COUNTROWS(c360_customer_mart), c360_customer_mart[has_multiple_products] = TRUE()), COUNTROWS(c360_customer_mart), 0) * 100',
                "category": "Cross-Sell",
                "description": "Percentage of customers holding 2+ banking product lines",
            },
            {
                "name": "Total AUM",
                "expression": "SUM(c360_customer_mart[total_deposit_balance]) + SUM(c360_customer_mart[total_loan_outstanding])",
                "category": "Portfolio",
                "description": "Total Assets Under Management across deposits and loans",
            },
            {
                "name": "NPL Ratio %",
                "expression": 'DIVIDE(CALCULATE(SUM(fact_loan_performance[outstanding_balance]), fact_loan_performance[is_npl] = TRUE()), SUM(fact_loan_performance[outstanding_balance]), 0) * 100',
                "category": "Risk",
                "description": "Non-Performing Loan ratio as percentage of total loan book",
            },
            {
                "name": "Delinquency Rate %",
                "expression": 'DIVIDE(CALCULATE(COUNTROWS(c360_customer_mart), c360_customer_mart[has_overdue_loan] = TRUE()), COUNTROWS(c360_customer_mart), 0) * 100',
                "category": "Risk",
                "description": "Percentage of customers with overdue loans",
            },
            {
                "name": "Avg LTV Score",
                "expression": "AVERAGE(c360_customer_mart[ltv_score])",
                "category": "Customer Value",
                "description": "Average Customer Lifetime Value score (0-100)",
            },
            {
                "name": "Card Utilization %",
                "expression": "DIVIDE(SUM(c360_customer_mart[total_credit_outstanding]), SUM(c360_customer_mart[total_credit_limit]), 0) * 100",
                "category": "Credit",
                "description": "Net credit card utilization percentage across portfolio",
            },
            {
                "name": "Churn Risk Rate %",
                "expression": 'DIVIDE(CALCULATE(COUNTROWS(c360_customer_mart), c360_customer_mart[engagement_status] = "DECLINING" || c360_customer_mart[engagement_status] = "DORMANT"), COUNTROWS(c360_customer_mart), 0) * 100',
                "category": "Engagement",
                "description": "Percentage of customers with declining or dormant engagement",
            },
        ],
    }


# ============================================================================
# 3. Tableau Semantic Model & Calculated Fields Library
# ============================================================================
@router.get("/tableau/semantic-model")
def get_tableau_semantic_model():
    """
    Return the Tableau semantic model definition with calculated fields,
    table relationships, and data source metadata.
    """
    return {
        "model_name": "BFSI_Customer_360_Tableau_DataSource",
        "model_version": "2.0",
        "platform": "Tableau",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "connection": {
            "class": "postgres",
            "server": "localhost",
            "port": 5432,
            "dbname": "bfsi_enterprise_dw",
            "authentication": "password",
        },
        "tables": [
            {"name": "dim_customer", "role": "Dimension", "alias": "Customer", "join_key": "customer_key"},
            {"name": "dim_date", "role": "Dimension", "alias": "Date", "join_key": "date_key"},
            {"name": "dim_product", "role": "Dimension", "alias": "Product", "join_key": "product_key"},
            {"name": "dim_channel", "role": "Dimension", "alias": "Channel", "join_key": "channel_key"},
            {"name": "dim_branch", "role": "Dimension", "alias": "Branch", "join_key": "branch_key"},
            {"name": "fact_transactions", "role": "Fact", "alias": "Transactions", "foreign_keys": ["customer_key", "date_key", "product_key", "channel_key"]},
            {"name": "fact_daily_account_snapshot", "role": "Fact", "alias": "Account Snapshots", "foreign_keys": ["customer_key", "date_key"]},
            {"name": "fact_loan_performance", "role": "Fact", "alias": "Loan Performance", "foreign_keys": ["customer_key", "date_key", "product_key"]},
            {"name": "fact_customer_interactions", "role": "Fact", "alias": "CRM Interactions", "foreign_keys": ["customer_key", "date_key"]},
            {"name": "c360_customer_mart", "role": "ServingMart", "alias": "Customer 360 Mart", "join_key": "customer_key"},
        ],
        "calculated_fields": [
            {
                "name": "Total AUM",
                "formula": "[Total Deposit Balance] + [Total Loan Outstanding]",
                "category": "Portfolio",
                "description": "Assets Under Management across all products",
            },
            {
                "name": "NPL Flag",
                "formula": 'IF [Overdue Days] >= 90 THEN "NPL" ELSE "Performing" END',
                "category": "Risk",
                "description": "Non-Performing Loan classification based on 90+ DPD",
            },
            {
                "name": "Delinquency Bucket",
                "formula": 'IF [Overdue Days] = 0 THEN "Current" ELSEIF [Overdue Days] < 30 THEN "1-29 DPD" ELSEIF [Overdue Days] < 60 THEN "30-59 DPD" ELSEIF [Overdue Days] < 90 THEN "60-89 DPD" ELSE "90+ DPD (NPL)" END',
                "category": "Risk",
                "description": "Days Past Due aging bucket classification",
            },
            {
                "name": "Credit Utilization %",
                "formula": "IF [Total Credit Limit] > 0 THEN [Total Credit Outstanding] / [Total Credit Limit] * 100 ELSE 0 END",
                "category": "Credit",
                "description": "Credit card utilization percentage",
            },
            {
                "name": "Customer Risk Category",
                "formula": 'IF [Composite Risk Score] >= 50 THEN "Critical" ELSEIF [Composite Risk Score] >= 35 THEN "High" ELSEIF [Composite Risk Score] >= 20 THEN "Medium" ELSE "Low" END',
                "category": "Risk",
                "description": "Risk tier classification based on composite score",
            },
            {
                "name": "Cross-Sell Flag",
                "formula": 'IF [Total Products Held] >= 2 THEN "Multi-Product" ELSE "Single Product" END',
                "category": "Cross-Sell",
                "description": "Multi-product customer identification for cross-sell analysis",
            },
            {
                "name": "Churn Risk Indicator",
                "formula": 'IF [Engagement Status] = "DECLINING" OR [Engagement Status] = "DORMANT" THEN "At Risk" ELSEIF [Avg Sentiment Score] < -0.1 THEN "Negative Sentiment" ELSEIF [Txn Count 30d] = 0 THEN "Inactive" ELSE "Healthy" END',
                "category": "Engagement",
                "description": "Early warning churn signal combining engagement and sentiment",
            },
        ],
        "recommended_dashboards": [
            {"name": "Executive Banking Overview", "worksheets": ["Portfolio KPI Bar", "Monthly Transaction Volume", "Customer Segment Treemap", "Risk Heatmap"]},
            {"name": "Loan Portfolio & NPL Tracker", "worksheets": ["Delinquency Aging Waterfall", "NPL Exposure Treemap", "Loss Provision Trend", "Top Delinquent Customers"]},
            {"name": "Customer 360 Profile Drill-Down", "worksheets": ["Customer Search", "Financial Snapshot", "Transaction Timeline", "Sentiment Analysis"]},
            {"name": "Channel & Digital Adoption", "worksheets": ["Channel Distribution", "Digital vs Physical", "Channel Trend"]},
        ],
    }


# ============================================================================
# 4. BI Integration Summary Stats
# ============================================================================
@router.get("/bi-summary")
def get_bi_integration_summary(db: Session = Depends(get_warehouse_db)):
    """
    Summary statistics for the BI Integration Hub — record counts, data freshness,
    and export availability across Power BI and Tableau.
    """
    total_customers = db.query(func.count(C360CustomerMart.customer_key)).scalar() or 0
    total_transactions = db.query(func.count(FactTransaction.fact_txn_key)).scalar() or 0
    total_loans = db.query(func.count(FactLoanPerformance.loan_fact_key)).scalar() or 0
    total_dimensions = (
        (db.query(func.count(DimCustomer.customer_key)).scalar() or 0)
        + (db.query(func.count(DimDate.date_key)).scalar() or 0)
        + (db.query(func.count(DimProduct.product_key)).scalar() or 0)
        + (db.query(func.count(DimChannel.channel_key)).scalar() or 0)
    )

    return {
        "data_warehouse": {
            "total_c360_records": total_customers,
            "total_transactions": total_transactions,
            "total_loan_records": total_loans,
            "total_dimension_records": total_dimensions,
            "schema_type": "Kimball Star Schema",
            "database": "PostgreSQL 16 / SQLite",
        },
        "power_bi": {
            "status": "Ready",
            "semantic_model_version": "2.0",
            "dax_measures_count": 7,
            "relationships_count": 10,
            "connection_modes": ["DirectQuery", "Import", "REST API / Web"],
            "export_formats": ["CSV", "JSON Semantic Model"],
        },
        "tableau": {
            "status": "Ready",
            "datasource_version": "2.0",
            "calculated_fields_count": 7,
            "relationships_count": 10,
            "connection_modes": ["PostgreSQL Direct", "CSV Extract", "Web Data Connector"],
            "export_formats": ["CSV", "JSON Data Source Config"],
            "recommended_dashboards": 4,
        },
        "export_endpoints": {
            "csv_customer_360": "/api/exports/csv/customer-360-mart",
            "csv_transactions": "/api/exports/csv/fact-transactions",
            "csv_loan_performance": "/api/exports/csv/loan-performance",
            "powerbi_semantic_model": "/api/exports/powerbi/semantic-model",
            "tableau_semantic_model": "/api/exports/tableau/semantic-model",
        },
    }
