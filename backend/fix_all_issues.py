# fix_all_issues.py
import subprocess
import sys
import time

def run_command(command, description=""):
    """Ejecutar un comando y mostrar el resultado"""
    print(f"\n🔄 {description}")
    print(f"Comando: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Éxito")
            if result.stdout.strip():
                print(f"Salida: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Error")
            if result.stderr.strip():
                print(f"Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ Excepción: {e}")
        return False

def install_missing_deps():
    """Instalar dependencias faltantes"""
    print("📦 Instalando dependencias faltantes...")
    
    # Instalar PyJWT
    success = run_command('pip install PyJWT', 'Instalando PyJWT')
    
    if success:
        print("✅ PyJWT instalado correctamente")
        return True
    else:
        print("❌ No se pudo instalar PyJWT")
        return False

def check_docker_status():
    """Verificar el estado de Docker"""
    print("\n🐳 Verificando estado de Docker...")
    
    # Verificar si Docker está instalado
    success, output = run_command('docker --version', 'Verificando Docker')
    if not success:
        print("❌ Docker no está instalado")
        return False
    
    # Verificar si Docker está funcionando
    success, output = run_command('docker ps', 'Verificando si Docker responde')
    if not success:
        print("❌ Docker no está respondiendo")
        print("\n💡 SOLUCIÓN:")
        print("1. Abre Docker Desktop desde el menú de inicio")
        print("2. Espera a que esté completamente iniciado (1-2 minutos)")
        print("3. Vuelve a ejecutar este script")
        return False
    
    print("✅ Docker está funcionando correctamente")
    return True

def setup_postgresql():
    """Configurar PostgreSQL"""
    print("\n🗄️ Configurando PostgreSQL...")
    
    # Detener y eliminar contenedor existente
    run_command('docker stop trading_db', 'Deteniendo contenedor existente')
    run_command('docker rm trading_db', 'Eliminando contenedor existente')
    
    # Esperar un momento
    time.sleep(2)
    
    # Crear nuevo contenedor
    success = run_command(
        'docker run --name trading_db -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -e POSTGRES_DB=trading_db -p 5432:5432 -d postgres:13',
        'Creando contenedor PostgreSQL'
    )
    
    if not success:
        print("❌ No se pudo crear el contenedor")
        return False
    
    # Esperar a que PostgreSQL esté listo
    print("⏳ Esperando a que PostgreSQL esté listo (30 segundos)...")
    time.sleep(30)
    
    # Verificar que el contenedor está corriendo
    success, output = run_command('docker ps', 'Verificando contenedor')
    
    if 'trading_db' in output:
        print("✅ Contenedor PostgreSQL está corriendo")
        return True
    else:
        print("❌ El contenedor no está corriendo")
        return False

def test_connection():
    """Probar la conexión a PostgreSQL"""
    print("\n🔌 Probando conexión a PostgreSQL...")
    
    try:
        import psycopg2
        
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="trading_db",
            user="user",
            password="password"
        )
        conn.close()
        print("✅ Conexión exitosa")
        return True
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def fix_import_issues():
    """Corregir problemas de importación"""
    print("\n🔧 Corrigiendo problemas de importación...")
    
    # Crear una versión fija del archivo simulator.py
    simulator_code = '''# simulator.py - Versión corregida

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
import os

# Importar RiskManager directamente
from risk_management import RiskManager

class TradingSimulator:
    def __init__(self, db: Session):
        self.db = db
        self.risk_manager = RiskManager()
    
    def create_simulation_account(self, user_id: int, account_name: str, initial_balance: float):
        """Crear una nueva cuenta de simulación"""
        # Importar modelos desde main para evitar importaciones circulares
        from main import SimulationAccount
        
        db_account = SimulationAccount(
            user_id=user_id,
            account_name=account_name,
            initial_balance=initial_balance,
            current_balance=initial_balance,
            created_at=datetime.utcnow()
        )
        self.db.add(db_account)
        self.db.commit()
        self.db.refresh(db_account)
        return db_account
    
    def get_user_simulation_accounts(self, user_id: int):
        """Obtener todas las cuentas de simulación de un usuario"""
        from main import SimulationAccount
        return self.db.query(SimulationAccount).filter(
            SimulationAccount.user_id == user_id
        ).all()
    
    def get_simulation_account(self, account_id: int, user_id: int):
        """Obtener una cuenta de simulación específica"""
        from main import SimulationAccount
        return self.db.query(SimulationAccount).filter(
            SimulationAccount.id == account_id,
            SimulationAccount.user_id == user_id
        ).first()
    
    def get_account_balance(self, account_id: int):
        """Obtener el saldo actual de una cuenta de simulación"""
        from main import SimulationAccount
        account = self.db.query(SimulationAccount).filter(
            SimulationAccount.id == account_id
        ).first()
        return account.current_balance if account else None
    
    def get_account_positions(self, account_id: int):
        """Obtener las posiciones actuales de una cuenta de simulación"""
        from main import SimulationPosition
        return self.db.query(SimulationPosition).filter(
            SimulationPosition.account_id == account_id
        ).all()
    
    def get_account_operations(self, account_id: int, limit: int = 100):
        """Obtener el historial de operaciones de una cuenta de simulación"""
        from main import SimulationOperation
        return self.db.query(SimulationOperation).filter(
            SimulationOperation.account_id == account_id
        ).order_by(SimulationOperation.timestamp.desc()).limit(limit).all()
    
    def execute_buy_order(self, account_id: int, asset_id: int, quantity: float, price: float):
        """Ejecutar una orden de compra en la cuenta de simulación"""
        from main import SimulationAccount, SimulationOperation, SimulationPosition
        
        account = self.db.query(SimulationAccount).filter(
            SimulationAccount.id == account_id
        ).first()
        
        if not account:
            raise ValueError("Cuenta no encontrada")
        
        total_cost = quantity * price
        if account.current_balance < total_cost:
            raise ValueError("Saldo insuficiente")
        
        account.current_balance -= total_cost
        
        operation = SimulationOperation(
            account_id=account_id,
            asset_id=asset_id,
            operation_type="buy",
            quantity=quantity,
            price=price,
            timestamp=datetime.utcnow()
        )
        self.db.add(operation)
        
        position = self.db.query(SimulationPosition).filter(
            SimulationPosition.account_id == account_id,
            SimulationPosition.asset_id == asset_id
        ).first()
        
        if position:
            total_quantity = position.quantity + quantity
            total_value = (position.quantity * position.average_price) + (quantity * price)
            position.average_price = total_value / total_quantity
            position.quantity = total_quantity
            position.updated_at = datetime.utcnow()
        else:
            position = SimulationPosition(
                account_id=account_id,
                asset_id=asset_id,
                quantity=quantity,
                average_price=price,
                updated_at=datetime.utcnow()
            )
            self.db.add(position)
        
        self.db.commit()
        return operation
    
    def execute_sell_order(self, account_id: int, asset_id: int, quantity: float, price: float):
        """Ejecutar una orden de venta en la cuenta de simulación"""
        from main import SimulationAccount, SimulationOperation, SimulationPosition
        
        position = self.db.query(SimulationPosition).filter(
            SimulationPosition.account_id == account_id,
            SimulationPosition.asset_id == asset_id
        ).first()
        
        if not position or position.quantity < quantity:
            raise ValueError("No hay suficiente posición para vender")
        
        position.quantity -= quantity
        if position.quantity == 0:
            self.db.delete(position)
        else:
            position.updated_at = datetime.utcnow()
        
        account = self.db.query(SimulationAccount).filter(
            SimulationAccount.id == account_id
        ).first()
        account.current_balance += quantity * price
        
        operation = SimulationOperation(
            account_id=account_id,
            asset_id=asset_id,
            operation_type="sell",
            quantity=quantity,
            price=price,
            timestamp=datetime.utcnow()
        )
        self.db.add(operation)
        
        self.db.commit()
        return operation
    
    def execute_trade_based_on_prediction(self, account_id: int, prediction: dict):
        """Ejecutar una operación basada en una predicción"""
        from main import SimulationAccount, SimulationPosition, Asset
        
        account = self.db.query(SimulationAccount).filter(
            SimulationAccount.id == account_id
        ).first()
        
        if not account:
            raise ValueError("Cuenta no encontrada")
        
        asset = self.db.query(Asset).filter(
            Asset.symbol == prediction['symbol']
        ).first()
        
        if not asset:
            raise ValueError("Activo no encontrado")
        
        position = self.db.query(SimulationPosition).filter(
            SimulationPosition.account_id == account_id,
            SimulationPosition.asset_id == asset.id
        ).first()
        
        current_price = prediction['current_price']
        recommendation = prediction['recommendation']
        
        position_size = self.risk_manager.calculate_position_size(
            symbol=prediction['symbol'],
            current_price=current_price,
            account_balance=account.current_balance
        )
        
        if recommendation == 'comprar':
            if position and position.quantity > 0:
                return {"message": "Ya existe una posición para este activo"}
            
            try:
                operation = self.execute_buy_order(
                    account_id=account_id,
                    asset_id=asset.id,
                    quantity=position_size,
                    price=current_price
                )
                return {"message": "Orden de compra ejecutada", "operation_id": operation.id}
            except ValueError as e:
                return {"error": str(e)}
        
        elif recommendation == 'vender':
            if not position or position.quantity == 0:
                return {"message": "No hay posición para vender"}
            
            quantity_to_sell = position.quantity
            
            try:
                operation = self.execute_sell_order(
                    account_id=account_id,
                    asset_id=asset.id,
                    quantity=quantity_to_sell,
                    price=current_price
                )
                return {"message": "Orden de venta ejecutada", "operation_id": operation.id}
            except ValueError as e:
                return {"error": str(e)}
        
        else:
            return {"message": "Mantener posición actual"}
    
    def get_account_performance(self, account_id: int):
        """Calcular el rendimiento de una cuenta de simulación"""
        from main import SimulationAccount, SimulationOperation, SimulationPosition
        
        account = self.db.query(SimulationAccount).filter(
            SimulationAccount.id == account_id
        ).first()
        
        if not account:
            return None
        
        positions = self.get_account_positions(account_id)
        portfolio_value = account.current_balance
        
        for position in positions:
            last_operation = self.db.query(SimulationOperation).filter(
                SimulationOperation.account_id == account_id,
                SimulationOperation.asset_id == position.asset_id
            ).order_by(SimulationOperation.timestamp.desc()).first()
            
            if last_operation:
                current_price = last_operation.price
                position_value = position.quantity * current_price
                portfolio_value += position_value
        
        total_return = (portfolio_value - account.initial_balance) / account.initial_balance * 100
        
        return {
            "account_id": account_id,
            "initial_balance": float(account.initial_balance),
            "current_balance": float(account.current_balance),
            "portfolio_value": float(portfolio_value),
            "total_return": float(total_return)
        }
'''
    
    try:
        with open('simulator.py', 'w', encoding='utf-8') as f:
            f.write(simulator_code)
        print("✅ Archivo simulator.py corregido")
        return True
    except Exception as e:
        print(f"❌ Error al corregir simulator.py: {e}")
        return False

def main():
    print("🔧 Solucionador de Todos los Problemas")
    print("=" * 50)
    
    steps = [
        ("Instalando dependencias faltantes", install_missing_deps),
        ("Verificando Docker", check_docker_status),
        ("Configurando PostgreSQL", setup_postgresql),
        ("Probando conexión", test_connection),
        ("Corrigiendo importaciones", fix_import_issues)
    ]
    
    completed_steps = 0
    
    for step_name, step_function in steps:
        print(f"\n📋 Paso {completed_steps + 1}/{len(steps)}: {step_name}")
        print("-" * 40)
        
        if step_function():
            completed_steps += 1
            print(f"✅ {step_name} completado")
        else:
            print(f"❌ {step_name} falló")
            break
    
    print(f"\n📊 Resumen: {completed_steps}/{len(steps)} pasos completados")
    
    if completed_steps == len(steps):
        print("\n🎉 ¡Todos los problemas solucionados!")
        print("\n📝 Siguientes pasos:")
        print("1. python init_db.py")
        print("2. python main.py")
        print("3. Acceder a http://localhost:8000")
    else:
        print(f"\n❌ Se detuvo en el paso {completed_steps + 1}")
        print("\n💡 Si Docker falló:")
        print("1. Abre Docker Desktop desde el menú de inicio")
        print("2. Espera 1-2 minutos a que inicie completamente")
        print("3. Vuelve a ejecutar este script")

if __name__ == "__main__":
    main()