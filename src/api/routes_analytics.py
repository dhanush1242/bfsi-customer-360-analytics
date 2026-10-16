from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, case
from src.database.connection import get_warehouse_db
from src.database.models_edw import C360CustomerMart, FactTransaction, DimDate, FactLoanPerformance, DimCustomer

router = APIRouter(prefix="/api/analytics", tags=["Analytics & Business Questions"])

@router.get("/kpis")
def get_executive_kpis(db: Session = Depends(get_warehouse_db)):
    """
    Executive BFSI Portfolio KPIs for summary cards.
    """
    total_cust = db.query(func.count(C360CustomerMart.customer_key)).scalar() or 0
    total_deposits = db.query(func.sum(C360CustomerMart.total_deposit_balance)).scalar() or 0.0
    total_loans = db.query(func.sum(C360CustomerMart.total_loan_outstanding)).scalar() or 0.0
    total_credit_limit = db.query(func.sum(C360CustomerMart.total_credit_limit)).scalar() or 0.0
    total_overdue = db.query(func.sum(C360CustomerMart.total_overdue_amount)).scalar() or 0.0
    
    delinq_cust_count = db.query(func.count(C360CustomerMart.customer_key)).filter(C360CustomerMart.has_overdue_loan == True).scalar() or 0
    high_val_count = db.query(func.count(C360CustomerMart.customer_key)).filter(C360CustomerMart.is_high_value == True).scalar() or 0
    high_risk_count = db.query(func.count(C360CustomerMart.customer_key)).filter(C360CustomerMart.is_high_risk == True).scalar() or 0
    multi_prod_count = db.query(func.count(C360CustomerMart.customer_key)).filter(C360CustomerMart.has_multiple_products == True).scalar() or 0

    # 30-day Txn Volume
    txn_vol_30d = db.query(func.sum(C360CustomerMart.txn_volume_30d)).scalar() or 0.0
    txn_cnt_30d = db.query(func.sum(C360CustomerMart.txn_count_30d)).scalar() or 0

    # NPL ratio (Loans > 90 days overdue / total loans)
    npl_exposure = (
        db.query(func.sum(FactLoanPerformance.outstanding_balance))
        .filter(FactLoanPerformance.is_npl == True)
        .scalar() or 0.0
    )
    npl_ratio = round((npl_exposure / total_loans * 100), 2) if total_loans > 0 else 0.0

    return {
        "portfolio_summary": {
            "total_customers": total_cust,
            "total_deposits": round(total_deposits, 2),
            "total_loans_outstanding": round(total_loans, 2),
            "total_credit_lines": round(total_credit_limit, 2),
            "total_relationship_assets": round(total_deposits + total_loans, 2),
            "total_overdue_amount": round(total_overdue, 2),
            "delinquency_rate_pct": round((delinq_cust_count / total_cust * 100), 2) if total_cust else 0,
            "npl_ratio_pct": npl_ratio,
            "multi_product_penetration_pct": round((multi_prod_count / total_cust * 100), 2) if total_cust else 0,
            "high_value_customer_pct": round((high_val_count / total_cust * 100), 2) if total_cust else 0,
            "high_risk_customer_pct": round((high_risk_count / total_cust * 100), 2) if total_cust else 0,
            "volume_30d": round(txn_vol_30d, 2),
            "transactions_30d": txn_cnt_30d
        }
    }

# ============================================================================
# BUSINESS QUESTION 1: Which customers have multiple products?
# ============================================================================
@router.get("/business-questions/multiple-products")
def get_multiple_product_customers(
    min_products: int = Query(2, ge=2),
    segment: str = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_warehouse_db)
):
    query = db.query(C360CustomerMart).filter(C360CustomerMart.total_products_held >= min_products)
    if segment:
        query = query.filter(C360CustomerMart.customer_segment == segment)

    total_multi = query.count()
    items = query.order_by(desc(C360CustomerMart.total_products_held), desc(C360CustomerMart.total_relationship_value)).offset(offset).limit(limit).all()

    # Product distribution breakdown
    dist = (
        db.query(C360CustomerMart.total_products_held, func.count(C360CustomerMart.customer_key))
        .group_by(C360CustomerMart.total_products_held)
        .order_by(C360CustomerMart.total_products_held)
        .all()
    )

    return {
        "question": "Which customers have multiple products?",
        "total_qualifying_customers": total_multi,
        "product_holding_distribution": [{"products_held": d[0], "customer_count": d[1]} for d in dist],
        "customers": [
            {
                "customer_id": r.customer_id,
                "full_name": r.full_name,
                "customer_segment": r.customer_segment,
                "total_products_held": r.total_products_held,
                "deposit_accounts": r.deposit_accounts_count,
                "active_loans": r.active_loans_count,
                "credit_cards": r.credit_cards_count,
                "total_relationship_value": r.total_relationship_value,
                "ltv_score": r.ltv_score
            }
            for r in items
        ]
    }

# ============================================================================
# BUSINESS QUESTION 2: Which customers are high-value?
# ============================================================================
@router.get("/business-questions/high-value")
def get_high_value_customers(
    min_ltv: float = Query(60.0, ge=0.0, le=100.0),
    min_value: float = Query(50000.0, ge=0.0),
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_warehouse_db)
):
    query = db.query(C360CustomerMart).filter(
        (C360CustomerMart.is_high_value == True) | 
        (C360CustomerMart.ltv_score >= min_ltv) | 
        (C360CustomerMart.total_relationship_value >= min_value)
    )
    total_hv = query.count()
    items = query.order_by(desc(C360CustomerMart.total_relationship_value)).offset(offset).limit(limit).all()

    # Tier breakdown
    tier_stats = (
        db.query(
            C360CustomerMart.customer_segment,
            func.count(C360CustomerMart.customer_key),
            func.avg(C360CustomerMart.total_relationship_value),
            func.avg(C360CustomerMart.ltv_score)
        )
        .filter(C360CustomerMart.is_high_value == True)
        .group_by(C360CustomerMart.customer_segment)
        .all()
    )

    return {
        "question": "Which customers are high-value?",
        "total_high_value_customers": total_hv,
        "segment_breakdown": [
            {
                "segment": t[0],
                "count": t[1],
                "avg_relationship_value": round(t[2], 2),
                "avg_ltv_score": round(t[3], 1)
            }
            for t in tier_stats
        ],
        "customers": [
            {
                "customer_id": r.customer_id,
                "full_name": r.full_name,
                "customer_segment": r.customer_segment,
                "total_deposit_balance": r.total_deposit_balance,
                "total_loan_outstanding": r.total_loan_outstanding,
                "total_credit_limit": r.total_credit_limit,
                "total_relationship_value": r.total_relationship_value,
                "ltv_score": r.ltv_score,
                "risk_tier": r.risk_tier,
                "txn_volume_30d": r.txn_volume_30d
            }
            for r in items
        ]
    }

# ============================================================================
# BUSINESS QUESTION 3: Which customers have overdue loans?
# ============================================================================
@router.get("/business-questions/overdue-loans")
def get_overdue_loan_customers(
    min_overdue_days: int = Query(1, ge=0),
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_warehouse_db)
):
    query = (
        db.query(
            FactLoanPerformance,
            DimCustomer
        )
        .join(DimCustomer, FactLoanPerformance.customer_key == DimCustomer.customer_key)
        .filter(FactLoanPerformance.overdue_days >= min_overdue_days)
    )
    total_overdue = query.count()
    items = query.order_by(desc(FactLoanPerformance.overdue_days), desc(FactLoanPerformance.overdue_amount)).offset(offset).limit(limit).all()

    # Bucketing
    buckets = [
        {"bucket": "1-29 DPD (Early Warning)", "min": 1, "max": 29},
        {"bucket": "30-59 DPD (Special Mention)", "min": 30, "max": 59},
        {"bucket": "60-89 DPD (Substandard)", "min": 60, "max": 89},
        {"bucket": "90+ DPD (Default / NPL)", "min": 90, "max": 9999}
    ]
    bucket_counts = []
    for b in buckets:
        cnt = db.query(func.count(FactLoanPerformance.loan_fact_key)).filter(FactLoanPerformance.overdue_days.between(b["min"], b["max"])).scalar() or 0
        amt = db.query(func.sum(FactLoanPerformance.overdue_amount)).filter(FactLoanPerformance.overdue_days.between(b["min"], b["max"])).scalar() or 0.0
        bucket_counts.append({"bucket": b["bucket"], "loan_count": cnt, "total_overdue_amount": round(amt, 2)})

    return {
        "question": "Which customers have overdue loans?",
        "total_overdue_loans": total_overdue,
        "delinquency_aging_matrix": bucket_counts,
        "loans": [
            {
                "customer_id": cust.customer_id,
                "full_name": cust.full_name,
                "phone": cust.phone,
                "customer_segment": cust.customer_segment,
                "loan_id": lp.loan_id,
                "principal_amount": lp.principal_amount,
                "outstanding_balance": lp.outstanding_balance,
                "overdue_days": lp.overdue_days,
                "overdue_amount": lp.overdue_amount,
                "delinquency_status": lp.delinquency_status,
                "is_npl": lp.is_npl,
                "loss_provision": lp.loan_loss_provision
            }
            for lp, cust in items
        ]
    }

# ============================================================================
# BUSINESS QUESTION 4: What is the monthly transaction volume?
# ============================================================================
@router.get("/business-questions/monthly-transactions")
def get_monthly_transaction_volume(db: Session = Depends(get_warehouse_db)):
    results = (
        db.query(
            DimDate.year,
            DimDate.month,
            DimDate.month_name,
            func.count(FactTransaction.fact_txn_key).label("txn_count"),
            func.sum(FactTransaction.amount).label("total_volume"),
            func.avg(FactTransaction.amount).label("avg_ticket"),
            func.sum(case((FactTransaction.transaction_type.in_(["DEBIT", "ATM_WITHDRAWAL", "POS"]), FactTransaction.amount), else_=0.0)).label("debit_vol"),
            func.sum(case((FactTransaction.transaction_type.in_(["CREDIT", "WIRE"]), FactTransaction.amount), else_=0.0)).label("credit_vol"),
            func.sum(case((FactTransaction.is_fraud_flag == True, 1), else_=0)).label("fraud_count")
        )
        .join(DimDate, FactTransaction.date_key == DimDate.date_key)
        .group_by(DimDate.year, DimDate.month, DimDate.month_name)
        .order_by(DimDate.year, DimDate.month)
        .all()
    )

    return {
        "question": "What is the monthly transaction volume?",
        "monthly_trends": [
            {
                "period": f"{r.year}-{r.month:02d}",
                "year": r.year,
                "month": r.month,
                "month_name": r.month_name,
                "transaction_count": r.txn_count,
                "total_volume": round(r.total_volume or 0.0, 2),
                "average_ticket_size": round(r.avg_ticket or 0.0, 2),
                "debit_volume": round(r.debit_vol or 0.0, 2),
                "credit_volume": round(r.credit_vol or 0.0, 2),
                "fraud_transactions_flagged": r.fraud_count
            }
            for r in results
        ]
    }

# ============================================================================
# BUSINESS QUESTION 5: Which customers have declining engagement?
# ============================================================================
@router.get("/business-questions/declining-engagement")
def get_declining_engagement_customers(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_warehouse_db)
):
    query = db.query(C360CustomerMart).filter(
        (C360CustomerMart.engagement_status.in_(["DECLINING", "DORMANT"])) |
        (C360CustomerMart.avg_sentiment_score < -0.1) |
        (C360CustomerMart.unresolved_complaints_count > 0)
    )
    total_declining = query.count()
    items = query.order_by(desc(C360CustomerMart.total_relationship_value), C360CustomerMart.avg_sentiment_score.asc()).offset(offset).limit(limit).all()

    # Breakdown by engagement status
    breakdown = (
        db.query(C360CustomerMart.engagement_status, func.count(C360CustomerMart.customer_key))
        .group_by(C360CustomerMart.engagement_status)
        .all()
    )

    return {
        "question": "Which customers have declining engagement?",
        "total_at_risk_customers": total_declining,
        "engagement_status_breakdown": [{"status": b[0], "count": b[1]} for b in breakdown],
        "customers": [
            {
                "customer_id": r.customer_id,
                "full_name": r.full_name,
                "customer_segment": r.customer_segment,
                "total_relationship_value": r.total_relationship_value,
                "engagement_status": r.engagement_status,
                "avg_sentiment_score": r.avg_sentiment_score,
                "unresolved_complaints": r.unresolved_complaints_count,
                "txn_count_30d": r.txn_count_30d,
                "interactions_count_90d": r.interactions_count_90d
            }
            for r in items
        ]
    }

# ============================================================================
# BUSINESS QUESTION 6: Which customer segments have the highest risk?
# ============================================================================
@router.get("/business-questions/high-risk-segments")
def get_high_risk_segments(db: Session = Depends(get_warehouse_db)):
    results = (
        db.query(
            C360CustomerMart.customer_segment,
            func.count(C360CustomerMart.customer_key).label("cust_count"),
            func.avg(C360CustomerMart.credit_score).label("avg_credit_score"),
            func.avg(C360CustomerMart.aml_risk_score).label("avg_aml_score"),
            func.avg(C360CustomerMart.composite_risk_score).label("avg_composite_risk"),
            func.sum(case((C360CustomerMart.has_overdue_loan == True, 1), else_=0)).label("overdue_cust_count"),
            func.sum(C360CustomerMart.total_overdue_amount).label("total_overdue_amt"),
            func.sum(case((C360CustomerMart.is_high_risk == True, 1), else_=0)).label("high_risk_count"),
            func.sum(C360CustomerMart.total_deposit_balance).label("total_deposits"),
            func.sum(C360CustomerMart.total_loan_outstanding).label("total_loans")
        )
        .group_by(C360CustomerMart.customer_segment)
        .order_by(desc("avg_composite_risk"))
        .all()
    )

    return {
        "question": "Which customer segments have the highest risk?",
        "segments": [
            {
                "customer_segment": r.customer_segment,
                "total_customers": r.cust_count,
                "avg_credit_score": round(r.avg_credit_score, 1),
                "avg_aml_risk_score": round(r.avg_aml_score, 2),
                "avg_composite_risk_score": round(r.avg_composite_risk, 2),
                "overdue_customers_count": r.overdue_cust_count,
                "delinquency_rate_pct": round((r.overdue_cust_count / r.cust_count * 100), 2) if r.cust_count else 0,
                "total_overdue_amount": round(r.total_overdue_amt or 0.0, 2),
                "high_risk_customers_count": r.high_risk_count,
                "high_risk_pct": round((r.high_risk_count / r.cust_count * 100), 2) if r.cust_count else 0,
                "total_deposits": round(r.total_deposits or 0.0, 2),
                "total_loans": round(r.total_loans or 0.0, 2),
                "risk_rating": "HIGH RISK" if r.avg_composite_risk >= 35 or (r.overdue_cust_count / r.cust_count > 0.15) else ("MODERATE RISK" if r.avg_composite_risk >= 25 else "LOW RISK")
            }
            for r in results
        ]
    }
