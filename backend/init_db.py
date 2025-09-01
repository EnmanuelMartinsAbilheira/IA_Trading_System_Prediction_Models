# init_db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import Base, Asset, User
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/trading_db")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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