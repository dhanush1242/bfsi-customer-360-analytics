from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Boolean, ForeignKey, Text
from src.database.connection import SourceBase

class SourceCustomer(SourceBase):
    __tablename__ = "src_customers"

    customer_id = Column(String(50), primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False)
    phone = Column(String(30), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(10), nullable=False)
    annual_income = Column(Float, nullable=False)
    occupation = Column(String(100))
    address_city = Column(String(100), nullable=False)
    address_state = Column(String(50), nullable=False)
    address_country = Column(String(50), default="USA")
    postal_code = Column(String(20))
    branch_id = Column(String(20), nullable=False)
    customer_segment = Column(String(50), nullable=False) # Retail, Affluent, HNI, Ultra HNI, Corporate
    credit_score = Column(Integer, nullable=False) # 300 to 850
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

class SourceAccount(SourceBase):
    __tablename__ = "src_accounts"

    account_id = Column(String(50), primary_key=True, index=True)
    customer_id = Column(String(50), nullable=False, index=True)
    account_type = Column(String(50), nullable=False) # Savings, Checking, Money Market, Certificate of Deposit
    currency = Column(String(10), default="USD")
    current_balance = Column(Float, nullable=False)
    available_balance = Column(Float, nullable=False)
    interest_rate = Column(Float, default=0.0)
    status = Column(String(20), default="ACTIVE") # ACTIVE, DORMANT, CLOSED, FROZEN
    opened_date = Column(Date, nullable=False)
    last_activity_date = Column(Date)
    branch_id = Column(String(20))

class SourceLoan(SourceBase):
    __tablename__ = "src_loans"

    loan_id = Column(String(50), primary_key=True, index=True)
    customer_id = Column(String(50), nullable=False, index=True)
    loan_type = Column(String(50), nullable=False) # Home Mortgage, Auto Loan, Personal Loan, Student Loan, Business Loan
    principal_amount = Column(Float, nullable=False)
    interest_rate = Column(Float, nullable=False)
    term_months = Column(Integer, nullable=False)
    outstanding_balance = Column(Float, nullable=False)
    monthly_installment = Column(Float, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(String(30), nullable=False) # CURRENT, DELINQUENT, DEFAULTED, CLOSED, GRACE_PERIOD
    overdue_days = Column(Integer, default=0)
    overdue_amount = Column(Float, default=0.0)
    collateral_value = Column(Float, default=0.0)

class SourceCreditCard(SourceBase):
    __tablename__ = "src_credit_cards"

    card_id = Column(String(50), primary_key=True, index=True)
    customer_id = Column(String(50), nullable=False, index=True)
    card_number_masked = Column(String(30), nullable=False)
    card_tier = Column(String(50), nullable=False) # Classic, Gold, Platinum, Infinite, Signature
    credit_limit = Column(Float, nullable=False)
    current_outstanding = Column(Float, default=0.0)
    available_credit = Column(Float, nullable=False)
    apr_rate = Column(Float, nullable=False)
    issue_date = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=False)
    status = Column(String(20), default="ACTIVE") # ACTIVE, BLOCKED, EXPIRED, SUSPENDED

class SourceTransaction(SourceBase):
    __tablename__ = "src_transactions"

    transaction_id = Column(String(100), primary_key=True, index=True)
    account_id = Column(String(50), nullable=False, index=True)
    customer_id = Column(String(50), nullable=False, index=True)
    transaction_type = Column(String(30), nullable=False) # DEBIT, CREDIT, TRANSFER, ATM_WITHDRAWAL, POS, WIRE
    channel = Column(String(30), nullable=False) # MOBILE, WEB, ATM, BRANCH, POS
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="USD")
    merchant_category = Column(String(100)) # Grocery, Dining, Travel, Utilities, Healthcare, Electronics
    merchant_name = Column(String(150))
    status = Column(String(20), default="SETTLED") # SETTLED, PENDING, FAILED, REVERSED
    is_fraud_flag = Column(Boolean, default=False)
    transaction_timestamp = Column(DateTime, nullable=False, index=True)

class SourcePayment(SourceBase):
    __tablename__ = "src_payments"

    payment_id = Column(String(100), primary_key=True, index=True)
    customer_id = Column(String(50), nullable=False, index=True)
    reference_id = Column(String(50), nullable=False) # loan_id or card_id
    payment_target = Column(String(30), nullable=False) # LOAN_EMI, CREDIT_CARD_BILL, UTILITY_BILL
    payment_method = Column(String(30), nullable=False) # ACH, AUTOPAY, DEBIT_CARD, WIRE
    payment_amount = Column(Float, nullable=False)
    payment_status = Column(String(20), default="COMPLETED") # COMPLETED, FAILED, BOUNCED
    payment_date = Column(DateTime, nullable=False)

class SourceKYC(SourceBase):
    __tablename__ = "src_kyc"

    kyc_id = Column(String(50), primary_key=True, index=True)
    customer_id = Column(String(50), nullable=False, unique=True, index=True)
    id_type = Column(String(50), nullable=False) # Passport, Driving License, SSN/National ID
    id_number_masked = Column(String(50), nullable=False)
    kyc_status = Column(String(30), nullable=False) # VERIFIED, PENDING_REVIEW, REJECTED, EXPIRED
    aml_risk_score = Column(Float, nullable=False) # 0.0 to 100.0 (High > 70)
    pep_flag = Column(Boolean, default=False) # Politically Exposed Person
    sanctions_check = Column(String(20), default="PASSED") # PASSED, FLAGGED, REQUIRES_MANUAL_REVIEW
    verified_at = Column(DateTime)
    last_reviewed_at = Column(DateTime, nullable=False)

class SourceInteraction(SourceBase):
    __tablename__ = "src_interactions"

    interaction_id = Column(String(100), primary_key=True, index=True)
    customer_id = Column(String(50), nullable=False, index=True)
    channel = Column(String(50), nullable=False) # Mobile App, Phone Banking, In-Branch, Email, Chatbot
    interaction_type = Column(String(50), nullable=False) # Inquire Balance, Loan Inquiry, Dispute Txn, Technical Support, Wealth Consultation
    sentiment = Column(String(20), nullable=False) # POSITIVE, NEUTRAL, NEGATIVE
    sentiment_score = Column(Float, nullable=False) # -1.0 to +1.0
    duration_minutes = Column(Float, default=5.0)
    is_complaint = Column(Boolean, default=False)
    resolution_status = Column(String(30), default="RESOLVED") # RESOLVED, ESCALATED, OPEN
    interaction_timestamp = Column(DateTime, nullable=False, index=True)
