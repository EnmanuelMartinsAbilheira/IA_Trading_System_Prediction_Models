# risk_management.py
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

class RiskManager:
    def __init__(self, max_portfolio_risk=0.02, max_position_size=0.1, stop_loss_pct=0.05):
        """
        Inicializar el gestor de riesgos
        
        Parámetros:
        - max_portfolio_risk: Máximo riesgo del portafolio (porcentaje del capital total)
        - max_position_size: Tamaño máximo de una posición (porcentaje del capital total)
        - stop_loss_pct: Porcentaje de stop loss para cada posición
        """
        self.max_portfolio_risk = max_portfolio_risk
        self.max_position_size = max_position_size
        self.stop_loss_pct = stop_loss_pct
        self.positions = {}  # {symbol: {'quantity': qty, 'purchase_price': price, 'stop_loss': price}}
    
    def calculate_position_size(self, symbol, current_price, account_balance, volatility=None):
        """
        Calcular el tamaño de la posición basado en el riesgo
        
        Parámetros:
        - symbol: Símbolo del activo
        - current_price: Precio actual del activo
        - account_balance: Saldo de la cuenta
        - volatility: Volatilidad del activo (opcional)
        
        Retorna:
        - Cantidad de activos a comprar
        """
        # Calcular el riesgo máximo por operación
        max_risk_per_trade = account_balance * self.max_portfolio_risk
        
        # Calcular el tamaño máximo de la posición
        max_position_value = account_balance * self.max_position_size
        
        # Si se proporciona la volatilidad, ajustar el tamaño de la posición
        if volatility:
            # Ajustar el tamaño de la posición inversamente a la volatilidad
            # Mayor volatilidad = menor tamaño de posición
            volatility_factor = min(1.0, 0.1 / volatility)
            adjusted_max_position_value = max_position_value * volatility_factor
        else:
            adjusted_max_position_value = max_position_value
        
        # Calcular el número de acciones/criptomonedas a comprar
        position_size = min(
            adjusted_max_position_value / current_price,
            max_risk_per_trade / (current_price * self.stop_loss_pct)
        )
        
        return position_size
    
    def check_stop_loss(self, symbol, current_price):
        """
        Verificar si se ha alcanzado el stop loss para una posición
        
        Parámetros:
        - symbol: Símbolo del activo
        - current_price: Precio actual del activo
        
        Retorna:
        - True si se ha alcanzado el stop loss, False en caso contrario
        """
        if symbol in self.positions:
            position = self.positions[symbol]
            stop_loss_price = position['stop_loss']
            
            if current_price <= stop_loss_price:
                return True
        
        return False
    
    def add_position(self, symbol, quantity, purchase_price):
        """
        Añadir una posición al gestor de riesgos
        
        Parámetros:
        - symbol: Símbolo del activo
        - quantity: Cantidad de activos
        - purchase_price: Precio de compra
        """
        # Calcular el precio de stop loss
        stop_loss_price = purchase_price * (1 - self.stop_loss_pct)
        
        self.positions[symbol] = {
            'quantity': quantity,
            'purchase_price': purchase_price,
            'stop_loss': stop_loss_price,
            'highest_price': purchase_price  # Para trailing stop
        }
    
    def update_position(self, symbol, current_price):
        """
        Actualizar una posición (por ejemplo, para trailing stop)
        
        Parámetros:
        - symbol: Símbolo del activo
        - current_price: Precio actual del activo
        """
        if symbol in self.positions:
            position = self.positions[symbol]
            
            # Actualizar el precio más alto si es necesario
            if current_price > position['highest_price']:
                position['highest_price'] = current_price
                
                # Actualizar el stop loss (trailing stop)
                position['stop_loss'] = position['highest_price'] * (1 - self.stop_loss_pct)
    
    def remove_position(self, symbol):
        """
        Eliminar una posición del gestor de riesgos
        
        Parámetros:
        - symbol: Símbolo del activo
        """
        if symbol in self.positions:
            del self.positions[symbol]
    
    def calculate_portfolio_risk(self, current_prices):
        """
        Calcular el riesgo actual del portafolio
        
        Parámetros:
        - current_prices: Diccionario con los precios actuales de los activos {symbol: price}
        
        Retorna:
        - Riesgo actual del portafolio (porcentaje)
        """
        total_risk = 0
        total_value = 0
        
        for symbol, position in self.positions.items():
            if symbol in current_prices:
                current_price = current_prices[symbol]
                position_value = position['quantity'] * current_price
                position_risk = position_value * self.stop_loss_pct
                
                total_risk += position_risk
                total_value += position_value
        
        if total_value > 0:
            portfolio_risk = total_risk / total_value
        else:
            portfolio_risk = 0
        
        return portfolio_risk
    
    def get_position_info(self, symbol):
        """
        Obtener información sobre una posición
        
        Parámetros:
        - symbol: Símbolo del activo
        
        Retorna:
        - Diccionario con información de la posición o None si no existe
        """
        return self.positions.get(symbol)