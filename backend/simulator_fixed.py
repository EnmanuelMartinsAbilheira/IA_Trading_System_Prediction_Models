# simulator_fixed.py
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
import os

# Importaciones absolutas en lugar de relativas
from risk_management import RiskManager

class TradingSimulator:
    def __init__(self, db: Session):
        self.db = db
        self.risk_manager = RiskManager()
    
    def create_simulation_account(self, user_id: int, account_name: str, initial_balance: float):
        """Crear una nueva cuenta de simulación"""
        # Importar modelos aquí para evitar problemas de importación circular
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
        # Importar modelos aquí
        from main import SimulationAccount, SimulationOperation, SimulationPosition
        
        # Verificar si hay suficiente saldo
        account = self.db.query(SimulationAccount).filter(
            SimulationAccount.id == account_id
        ).first()
        
        if not account:
            raise ValueError("Cuenta no encontrada")
        
        total_cost = quantity * price
        if account.current_balance < total_cost:
            raise ValueError("Saldo insuficiente")
        
        # Actualizar saldo
        account.current_balance -= total_cost
        
        # Registrar la operación
        operation = SimulationOperation(
            account_id=account_id,
            asset_id=asset_id,
            operation_type="buy",
            quantity=quantity,
            price=price,
            timestamp=datetime.utcnow()
        )
        self.db.add(operation)
        
        # Actualizar o crear la posición
        position = self.db.query(SimulationPosition).filter(
            SimulationPosition.account_id == account_id,
            SimulationPosition.asset_id == asset_id
        ).first()
        
        if position:
            # Calcular nuevo precio promedio
            total_quantity = position.quantity + quantity
            total_value = (position.quantity * position.average_price) + (quantity * price)
            position.average_price = total_value / total_quantity
            position.quantity = total_quantity
            position.updated_at = datetime.utcnow()
        else:
            # Crear nueva posición
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
        # Importar modelos aquí
        from main import SimulationAccount, SimulationOperation, SimulationPosition
        
        # Verificar si hay suficiente posición
        position = self.db.query(SimulationPosition).filter(
            SimulationPosition.account_id == account_id,
            SimulationPosition.asset_id == asset_id
        ).first()
        
        if not position or position.quantity < quantity:
            raise ValueError("No hay suficiente posición para vender")
        
        # Actualizar posición
        position.quantity -= quantity
        if position.quantity == 0:
            self.db.delete(position)
        else:
            position.updated_at = datetime.utcnow()
        
        # Actualizar saldo
        account = self.db.query(SimulationAccount).filter(
            SimulationAccount.id == account_id
        ).first()
        account.current_balance += quantity * price
        
        # Registrar la operación
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
        """
        Ejecutar una operación basada en una predicción
        Utiliza la gestión de riesgos para determinar el tamaño de la posición
        """
        # Importar modelos aquí
        from main import SimulationAccount, SimulationPosition, Asset
        
        # Obtener la cuenta
        account = self.db.query(SimulationAccount).filter(
            SimulationAccount.id == account_id
        ).first()
        
        if not account:
            raise ValueError("Cuenta no encontrada")
        
        # Obtener el activo
        asset = self.db.query(Asset).filter(
            Asset.symbol == prediction['symbol']
        ).first()
        
        if not asset:
            raise ValueError("Activo no encontrado")
        
        # Obtener la posición actual
        position = self.db.query(SimulationPosition).filter(
            SimulationPosition.account_id == account_id,
            SimulationPosition.asset_id == asset.id
        ).first()
        
        current_price = prediction['current_price']
        recommendation = prediction['recommendation']
        
        # Calcular el tamaño de la posición usando el gestor de riesgos
        position_size = self.risk_manager.calculate_position_size(
            symbol=prediction['symbol'],
            current_price=current_price,
            account_balance=account.current_balance
        )
        
        if recommendation == 'comprar':
            # Verificar si ya tenemos una posición (no comprar más si ya tenemos)
            if position and position.quantity > 0:
                return {"message": "Ya existe una posición para este activo"}
            
            # Ejecutar compra
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
            # Verificar si tenemos posición para vender
            if not position or position.quantity == 0:
                return {"message": "No hay posición para vender"}
            
            # Calcular cantidad a vender (vender toda la posición)
            quantity_to_sell = position.quantity
            
            # Ejecutar venta
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
        
        else:  # mantener
            return {"message": "Mantener posición actual"}
    
    def get_account_performance(self, account_id: int):
        """Calcular el rendimiento de una cuenta de simulación"""
        from main import SimulationAccount, SimulationOperation, SimulationPosition
        
        account = self.db.query(SimulationAccount).filter(
            SimulationAccount.id == account_id
        ).first()
        
        if not account:
            return None
        
        # Calcular el valor actual del portafolio
        positions = self.get_account_positions(account_id)
        portfolio_value = account.current_balance
        
        for position in positions:
            # Obtener el precio actual del activo (en una implementación real, esto se obtendría de la API)
            # Por ahora, usamos el último precio de la operación
            last_operation = self.db.query(SimulationOperation).filter(
                SimulationOperation.account_id == account_id,
                SimulationOperation.asset_id == position.asset_id
            ).order_by(SimulationOperation.timestamp.desc()).first()
            
            if last_operation:
                current_price = last_operation.price
                position_value = position.quantity * current_price
                portfolio_value += position_value
        
        # Calcular rendimiento
        total_return = (portfolio_value - account.initial_balance) / account.initial_balance * 100
        
        return {
            "account_id": account_id,
            "initial_balance": float(account.initial_balance),
            "current_balance": float(account.current_balance),
            "portfolio_value": float(portfolio_value),
            "total_return": float(total_return)
        }
    
    def simulate_trading_period(self, account_id: int, symbol: str, asset_type: str, model_type: str, days: int = 30):
        """
        Simular un período de trading automático basado en predicciones diarias
        """
        # Importar aquí para evitar problemas
        from main import SimulationAccount, Asset
        from prediction_model import TradingPredictor
        
        # Obtener la cuenta
        account = self.db.query(SimulationAccount).filter(
            SimulationAccount.id == account_id
        ).first()
        
        if not account:
            raise ValueError("Cuenta no encontrada")
        
        # Obtener el activo
        asset = self.db.query(Asset).filter(
            Asset.symbol == symbol
        ).first()
        
        if not asset:
            raise ValueError("Activo no encontrado")
        
        # Crear predictor
        predictor = TradingPredictor(model_type=model_type)
        
        # Cargar o entrenar el modelo
        if not predictor.load_model(symbol, asset_type):
            predictor.train(symbol, asset_type)
        
        # Obtener datos históricos para el período de simulación
        if asset_type == 'stock':
            data_fetcher = TradingPredictor()
            data = data_fetcher.fetch_stock_data(symbol, period=f'{days}d')
        else:  # crypto
            data = predictor.fetch_crypto_data(symbol, days=days)
        
        # Ejecutar simulación para cada día
        simulation_results = []
        
        for i in range(len(data)):
            date = data.index[i]
            current_price = data['close'].iloc[i]
            
            # Obtener predicción para el día actual
            # En una implementación real, esto se haría con datos hasta el día anterior
            prediction = predictor.predict(symbol, asset_type)
            
            # Ejecutar operación basada en la predicción
            result = self.execute_trade_based_on_prediction(account_id, prediction)
            
            # Registrar resultado
            simulation_results.append({
                "date": date,
                "price": current_price,
                "prediction": prediction,
                "operation_result": result
            })
        
        # Calcular rendimiento final
        performance = self.get_account_performance(account_id)
        
        return {
            "account_id": account_id,
            "symbol": symbol,
            "asset_type": asset_type,
            "model_type": model_type,
            "simulation_period_days": days,
            "simulation_results": simulation_results,
            "final_performance": performance
        }