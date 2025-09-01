# backtesting.py
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import yfinance as yf
import ccxt
from prediction_model import TradingPredictor
import os

class Backtester:
    def __init__(self, initial_balance=10000):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.positions = {}  # {symbol: {'quantity': qty, 'purchase_price': price}}
        self.trade_history = []
        self.portfolio_value = []
        self.dates = []
        
    def fetch_stock_data(self, symbol, start_date, end_date):
        """Obtener datos históricos de acciones"""
        data = yf.download(symbol, start=start_date, end=end_date)
        return data
    
    def fetch_crypto_data(self, symbol, start_date, end_date):
        """Obtener datos históricos de criptomonedas"""
        exchange = ccxt.binance()
        since = exchange.parse8601(start_date)
        ohlcv = exchange.fetch_ohlcv(symbol, '1d', since=since)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df[df['timestamp'] <= pd.to_datetime(end_date)]
        return df
    
    def run_backtest(self, symbol, asset_type, model_type, start_date, end_date, 
                    train_period_days=365, retrain_interval=30):
        """
        Ejecutar backtesting de una estrategia de trading basada en predicciones
        
        Parámetros:
        - symbol: Símbolo del activo
        - asset_type: 'stock' o 'crypto'
        - model_type: 'lstm', 'random_forest', o 'xgboost'
        - start_date: Fecha de inicio del backtesting (formato: 'YYYY-MM-DD')
        - end_date: Fecha de fin del backtesting (formato: 'YYYY-MM-DD')
        - train_period_days: Días de datos para entrenar el modelo
        - retrain_interval: Intervalo en días para reentrenar el modelo
        """
        # Obtener datos históricos
        if asset_type == 'stock':
            data = self.fetch_stock_data(symbol, start_date, end_date)
        else:  # crypto
            data = self.fetch_crypto_data(symbol, start_date, end_date)
        
        # Convertir fechas a datetime
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        
        # Inicializar variables
        current_date = start_date
        last_retrain_date = start_date - timedelta(days=retrain_interval)
        
        # Iterar sobre cada día en el período de backtesting
        for i in range(len(data)):
            current_date = data.index[i]
            current_price = data['close'].iloc[i]
            
            # Registrar el valor del portafolio
            portfolio_value = self.balance
            for asset, position in self.positions.items():
                portfolio_value += position['quantity'] * current_price
            
            self.portfolio_value.append(portfolio_value)
            self.dates.append(current_date)
            
            # Reentrenar el modelo si es necesario
            if (current_date - last_retrain_date).days >= retrain_interval:
                train_start = current_date - timedelta(days=train_period_days)
                train_end = current_date - timedelta(days=1)
                
                # Obtener datos de entrenamiento
                if asset_type == 'stock':
                    train_data = self.fetch_stock_data(symbol, train_start.strftime('%Y-%m-%d'), train_end.strftime('%Y-%m-%d'))
                else:  # crypto
                    train_data = self.fetch_crypto_data(symbol, train_start.strftime('%Y-%m-%d'), train_end.strftime('%Y-%m-%d'))
                
                # Entrenar el modelo
                predictor = TradingPredictor(model_type=model_type)
                predictor.train(symbol, asset_type, look_back=60)
                
                last_retrain_date = current_date
            
            # Obtener predicción para el día actual
            predictor = TradingPredictor(model_type=model_type)
            if predictor.load_model(symbol, asset_type):
                prediction = predictor.predict(symbol, asset_type)
                recommendation = prediction['recommendation']
                
                # Ejecutar operación según la recomendación
                if recommendation == 'comprar' and symbol not in self.positions:
                    # Comprar con el 10% del balance
                    invest_amount = self.balance * 0.1
                    quantity = invest_amount / current_price
                    
                    self.positions[symbol] = {
                        'quantity': quantity,
                        'purchase_price': current_price
                    }
                    
                    self.balance -= invest_amount
                    
                    self.trade_history.append({
                        'date': current_date,
                        'type': 'buy',
                        'symbol': symbol,
                        'quantity': quantity,
                        'price': current_price,
                        'amount': invest_amount
                    })
                
                elif recommendation == 'vender' and symbol in self.positions:
                    # Vender toda la posición
                    position = self.positions[symbol]
                    quantity = position['quantity']
                    sale_amount = quantity * current_price
                    
                    del self.positions[symbol]
                    self.balance += sale_amount
                    
                    self.trade_history.append({
                        'date': current_date,
                        'type': 'sell',
                        'symbol': symbol,
                        'quantity': quantity,
                        'price': current_price,
                        'amount': sale_amount
                    })
        
        # Cerrar todas las posiciones al final del backtesting
        for symbol, position in self.positions.items():
            quantity = position['quantity']
            sale_amount = quantity * data['close'].iloc[-1]
            
            self.balance += sale_amount
            
            self.trade_history.append({
                'date': end_date,
                'type': 'sell',
                'symbol': symbol,
                'quantity': quantity,
                'price': data['close'].iloc[-1],
                'amount': sale_amount
            })
        
        # Calcular métricas de rendimiento
        self.calculate_performance_metrics()
        
        # Generar gráficos
        self.plot_results(symbol, asset_type, model_type)
        
        return {
            'initial_balance': self.initial_balance,
            'final_balance': self.balance,
            'total_return': (self.balance - self.initial_balance) / self.initial_balance * 100,
            'trade_history': self.trade_history,
            'portfolio_values': self.portfolio_value,
            'dates': self.dates
        }
    
    def calculate_performance_metrics(self):
        """Calcular métricas de rendimiento del backtesting"""
        # Convertir a DataFrame para facilitar los cálculos
        df = pd.DataFrame({
            'date': self.dates,
            'portfolio_value': self.portfolio_value
        })
        
        # Calcular retornos diarios
        df['daily_return'] = df['portfolio_value'].pct_change()
        
        # Métricas de rendimiento
        self.total_return = (df['portfolio_value'].iloc[-1] - df['portfolio_value'].iloc[0]) / df['portfolio_value'].iloc[0] * 100
        self.annualized_return = (1 + df['daily_return'].mean()) ** 252 - 1
        self.annualized_volatility = df['daily_return'].std() * np.sqrt(252)
        self.sharpe_ratio = self.annualized_return / self.annualized_volatility if self.annualized_volatility != 0 else 0
        
        # Calcular drawdown máximo
        df['cumulative_return'] = (1 + df['daily_return']).cumprod()
        df['cumulative_max'] = df['cumulative_return'].cummax()
        df['drawdown'] = (df['cumulative_return'] / df['cumulative_max'] - 1) * 100
        self.max_drawdown = df['drawdown'].min()
        
        # Número de operaciones
        self.num_trades = len(self.trade_history)
        
        # Tasa de acierto (win rate)
        wins = 0
        for i in range(0, len(self.trade_history), 2):
            if i + 1 < len(self.trade_history):
                buy_trade = self.trade_history[i]
                sell_trade = self.trade_history[i + 1]
                if buy_trade['type'] == 'buy' and sell_trade['type'] == 'sell':
                    if sell_trade['price'] > buy_trade['price']:
                        wins += 1
        
        self.win_rate = wins / (len(self.trade_history) // 2) * 100 if self.trade_history else 0
    
    def plot_results(self, symbol, asset_type, model_type):
        """Generar gráficos de resultados del backtesting"""
        # Crear figura con subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Gráfico del valor del portafolio
        ax1.plot(self.dates, self.portfolio_value, label='Valor del Portafolio')
        ax1.axhline(y=self.initial_balance, color='r', linestyle='--', label='Balance Inicial')
        ax1.set_title(f'Backtesting: {symbol} ({asset_type}) con {model_type}')
        ax1.set_ylabel('Valor ($)')
        ax1.legend()
        ax1.grid(True)
        
        # Gráfico de drawdown
        df = pd.DataFrame({
            'date': self.dates,
            'portfolio_value': self.portfolio_value
        })
        df['daily_return'] = df['portfolio_value'].pct_change()
        df['cumulative_return'] = (1 + df['daily_return']).cumprod()
        df['cumulative_max'] = df['cumulative_return'].cummax()
        df['drawdown'] = (df['cumulative_return'] / df['cumulative_max'] - 1) * 100
        
        ax2.fill_between(df['date'], df['drawdown'], 0, color='red', alpha=0.3)
        ax2.set_title('Drawdown')
        ax2.set_ylabel('Drawdown (%)')
        ax2.set_xlabel('Fecha')
        ax2.grid(True)
        
        plt.tight_layout()
        
        # Guardar gráfico
        os.makedirs('backtest_results', exist_ok=True)
        filename = f"backtest_results/{symbol}_{asset_type}_{model_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(filename)
        plt.close()
        
        return filename