from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Boolean, ForeignKey, Text
from src.database.connection import WarehouseBase

# ==========================================
# CONFORMED DIMENSION TABLES
# ==========================================

class DimDate(WarehouseBase):
    __tablename__ = "dim_date"

    date_key = Column(Integer, primary_key=True) # e.g. 20261005
    full_date = Column(Date, nullable=False, unique=True, index=True)
    day_of_month = Column(Integer, nullable=False)
    day_name = Column(String(15), nullable=False)
    day_of_week = Column(Integer, nullable=False) # 1-7
    is_weekend = Column(Boolean, nullable=False)
    month = Column(Integer, nullable=False) # 1-12
    month_name = Column(String(15), nullable=False)
    quarter = Column(Integer, nullable=False) # 1-4
    year = Column(Integer, nullable=False)
    fiscal_quarter = Column(String(10), nullable=False)

class DimCustomer(WarehouseBase):
    __tablename__ = "dim_customer"

    customer_key = Column(Integer, primary_key=True, autoincrement=True) # Surrogate Key
    customer_id = Column(String(50), nullable=False, unique=True, index=True) # Natural Key
    full_name = Column(String(200), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False)
    phone = Column(String(30))
    age = Column(Integer, nullable=False)
    age_bracket = Column(String(30)) # 18-25, 26-35, 36-50, 51-65, 65+
    gender = Column(String(10))
    annual_income = Column(Float, nullable=False)
    income_bracket = Column(String(50)) # <$30k, $30k-$75k, $75k-$150k, $150k+
    occupation = Column(String(100))
    city = Column(String(100), nullable=False)
    state = Column(String(50), nullable=False)
    country = Column(String(50), default="USA")
    branch_id = Column(String(20))
    customer_segment = Column(String(50), nullable=False, index=True) # Retail, Affluent, HNI, Ultra HNI, Corporate
    credit_score = Column(Integer, nullable=False)
    credit_score_bracket = Column(String(30)) # Poor (<580), Fair (580-669), Good (670-739), Very Good (740-799), Exceptional (800+)
    kyc_status = Column(String(30), nullable=False) # VERIFIED, PENDING_REVIEW, REJECTED, EXPIRED
    aml_risk_score = Column(Float, default=0.0)
    pep_flag = Column(Boolean, default=False)
    risk_tier = Column(String(20), default="LOW", index=True) # LOW, MEDIUM, HIGH, CRITICAL
    onboarded_date = Column(Date)
    is_active = Column(Boolean, default=True)

class DimProduct(WarehouseBase):
    __tablename__ = "dim_product"

    product_key = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(String(50), nullable=False, unique=True, index=True)
    product_category = Column(String(50), nullable=False, index=True) # DEPOSIT, LOAN, CREDIT_CARD, WEALTH
    product_sub_type = Column(String(100), nullable=False) # Savings, Checking, Home Mortgage, Platinum Card
    product_name = Column(String(150), nullable=False)
    standard_interest_rate = Column(Float, default=0.0)
    risk_weight = Column(Float, default=1.0)

class DimBranch(WarehouseBase):
    __tablename__ = "dim_branch"

    branch_key = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(String(20), nullable=False, unique=True, index=True)
    branch_name = Column(String(100), nullable=False)
    region = Column(String(50), nullable=False) # Northeast, Southeast, Midwest, Southwest, West
    city = Column(String(100), nullable=False)
    state = Column(String(50), nullable=False)

class DimChannel(WarehouseBase):
    __tablename__ = "dim_channel"

    channel_key = Column(Integer, primary_key=True, autoincrement=True)
    channel_code = Column(String(30), nullable=False, unique=True, index=True)
    channel_name = Column(String(100), nullable=False)
    channel_type = Column(String(30), nullable=False) # DIGITAL, PHYSICAL, ASSISTED

# ==========================================
# FACT TABLES
# ==========================================

class FactTransaction(WarehouseBase):
    __tablename__ = "fact_transactions"

    fact_txn_key = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(String(100), nullable=False, index=True)
    customer_key = Column(Integer, ForeignKey("dim_customer.customer_key"), nullable=False, index=True)
    date_key = Column(Integer, ForeignKey("dim_date.date_key"), nullable=False, index=True)
    product_key = Column(Integer, ForeignKey("dim_product.product_key"), nullable=False)
    channel_key = Column(Integer, ForeignKey("dim_channel.channel_key"), nullable=False)
    branch_key = Column(Integer, ForeignKey("dim_branch.branch_key"))
    
    transaction_type = Column(String(30), nullable=False) # DEBIT, CREDIT, TRANSFER, ATM, POS
    amount = Column(Float, nullable=False)
    merchant_category = Column(String(100))
    status = Column(String(20), default="SETTLED")
    is_fraud_flag = Column(Boolean, default=False)
    created_timestamp = Column(DateTime, nullable=False)

class FactDailyAccountSnapshot(WarehouseBase):
    __tablename__ = "fact_daily_account_snapshot"

    snapshot_key = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(String(50), nullable=False, index=True)
    customer_key = Column(Integer, ForeignKey("dim_customer.customer_key"), nullable=False, index=True)
    date_key = Column(Integer, ForeignKey("dim_date.date_key"), nullable=False, index=True)
    product_key = Column(Integer, ForeignKey("dim_product.product_key"), nullable=False)
    branch_key = Column(Integer, ForeignKey("dim_branch.branch_key"))
    
    current_balance = Column(Float, nullable=False)
    available_balance = Column(Float, nullable=False)
    interest_rate = Column(Float, default=0.0)
    status = Column(String(20), default="ACTIVE")

class FactLoanPerformance(WarehouseBase):
    __tablename__ = "fact_loan_performance"

    loan_fact_key = Column(Integer, primary_key=True, autoincrement=True)
    loan_id = Column(String(50), nullable=False, index=True)
    customer_key = Column(Integer, ForeignKey("dim_customer.customer_key"), nullable=False, index=True)
    date_key = Column(Integer, ForeignKey("dim_date.date_key"), nullable=False, index=True)
    product_key = Column(Integer, ForeignKey("dim_product.product_key"), nullable=False)
    
    principal_amount = Column(Float, nullable=False)
    outstanding_balance = Column(Float, nullable=False)
    monthly_installment = Column(Float, nullable=False)
    overdue_days = Column(Integer, default=0)
    overdue_amount = Column(Float, default=0.0)
    delinquency_status = Column(String(30), nullable=False) # CURRENT, 30_DAYS, 60_DAYS, 90_DAYS_PLUS, DEFAULTED
    is_npl = Column(Boolean, default=False) # Non-performing loan (>90 days overdue)
    loan_loss_provision = Column(Float, default=0.0)

class FactCustomerInteraction(WarehouseBase):
    __tablename__ = "fact_customer_interactions"

    interaction_fact_key = Column(Integer, primary_key=True, autoincrement=True)
    interaction_id = Column(String(100), nullable=False, index=True)
    customer_key = Column(Integer, ForeignKey("dim_customer.customer_key"), nullable=False, index=True)
    date_key = Column(Integer, ForeignKey("dim_date.date_key"), nullable=False, index=True)
    channel_key = Column(Integer, ForeignKey("dim_channel.channel_key"), nullable=False)
    
    interaction_type = Column(String(50), nullable=False)
    sentiment = Column(String(20), nullable=False)
    sentiment_score = Column(Float, nullable=False) # -1.0 to 1.0
    duration_minutes = Column(Float, default=5.0)
    is_complaint = Column(Boolean, default=False)
    resolution_status = Column(String(30), default="RESOLVED")

# ==========================================
# CONSOLIDATED CUSTOMER 360 SERVING MART
# ==========================================

class C360CustomerMart(WarehouseBase):
    __tablename__ = "c360_customer_mart"

    customer_key = Column(Integer, primary_key=True)
    customer_id = Column(String(50), nullable=False, unique=True, index=True)
    full_name = Column(String(200), nullable=False)
    email = Column(String(150), nullable=False)
    phone = Column(String(30))
    city = Column(String(100))
    state = Column(String(50))
    customer_segment = Column(String(50), nullable=False, index=True)
    credit_score = Column(Integer, nullable=False)
    credit_score_bracket = Column(String(30))
    kyc_status = Column(String(30), nullable=False)
    aml_risk_score = Column(Float, default=0.0)
    risk_tier = Column(String(20), nullable=False, index=True)
    
    # Financial Aggregates
    deposit_accounts_count = Column(Integer, default=0)
    total_deposit_balance = Column(Float, default=0.0)
    
    active_loans_count = Column(Integer, default=0)
    total_loan_outstanding = Column(Float, default=0.0)
    max_overdue_days = Column(Integer, default=0)
    total_overdue_amount = Column(Float, default=0.0)
    has_overdue_loan = Column(Boolean, default=False, index=True)
    
    credit_cards_count = Column(Integer, default=0)
    total_credit_limit = Column(Float, default=0.0)
    total_credit_outstanding = Column(Float, default=0.0)
    credit_utilization_pct = Column(Float, default=0.0)
    
    # Customer 360 KPIs
    total_products_held = Column(Integer, default=0, index=True)
    has_multiple_products = Column(Boolean, default=False, index=True) # Question #1
    
    total_relationship_value = Column(Float, default=0.0)
    ltv_score = Column(Float, default=0.0, index=True)
    is_high_value = Column(Boolean, default=False, index=True) # Question #2
    
    # Transaction Behavior (Trailing 30-90 Days)
    txn_count_30d = Column(Integer, default=0)
    txn_volume_30d = Column(Float, default=0.0) # Question #4
    avg_txn_amount_30d = Column(Float, default=0.0)
    
    # Interactions & Engagement
    interactions_count_90d = Column(Integer, default=0)
    avg_sentiment_score = Column(Float, default=0.0)
    unresolved_complaints_count = Column(Integer, default=0)
    engagement_status = Column(String(30), default="ACTIVE", index=True) # ACTIVE, STABLE, DECLINING, DORMANT (Question #5)
    
    # Composite Risk Matrix (Question #6)
    composite_risk_score = Column(Float, default=0.0) # 0 - 100
    is_high_risk = Column(Boolean, default=False, index=True)
    
    last_synced_at = Column(DateTime, nullable=False)
