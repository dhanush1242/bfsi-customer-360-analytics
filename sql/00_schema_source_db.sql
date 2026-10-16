-- ============================================================================
-- Enterprise BFSI Operational Source System Schemas
-- Simulates Core Banking, Loan Origination, Cards, Transactions & CRM databases
-- ============================================================================

CREATE TABLE IF NOT EXISTS src_customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL,
    phone VARCHAR(30) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender VARCHAR(10) NOT NULL,
    annual_income DOUBLE PRECISION NOT NULL,
    occupation VARCHAR(100),
    address_city VARCHAR(100) NOT NULL,
    address_state VARCHAR(50) NOT NULL,
    address_country VARCHAR(50) DEFAULT 'USA',
    postal_code VARCHAR(20),
    branch_id VARCHAR(20) NOT NULL,
    customer_segment VARCHAR(50) NOT NULL, -- Retail, Affluent, HNI, Ultra HNI, Corporate
    credit_score INT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS src_accounts (
    account_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL REFERENCES src_customers(customer_id),
    account_type VARCHAR(50) NOT NULL, -- Savings, Checking, Money Market, CD
    currency VARCHAR(10) DEFAULT 'USD',
    current_balance DOUBLE PRECISION NOT NULL,
    available_balance DOUBLE PRECISION NOT NULL,
    interest_rate DOUBLE PRECISION DEFAULT 0.0,
    status VARCHAR(20) DEFAULT 'ACTIVE',
    opened_date DATE NOT NULL,
    last_activity_date DATE,
    branch_id VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS src_loans (
    loan_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL REFERENCES src_customers(customer_id),
    loan_type VARCHAR(50) NOT NULL, -- Home Mortgage, Auto, Personal, Student
    principal_amount DOUBLE PRECISION NOT NULL,
    interest_rate DOUBLE PRECISION NOT NULL,
    term_months INT NOT NULL,
    outstanding_balance DOUBLE PRECISION NOT NULL,
    monthly_installment DOUBLE PRECISION NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status VARCHAR(30) NOT NULL, -- CURRENT, DELINQUENT, DEFAULTED, CLOSED
    overdue_days INT DEFAULT 0,
    overdue_amount DOUBLE PRECISION DEFAULT 0.0,
    collateral_value DOUBLE PRECISION DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS src_credit_cards (
    card_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL REFERENCES src_customers(customer_id),
    card_number_masked VARCHAR(30) NOT NULL,
    card_tier VARCHAR(50) NOT NULL, -- Classic, Gold, Platinum, Signature
    credit_limit DOUBLE PRECISION NOT NULL,
    current_outstanding DOUBLE PRECISION DEFAULT 0.0,
    available_credit DOUBLE PRECISION NOT NULL,
    apr_rate DOUBLE PRECISION NOT NULL,
    issue_date DATE NOT NULL,
    expiry_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'ACTIVE'
);

CREATE TABLE IF NOT EXISTS src_transactions (
    transaction_id VARCHAR(100) PRIMARY KEY,
    account_id VARCHAR(50) NOT NULL REFERENCES src_accounts(account_id),
    customer_id VARCHAR(50) NOT NULL REFERENCES src_customers(customer_id),
    transaction_type VARCHAR(30) NOT NULL, -- DEBIT, CREDIT, TRANSFER, ATM, POS
    channel VARCHAR(30) NOT NULL, -- MOBILE, WEB, ATM, BRANCH, POS
    amount DOUBLE PRECISION NOT NULL,
    currency VARCHAR(10) DEFAULT 'USD',
    merchant_category VARCHAR(100),
    merchant_name VARCHAR(150),
    status VARCHAR(20) DEFAULT 'SETTLED',
    is_fraud_flag BOOLEAN DEFAULT FALSE,
    transaction_timestamp TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS src_payments (
    payment_id VARCHAR(100) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL REFERENCES src_customers(customer_id),
    reference_id VARCHAR(50) NOT NULL, -- loan_id or card_id
    payment_target VARCHAR(30) NOT NULL, -- LOAN_EMI, CREDIT_CARD_BILL
    payment_method VARCHAR(30) NOT NULL, -- ACH, AUTOPAY, WIRE
    payment_amount DOUBLE PRECISION NOT NULL,
    payment_status VARCHAR(20) DEFAULT 'COMPLETED',
    payment_date TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS src_kyc (
    kyc_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) UNIQUE NOT NULL REFERENCES src_customers(customer_id),
    id_type VARCHAR(50) NOT NULL,
    id_number_masked VARCHAR(50) NOT NULL,
    kyc_status VARCHAR(30) NOT NULL, -- VERIFIED, PENDING_REVIEW, REJECTED
    aml_risk_score DOUBLE PRECISION NOT NULL,
    pep_flag BOOLEAN DEFAULT FALSE,
    sanctions_check VARCHAR(20) DEFAULT 'PASSED',
    verified_at TIMESTAMP,
    last_reviewed_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS src_interactions (
    interaction_id VARCHAR(100) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL REFERENCES src_customers(customer_id),
    channel VARCHAR(50) NOT NULL,
    interaction_type VARCHAR(50) NOT NULL,
    sentiment VARCHAR(20) NOT NULL,
    sentiment_score DOUBLE PRECISION NOT NULL,
    duration_minutes DOUBLE PRECISION DEFAULT 5.0,
    is_complaint BOOLEAN DEFAULT FALSE,
    resolution_status VARCHAR(30) DEFAULT 'RESOLVED',
    interaction_timestamp TIMESTAMP NOT NULL
);
