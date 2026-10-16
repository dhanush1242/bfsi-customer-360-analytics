import datetime
from datetime import timedelta
from typing import Dict, List, Any, Tuple
from collections import defaultdict

from src.database.models_edw import (
    DimDate, DimCustomer, DimProduct, DimBranch, DimChannel,
    FactTransaction, FactDailyAccountSnapshot, FactLoanPerformance,
    FactCustomerInteraction, C360CustomerMart
)

def compute_age(birth_date: datetime.date) -> int:
    today = datetime.date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

def get_age_bracket(age: int) -> str:
    if age < 25:
        return "18-24 (Gen Z)"
    elif age < 36:
        return "25-35 (Early Career)"
    elif age < 50:
        return "36-49 (Prime Earning)"
    elif age < 65:
        return "50-64 (Mature Pre-Retiree)"
    else:
        return "65+ (Senior / Retiree)"

def get_income_bracket(income: float) -> str:
    if income < 40000:
        return "Low Income (<$40k)"
    elif income < 90000:
        return "Middle Income ($40k-$90k)"
    elif income < 200000:
        return "Upper Middle ($90k-$200k)"
    elif income < 500000:
        return "High Net Worth ($200k-$500k)"
    else:
        return "Ultra High Net Worth ($500k+)"

def get_credit_score_bracket(score: int) -> str:
    if score < 580:
        return "Poor (<580)"
    elif score < 670:
        return "Fair (580-669)"
    elif score < 740:
        return "Good (670-739)"
    elif score < 800:
        return "Very Good (740-799)"
    else:
        return "Exceptional (800+)"

class DataTransformer:
    @staticmethod
    def transform(extracted_data: Dict[str, List[Any]]) -> Dict[str, Any]:
        print("[ETL:Transform] Transforming into Star Schema Dimensions & Facts...")
        
        now = datetime.datetime.now()
        today = now.date()

        # 1. Transform Date Dimension (covering -365 days to +365 days)
        dim_dates = []
        date_key_map = {} # date_obj -> date_key
        start_date = today - timedelta(days=365)
        for i in range(730):
            d = start_date + timedelta(days=i)
            dkey = int(d.strftime("%Y%m%d"))
            date_key_map[d] = dkey
            
            quarter = (d.month - 1) // 3 + 1
            dim_dates.append(DimDate(
                date_key=dkey,
                full_date=d,
                day_of_month=d.day,
                day_name=d.strftime("%A"),
                day_of_week=d.isoweekday(),
                is_weekend=d.isoweekday() in [6, 7],
                month=d.month,
                month_name=d.strftime("%B"),
                quarter=quarter,
                year=d.year,
                fiscal_quarter=f"FY{d.year}-Q{quarter}"
            ))

        # 2. Transform Product Dimension
        dim_products = [
            DimProduct(product_key=1, product_id="PROD-DEP-SAV", product_category="DEPOSIT", product_sub_type="Savings Account", product_name="High-Yield Savings Account", standard_interest_rate=4.25, risk_weight=0.2),
            DimProduct(product_key=2, product_id="PROD-DEP-CHK", product_category="DEPOSIT", product_sub_type="Checking Account", product_name="Premier Checking Account", standard_interest_rate=0.05, risk_weight=0.1),
            DimProduct(product_key=3, product_id="PROD-DEP-MM", product_category="DEPOSIT", product_sub_type="Money Market", product_name="Advantage Money Market", standard_interest_rate=4.75, risk_weight=0.2),
            DimProduct(product_key=4, product_id="PROD-DEP-CD", product_category="DEPOSIT", product_sub_type="Certificate of Deposit", product_name="12-Month CD Term Deposit", standard_interest_rate=5.10, risk_weight=0.1),
            DimProduct(product_key=5, product_id="PROD-LOAN-MTG", product_category="LOAN", product_sub_type="Home Mortgage", product_name="30-Year Fixed Mortgage", standard_interest_rate=6.75, risk_weight=1.0),
            DimProduct(product_key=6, product_id="PROD-LOAN-AUTO", product_category="LOAN", product_sub_type="Auto Loan", product_name="Auto Purchase Financing", standard_interest_rate=6.20, risk_weight=0.8),
            DimProduct(product_key=7, product_id="PROD-LOAN-PERS", product_category="LOAN", product_sub_type="Personal Loan", product_name="Unsecured Personal Loan", standard_interest_rate=10.50, risk_weight=1.5),
            DimProduct(product_key=8, product_id="PROD-LOAN-BIZ", product_category="LOAN", product_sub_type="Business Loan", product_name="Commercial Line of Credit", standard_interest_rate=8.50, risk_weight=1.2),
            DimProduct(product_key=9, product_id="PROD-CARD-CLS", product_category="CREDIT_CARD", product_sub_type="Classic Card", product_name="Blue Everyday Classic", standard_interest_rate=19.99, risk_weight=1.1),
            DimProduct(product_key=10, product_id="PROD-CARD-GLD", product_category="CREDIT_CARD", product_sub_type="Gold Card", product_name="Gold Rewards Credit Card", standard_interest_rate=18.49, risk_weight=1.0),
            DimProduct(product_key=11, product_id="PROD-CARD-PLT", product_category="CREDIT_CARD", product_sub_type="Platinum Card", product_name="Platinum Prestige Card", standard_interest_rate=16.99, risk_weight=0.8),
            DimProduct(product_key=12, product_id="PROD-CARD-INF", product_category="CREDIT_CARD", product_sub_type="Infinite Card", product_name="Infinite Private Wealth Card", standard_interest_rate=14.99, risk_weight=0.6)
        ]
        
        prod_map = {
            "Savings": 1, "Checking": 2, "Money Market": 3, "Certificate of Deposit": 4,
            "Home Mortgage": 5, "Auto Loan": 6, "Personal Loan": 7, "Student Loan": 7, "Business Loan": 8,
            "Classic": 9, "Gold": 10, "Platinum": 11, "Signature": 11, "Infinite": 12
        }

        # 3. Transform Branch Dimension
        branches_raw = [
            ("BR-NEW-100", "New York Flagship Branch", "Northeast", "New York", "NY"),
            ("BR-BOS-101", "Boston Back Bay Branch", "Northeast", "Boston", "MA"),
            ("BR-CHA-102", "Charlotte Uptown Branch", "Southeast", "Charlotte", "NC"),
            ("BR-ATL-103", "Atlanta Midtown Branch", "Southeast", "Atlanta", "GA"),
            ("BR-MIA-104", "Miami Brickell Branch", "Southeast", "Miami", "FL"),
            ("BR-CHI-105", "Chicago Loop Financial Branch", "Midwest", "Chicago", "IL"),
            ("BR-COL-106", "Columbus City Center Branch", "Midwest", "Columbus", "OH"),
            ("BR-DAL-107", "Dallas Downtown Branch", "Southwest", "Dallas", "TX"),
            ("BR-AUS-108", "Austin Silicon Hills Branch", "Southwest", "Austin", "TX"),
            ("BR-DEN-109", "Denver Lower Downtown Branch", "West", "Denver", "CO"),
            ("BR-SAN-110", "San Francisco Financial Center", "West", "San Francisco", "CA"),
            ("BR-LOS-111", "Los Angeles Century City Branch", "West", "Los Angeles", "CA"),
            ("BR-SEA-112", "Seattle Waterfront Branch", "West", "Seattle", "WA")
        ]
        dim_branches = []
        branch_key_map = {}
        for idx, (b_id, name, region, city, state) in enumerate(branches_raw, 1):
            dim_branches.append(DimBranch(branch_key=idx, branch_id=b_id, branch_name=name, region=region, city=city, state=state))
            branch_key_map[b_id] = idx

        # 4. Transform Channel Dimension
        channels_raw = [
            ("MOBILE", "Mobile Banking App", "DIGITAL"),
            ("WEB", "Online Banking Portal", "DIGITAL"),
            ("ATM", "ATM Terminal Network", "PHYSICAL"),
            ("BRANCH", "In-Branch Teller & Officer", "PHYSICAL"),
            ("POS", "Point of Sale Terminal", "PHYSICAL"),
            ("PHONE", "Phone Banking / IVR", "ASSISTED"),
            ("CHATBOT", "AI Virtual Assistant", "DIGITAL")
        ]
        dim_channels = []
        channel_key_map = {}
        for idx, (code, name, c_type) in enumerate(channels_raw, 1):
            dim_channels.append(DimChannel(channel_key=idx, channel_code=code, channel_name=name, channel_type=c_type))
            channel_key_map[code] = idx

        # Map KYC records
        kyc_dict = {k.customer_id: k for k in extracted_data["kyc"]}

        # 5. Transform Customer Dimension
        dim_customers = []
        cust_key_map = {} # customer_id -> customer_key
        
        for idx, c in enumerate(extracted_data["customers"], 1):
            cust_key_map[c.customer_id] = idx
            age = compute_age(c.date_of_birth)
            
            kyc_rec = kyc_dict.get(c.customer_id)
            kyc_status = kyc_rec.kyc_status if kyc_rec else "VERIFIED"
            aml_score = kyc_rec.aml_risk_score if kyc_rec else 15.0
            pep_flag = kyc_rec.pep_flag if kyc_rec else False
            
            # Risk tier determination
            if c.credit_score < 580 or aml_score > 75 or pep_flag:
                risk_tier = "CRITICAL" if aml_score > 85 else "HIGH"
            elif c.credit_score < 670 or aml_score > 50:
                risk_tier = "MEDIUM"
            else:
                risk_tier = "LOW"

            dim_cust = DimCustomer(
                customer_key=idx,
                customer_id=c.customer_id,
                full_name=f"{c.first_name} {c.last_name}",
                first_name=c.first_name,
                last_name=c.last_name,
                email=c.email,
                phone=c.phone,
                age=age,
                age_bracket=get_age_bracket(age),
                gender=c.gender,
                annual_income=c.annual_income,
                income_bracket=get_income_bracket(c.annual_income),
                occupation=c.occupation,
                city=c.address_city,
                state=c.address_state,
                country=c.address_country,
                branch_id=c.branch_id,
                customer_segment=c.customer_segment,
                credit_score=c.credit_score,
                credit_score_bracket=get_credit_score_bracket(c.credit_score),
                kyc_status=kyc_status,
                aml_risk_score=aml_score,
                pep_flag=pep_flag,
                risk_tier=risk_tier,
                onboarded_date=c.created_at.date(),
                is_active=True
            )
            dim_customers.append(dim_cust)

        # 6. Transform Account Daily Snapshots (Fact)
        fact_snapshots = []
        cust_deposit_map = defaultdict(lambda: {"count": 0, "balance": 0.0})
        for acc in extracted_data["accounts"]:
            ckey = cust_key_map.get(acc.customer_id)
            if not ckey:
                continue
            
            dkey = date_key_map.get(acc.last_activity_date or today, int(today.strftime("%Y%m%d")))
            pkey = prod_map.get(acc.account_type, 1)
            bkey = branch_key_map.get(acc.branch_id, 1)

            if acc.status == "ACTIVE":
                cust_deposit_map[acc.customer_id]["count"] += 1
                cust_deposit_map[acc.customer_id]["balance"] += acc.current_balance

            fact_snapshots.append(FactDailyAccountSnapshot(
                account_id=acc.account_id,
                customer_key=ckey,
                date_key=dkey,
                product_key=pkey,
                branch_key=bkey,
                current_balance=acc.current_balance,
                available_balance=acc.available_balance,
                interest_rate=acc.interest_rate,
                status=acc.status
            ))

        # 7. Transform Loan Portfolio Performance (Fact)
        fact_loans = []
        cust_loan_map = defaultdict(lambda: {"count": 0, "outstanding": 0.0, "max_overdue_days": 0, "total_overdue": 0.0, "has_overdue": False})
        for l in extracted_data["loans"]:
            ckey = cust_key_map.get(l.customer_id)
            if not ckey:
                continue

            dkey = int(today.strftime("%Y%m%d"))
            pkey = prod_map.get(l.loan_type, 5)

            is_npl = l.overdue_days >= 90
            delinq_status = "CURRENT"
            if l.overdue_days >= 90:
                delinq_status = "90_DAYS_PLUS"
            elif l.overdue_days >= 60:
                delinq_status = "60_DAYS"
            elif l.overdue_days >= 30:
                delinq_status = "30_DAYS"
            elif l.overdue_days > 0:
                delinq_status = "EARLY_STAGE"

            provision = round(l.outstanding_balance * (0.50 if is_npl else (0.15 if l.overdue_days >= 30 else 0.01)), 2)

            if l.outstanding_balance > 0:
                cust_loan_map[l.customer_id]["count"] += 1
                cust_loan_map[l.customer_id]["outstanding"] += l.outstanding_balance
                if l.overdue_days > cust_loan_map[l.customer_id]["max_overdue_days"]:
                    cust_loan_map[l.customer_id]["max_overdue_days"] = l.overdue_days
                cust_loan_map[l.customer_id]["total_overdue"] += l.overdue_amount
                if l.overdue_days > 0:
                    cust_loan_map[l.customer_id]["has_overdue"] = True

            fact_loans.append(FactLoanPerformance(
                loan_id=l.loan_id,
                customer_key=ckey,
                date_key=dkey,
                product_key=pkey,
                principal_amount=l.principal_amount,
                outstanding_balance=l.outstanding_balance,
                monthly_installment=l.monthly_installment,
                overdue_days=l.overdue_days,
                overdue_amount=l.overdue_amount,
                delinquency_status=delinq_status,
                is_npl=is_npl,
                loan_loss_provision=provision
            ))

        # 8. Transform Credit Cards Aggregates
        cust_card_map = defaultdict(lambda: {"count": 0, "limit": 0.0, "outstanding": 0.0})
        for c in extracted_data["cards"]:
            if c.status == "ACTIVE":
                cust_card_map[c.customer_id]["count"] += 1
                cust_card_map[c.customer_id]["limit"] += c.credit_limit
                cust_card_map[c.customer_id]["outstanding"] += c.current_outstanding

        # 9. Transform Transactions (Fact)
        fact_txns = []
        cust_txn_30d_map = defaultdict(lambda: {"count": 0, "volume": 0.0})
        thirty_days_ago = now - timedelta(days=30)
        
        for t in extracted_data["transactions"]:
            ckey = cust_key_map.get(t.customer_id)
            if not ckey:
                continue

            t_date = t.transaction_timestamp.date()
            dkey = date_key_map.get(t_date, int(t_date.strftime("%Y%m%d")))
            pkey = 2 # default checking
            ch_code = t.channel.upper()
            chkey = channel_key_map.get(ch_code, 1)

            if t.transaction_timestamp >= thirty_days_ago:
                cust_txn_30d_map[t.customer_id]["count"] += 1
                cust_txn_30d_map[t.customer_id]["volume"] += t.amount

            fact_txns.append(FactTransaction(
                transaction_id=t.transaction_id,
                customer_key=ckey,
                date_key=dkey,
                product_key=pkey,
                channel_key=chkey,
                branch_key=1,
                transaction_type=t.transaction_type,
                amount=t.amount,
                merchant_category=t.merchant_category,
                status=t.status,
                is_fraud_flag=t.is_fraud_flag,
                created_timestamp=t.transaction_timestamp
            ))

        # 10. Transform Interactions (Fact)
        fact_interactions = []
        cust_inter_map = defaultdict(lambda: {"count_90d": 0, "sentiments": [], "unresolved_complaints": 0})
        ninety_days_ago = now - timedelta(days=90)
        
        chan_lookup = {
            "Mobile App": "MOBILE", "Phone Banking": "PHONE",
            "In-Branch": "BRANCH", "Email": "WEB", "Chatbot": "CHATBOT"
        }

        for inter in extracted_data["interactions"]:
            ckey = cust_key_map.get(inter.customer_id)
            if not ckey:
                continue

            i_date = inter.interaction_timestamp.date()
            dkey = date_key_map.get(i_date, int(i_date.strftime("%Y%m%d")))
            c_code = chan_lookup.get(inter.channel, "MOBILE")
            chkey = channel_key_map.get(c_code, 1)

            if inter.interaction_timestamp >= ninety_days_ago:
                cust_inter_map[inter.customer_id]["count_90d"] += 1
                cust_inter_map[inter.customer_id]["sentiments"].append(inter.sentiment_score)
                if inter.is_complaint and inter.resolution_status != "RESOLVED":
                    cust_inter_map[inter.customer_id]["unresolved_complaints"] += 1

            fact_interactions.append(FactCustomerInteraction(
                interaction_id=inter.interaction_id,
                customer_key=ckey,
                date_key=dkey,
                channel_key=chkey,
                interaction_type=inter.interaction_type,
                sentiment=inter.sentiment,
                sentiment_score=inter.sentiment_score,
                duration_minutes=inter.duration_minutes,
                is_complaint=inter.is_complaint,
                resolution_status=inter.resolution_status
            ))

        # 11. Populate Customer 360 Consolidated Serving Mart
        print("[ETL:Transform] Generating Customer 360 Consolidated Mart records...")
        c360_records = []
        for dc in dim_customers:
            cid = dc.customer_id
            dep_info = cust_deposit_map[cid]
            loan_info = cust_loan_map[cid]
            card_info = cust_card_map[cid]
            txn_info = cust_txn_30d_map[cid]
            inter_info = cust_inter_map[cid]

            # Product count: deposits + loans + cards
            prod_count = dep_info["count"] + loan_info["count"] + card_info["count"]
            has_multiple = prod_count > 1

            # Financial value
            rel_val = round(dep_info["balance"] + loan_info["outstanding"] + card_info["limit"], 2)
            
            # Card utilization
            util_pct = round((card_info["outstanding"] / card_info["limit"] * 100), 2) if card_info["limit"] > 0 else 0.0

            # LTV Score calculation (normalized 0 - 100)
            ltv_score = round(min(100.0, (
                (min(dep_info["balance"], 200000) / 200000 * 35) +
                (min(loan_info["outstanding"], 500000) / 500000 * 25) +
                (min(txn_info["volume"], 15000) / 15000 * 25) +
                (min(prod_count, 5) / 5 * 15)
            )), 1)
            is_high_val = ltv_score >= 60.0 or rel_val >= 100000.0

            # Engagement status
            sents = inter_info["sentiments"]
            avg_sent = round(sum(sents) / len(sents), 2) if sents else 0.0
            
            if inter_info["unresolved_complaints"] > 0 or avg_sent < -0.2:
                eng_status = "DECLINING"
            elif txn_info["count"] == 0 and inter_info["count_90d"] == 0:
                eng_status = "DORMANT"
            elif txn_info["count"] >= 5:
                eng_status = "ACTIVE"
            else:
                eng_status = "STABLE"

            # Composite Risk Score (0 to 100)
            credit_penalty = max(0.0, (750 - dc.credit_score) / 4.5)
            overdue_penalty = min(40.0, loan_info["max_overdue_days"] * 0.8)
            aml_penalty = dc.aml_risk_score * 0.3
            comp_risk = round(min(100.0, credit_penalty + overdue_penalty + aml_penalty), 1)
            is_high_risk = comp_risk >= 50.0 or loan_info["max_overdue_days"] >= 30

            avg_txn_amt = round(txn_info["volume"] / txn_info["count"], 2) if txn_info["count"] > 0 else 0.0

            c360_records.append(C360CustomerMart(
                customer_key=dc.customer_key,
                customer_id=cid,
                full_name=dc.full_name,
                email=dc.email,
                phone=dc.phone,
                city=dc.city,
                state=dc.state,
                customer_segment=dc.customer_segment,
                credit_score=dc.credit_score,
                credit_score_bracket=dc.credit_score_bracket,
                kyc_status=dc.kyc_status,
                aml_risk_score=dc.aml_risk_score,
                risk_tier=dc.risk_tier,
                deposit_accounts_count=dep_info["count"],
                total_deposit_balance=round(dep_info["balance"], 2),
                active_loans_count=loan_info["count"],
                total_loan_outstanding=round(loan_info["outstanding"], 2),
                max_overdue_days=loan_info["max_overdue_days"],
                total_overdue_amount=round(loan_info["total_overdue"], 2),
                has_overdue_loan=loan_info["has_overdue"],
                credit_cards_count=card_info["count"],
                total_credit_limit=round(card_info["limit"], 2),
                total_credit_outstanding=round(card_info["outstanding"], 2),
                credit_utilization_pct=util_pct,
                total_products_held=prod_count,
                has_multiple_products=has_multiple,
                total_relationship_value=rel_val,
                ltv_score=ltv_score,
                is_high_value=is_high_val,
                txn_count_30d=txn_info["count"],
                txn_volume_30d=round(txn_info["volume"], 2),
                avg_txn_amount_30d=avg_txn_amt,
                interactions_count_90d=inter_info["count_90d"],
                avg_sentiment_score=avg_sent,
                unresolved_complaints_count=inter_info["unresolved_complaints"],
                engagement_status=eng_status,
                composite_risk_score=comp_risk,
                is_high_risk=is_high_risk,
                last_synced_at=now
            ))

        return {
            "dim_dates": dim_dates,
            "dim_products": dim_products,
            "dim_branches": dim_branches,
            "dim_channels": dim_channels,
            "dim_customers": dim_customers,
            "fact_snapshots": fact_snapshots,
            "fact_loans": fact_loans,
            "fact_txns": fact_txns,
            "fact_interactions": fact_interactions,
            "c360_records": c360_records
        }
