# init_sqlite.py - Inicialización de base de datos SQLite
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Numeric, ForeignKey, Boolean, JSON, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Configuración de la base de datos SQLite
DATABASE_URL = "sqlite:///./trading.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelos de la base de datos
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

def init_sqlite_db():
    """Inicializar la base de datos SQLite"""
    print("🚀 Inicializando Base de Datos SQLite")
    print("=" * 50)
    
    try:
        # Crear las tablas
        print("📋 Creando tablas...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas creadas exitosamente")
        
        # Crear sesión
        session = SessionLocal()
        
        # Agregar activos iniciales
        print("\n💰 Agregando activos iniciales...")
        assets_data = [
            {'simbolo': 'AAPL', 'nombre': 'Apple Inc.', 'tipo': 'accion', 'mercado': 'bolsa'},
            {'simbolo': 'MSFT', 'nombre': 'Microsoft Corporation', 'tipo': 'accion', 'mercado': 'bolsa'},
            {'simbolo': 'GOOGL', 'nombre': 'Alphabet Inc.', 'tipo': 'accion', 'mercado': 'bolsa'},
            {'simbolo': 'AMZN', 'nombre': 'Amazon.com Inc.', 'tipo': 'accion', 'mercado': 'bolsa'},
            {'simbolo': 'TSLA', 'nombre': 'Tesla Inc.', 'tipo': 'accion', 'mercado': 'bolsa'},
            {'simbolo': 'BTC/USDT', 'nombre': 'Bitcoin', 'tipo': 'cripto', 'mercado': 'crypto'},
            {'simbolo': 'ETH/USDT', 'nombre': 'Ethereum', 'tipo': 'cripto', 'mercado': 'crypto'},
            {'simbolo': 'BNB/USDT', 'nombre': 'Binance Coin', 'tipo': 'cripto', 'mercado': 'crypto'},
            {'simbolo': 'ADA/USDT', 'nombre': 'Cardano', 'tipo': 'cripto', 'mercado': 'crypto'},
            {'simbolo': 'SOL/USDT', 'nombre': 'Solana', 'tipo': 'cripto', 'mercado': 'crypto'},
        ]
        
        assets_added = 0
        for asset_data in assets_data:
            # Verificar si ya existe
            existing = session.query(Asset).filter(Asset.simbolo == asset_data['simbolo']).first()
            if not existing:
                asset = Asset(**asset_data)
                session.add(asset)
                assets_added += 1
                print(f"  ➕ {asset_data['simbolo']} - {asset_data['nombre']}")
        
        # Agregar usuario de prueba
        print("\n👤 Agregando usuario de prueba...")
        existing_user = session.query(User).filter(User.username == 'test').first()
        if not existing_user:
            user = User(username='test', password_hash='test', email='test@example.com')
            session.add(user)
            print("  ➕ Usuario: test")
        
        # Confirmar cambios
        session.commit()
        session.close()
        
        print(f"\n🎉 ¡Base de datos SQLite inicializada exitosamente!")
        print(f"📊 Resumen:")
        print(f"   - {assets_added} activos agregados")
        print(f"   - Tablas creadas: usuarios, activos, y más")
        print(f"   - Usuario de prueba: test")
        print(f"   - Archivo de base de datos: trading.db")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la inicialización: {e}")
        return False

def main():
    print("🏗️  Inicializador de Base de Datos SQLite")
    print("=" * 50)
    
    if init_sqlite_db():
        print("\n🚀 ¡Listo para iniciar el servidor!")
        print("Ejecuta: python main_sqlite.py")
        print("\n🌐 Accede a:")
        print("  - Backend: http://localhost:8000")
        print("  - Documentación: http://localhost:8000/docs")
    else:
        print("\n❌ No se pudo inicializar la base de datos")

if __name__ == "__main__":
    main()