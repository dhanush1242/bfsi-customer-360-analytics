from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from typing import Optional

from src.database.connection import get_warehouse_db, get_source_db
from src.database.models_edw import C360CustomerMart, DimCustomer, FactDailyAccountSnapshot, FactLoanPerformance, FactTransaction, FactCustomerInteraction
from src.database.models_source import SourceCreditCard, SourceKYC

router = APIRouter(prefix="/api/c360", tags=["Customer 360"])

@router.get("/customers")
def get_customers(
    search: Optional[str] = None,
    segment: Optional[str] = None,
    risk_tier: Optional[str] = None,
    has_overdue: Optional[bool] = None,
    has_multiple_products: Optional[bool] = None,
    is_high_value: Optional[bool] = None,
    engagement_status: Optional[str] = None,
    sort_by: str = Query("total_relationship_value", pattern="^(total_relationship_value|ltv_score|composite_risk_score|total_deposit_balance|total_loan_outstanding|max_overdue_days|credit_score)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_warehouse_db)
):
    """
    Search and filter customers with multidimensional BFSI attributes.
    """
    query = db.query(C360CustomerMart)

    if search:
        term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                C360CustomerMart.full_name.ilike(term),
                C360CustomerMart.customer_id.ilike(term),
                C360CustomerMart.email.ilike(term),
                C360CustomerMart.city.ilike(term)
            )
        )

    if segment:
        query = query.filter(C360CustomerMart.customer_segment == segment)
    if risk_tier:
        query = query.filter(C360CustomerMart.risk_tier == risk_tier)
    if has_overdue is not None:
        query = query.filter(C360CustomerMart.has_overdue_loan == has_overdue)
    if has_multiple_products is not None:
        query = query.filter(C360CustomerMart.has_multiple_products == has_multiple_products)
    if is_high_value is not None:
        query = query.filter(C360CustomerMart.is_high_value == is_high_value)
    if engagement_status:
        query = query.filter(C360CustomerMart.engagement_status == engagement_status)

    total_count = query.count()

    order_col = getattr(C360CustomerMart, sort_by)
    if sort_order == "desc":
        query = query.order_by(desc(order_col))
    else:
        query = query.order_by(order_col)

    records = query.offset(offset).limit(limit).all()

    return {
        "total": total_count,
        "offset": offset,
        "limit": limit,
        "items": [
            {
                "customer_id": r.customer_id,
                "full_name": r.full_name,
                "email": r.email,
                "phone": r.phone,
                "city": r.city,
                "state": r.state,
                "customer_segment": r.customer_segment,
                "credit_score": r.credit_score,
                "credit_score_bracket": r.credit_score_bracket,
                "kyc_status": r.kyc_status,
                "risk_tier": r.risk_tier,
                "total_products_held": r.total_products_held,
                "has_multiple_products": r.has_multiple_products,
                "total_deposit_balance": r.total_deposit_balance,
                "total_loan_outstanding": r.total_loan_outstanding,
                "total_credit_limit": r.total_credit_limit,
                "total_relationship_value": r.total_relationship_value,
                "ltv_score": r.ltv_score,
                "is_high_value": r.is_high_value,
                "has_overdue_loan": r.has_overdue_loan,
                "max_overdue_days": r.max_overdue_days,
                "total_overdue_amount": r.total_overdue_amount,
                "txn_count_30d": r.txn_count_30d,
                "txn_volume_30d": r.txn_volume_30d,
                "avg_sentiment_score": r.avg_sentiment_score,
                "engagement_status": r.engagement_status,
                "composite_risk_score": r.composite_risk_score,
                "is_high_risk": r.is_high_risk
            }
            for r in records
        ]
    }

@router.get("/customers/{customer_id}")
def get_customer_360_profile(
    customer_id: str,
    db: Session = Depends(get_warehouse_db),
    src_db: Session = Depends(get_source_db)
):
    """
    Consolidated Customer 360 View:
    Demographics, Accounts, Loans, Cards, KYC, Recent Txns, CRM Interactions.
    """
    mart_rec = db.query(C360CustomerMart).filter(C360CustomerMart.customer_id == customer_id).first()
    if not mart_rec:
        raise HTTPException(status_code=404, detail="Customer not found in 360 data product")

    dim_cust = db.query(DimCustomer).filter(DimCustomer.customer_id == customer_id).first()

    # Deposit Accounts
    accounts = db.query(FactDailyAccountSnapshot).filter(FactDailyAccountSnapshot.customer_key == mart_rec.customer_key).all()
    
    # Active Loans
    loans = db.query(FactLoanPerformance).filter(FactLoanPerformance.customer_key == mart_rec.customer_key).all()

    # Credit Cards (from source repository or credit card model)
    cards = src_db.query(SourceCreditCard).filter(SourceCreditCard.customer_id == customer_id).all()

    # KYC Info
    kyc = src_db.query(SourceKYC).filter(SourceKYC.customer_id == customer_id).first()

    # Recent Transactions (last 15)
    txns = (
        db.query(FactTransaction)
        .filter(FactTransaction.customer_key == mart_rec.customer_key)
        .order_by(desc(FactTransaction.created_timestamp))
        .limit(15)
        .all()
    )

    # Recent Interactions (last 10)
    interactions = (
        db.query(FactCustomerInteraction)
        .filter(FactCustomerInteraction.customer_key == mart_rec.customer_key)
        .limit(10)
        .all()
    )

    return {
        "summary": {
            "customer_id": mart_rec.customer_id,
            "full_name": mart_rec.full_name,
            "email": mart_rec.email,
            "phone": mart_rec.phone,
            "age": dim_cust.age if dim_cust else 35,
            "gender": dim_cust.gender if dim_cust else "N/A",
            "occupation": dim_cust.occupation if dim_cust else "N/A",
            "city": mart_rec.city,
            "state": mart_rec.state,
            "customer_segment": mart_rec.customer_segment,
            "credit_score": mart_rec.credit_score,
            "credit_score_bracket": mart_rec.credit_score_bracket,
            "risk_tier": mart_rec.risk_tier,
            "composite_risk_score": mart_rec.composite_risk_score,
            "is_high_risk": mart_rec.is_high_risk,
            "ltv_score": mart_rec.ltv_score,
            "is_high_value": mart_rec.is_high_value,
            "engagement_status": mart_rec.engagement_status,
            "total_products_held": mart_rec.total_products_held,
            "has_multiple_products": mart_rec.has_multiple_products,
            "total_relationship_value": mart_rec.total_relationship_value,
            "total_deposit_balance": mart_rec.total_deposit_balance,
            "total_loan_outstanding": mart_rec.total_loan_outstanding,
            "total_credit_limit": mart_rec.total_credit_limit,
            "credit_utilization_pct": mart_rec.credit_utilization_pct,
            "has_overdue_loan": mart_rec.has_overdue_loan,
            "max_overdue_days": mart_rec.max_overdue_days,
            "total_overdue_amount": mart_rec.total_overdue_amount,
            "avg_sentiment_score": mart_rec.avg_sentiment_score,
            "last_synced_at": mart_rec.last_synced_at.isoformat() if mart_rec.last_synced_at else None
        },
        "kyc": {
            "kyc_id": kyc.kyc_id if kyc else None,
            "id_type": kyc.id_type if kyc else "N/A",
            "id_number_masked": kyc.id_number_masked if kyc else "N/A",
            "kyc_status": kyc.kyc_status if kyc else mart_rec.kyc_status,
            "aml_risk_score": kyc.aml_risk_score if kyc else 0.0,
            "pep_flag": kyc.pep_flag if kyc else False,
            "sanctions_check": kyc.sanctions_check if kyc else "PASSED",
            "last_reviewed_at": kyc.last_reviewed_at.isoformat() if kyc and kyc.last_reviewed_at else None
        },
        "accounts": [
            {
                "account_id": a.account_id,
                "current_balance": a.current_balance,
                "available_balance": a.available_balance,
                "interest_rate": a.interest_rate,
                "status": a.status
            }
            for a in accounts
        ],
        "loans": [
            {
                "loan_id": l.loan_id,
                "principal_amount": l.principal_amount,
                "outstanding_balance": l.outstanding_balance,
                "monthly_installment": l.monthly_installment,
                "overdue_days": l.overdue_days,
                "overdue_amount": l.overdue_amount,
                "delinquency_status": l.delinquency_status,
                "is_npl": l.is_npl,
                "loan_loss_provision": l.loan_loss_provision
            }
            for l in loans
        ],
        "credit_cards": [
            {
                "card_id": c.card_id,
                "card_tier": c.card_tier,
                "card_number_masked": c.card_number_masked,
                "credit_limit": c.credit_limit,
                "current_outstanding": c.current_outstanding,
                "available_credit": c.available_credit,
                "apr_rate": c.apr_rate,
                "status": c.status
            }
            for c in cards
        ],
        "recent_transactions": [
            {
                "transaction_id": t.transaction_id,
                "transaction_type": t.transaction_type,
                "amount": t.amount,
                "merchant_category": t.merchant_category,
                "status": t.status,
                "is_fraud_flag": t.is_fraud_flag,
                "timestamp": t.created_timestamp.isoformat()
            }
            for t in txns
        ],
        "interactions": [
            {
                "interaction_id": i.interaction_id,
                "interaction_type": i.interaction_type,
                "sentiment": i.sentiment,
                "sentiment_score": i.sentiment_score,
                "duration_minutes": i.duration_minutes,
                "is_complaint": i.is_complaint,
                "resolution_status": i.resolution_status
            }
            for i in interactions
        ]
    }
