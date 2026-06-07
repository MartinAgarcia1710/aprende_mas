from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datos.base import Base

DATABASE_URL = "sqlite:///aprende_mas.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def inicializar_base_de_datos():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()