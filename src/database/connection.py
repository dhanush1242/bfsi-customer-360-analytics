from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.config import SOURCE_DB_URL, WAREHOUSE_DB_URL, DB_TYPE

# Source Engine
connect_args_source = {"check_same_thread": False} if "sqlite" in SOURCE_DB_URL else {}
source_engine = create_engine(SOURCE_DB_URL, connect_args=connect_args_source, echo=False)
SourceSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=source_engine)

# Warehouse Engine
connect_args_wh = {"check_same_thread": False} if "sqlite" in WAREHOUSE_DB_URL else {}
warehouse_engine = create_engine(WAREHOUSE_DB_URL, connect_args=connect_args_wh, echo=False)
WarehouseSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=warehouse_engine)

SourceBase = declarative_base()
WarehouseBase = declarative_base()

def get_source_db():
    db = SourceSessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_warehouse_db():
    db = WarehouseSessionLocal()
    try:
        yield db
    finally:
        db.close()
