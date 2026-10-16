from typing import Dict, Any, List
from src.database.connection import SourceSessionLocal
from src.database.models_source import (
    SourceCustomer, SourceAccount, SourceLoan, SourceCreditCard,
    SourceTransaction, SourcePayment, SourceKYC, SourceInteraction
)

class DataExtractor:
    @staticmethod
    def extract_all() -> Dict[str, List[Any]]:
        session = SourceSessionLocal()
        try:
            print("[ETL:Extract] Extracting customers...")
            customers = session.query(SourceCustomer).all()
            print(f"[ETL:Extract] Extracted {len(customers)} customers.")

            print("[ETL:Extract] Extracting deposit accounts...")
            accounts = session.query(SourceAccount).all()
            print(f"[ETL:Extract] Extracted {len(accounts)} accounts.")

            print("[ETL:Extract] Extracting loans...")
            loans = session.query(SourceLoan).all()
            print(f"[ETL:Extract] Extracted {len(loans)} loans.")

            print("[ETL:Extract] Extracting credit cards...")
            cards = session.query(SourceCreditCard).all()
            print(f"[ETL:Extract] Extracted {len(cards)} credit cards.")

            print("[ETL:Extract] Extracting transactions...")
            transactions = session.query(SourceTransaction).all()
            print(f"[ETL:Extract] Extracted {len(transactions)} transactions.")

            print("[ETL:Extract] Extracting KYC records...")
            kyc = session.query(SourceKYC).all()
            print(f"[ETL:Extract] Extracted {len(kyc)} KYC records.")

            print("[ETL:Extract] Extracting CRM interactions...")
            interactions = session.query(SourceInteraction).all()
            print(f"[ETL:Extract] Extracted {len(interactions)} interactions.")

            return {
                "customers": customers,
                "accounts": accounts,
                "loans": loans,
                "cards": cards,
                "transactions": transactions,
                "kyc": kyc,
                "interactions": interactions
            }
        finally:
            session.close()
