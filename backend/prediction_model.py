# prediction_model.py
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error
import xgboost as xgb
import yfinance as yf
import ccxt
import joblib
import os
from datetime import datetime, timedelta
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TradingPredictor:
    def __init__(self, model_type='lstm'):
        self.model_type = model_type
        self.model = None
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.look_back = 60  # Ventana de tiempo para las secuencias
        self.model_dir = "models"
        
        # Crear directorio para modelos si no existe
        os.makedirs(self.model_dir, exist_ok=True)
        
    def fetch_stock_data(self, symbol, period='1y', interval='1d'):
        """Obtener datos de acciones usando yfinance"""
        try:
            data = yf.download(symbol, period=period, interval=interval)
            if len(data) == 0:
                raise ValueError(f"No se encontraron datos para {symbol}")
            return data
        except Exception as e:
            logging.error(f"Error al obtener datos de {symbol}: {e}")
            raise
    
    def fetch_crypto_data(self, symbol, days=365):
        """Obtener datos de criptomonedas usando ccxt"""
        try:
            exchange = ccxt.binance()
            since = exchange.parse8601((datetime.now() - timedelta(days=days)).isoformat())
            ohlcv = exchange.fetch_ohlcv(symbol, '1d', since=since)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            if len(df) == 0:
                raise ValueError(f"No se encontraron datos para {symbol}")
            return df
        except Exception as e:
            logging.error(f"Error al obtener datos de {symbol}: {e}")
            raise
    
    def preprocess_data(self, data, look_back=None):
        """Preprocesar datos para el modelo"""
        if look_back is None:
            look_back = self.look_back
            
        # Usar solo el precio de cierre
        close_data = data['close'].values.reshape(-1, 1)
        
        # Normalizar datos
        scaled_data = self.scaler.fit_transform(close_data)
        
        # Crear secuencias para LSTM
        X, y = [], []
        for i in range(len(scaled_data) - look_back):
            X.append(scaled_data[i:i+look_back, 0])
            y.append(scaled_data[i+look_back, 0])
        
        return np.array(X), np.array(y)
    
    def preprocess_data_for_tree_models(self, data, look_back=None):
        """Preprocesar datos para modelos basados en árboles (Random Forest, XGBoost)"""
        if look_back is None:
            look_back = self.look_back
            
        # Crear características a partir de los precios de cierre pasados
        df = pd.DataFrame(data['close'].values, columns=['close'])
        
        # Añadir características de retardos (lags)
        for i in range(1, look_back + 1):
            df[f'lag_{i}'] = df['close'].shift(i)
        
        # Añadir características de media móvil
        df['ma_5'] = df['close'].rolling(window=5).mean().shift(1)
        df['ma_10'] = df['close'].rolling(window=10).mean().shift(1)
        df['ma_20'] = df['close'].rolling(window=20).mean().shift(1)
        
        # Añadir características de volatilidad
        df['volatility_5'] = df['close'].rolling(window=5).std().shift(1)
        df['volatility_10'] = df['close'].rolling(window=10).std().shift(1)
        
        # Añadir características de RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs)).shift(1)
        
        # Eliminar filas con NaN
        df = df.dropna()
        
        # Separar características y objetivo
        X = df.drop('close', axis=1).values
        y = df['close'].values
        
        return X, y
    
    def build_lstm_model(self, input_shape):
        """Construir modelo LSTM"""
        model = Sequential()
        model.add(LSTM(units=50, return_sequences=True, input_shape=input_shape))
        model.add(Dropout(0.2))
        model.add(LSTM(units=50, return_sequences=False))
        model.add(Dropout(0.2))
        model.add(Dense(units=25))
        model.add(Dense(units=1))
        
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model
    
    def build_random_forest_model(self):
        """Construir modelo Random Forest"""
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        return model
    
    def build_xgboost_model(self):
        """Construir modelo XGBoost"""
        model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            n_jobs=-1
        )
        return model
    
    def train(self, symbol, asset_type='stock', look_back=60, epochs=25, batch_size=32):
        """Entrenar el modelo"""
        try:
            logging.info(f"Entrenando modelo {self.model_type} para {symbol} ({asset_type})")
            self.look_back = look_back
            
            # Obtener datos según el tipo de activo
            if asset_type == 'stock':
                data = self.fetch_stock_data(symbol)
            else:  # crypto
                data = self.fetch_crypto_data(symbol)
            
            # Preprocesar datos según el tipo de modelo
            if self.model_type == 'lstm':
                X, y = self.preprocess_data(data, look_back)
                
                # Dividir en entrenamiento y prueba
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                
                # Reshape para LSTM [samples, time steps, features]
                X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
                X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))
                
                # Construir y entrenar el modelo
                self.model = self.build_lstm_model((look_back, 1))
                self.model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, validation_data=(X_test, y_test))
                
                # Evaluar el modelo
                loss = self.model.evaluate(X_test, y_test)
                logging.info(f"Pérdida del modelo LSTM: {loss}")
                
            elif self.model_type in ['random_forest', 'xgboost']:
                X, y = self.preprocess_data_for_tree_models(data, look_back)
                
                # Dividir en entrenamiento y prueba
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                
                # Construir y entrenar el modelo
                if self.model_type == 'random_forest':
                    self.model = self.build_random_forest_model()
                else:  # xgboost
                    self.model = self.build_xgboost_model()
                
                self.model.fit(X_train, y_train)
                
                # Evaluar el modelo
                y_pred = self.model.predict(X_test)
                loss = mean_squared_error(y_test, y_pred)
                logging.info(f"Pérdida del modelo {self.model_type}: {loss}")
            
            # Guardar el modelo y el scaler
            model_filename = os.path.join(self.model_dir, f"{symbol}_{asset_type}_{self.model_type}.pkl")
            scaler_filename = os.path.join(self.model_dir, f"{symbol}_{asset_type}_{self.model_type}_scaler.pkl")
            
            joblib.dump(self.model, model_filename)
            joblib.dump(self.scaler, scaler_filename)
            
            # Guardar timestamp del entrenamiento
            timestamp_filename = os.path.join(self.model_dir, f"{symbol}_{asset_type}_{self.model_type}_timestamp.txt")
            with open(timestamp_filename, 'w') as f:
                f.write(str(datetime.now().timestamp()))
            
            logging.info(f"Modelo guardado en {model_filename}")
            return loss
            
        except Exception as e:
            logging.error(f"Error durante el entrenamiento: {e}")
            raise
    
    def load_model(self, symbol, asset_type):
        """Cargar modelo entrenado"""
        model_filename = os.path.join(self.model_dir, f"{symbol}_{asset_type}_{self.model_type}.pkl")
        scaler_filename = os.path.join(self.model_dir, f"{symbol}_{asset_type}_{self.model_type}_scaler.pkl")
        
        if os.path.exists(model_filename) and os.path.exists(scaler_filename):
            self.model = joblib.load(model_filename)
            self.scaler = joblib.load(scaler_filename)
            return True
        return False
    
    def model_exists(self, symbol, asset_type):
        """Verificar si el modelo ya existe"""
        model_filename = os.path.join(self.model_dir, f"{symbol}_{asset_type}_{self.model_type}.pkl")
        return os.path.exists(model_filename)
    
    def get_model_age(self, symbol, asset_type):
        """Obtener la antigüedad del modelo en días"""
        timestamp_filename = os.path.join(self.model_dir, f"{symbol}_{asset_type}_{self.model_type}_timestamp.txt")
        if os.path.exists(timestamp_filename):
            with open(timestamp_filename, 'r') as f:
                timestamp = float(f.read())
            now = datetime.now().timestamp()
            age_days = (now - timestamp) / (24 * 3600)
            return age_days
        return None
    
    def should_retrain(self, symbol, asset_type, max_age_days=7):
        """Determinar si el modelo debe ser reentrenado"""
        if not self.model_exists(symbol, asset_type):
            return True
        
        age = self.get_model_age(symbol, asset_type)
        if age is None or age > max_age_days:
            return True
        
        return False
    
    def predict(self, symbol, asset_type='stock', days_ahead=1, force_retrain=False):
        """Realizar predicción, entrenando el modelo si es necesario"""
        try:
            # Verificar si el modelo existe y si debe ser reentrenado
            if force_retrain or self.should_retrain(symbol, asset_type):
                logging.info(f"Modelo necesita entrenamiento. Entrenando modelo {self.model_type} para {symbol} ({asset_type})...")
                self.train(symbol, asset_type)
            else:
                # Cargar el modelo existente
                if not self.load_model(symbol, asset_type):
                    logging.info(f"No se pudo cargar el modelo, entrenando uno nuevo...")
                    self.train(symbol, asset_type)
            
            # Obtener datos recientes
            if asset_type == 'stock':
                data = self.fetch_stock_data(symbol, period='60d')
            else:  # crypto
                data = self.fetch_crypto_data(symbol, days=60)
            
            # Realizar predicción según el tipo de modelo
            if self.model_type == 'lstm':
                # Preprocesar datos
                recent_data = data['close'].values[-self.look_back:].reshape(-1, 1)
                scaled_data = self.scaler.transform(recent_data)
                
                # Reshape para predicción
                X_pred = np.reshape(scaled_data, (1, self.look_back, 1))
                
                # Realizar predicción
                predicted_price = self.model.predict(X_pred)
                predicted_price = self.scaler.inverse_transform(predicted_price)
                
            elif self.model_type in ['random_forest', 'xgboost']:
                # Preprocesar datos para modelos de árbol
                X, _ = self.preprocess_data_for_tree_models(data, self.look_back)
                
                # Tomar la última fila para la predicción
                X_pred = X[-1:].reshape(1, -1)
                
                # Realizar predicción
                predicted_price = self.model.predict(X_pred)
            
            # Obtener último precio real
            last_price = data['close'].values[-1]
            
            # Determinar tendencia y recomendación
            change_percent = ((predicted_price[0] - last_price) / last_price) * 100
            
            if change_percent > 2:
                trend = "subira"
                recommendation = "comprar"
            elif change_percent < -2:
                trend = "bajara"
                recommendation = "vender"
            else:
                trend = "mantendra"
                recommendation = "mantener"
            
            # Calcular confianza (simplificado)
            confidence = min(abs(change_percent) / 5, 0.99)
            
            result = {
                "symbol": symbol,
                "current_price": float(last_price),
                "predicted_price": float(predicted_price[0]),
                "change_percent": float(change_percent),
                "trend": trend,
                "recommendation": recommendation,
                "confidence": float(confidence),
                "prediction_date": datetime.now().isoformat(),
                "target_date": (datetime.now() + timedelta(days=days_ahead)).isoformat(),
                "model": self.model_type
            }
            
            logging.info(f"Predicción generada: {result}")
            return result
            
        except Exception as e:
            logging.error(f"Error durante la predicción: {e}")
            raise


# Función para entrenar modelos para múltiples activos
def train_models_for_assets(assets, model_types=['lstm', 'random_forest', 'xgboost']):
    """Entrenar modelos para una lista de activos"""
    for asset in assets:
        symbol = asset['symbol']
        asset_type = asset['type']
        
        for model_type in model_types:
            try:
                predictor = TradingPredictor(model_type=model_type)
                predictor.train(symbol, asset_type)
                logging.info(f"Modelo {model_type} entrenado para {symbol}")
            except Exception as e:
                logging.error(f"Error al entrenar modelo {model_type} para {symbol}: {e}")


# Ejemplo de uso
if __name__ == "__main__":
    # Lista de activos para entrenar
    assets_to_train = [
        {'symbol': 'AAPL', 'type': 'stock'},
        {'symbol': 'MSFT', 'type': 'stock'},
        {'symbol': 'GOOGL', 'type': 'stock'},
        {'symbol': 'BTC/USDT', 'type': 'crypto'},
        {'symbol': 'ETH/USDT', 'type': 'crypto'}
    ]
    
    # Entrenar modelos para todos los activos
    train_models_for_assets(assets_to_train)
    
    # Probar predicciones
    predictor = TradingPredictor(model_type='lstm')
    prediction = predictor.predict('AAPL', 'stock')
    print("\nPredicción LSTM para AAPL:")
    print(prediction)
    
    predictor = TradingPredictor(model_type='random_forest')
    prediction = predictor.predict('AAPL', 'stock')
    print("\nPredicción Random Forest para AAPL:")
    print(prediction)
    
    predictor = TradingPredictor(model_type='xgboost')
    prediction = predictor.predict('AAPL', 'stock')
    print("\nPredicción XGBoost para AAPL:")
    print(prediction)
    
    # Probar con criptomonedas
    predictor = TradingPredictor(model_type='lstm')
    prediction = predictor.predict('BTC/USDT', 'crypto')
    print("\nPredicción LSTM para BTC/USDT:")
    print(prediction)