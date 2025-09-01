# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Numeric, ForeignKey, Boolean, JSON, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import jwt
import uvicorn
import os
from prediction_model import TradingPredictor
from backtesting import Backtester
from notifications import NotificationManager
from risk_management import RiskManager
from simulator import TradingSimulator

# Configuración de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/trading_db")
engine = create_engine(DATABASE_URL)
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
    
    # Relaciones
    notification_preferences = relationship("NotificationPreference", back_populates="user")

class Asset(Base):
    __tablename__ = "activos"
    
    id = Column(Integer, primary_key=True, index=True)
    simbolo = Column(String(20), unique=True, index=True)
    nombre = Column(String(100))
    tipo = Column(String(20))
    mercado = Column(String(50))
    

class MarketData(Base):
    __tablename__ = "datos_mercado"
    
    id = Column(Integer, primary_key=True, index=True)
    activo_id = Column(Integer, ForeignKey("activos.id"))
    fecha = Column(DateTime, nullable=False)
    apertura = Column(Numeric(20, 8))
    maximo = Column(Numeric(20, 8))
    minimo = Column(Numeric(20, 8))
    cierre = Column(Numeric(20, 8))
    volumen = Column(Numeric(20, 8))
    
    # Definir una restricción única para evitar duplicados
    __table_args__ = (UniqueConstraint('activo_id', 'fecha', name='_activo_fecha_uc'),)

class Prediction(Base):
    __tablename__ = "predicciones"
    
    id = Column(Integer, primary_key=True, index=True)
    activo_id = Column(Integer, ForeignKey("activos.id"))
    fecha_prediccion = Column(DateTime, nullable=False)
    fecha_objetivo = Column(DateTime, nullable=False)
    prediccion = Column(String(10), nullable=False)  # 'subira', 'bajara', 'mantendra'
    recomendacion = Column(String(10), nullable=False)  # 'comprar', 'vender', 'mantener'
    confianza = Column(Numeric(5, 4))
    modelo = Column(String(50))
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

class Operation(Base):
    __tablename__ = "operaciones"
    
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    activo_id = Column(Integer, ForeignKey("activos.id"))
    tipo_operacion = Column(String(10), nullable=False)  # 'compra', 'venta'
    cantidad = Column(Numeric(20, 8))
    precio_unitario = Column(Numeric(20, 8))
    fecha = Column(DateTime, default=datetime.utcnow)


class NotificationPreference(Base):
    __tablename__ = "preferencias_notificacion"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("usuarios.id"))
    email_notifications = Column(Boolean, default=False)
    telegram_notifications = Column(Boolean, default=False)
    webhook_notifications = Column(Boolean, default=False)
    email = Column(String(100))
    telegram_chat_id = Column(String(50))
    webhook_url = Column(String(255))
    
    # Relaciones
    user = relationship("User", back_populates="notification_preferences")

class BacktestResult(Base):
    __tablename__ = "resultados_backtest"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("usuarios.id"))
    asset_id = Column(Integer, ForeignKey("activos.id"))
    model_type = Column(String(50))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    initial_balance = Column(Numeric(15, 2))
    final_balance = Column(Numeric(15, 2))
    total_return = Column(Numeric(10, 4))
    annualized_return = Column(Numeric(10, 4))
    annualized_volatility = Column(Numeric(10, 4))
    sharpe_ratio = Column(Numeric(10, 4))
    max_drawdown = Column(Numeric(10, 4))
    num_trades = Column(Integer)
    win_rate = Column(Numeric(10, 4))
    chart_path = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)



class SimulationAccount(Base):
    __tablename__ = "simulation_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("usuarios.id"))
    account_name = Column(String(100), nullable=False)
    initial_balance = Column(Numeric(15, 2), nullable=False)
    current_balance = Column(Numeric(15, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class SimulationOperation(Base):
    __tablename__ = "simulation_operations"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("simulation_accounts.id"))
    asset_id = Column(Integer, ForeignKey("activos.id"))
    operation_type = Column(String(10), nullable=False)  # 'buy', 'sell'
    quantity = Column(Numeric(20, 8), nullable=False)
    price = Column(Numeric(20, 8), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

class SimulationPosition(Base):
    __tablename__ = "simulation_positions"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("simulation_accounts.id"))
    asset_id = Column(Integer, ForeignKey("activos.id"))
    quantity = Column(Numeric(20, 8), nullable=False)
    average_price = Column(Numeric(20, 8), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # Restricción única para evitar duplicados
    __table_args__ = (UniqueConstraint('account_id', 'asset_id', name='_account_asset_uc'),)





# Crear las tablas
Base.metadata.create_all(bind=engine)

# Configuración de la aplicación FastAPI
app = FastAPI(title="Trading AI System", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Inicializar gestores
notification_manager = NotificationManager(
    email_config={
        'smtp_server': os.getenv("SMTP_SERVER"),
        'smtp_port': int(os.getenv("SMTP_PORT", 587)),
        'from_email': os.getenv("FROM_EMAIL"),
        'password': os.getenv("EMAIL_PASSWORD")
    },
    telegram_config={
        'bot_token': os.getenv("TELEGRAM_BOT_TOKEN"),
        'chat_id': os.getenv("TELEGRAM_CHAT_ID")
    },
    webhook_url=os.getenv("WEBHOOK_URL")
)

risk_manager = RiskManager(
    max_portfolio_risk=0.02,
    max_position_size=0.1,
    stop_loss_pct=0.05
)

# Endpoints
@app.get("/")
def read_root():
    return {"message": "Trading AI System API"}

@app.get("/assets", response_model=List[dict])
def get_assets(db: Session = Depends(get_db)):
    assets = db.query(Asset).all()
    return [{"id": asset.id, "simbolo": asset.simbolo, "nombre": asset.nombre, "tipo": asset.tipo, "mercado": asset.mercado} for asset in assets]

@app.get("/predict")
def predict(symbol: str, asset_type: str, model_type: str = "lstm", db: Session = Depends(get_db)):
    """Obtener predicción para un activo"""
    # Verificar si el activo existe
    asset = db.query(Asset).filter(Asset.simbolo == symbol).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    # Crear predictor y cargar modelo si existe
    predictor = TradingPredictor(model_type=model_type)
    if not predictor.load_model(symbol, asset_type):
        # Entrenar modelo si no existe
        predictor.train(symbol, asset_type)
    
    # Realizar predicción
    prediction = predictor.predict(symbol, asset_type)
    
    # Enviar notificación si hay preferencias configuradas
    # (En una implementación real, esto se haría para usuarios específicos)
    # user_preferences = db.query(NotificationPreference).filter(NotificationPreference.user_id == user_id).first()
    # if user_preferences:
    #     notification_manager.send_prediction_notification(prediction, user_preferences.__dict__)
    
    return prediction

@app.post("/backtest")
def run_backtest(
    symbol: str,
    asset_type: str,
    model_type: str,
    start_date: str,
    end_date: str,
    initial_balance: float = 10000,
    train_period_days: int = 365,
    retrain_interval: int = 30,
    user_id: int = 1,  # En una implementación real, esto vendría de la autenticación
    db: Session = Depends(get_db)
):
    """Ejecutar backtesting para una estrategia"""
    # Verificar si el activo existe
    asset = db.query(Asset).filter(Asset.simbolo == symbol).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    # Crear y ejecutar backtester
    backtester = Backtester(initial_balance=initial_balance)
    results = backtester.run_backtest(
        symbol=symbol,
        asset_type=asset_type,
        model_type=model_type,
        start_date=start_date,
        end_date=end_date,
        train_period_days=train_period_days,
        retrain_interval=retrain_interval
    )
    
    # Guardar resultados en la base de datos
    backtest_result = BacktestResult(
        user_id=user_id,
        asset_id=asset.id,
        model_type=model_type,
        start_date=datetime.strptime(start_date, "%Y-%m-%d"),
        end_date=datetime.strptime(end_date, "%Y-%m-%d"),
        initial_balance=initial_balance,
        final_balance=results['final_balance'],
        total_return=results['total_return'],
        annualized_return=backtester.annualized_return,
        annualized_volatility=backtester.annualized_volatility,
        sharpe_ratio=backtester.sharpe_ratio,
        max_drawdown=backtester.max_drawdown,
        num_trades=backtester.num_trades,
        win_rate=backtester.win_rate,
        chart_path=f"backtest_results/{symbol}_{asset_type}_{model_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    )
    
    db.add(backtest_result)
    db.commit()
    
    return {
        "message": "Backtest completed successfully",
        "results": {
            "initial_balance": results['initial_balance'],
            "final_balance": results['final_balance'],
            "total_return": results['total_return'],
            "annualized_return": backtester.annualized_return,
            "annualized_volatility": backtester.annualized_volatility,
            "sharpe_ratio": backtester.sharpe_ratio,
            "max_drawdown": backtester.max_drawdown,
            "num_trades": backtester.num_trades,
            "win_rate": backtester.win_rate,
            "chart_path": backtest_result.chart_path
        }
    }

@app.get("/backtest/results")
def get_backtest_results(user_id: int = 1, db: Session = Depends(get_db)):
    """Obtener resultados de backtesting para un usuario"""
    results = db.query(BacktestResult).filter(BacktestResult.user_id == user_id).all()
    
    return [{
        "id": result.id,
        "symbol": result.asset.simbolo,
        "asset_type": result.asset.tipo,
        "model_type": result.model_type,
        "start_date": result.start_date.strftime("%Y-%m-%d"),
        "end_date": result.end_date.strftime("%Y-%m-%d"),
        "initial_balance": float(result.initial_balance),
        "final_balance": float(result.final_balance),
        "total_return": float(result.total_return),
        "annualized_return": float(result.annualized_return),
        "sharpe_ratio": float(result.sharpe_ratio),
        "max_drawdown": float(result.max_drawdown),
        "win_rate": float(result.win_rate),
        "created_at": result.created_at.strftime("%Y-%m-%d %H:%M:%S")
    } for result in results]

@app.post("/notification/preferences")
def set_notification_preferences(
    user_id: int,
    email_notifications: bool = False,
    telegram_notifications: bool = False,
    webhook_notifications: bool = False,
    email: Optional[str] = None,
    telegram_chat_id: Optional[str] = None,
    webhook_url: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Establecer preferencias de notificación para un usuario"""
    # Verificar si ya existen preferencias para el usuario
    preferences = db.query(NotificationPreference).filter(NotificationPreference.user_id == user_id).first()
    
    if preferences:
        # Actualizar preferencias existentes
        preferences.email_notifications = email_notifications
        preferences.telegram_notifications = telegram_notifications
        preferences.webhook_notifications = webhook_notifications
        preferences.email = email
        preferences.telegram_chat_id = telegram_chat_id
        preferences.webhook_url = webhook_url
    else:
        # Crear nuevas preferencias
        preferences = NotificationPreference(
            user_id=user_id,
            email_notifications=email_notifications,
            telegram_notifications=telegram_notifications,
            webhook_notifications=webhook_notifications,
            email=email,
            telegram_chat_id=telegram_chat_id,
            webhook_url=webhook_url
        )
        db.add(preferences)
    
    db.commit()
    
    return {"message": "Notification preferences updated successfully"}

@app.get("/notification/preferences")
def get_notification_preferences(user_id: int, db: Session = Depends(get_db)):
    """Obtener preferencias de notificación para un usuario"""
    preferences = db.query(NotificationPreference).filter(NotificationPreference.user_id == user_id).first()
    
    if not preferences:
        raise HTTPException(status_code=404, detail="Notification preferences not found")
    
    return {
        "email_notifications": preferences.email_notifications,
        "telegram_notifications": preferences.telegram_notifications,
        "webhook_notifications": preferences.webhook_notifications,
        "email": preferences.email,
        "telegram_chat_id": preferences.telegram_chat_id,
        "webhook_url": preferences.webhook_url
    }

@app.post("/risk/position_size")
def calculate_position_size(
    symbol: str,
    current_price: float,
    account_balance: float,
    volatility: Optional[float] = None
):
    """Calcular el tamaño de la posición basado en el riesgo"""
    position_size = risk_manager.calculate_position_size(
        symbol=symbol,
        current_price=current_price,
        account_balance=account_balance,
        volatility=volatility
    )
    
    return {
        "symbol": symbol,
        "current_price": current_price,
        "position_size": position_size,
        "position_value": position_size * current_price,
        "risk_percentage": risk_manager.stop_loss_pct * 100
    }

@app.post("/risk/add_position")
def add_position(
    symbol: str,
    quantity: float,
    purchase_price: float
):
    """Añadir una posición al gestor de riesgos"""
    risk_manager.add_position(
        symbol=symbol,
        quantity=quantity,
        purchase_price=purchase_price
    )
    
    return {"message": f"Position for {symbol} added successfully"}

@app.post("/risk/update_position")
def update_position(
    symbol: str,
    current_price: float
):
    """Actualizar una posición (por ejemplo, para trailing stop)"""
    risk_manager.update_position(
        symbol=symbol,
        current_price=current_price
    )
    
    position_info = risk_manager.get_position_info(symbol)
    
    if position_info:
        return {
            "symbol": symbol,
            "quantity": position_info['quantity'],
            "purchase_price": position_info['purchase_price'],
            "current_price": current_price,
            "stop_loss": position_info['stop_loss'],
            "highest_price": position_info['highest_price']
        }
    else:
        return {"message": f"Position for {symbol} not found"}

@app.post("/risk/check_stop_loss")
def check_stop_loss(
    symbol: str,
    current_price: float
):
    """Verificar si se ha alcanzado el stop loss para una posición"""
    stop_loss_triggered = risk_manager.check_stop_loss(
        symbol=symbol,
        current_price=current_price
    )
    
    return {
        "symbol": symbol,
        "current_price": current_price,
        "stop_loss_triggered": stop_loss_triggered
    }

@app.post("/risk/remove_position")
def remove_position(
    symbol: str
):
    """Eliminar una posición del gestor de riesgos"""
    risk_manager.remove_position(symbol)
    
    return {"message": f"Position for {symbol} removed successfully"}

@app.post("/risk/portfolio_risk")
def calculate_portfolio_risk(current_prices: Dict[str, float]):
    """Calcular el riesgo actual del portafolio"""
    portfolio_risk = risk_manager.calculate_portfolio_risk(current_prices)
    
    return {
        "portfolio_risk": portfolio_risk,
        "max_portfolio_risk": risk_manager.max_portfolio_risk,
        "risk_percentage": portfolio_risk * 100
    }



# ... después de los endpoints existentes ...

@app.post("/simulation/accounts")
def create_simulation_account(
    account_name: str,
    initial_balance: float = 10000,
    user_id: int = 1,  # En una implementación real, esto vendría de la autenticación
    db: Session = Depends(get_db)
):
    """Crear una nueva cuenta de simulación"""
    simulator = TradingSimulator(db)
    account = simulator.create_simulation_account(
        user_id=user_id,
        account_name=account_name,
        initial_balance=initial_balance
    )
    return {
        "id": account.id,
        "user_id": account.user_id,
        "account_name": account.account_name,
        "initial_balance": float(account.initial_balance),
        "current_balance": float(account.current_balance),
        "created_at": account.created_at
    }

@app.get("/simulation/accounts")
def get_simulation_accounts(
    user_id: int = 1,  # En una implementación real, esto vendría de la autenticación
    db: Session = Depends(get_db)
):
    """Obtener todas las cuentas de simulación de un usuario"""
    simulator = TradingSimulator(db)
    accounts = simulator.get_user_simulation_accounts(user_id)
    return [{
        "id": account.id,
        "account_name": account.account_name,
        "initial_balance": float(account.initial_balance),
        "current_balance": float(account.current_balance),
        "created_at": account.created_at
    } for account in accounts]

@app.get("/simulation/accounts/{account_id}")
def get_simulation_account(
    account_id: int,
    user_id: int = 1,  # En una implementación real, esto vendría de la autenticación
    db: Session = Depends(get_db)
):
    """Obtener una cuenta de simulación específica"""
    simulator = TradingSimulator(db)
    account = simulator.get_simulation_account(account_id, user_id)
    if not account:
        raise HTTPException(status_code=404, detail="Simulation account not found")
    
    return {
        "id": account.id,
        "account_name": account.account_name,
        "initial_balance": float(account.initial_balance),
        "current_balance": float(account.current_balance),
        "created_at": account.created_at
    }

@app.get("/simulation/accounts/{account_id}/balance")
def get_account_balance(
    account_id: int,
    user_id: int = 1,  # En una implementación real, esto vendría de la autenticación
    db: Session = Depends(get_db)
):
    """Obtener el saldo actual de una cuenta de simulación"""
    simulator = TradingSimulator(db)
    # Verificar que la cuenta pertenece al usuario
    account = simulator.get_simulation_account(account_id, user_id)
    if not account:
        raise HTTPException(status_code=404, detail="Simulation account not found")
    
    balance = simulator.get_account_balance(account_id)
    return {"account_id": account_id, "balance": float(balance)}

@app.get("/simulation/accounts/{account_id}/positions")
def get_account_positions(
    account_id: int,
    user_id: int = 1,  # En una implementación real, esto vendría de la autenticación
    db: Session = Depends(get_db)
):
    """Obtener las posiciones actuales de una cuenta de simulación"""
    simulator = TradingSimulator(db)
    # Verificar que la cuenta pertenece al usuario
    account = simulator.get_simulation_account(account_id, user_id)
    if not account:
        raise HTTPException(status_code=404, detail="Simulation account not found")
    
    positions = simulator.get_account_positions(account_id)
    return [{
        "id": position.id,
        "asset_id": position.asset_id,
        "asset_symbol": position.asset.symbol,
        "quantity": float(position.quantity),
        "average_price": float(position.average_price),
        "updated_at": position.updated_at
    } for position in positions]

@app.get("/simulation/accounts/{account_id}/operations")
def get_account_operations(
    account_id: int,
    user_id: int = 1,  # En una implementación real, esto vendría de la autenticación
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener el historial de operaciones de una cuenta de simulación"""
    simulator = TradingSimulator(db)
    # Verificar que la cuenta pertenece al usuario
    account = simulator.get_simulation_account(account_id, user_id)
    if not account:
        raise HTTPException(status_code=404, detail="Simulation account not found")
    
    operations = simulator.get_account_operations(account_id, limit)
    return [{
        "id": operation.id,
        "asset_id": operation.asset_id,
        "asset_symbol": operation.asset.symbol,
        "operation_type": operation.operation_type,
        "quantity": float(operation.quantity),
        "price": float(operation.price),
        "timestamp": operation.timestamp
    } for operation in operations]

@app.post("/simulation/accounts/{account_id}/buy")
def execute_buy_order(
    account_id: int,
    asset_symbol: str,
    quantity: float,
    price: float,
    user_id: int = 1,  # En una implementación real, esto vendría de la autenticación
    db: Session = Depends(get_db)
):
    """Ejecutar una orden de compra en la cuenta de simulación"""
    simulator = TradingSimulator(db)
    # Verificar que la cuenta pertenece al usuario
    account = simulator.get_simulation_account(account_id, user_id)
    if not account:
        raise HTTPException(status_code=404, detail="Simulation account not found")
    
    # Obtener el activo
    asset = db.query(Asset).filter(Asset.symbol == asset_symbol).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    try:
        operation = simulator.execute_buy_order(
            account_id=account_id,
            asset_id=asset.id,
            quantity=quantity,
            price=price
        )
        return {
            "message": "Buy order executed successfully",
            "operation_id": operation.id,
            "account_id": account_id,
            "asset_symbol": asset_symbol,
            "quantity": float(operation.quantity),
            "price": float(operation.price)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/simulation/accounts/{account_id}/sell")
def execute_sell_order(
    account_id: int,
    asset_symbol: str,
    quantity: float,
    price: float,
    user_id: int = 1,  # En una implementación real, esto vendría de la autenticación
    db: Session = Depends(get_db)
):
    """Ejecutar una orden de venta en la cuenta de simulación"""
    simulator = TradingSimulator(db)
    # Verificar que la cuenta pertenece al usuario
    account = simulator.get_simulation_account(account_id, user_id)
    if not account:
        raise HTTPException(status_code=404, detail="Simulation account not found")
    
    # Obtener el activo
    asset = db.query(Asset).filter(Asset.symbol == asset_symbol).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    try:
        operation = simulator.execute_sell_order(
            account_id=account_id,
            asset_id=asset.id,
            quantity=quantity,
            price=price
        )
        return {
            "message": "Sell order executed successfully",
            "operation_id": operation.id,
            "account_id": account_id,
            "asset_symbol": asset_symbol,
            "quantity": float(operation.quantity),
            "price": float(operation.price)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/simulation/accounts/{account_id}/trade")
def execute_trade_based_on_prediction(
    account_id: int,
    symbol: str,
    asset_type: str,
    model_type: str = "lstm",
    user_id: int = 1,  # En una implementación real, esto vendría de la autenticación
    db: Session = Depends(get_db)
):
    """Ejecutar una operación basada en una predicción"""
    simulator = TradingSimulator(db)
    # Verificar que la cuenta pertenece al usuario
    account = simulator.get_simulation_account(account_id, user_id)
    if not account:
        raise HTTPException(status_code=404, detail="Simulation account not found")
    
    # Obtener predicción
    predictor = TradingPredictor(model_type=model_type)
    if not predictor.load_model(symbol, asset_type):
        # Entrenar modelo si no existe
        predictor.train(symbol, asset_type)
    
    prediction = predictor.predict(symbol, asset_type)
    
    # Ejecutar operación basada en la predicción
    result = simulator.execute_trade_based_on_prediction(account_id, prediction)
    
    return {
        "prediction": prediction,
        "trade_result": result
    }

@app.get("/simulation/accounts/{account_id}/performance")
def get_account_performance(
    account_id: int,
    user_id: int = 1,  # En una implementación real, esto vendría de la autenticación
    db: Session = Depends(get_db)
):
    """Obtener el rendimiento de una cuenta de simulación"""
    simulator = TradingSimulator(db)
    # Verificar que la cuenta pertenece al usuario
    account = simulator.get_simulation_account(account_id, user_id)
    if not account:
        raise HTTPException(status_code=404, detail="Simulation account not found")
    
    performance = simulator.get_account_performance(account_id)
    return performance

@app.post("/simulation/accounts/{account_id}/simulate")
def simulate_trading_period(
    account_id: int,
    symbol: str,
    asset_type: str,
    model_type: str = "lstm",
    days: int = 30,
    user_id: int = 1,  # En una implementación real, esto vendría de la autenticación
    db: Session = Depends(get_db)
):
    """Simular un período de trading automático"""
    simulator = TradingSimulator(db)
    # Verificar que la cuenta pertenece al usuario
    account = simulator.get_simulation_account(account_id, user_id)
    if not account:
        raise HTTPException(status_code=404, detail="Simulation account not found")
    
    # Ejecutar simulación
    results = simulator.simulate_trading_period(
        account_id=account_id,
        symbol=symbol,
        asset_type=asset_type,
        model_type=model_type,
        days=days
    )
    
    return results
    


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)