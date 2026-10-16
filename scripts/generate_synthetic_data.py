import random
import datetime
from datetime import timedelta
from sqlalchemy.orm import Session
from src.config import (
    NUM_CUSTOMERS, NUM_ACCOUNTS, NUM_LOANS, NUM_CARDS,
    NUM_TRANSACTIONS, NUM_INTERACTIONS, DATA_SEED
)
from src.database.connection import source_engine, SourceBase, SourceSessionLocal
from src.database.models_source import (
    SourceCustomer, SourceAccount, SourceLoan, SourceCreditCard,
    SourceTransaction, SourcePayment, SourceKYC, SourceInteraction
)

random.seed(DATA_SEED)

FIRST_NAMES = [
    "Alexander", "Sophia", "Ethan", "Olivia", "Liam", "Emma", "Noah", "Ava", "Lucas", "Isabella",
    "Mason", "Mia", "James", "Harper", "Benjamin", "Evelyn", "Elijah", "Abigail", "William", "Emily",
    "Michael", "Elizabeth", "Daniel", "Mila", "Henry", "Ella", "Jackson", "Avery", "Sebastian", "Scarlett",
    "Aiden", "Victoria", "Matthew", "Madison", "Samuel", "Luna", "David", "Grace", "Joseph", "Chloe",
    "Carter", "Penelope", "Owen", "Layla", "Wyatt", "Riley", "John", "Zoey", "Jack", "Nora"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
    "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
    "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts"
]

CITIES = [
    ("New York", "NY", "Northeast"),
    ("Boston", "MA", "Northeast"),
    ("Charlotte", "NC", "Southeast"),
    ("Atlanta", "GA", "Southeast"),
    ("Miami", "FL", "Southeast"),
    ("Chicago", "IL", "Midwest"),
    ("Columbus", "OH", "Midwest"),
    ("Dallas", "TX", "Southwest"),
    ("Austin", "TX", "Southwest"),
    ("Denver", "CO", "West"),
    ("San Francisco", "CA", "West"),
    ("Los Angeles", "CA", "West"),
    ("Seattle", "WA", "West")
]

BRANCHES = [f"BR-{city[:3].upper()}-{100 + i}" for i, (city, _, _) in enumerate(CITIES)]

OCCUPATIONS = [
    "Software Engineer", "Physician", "Financial Analyst", "Marketing Director", "Teacher",
    "Management Consultant", "Attorney", "Nurse Practitioner", "Data Scientist", "Sales Executive",
    "Accountant", "Architect", "Small Business Owner", "Product Manager", "Real Estate Broker"
]

MERCHANTS = {
    "Grocery": ["Whole Foods Market", "Trader Joe's", "Kroger", "Safeway", "Costco Wholesale"],
    "Dining": ["Starbucks", "Sweetgreen", "Chipotle", "Capital Grille", "Uber Eats", "DoorDash"],
    "Travel": ["Delta Air Lines", "United Airlines", "Marriott Hotels", "Airbnb", "Uber", "Lyft"],
    "Utilities": ["ConEdison", "AT&T", "Verizon Wireless", "Duke Energy", "Water Utility"],
    "Electronics": ["Apple Store", "Best Buy", "Amazon.com", "B&H Photo"],
    "Healthcare": ["CVS Pharmacy", "Walgreens", "Quest Diagnostics", "CityMD"]
}

def generate_all_data():
    print(f"[*] Initializing Operational Source Database Schema...")
    SourceBase.metadata.drop_all(bind=source_engine)
    SourceBase.metadata.create_all(bind=source_engine)
    
    session: Session = SourceSessionLocal()
    now = datetime.datetime.now()
    
    try:
        print(f"[*] Generating {NUM_CUSTOMERS} customers...")
        customers = []
        customer_ids = []
        
        for i in range(1, NUM_CUSTOMERS + 1):
            cid = f"CUST-{i:06d}"
            customer_ids.append(cid)
            fname = random.choice(FIRST_NAMES)
            lname = random.choice(LAST_NAMES)
            city_info = random.choice(CITIES)
            
            # Segment & income distribution
            seg_roll = random.random()
            if seg_roll < 0.50:
                segment = "Retail"
                income = round(random.uniform(32000, 85000), 2)
                credit_score = random.randint(580, 750)
            elif seg_roll < 0.80:
                segment = "Affluent"
                income = round(random.uniform(85000, 200000), 2)
                credit_score = random.randint(680, 810)
            elif seg_roll < 0.95:
                segment = "HNI"
                income = round(random.uniform(200000, 600000), 2)
                credit_score = random.randint(720, 830)
            elif seg_roll < 0.98:
                segment = "Ultra HNI"
                income = round(random.uniform(600000, 2500000), 2)
                credit_score = random.randint(750, 850)
            else:
                segment = "Corporate"
                income = round(random.uniform(1200000, 5000000), 2)
                credit_score = random.randint(700, 820)
                
            # Occasional subprime score for realistic credit risk
            if random.random() < 0.08:
                credit_score = random.randint(480, 579)

            dob = now.date() - timedelta(days=random.randint(21 * 365, 75 * 365))
            created_days_ago = random.randint(60, 1800)
            created_at = now - timedelta(days=created_days_ago)

            cust = SourceCustomer(
                customer_id=cid,
                first_name=fname,
                last_name=lname,
                email=f"{fname.lower()}.{lname.lower()}_{i}@bfsi-sample.com",
                phone=f"+1-{random.randint(200,999)}-{random.randint(200,999)}-{random.randint(1000,9999)}",
                date_of_birth=dob,
                gender=random.choice(["Male", "Female", "Non-Binary"]),
                annual_income=income,
                occupation=random.choice(OCCUPATIONS),
                address_city=city_info[0],
                address_state=city_info[1],
                address_country="USA",
                postal_code=f"{random.randint(10000, 99999)}",
                branch_id=random.choice(BRANCHES),
                customer_segment=segment,
                credit_score=credit_score,
                created_at=created_at,
                updated_at=now
            )
            customers.append(cust)

        session.bulk_save_objects(customers)
        session.commit()
        print(f"[OK] {len(customers)} customers created.")

        print(f"[*] Generating {NUM_ACCOUNTS} deposit & current accounts...")
        accounts = []
        account_ids = []
        account_cust_map = {}
        
        # Ensure every customer has at least 1 account, and some have multiple
        account_counter = 1
        for cid in customer_ids:
            num_accs = 1
            r = random.random()
            if r < 0.40:
                num_accs = 2
            elif r < 0.15:
                num_accs = 3
                
            for _ in range(num_accs):
                aid = f"ACC-{account_counter:07d}"
                account_counter += 1
                account_ids.append(aid)
                account_cust_map[aid] = cid
                
                acc_type = random.choice(["Savings", "Checking", "Money Market", "Certificate of Deposit"])
                bal_base = random.uniform(500, 25000)
                if acc_type in ["Money Market", "Certificate of Deposit"]:
                    bal_base *= random.uniform(2.5, 8.0)
                    
                cur_bal = round(bal_base, 2)
                avail_bal = round(cur_bal * random.uniform(0.90, 1.0), 2)
                rate = 0.05 if acc_type == "Checking" else round(random.uniform(1.5, 5.2), 2)
                
                status_roll = random.random()
                status = "ACTIVE"
                if status_roll < 0.04:
                    status = "DORMANT"
                elif status_roll < 0.06:
                    status = "FROZEN"

                opened_dt = now.date() - timedelta(days=random.randint(30, 1200))
                last_act = now.date() - timedelta(days=random.randint(0, 45)) if status == "ACTIVE" else now.date() - timedelta(days=random.randint(90, 300))

                acc = SourceAccount(
                    account_id=aid,
                    customer_id=cid,
                    account_type=acc_type,
                    currency="USD",
                    current_balance=cur_bal,
                    available_balance=avail_bal,
                    interest_rate=rate,
                    status=status,
                    opened_date=opened_dt,
                    last_activity_date=last_act,
                    branch_id=random.choice(BRANCHES)
                )
                accounts.append(acc)

        session.bulk_save_objects(accounts)
        session.commit()
        print(f"[OK] {len(accounts)} accounts created.")

        print(f"[*] Generating {NUM_LOANS} loan portfolio contracts...")
        loans = []
        loan_counter = 1
        # Sample customers for loans
        loan_customers = random.sample(customer_ids, min(NUM_LOANS, len(customer_ids)))
        
        for cid in loan_customers:
            lid = f"LOAN-{loan_counter:06d}"
            loan_counter += 1
            ltype = random.choice(["Home Mortgage", "Auto Loan", "Personal Loan", "Student Loan", "Business Loan"])
            
            if ltype == "Home Mortgage":
                principal = round(random.uniform(250000, 950000), 2)
                rate = round(random.uniform(5.5, 7.8), 2)
                term = random.choice([180, 360]) # 15 or 30 yrs
            elif ltype == "Auto Loan":
                principal = round(random.uniform(20000, 65000), 2)
                rate = round(random.uniform(4.5, 9.5), 2)
                term = random.choice([36, 48, 60, 72])
            elif ltype == "Business Loan":
                principal = round(random.uniform(100000, 500000), 2)
                rate = round(random.uniform(6.5, 11.0), 2)
                term = random.choice([60, 120])
            else:
                principal = round(random.uniform(5000, 35000), 2)
                rate = round(random.uniform(8.0, 16.0), 2)
                term = random.choice([24, 36, 48])

            elapsed_months = random.randint(2, min(term - 1, 36))
            payoff_ratio = (term - elapsed_months) / term
            outstanding = round(principal * payoff_ratio, 2)
            monthly_emi = round((principal / term) * (1 + (rate / 100)), 2)

            start_dt = now.date() - timedelta(days=elapsed_months * 30)
            end_dt = start_dt + timedelta(days=term * 30)

            # Delinquency modeling
            delinq_roll = random.random()
            if delinq_roll < 0.78:
                status = "CURRENT"
                overdue_days = 0
                overdue_amount = 0.0
            elif delinq_roll < 0.88:
                status = "DELINQUENT"
                overdue_days = random.randint(15, 29)
                overdue_amount = round(monthly_emi * 1.0, 2)
            elif delinq_roll < 0.94:
                status = "DELINQUENT"
                overdue_days = random.randint(30, 59)
                overdue_amount = round(monthly_emi * 2.0, 2)
            elif delinq_roll < 0.98:
                status = "DELINQUENT"
                overdue_days = random.randint(60, 89)
                overdue_amount = round(monthly_emi * 3.0, 2)
            else:
                status = "DEFAULTED"
                overdue_days = random.randint(90, 180)
                overdue_amount = round(monthly_emi * random.uniform(4.0, 6.0), 2)

            collateral = round(principal * 1.2, 2) if ltype in ["Home Mortgage", "Auto Loan"] else 0.0

            loan = SourceLoan(
                loan_id=lid,
                customer_id=cid,
                loan_type=ltype,
                principal_amount=principal,
                interest_rate=rate,
                term_months=term,
                outstanding_balance=outstanding,
                monthly_installment=monthly_emi,
                start_date=start_dt,
                end_date=end_dt,
                status=status,
                overdue_days=overdue_days,
                overdue_amount=overdue_amount,
                collateral_value=collateral
            )
            loans.append(loan)

        session.bulk_save_objects(loans)
        session.commit()
        print(f"[OK] {len(loans)} loans created.")

        print(f"[*] Generating {NUM_CARDS} credit cards...")
        cards = []
        card_counter = 1
        card_customers = random.sample(customer_ids, min(NUM_CARDS, len(customer_ids)))
        
        for cid in card_customers:
            card_id = f"CARD-{card_counter:06d}"
            card_counter += 1
            tier = random.choice(["Classic", "Gold", "Platinum", "Infinite", "Signature"])
            
            limit_map = {
                "Classic": (2500, 6000),
                "Gold": (6000, 15000),
                "Platinum": (15000, 30000),
                "Infinite": (30000, 75000),
                "Signature": (20000, 50000)
            }
            limit_min, limit_max = limit_map[tier]
            credit_limit = round(random.uniform(limit_min, limit_max), -2)
            utilization = random.betavariate(2, 5) # most have low to moderate utilization, some high
            outstanding = round(credit_limit * utilization, 2)
            available = round(credit_limit - outstanding, 2)
            apr = round(random.uniform(14.99, 26.99), 2)

            issue_dt = now.date() - timedelta(days=random.randint(60, 900))
            exp_dt = issue_dt + timedelta(days=365 * 4)

            card = SourceCreditCard(
                card_id=card_id,
                customer_id=cid,
                card_number_masked=f"************{random.randint(1000, 9999)}",
                card_tier=tier,
                credit_limit=credit_limit,
                current_outstanding=outstanding,
                available_credit=available,
                apr_rate=apr,
                issue_date=issue_dt,
                expiry_date=exp_dt,
                status="ACTIVE" if random.random() > 0.03 else "BLOCKED"
            )
            cards.append(card)

        session.bulk_save_objects(cards)
        session.commit()
        print(f"[OK] {len(cards)} credit cards created.")

        print(f"[*] Generating {NUM_TRANSACTIONS} core transactions...")
        transactions = []
        txn_types = ["DEBIT", "CREDIT", "TRANSFER", "ATM_WITHDRAWAL", "POS", "WIRE"]
        type_weights = [0.45, 0.15, 0.15, 0.10, 0.12, 0.03]
        channels = ["MOBILE", "WEB", "ATM", "BRANCH", "POS"]
        channel_weights = [0.55, 0.25, 0.10, 0.05, 0.05]

        for i in range(1, NUM_TRANSACTIONS + 1):
            tid = f"TXN-{i:08d}"
            aid = random.choice(account_ids)
            cid = account_cust_map[aid]
            ttype = random.choices(txn_types, weights=type_weights, k=1)[0]
            chan = random.choices(channels, weights=channel_weights, k=1)[0]
            
            cat = random.choice(list(MERCHANTS.keys()))
            m_name = random.choice(MERCHANTS[cat])

            # Amounts: majority micro/daily, tail large transactions
            if ttype in ["ATM_WITHDRAWAL", "POS", "DEBIT"]:
                amt = round(random.expovariate(1 / 65) + 3.5, 2)
            elif ttype == "CREDIT":
                amt = round(random.uniform(500, 6500), 2)
            else: # WIRE / TRANSFER
                amt = round(random.uniform(200, 15000), 2)

            days_ago = random.randint(0, 180)
            txn_ts = now - timedelta(days=days_ago, minutes=random.randint(0, 1440))
            is_fraud = True if (amt > 5000 and random.random() < 0.02) else False

            txn = SourceTransaction(
                transaction_id=tid,
                account_id=aid,
                customer_id=cid,
                transaction_type=ttype,
                channel=chan,
                amount=amt,
                currency="USD",
                merchant_category=cat,
                merchant_name=m_name,
                status="SETTLED" if random.random() > 0.02 else "PENDING",
                is_fraud_flag=is_fraud,
                transaction_timestamp=txn_ts
            )
            transactions.append(txn)

        session.bulk_save_objects(transactions)
        session.commit()
        print(f"[OK] {len(transactions)} transactions generated.")

        print(f"[*] Generating KYC & AML Compliance records...")
        kyc_records = []
        for i, cid in enumerate(customer_ids, 1):
            kyc_id = f"KYC-{i:06d}"
            id_type = random.choice(["Passport", "Driving License", "National ID"])
            
            aml_score = round(random.betavariate(1.5, 8.0) * 100, 2) # mostly low risk
            pep = True if (aml_score > 60 and random.random() < 0.05) else False
            sanction = "FLAGGED" if (aml_score > 85 and random.random() < 0.08) else "PASSED"
            
            if aml_score > 80 or sanction == "FLAGGED":
                status = random.choice(["PENDING_REVIEW", "REJECTED"])
            else:
                status = "VERIFIED"

            verified_dt = now - timedelta(days=random.randint(30, 500)) if status == "VERIFIED" else None

            kyc = SourceKYC(
                kyc_id=kyc_id,
                customer_id=cid,
                id_type=id_type,
                id_number_masked=f"ID-***-{random.randint(1000, 9999)}",
                kyc_status=status,
                aml_risk_score=aml_score,
                pep_flag=pep,
                sanctions_check=sanction,
                verified_at=verified_dt,
                last_reviewed_at=now - timedelta(days=random.randint(1, 90))
            )
            kyc_records.append(kyc)

        session.bulk_save_objects(kyc_records)
        session.commit()
        print(f"[OK] {len(kyc_records)} KYC compliance profiles created.")

        print(f"[*] Generating {NUM_INTERACTIONS} omnichannel CRM customer interactions...")
        interactions = []
        interaction_types = [
            "Inquire Balance", "Loan Inquiry", "Dispute Txn", "Technical Support",
            "Wealth Consultation", "Credit Card Limit Increase", "Fee Waiver Request", "Account Statement"
        ]
        channels_crm = ["Mobile App", "Phone Banking", "In-Branch", "Email", "Chatbot"]

        for i in range(1, NUM_INTERACTIONS + 1):
            iid = f"INT-{i:07d}"
            cid = random.choice(customer_ids)
            itype = random.choice(interaction_types)
            chan = random.choice(channels_crm)
            
            # Sentiment correlation
            is_complaint = itype in ["Dispute Txn", "Fee Waiver Request", "Technical Support"] and random.random() < 0.45
            if is_complaint:
                sentiment = "NEGATIVE"
                sentiment_score = round(random.uniform(-1.0, -0.2), 2)
                res_status = random.choice(["RESOLVED", "ESCALATED", "OPEN"])
            elif itype == "Wealth Consultation":
                sentiment = "POSITIVE"
                sentiment_score = round(random.uniform(0.4, 1.0), 2)
                res_status = "RESOLVED"
            else:
                s_roll = random.random()
                if s_roll < 0.50:
                    sentiment = "POSITIVE"
                    sentiment_score = round(random.uniform(0.1, 0.8), 2)
                elif s_roll < 0.85:
                    sentiment = "NEUTRAL"
                    sentiment_score = round(random.uniform(-0.1, 0.1), 2)
                else:
                    sentiment = "NEGATIVE"
                    sentiment_score = round(random.uniform(-0.6, -0.1), 2)
                res_status = "RESOLVED"

            int_ts = now - timedelta(days=random.randint(0, 120), minutes=random.randint(0, 1440))

            inter = SourceInteraction(
                interaction_id=iid,
                customer_id=cid,
                channel=chan,
                interaction_type=itype,
                sentiment=sentiment,
                sentiment_score=sentiment_score,
                duration_minutes=round(random.uniform(1.5, 25.0), 1),
                is_complaint=is_complaint,
                resolution_status=res_status,
                interaction_timestamp=int_ts
            )
            interactions.append(inter)

        session.bulk_save_objects(interactions)
        session.commit()
        print(f"[OK] {len(interactions)} CRM interactions recorded.")

        print(f"[SUCCESS] Synthetic Data Generation complete for BFSI operational systems!")

    except Exception as e:
        session.rollback()
        print(f"[ERROR] Synthetic data generation failed: {e}")
        raise e
    finally:
        session.close()

if __name__ == "__main__":
    generate_all_data()
