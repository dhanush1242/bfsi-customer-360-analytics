-- ============================================================================
-- Enterprise BFSI Data Warehouse - Dimensional Star Schema
-- Conformed Dimensions + Fact Tables + Analytical Serving Layer
-- ============================================================================

-- 1. Conformed Date Dimension
CREATE TABLE IF NOT EXISTS dim_date (
    date_key INT PRIMARY KEY, -- e.g., 20261005
    full_date DATE NOT NULL UNIQUE,
    day_of_month INT NOT NULL,
    day_name VARCHAR(15) NOT NULL,
    day_of_week INT NOT NULL,
    is_weekend BOOLEAN NOT NULL,
    month INT NOT NULL,
    month_name VARCHAR(15) NOT NULL,
    quarter INT NOT NULL,
    year INT NOT NULL,
    fiscal_quarter VARCHAR(10) NOT NULL
);

-- 2. Conformed Customer Dimension (SCD Type 1/2 Ready)
CREATE TABLE IF NOT EXISTS dim_customer (
    customer_key SERIAL PRIMARY KEY, -- Surrogate Key
    customer_id VARCHAR(50) NOT NULL UNIQUE, -- Natural Business Key
    full_name VARCHAR(200) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL,
    phone VARCHAR(30),
    age INT NOT NULL,
    age_bracket VARCHAR(30),
    gender VARCHAR(10),
    annual_income DOUBLE PRECISION NOT NULL,
    income_bracket VARCHAR(50),
    occupation VARCHAR(100),
    city VARCHAR(100) NOT NULL,
    state VARCHAR(50) NOT NULL,
    country VARCHAR(50) DEFAULT 'USA',
    branch_id VARCHAR(20),
    customer_segment VARCHAR(50) NOT NULL,
    credit_score INT NOT NULL,
    credit_score_bracket VARCHAR(30),
    kyc_status VARCHAR(30) NOT NULL,
    aml_risk_score DOUBLE PRECISION DEFAULT 0.0,
    pep_flag BOOLEAN DEFAULT FALSE,
    risk_tier VARCHAR(20) DEFAULT 'LOW',
    onboarded_date DATE,
    is_active BOOLEAN DEFAULT TRUE
);
CREATE INDEX IF NOT EXISTS idx_dim_cust_segment ON dim_customer(customer_segment);
CREATE INDEX IF NOT EXISTS idx_dim_cust_risk ON dim_customer(risk_tier);

-- 3. Conformed Product Dimension
CREATE TABLE IF NOT EXISTS dim_product (
    product_key SERIAL PRIMARY KEY,
    product_id VARCHAR(50) NOT NULL UNIQUE,
    product_category VARCHAR(50) NOT NULL, -- DEPOSIT, LOAN, CREDIT_CARD, WEALTH
    product_sub_type VARCHAR(100) NOT NULL,
    product_name VARCHAR(150) NOT NULL,
    standard_interest_rate DOUBLE PRECISION DEFAULT 0.0,
    risk_weight DOUBLE PRECISION DEFAULT 1.0
);
CREATE INDEX IF NOT EXISTS idx_dim_prod_cat ON dim_product(product_category);

-- 4. Conformed Branch Dimension
CREATE TABLE IF NOT EXISTS dim_branch (
    branch_key SERIAL PRIMARY KEY,
    branch_id VARCHAR(20) NOT NULL UNIQUE,
    branch_name VARCHAR(100) NOT NULL,
    region VARCHAR(50) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(50) NOT NULL
);

-- 5. Conformed Channel Dimension
CREATE TABLE IF NOT EXISTS dim_channel (
    channel_key SERIAL PRIMARY KEY,
    channel_code VARCHAR(30) NOT NULL UNIQUE,
    channel_name VARCHAR(100) NOT NULL,
    channel_type VARCHAR(30) NOT NULL -- DIGITAL, PHYSICAL, ASSISTED
);

-- ============================================================================
-- FACT TABLES
-- ============================================================================

-- 6. Granular Transactions Fact Table
CREATE TABLE IF NOT EXISTS fact_transactions (
    fact_txn_key SERIAL PRIMARY KEY,
    transaction_id VARCHAR(100) NOT NULL,
    customer_key INT NOT NULL REFERENCES dim_customer(customer_key),
    date_key INT NOT NULL REFERENCES dim_date(date_key),
    product_key INT NOT NULL REFERENCES dim_product(product_key),
    channel_key INT NOT NULL REFERENCES dim_channel(channel_key),
    branch_key INT REFERENCES dim_branch(branch_key),
    transaction_type VARCHAR(30) NOT NULL,
    amount DOUBLE PRECISION NOT NULL,
    merchant_category VARCHAR(100),
    status VARCHAR(20) DEFAULT 'SETTLED',
    is_fraud_flag BOOLEAN DEFAULT FALSE,
    created_timestamp TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_fact_txn_cust ON fact_transactions(customer_key);
CREATE INDEX IF NOT EXISTS idx_fact_txn_date ON fact_transactions(date_key);

-- 7. Daily Account Balance Snapshots
CREATE TABLE IF NOT EXISTS fact_daily_account_snapshot (
    snapshot_key SERIAL PRIMARY KEY,
    account_id VARCHAR(50) NOT NULL,
    customer_key INT NOT NULL REFERENCES dim_customer(customer_key),
    date_key INT NOT NULL REFERENCES dim_date(date_key),
    product_key INT NOT NULL REFERENCES dim_product(product_key),
    branch_key INT REFERENCES dim_branch(branch_key),
    current_balance DOUBLE PRECISION NOT NULL,
    available_balance DOUBLE PRECISION NOT NULL,
    interest_rate DOUBLE PRECISION DEFAULT 0.0,
    status VARCHAR(20) DEFAULT 'ACTIVE'
);

-- 8. Loan Portfolio Performance Fact
CREATE TABLE IF NOT EXISTS fact_loan_performance (
    loan_fact_key SERIAL PRIMARY KEY,
    loan_id VARCHAR(50) NOT NULL,
    customer_key INT NOT NULL REFERENCES dim_customer(customer_key),
    date_key INT NOT NULL REFERENCES dim_date(date_key),
    product_key INT NOT NULL REFERENCES dim_product(product_key),
    principal_amount DOUBLE PRECISION NOT NULL,
    outstanding_balance DOUBLE PRECISION NOT NULL,
    monthly_installment DOUBLE PRECISION NOT NULL,
    overdue_days INT DEFAULT 0,
    overdue_amount DOUBLE PRECISION DEFAULT 0.0,
    delinquency_status VARCHAR(30) NOT NULL,
    is_npl BOOLEAN DEFAULT FALSE,
    loan_loss_provision DOUBLE PRECISION DEFAULT 0.0
);
CREATE INDEX IF NOT EXISTS idx_fact_loan_cust ON fact_loan_performance(customer_key);

-- 9. Customer Interactions & Omnichannel Touchpoint Fact
CREATE TABLE IF NOT EXISTS fact_customer_interactions (
    interaction_fact_key SERIAL PRIMARY KEY,
    interaction_id VARCHAR(100) NOT NULL,
    customer_key INT NOT NULL REFERENCES dim_customer(customer_key),
    date_key INT NOT NULL REFERENCES dim_date(date_key),
    channel_key INT NOT NULL REFERENCES dim_channel(channel_key),
    interaction_type VARCHAR(50) NOT NULL,
    sentiment VARCHAR(20) NOT NULL,
    sentiment_score DOUBLE PRECISION NOT NULL,
    duration_minutes DOUBLE PRECISION DEFAULT 5.0,
    is_complaint BOOLEAN DEFAULT FALSE,
    resolution_status VARCHAR(30) DEFAULT 'RESOLVED'
);

-- ============================================================================
-- CUSTOMER 360 AGGREGATED SERVING MART (PHYSICALIZED)
-- ============================================================================
CREATE TABLE IF NOT EXISTS c360_customer_mart (
    customer_key INT PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL UNIQUE,
    full_name VARCHAR(200) NOT NULL,
    email VARCHAR(150) NOT NULL,
    phone VARCHAR(30),
    city VARCHAR(100),
    state VARCHAR(50),
    customer_segment VARCHAR(50) NOT NULL,
    credit_score INT NOT NULL,
    credit_score_bracket VARCHAR(30),
    kyc_status VARCHAR(30) NOT NULL,
    aml_risk_score DOUBLE PRECISION DEFAULT 0.0,
    risk_tier VARCHAR(20) NOT NULL,
    
    deposit_accounts_count INT DEFAULT 0,
    total_deposit_balance DOUBLE PRECISION DEFAULT 0.0,
    
    active_loans_count INT DEFAULT 0,
    total_loan_outstanding DOUBLE PRECISION DEFAULT 0.0,
    max_overdue_days INT DEFAULT 0,
    total_overdue_amount DOUBLE PRECISION DEFAULT 0.0,
    has_overdue_loan BOOLEAN DEFAULT FALSE,
    
    credit_cards_count INT DEFAULT 0,
    total_credit_limit DOUBLE PRECISION DEFAULT 0.0,
    total_credit_outstanding DOUBLE PRECISION DEFAULT 0.0,
    credit_utilization_pct DOUBLE PRECISION DEFAULT 0.0,
    
    total_products_held INT DEFAULT 0,
    has_multiple_products BOOLEAN DEFAULT FALSE,
    
    total_relationship_value DOUBLE PRECISION DEFAULT 0.0,
    ltv_score DOUBLE PRECISION DEFAULT 0.0,
    is_high_value BOOLEAN DEFAULT FALSE,
    
    txn_count_30d INT DEFAULT 0,
    txn_volume_30d DOUBLE PRECISION DEFAULT 0.0,
    avg_txn_amount_30d DOUBLE PRECISION DEFAULT 0.0,
    
    interactions_count_90d INT DEFAULT 0,
    avg_sentiment_score DOUBLE PRECISION DEFAULT 0.0,
    unresolved_complaints_count INT DEFAULT 0,
    engagement_status VARCHAR(30) DEFAULT 'ACTIVE',
    
    composite_risk_score DOUBLE PRECISION DEFAULT 0.0,
    is_high_risk BOOLEAN DEFAULT FALSE,
    
    last_synced_at TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_c360_seg ON c360_customer_mart(customer_segment);
CREATE INDEX IF NOT EXISTS idx_c360_risk ON c360_customer_mart(is_high_risk);
CREATE INDEX IF NOT EXISTS idx_c360_val ON c360_customer_mart(is_high_value);
