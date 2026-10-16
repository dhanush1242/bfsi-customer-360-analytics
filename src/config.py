import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# Ensure required directories exist
(BASE_DIR / "data" / "raw").mkdir(parents=True, exist_ok=True)
(BASE_DIR / "data" / "warehouse").mkdir(parents=True, exist_ok=True)

DB_TYPE = os.getenv("DB_TYPE", "sqlite").lower()

# Source Database URL
if DB_TYPE == "postgres":
    pg_user = os.getenv("POSTGRES_USER", "bfsi_admin")
    pg_pass = os.getenv("POSTGRES_PASSWORD", "bfsi_secure_pass_2026")
    pg_host = os.getenv("POSTGRES_SERVER", "localhost")
    pg_port = os.getenv("POSTGRES_PORT", "5432")
    pg_db = os.getenv("POSTGRES_DB", "bfsi_enterprise_dw")
    SOURCE_DB_URL = f"postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}_source"
    WAREHOUSE_DB_URL = f"postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}"
else:
    source_path = BASE_DIR / os.getenv("SOURCE_DB_PATH", "data/raw/bfsi_source_systems.db")
    warehouse_path = BASE_DIR / os.getenv("WAREHOUSE_DB_PATH", "data/warehouse/bfsi_data_warehouse.db")
    SOURCE_DB_URL = f"sqlite:///{source_path}"
    WAREHOUSE_DB_URL = f"sqlite:///{warehouse_path}"

# API Settings
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_TITLE = os.getenv("API_TITLE", "Enterprise BFSI Customer 360 API")
API_VERSION = os.getenv("API_VERSION", "1.0.0")

# Pipeline / Synthetic data constants
DATA_SEED = int(os.getenv("DATA_SEED", "42"))
NUM_CUSTOMERS = int(os.getenv("NUM_CUSTOMERS", "1200"))
NUM_ACCOUNTS = int(os.getenv("NUM_ACCOUNTS", "2200"))
NUM_LOANS = int(os.getenv("NUM_LOANS", "650"))
NUM_CARDS = int(os.getenv("NUM_CARDS", "900"))
NUM_TRANSACTIONS = int(os.getenv("NUM_TRANSACTIONS", "25000"))
NUM_INTERACTIONS = int(os.getenv("NUM_INTERACTIONS", "4000"))
