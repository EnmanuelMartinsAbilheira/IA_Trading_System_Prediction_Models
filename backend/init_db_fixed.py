# init_db.py
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Numeric, ForeignKey, Boolean, JSON, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Configuración de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/trading_db")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelos de la base de datos (definidos aquí para evitar importar de main.py)
class User(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    password_hash = Column(String(255))
    email = Column(String(100), unique=True, index=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

class Asset(Base):
    __tablename__ = "activos"
    
    id = Column(Integer, primary_key=True, index=True)
    simbolo = Column(String(20), unique=True, index=True)
    nombre = Column(String(100))
    tipo = Column(String(20))
    mercado = Column(String(50))

def init_db():
    # Crear las tablas
    Base.metadata.create_all(bind=engine)
    
    # Crear una sesión
    session = Session()
    
    # Agregar algunos activos iniciales
    assets = [
        Asset(simbolo='AAPL', nombre='Apple Inc.', tipo='accion', mercado='bolsa'),
        Asset(simbolo='MSFT', nombre='Microsoft Corporation', tipo='accion', mercado='bolsa'),
        Asset(simbolo='GOOGL', nombre='Alphabet Inc.', tipo='accion', mercado='bolsa'),
        Asset(simbolo='AMZN', nombre='Amazon.com Inc.', tipo='accion', mercado='bolsa'),
        Asset(simbolo='TSLA', nombre='Tesla Inc.', tipo='accion', mercado='bolsa'),
        Asset(simbolo='BTC/USDT', nombre='Bitcoin', tipo='cripto', mercado='crypto'),
        Asset(simbolo='ETH/USDT', nombre='Ethereum', tipo='cripto', mercado='crypto'),
        Asset(simbolo='BNB/USDT', nombre='Binance Coin', tipo='cripto', mercado='crypto'),
        Asset(simbolo='ADA/USDT', nombre='Cardano', tipo='cripto', mercado='crypto'),
        Asset(simbolo='SOL/USDT', nombre='Solana', tipo='cripto', mercado='crypto'),
    ]
    
    # Agregar los activos a la base de datos
    for asset in assets:
        # Verificar si ya existe
        existing = session.query(Asset).filter(Asset.simbolo == asset.simbolo).first()
        if not existing:
            session.add(asset)
    
    # Agregar un usuario de prueba
    user = User(username='test', password_hash='test', email='test@example.com')
    existing_user = session.query(User).filter(User.username == user.username).first()
    if not existing_user:
        session.add(user)
    
    # Confirmar los cambios
    session.commit()
    session.close()
    
    print("Base de datos inicializada correctamente.")

if __name__ == "__main__":
    init_db()