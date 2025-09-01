// App.js
import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [assets, setAssets] = useState([]);
  const [selectedAsset, setSelectedAsset] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('predict'); // 'predict', 'backtest', 'risk', 'notifications', 'simulation'
  const [backtestResults, setBacktestResults] = useState([]);
  const [backtestForm, setBacktestForm] = useState({
    symbol: '',
    assetType: 'stock',
    modelType: 'lstm',
    startDate: '',
    endDate: '',
    initialBalance: 10000,
    trainPeriodDays: 365,
    retrainInterval: 30
  });
  const [notificationPreferences, setNotificationPreferences] = useState({
    emailNotifications: false,
    telegramNotifications: false,
    webhookNotifications: false,
    email: '',
    telegramChatId: '',
    webhookUrl: ''
  });
  const [riskForm, setRiskForm] = useState({
    symbol: '',
    currentPrice: 0,
    accountBalance: 10000,
    volatility: 0
  });
  const [positionSize, setPositionSize] = useState(null);
  const [portfolioRisk, setPortfolioRisk] = useState(null);
  
  // Estados para la simulación
  const [simulationAccounts, setSimulationAccounts] = useState([]);
  const [selectedSimulationAccount, setSelectedSimulationAccount] = useState(null);
  const [simulationPositions, setSimulationPositions] = useState([]);
  const [simulationOperations, setSimulationOperations] = useState([]);
  const [simulationPerformance, setSimulationPerformance] = useState(null);
  const [newAccountForm, setNewAccountForm] = useState({
    name: '',
    initialBalance: 10000
  });
  const [tradeForm, setTradeForm] = useState({
    symbol: '',
    assetType: 'stock',
    modelType: 'lstm'
  });
  const [simulationForm, setSimulationForm] = useState({
    symbol: '',
    assetType: 'stock',
    modelType: 'lstm',
    days: 30
  });

  useEffect(() => {
    // Cargar activos disponibles
    fetch('http://localhost:8000/assets')
      .then(response => response.json())
      .then(data => setAssets(data))
      .catch(error => console.error('Error fetching assets:', error));
    
    // Cargar resultados de backtesting
    fetch('http://localhost:8000/backtest/results')
      .then(response => response.json())
      .then(data => setBacktestResults(data))
      .catch(error => console.error('Error fetching backtest results:', error));
    
    // Cargar preferencias de notificación
    fetch('http://localhost:8000/notification/preferences?user_id=1')
      .then(response => response.json())
      .then(data => setNotificationPreferences(data))
      .catch(error => console.error('Error fetching notification preferences:', error));
    
    // Cargar cuentas de simulación
    fetch('http://localhost:8000/simulation/accounts')
      .then(response => response.json())
      .then(data => setSimulationAccounts(data))
      .catch(error => console.error('Error fetching simulation accounts:', error));
  }, []);

  const handleAssetSelect = (asset) => {
    setSelectedAsset(asset);
    setPrediction(null);
    
    // Actualizar formularios con el activo seleccionado
    setBacktestForm({
      ...backtestForm,
      symbol: asset.simbolo,
      assetType: asset.tipo === 'accion' ? 'stock' : 'crypto'
    });
    
    setRiskForm({
      ...riskForm,
      symbol: asset.simbolo
    });
  };

  const handlePredict = () => {
    if (!selectedAsset) return;
    
    setLoading(true);
    
    // Determinar el tipo de activo
    const assetType = selectedAsset.tipo === 'accion' ? 'stock' : 'crypto';
    
    // Obtener predicción
    fetch(`http://localhost:8000/predict?symbol=${selectedAsset.simbolo}&asset_type=${assetType}`)
      .then(response => response.json())
      .then(data => {
        setPrediction(data);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error fetching prediction:', error);
        setLoading(false);
      });
  };

  const handleBacktest = () => {
    setLoading(true);
    
    fetch('http://localhost:8000/backtest', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(backtestForm),
    })
      .then(response => response.json())
      .then(data => {
        console.log('Backtest results:', data);
        // Recargar resultados de backtesting
        fetch('http://localhost:8000/backtest/results')
          .then(response => response.json())
          .then(data => setBacktestResults(data))
          .catch(error => console.error('Error fetching backtest results:', error));
        setLoading(false);
      })
      .catch(error => {
        console.error('Error running backtest:', error);
        setLoading(false);
      });
  };

  const handleNotificationPreferences = () => {
    setLoading(true);
    
    fetch('http://localhost:8000/notification/preferences', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: 1,
        ...notificationPreferences
      }),
    })
      .then(response => response.json())
      .then(data => {
        console.log('Notification preferences updated:', data);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error updating notification preferences:', error);
        setLoading(false);
      });
  };

  const handleCalculatePositionSize = () => {
    setLoading(true);
    
    fetch('http://localhost:8000/risk/position_size', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(riskForm),
    })
      .then(response => response.json())
      .then(data => {
        setPositionSize(data);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error calculating position size:', error);
        setLoading(false);
      });
  };

  const handleCalculatePortfolioRisk = () => {
    setLoading(true);
    
    // En una implementación real, esto se basaría en las posiciones actuales del usuario
    const currentPrices = {
      'AAPL': 150.0,
      'MSFT': 280.0,
      'BTC/USDT': 35000.0
    };
    
    fetch('http://localhost:8000/risk/portfolio_risk', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(currentPrices),
    })
      .then(response => response.json())
      .then(data => {
        setPortfolioRisk(data);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error calculating portfolio risk:', error);
        setLoading(false);
      });
  };

  // Funciones para la simulación
  const handleCreateSimulationAccount = () => {
    setLoading(true);
    
    fetch('http://localhost:8000/simulation/accounts', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        account_name: newAccountForm.name,
        initial_balance: newAccountForm.initialBalance
      }),
    })
      .then(response => response.json())
      .then(data => {
        console.log('Simulation account created:', data);
        // Recargar cuentas
        fetch('http://localhost:8000/simulation/accounts')
          .then(response => response.json())
          .then(data => setSimulationAccounts(data))
          .catch(error => console.error('Error fetching simulation accounts:', error));
        setLoading(false);
      })
      .catch(error => {
        console.error('Error creating simulation account:', error);
        setLoading(false);
      });
  };

  const handleSelectSimulationAccount = (account) => {
    setSelectedSimulationAccount(account);
    
    // Cargar posiciones
    fetch(`http://localhost:8000/simulation/accounts/${account.id}/positions`)
      .then(response => response.json())
      .then(data => setSimulationPositions(data))
      .catch(error => console.error('Error fetching simulation positions:', error));
    
    // Cargar operaciones
    fetch(`http://localhost:8000/simulation/accounts/${account.id}/operations`)
      .then(response => response.json())
      .then(data => setSimulationOperations(data))
      .catch(error => console.error('Error fetching simulation operations:', error));
    
    // Cargar rendimiento
    fetch(`http://localhost:8000/simulation/accounts/${account.id}/performance`)
      .then(response => response.json())
      .then(data => setSimulationPerformance(data))
      .catch(error => console.error('Error fetching simulation performance:', error));
  };

  const handleExecuteTrade = () => {
    if (!selectedSimulationAccount) return;
    
    setLoading(true);
    
    fetch(`http://localhost:8000/simulation/accounts/${selectedSimulationAccount.id}/trade`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(tradeForm),
    })
      .then(response => response.json())
      .then(data => {
        console.log('Trade executed:', data);
        // Recargar datos de la cuenta
        handleSelectSimulationAccount(selectedSimulationAccount);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error executing trade:', error);
        setLoading(false);
      });
  };

  const handleSimulateTrading = () => {
    if (!selectedSimulationAccount) return;
    
    setLoading(true);
    
    fetch(`http://localhost:8000/simulation/accounts/${selectedSimulationAccount.id}/simulate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(simulationForm),
    })
      .then(response => response.json())
      .then(data => {
        console.log('Simulation completed:', data);
        // Recargar datos de la cuenta
        handleSelectSimulationAccount(selectedSimulationAccount);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error simulating trading:', error);
        setLoading(false);
      });
  };

  const getRecommendationColor = (recommendation) => {
    switch (recommendation) {
      case 'comprar': return 'green';
      case 'vender': return 'red';
      default: return 'orange';
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Sistema de Trading con IA</h1>
      </header>
      
      <div className="tabs">
        <button className={`tab ${activeTab === 'predict' ? 'active' : ''}`} onClick={() => setActiveTab('predict')}>Predicción</button>
        <button className={`tab ${activeTab === 'backtest' ? 'active' : ''}`} onClick={() => setActiveTab('backtest')}>Backtesting</button>
        <button className={`tab ${activeTab === 'risk' ? 'active' : ''}`} onClick={() => setActiveTab('risk')}>Gestión de Riesgos</button>
        <button className={`tab ${activeTab === 'notifications' ? 'active' : ''}`} onClick={() => setActiveTab('notifications')}>Notificaciones</button>
        <button className={`tab ${activeTab === 'simulation' ? 'active' : ''}`} onClick={() => setActiveTab('simulation')}>Simulación</button>
      </div>
      
      <div className="container">
        <div className="asset-selector">
          <h2>Seleccionar Activo</h2>
          <div className="asset-list">
            {assets.map(asset => (
              <div 
                key={asset.id} 
                className={`asset-item ${selectedAsset && selectedAsset.id === asset.id ? 'selected' : ''}`}
                onClick={() => handleAssetSelect(asset)}
              >
                <span className="symbol">{asset.simbolo}</span>
                <span className="name">{asset.nombre}</span>
                <span className="type">{asset.tipo}</span>
              </div>
            ))}
          </div>
        </div>
        
        <div className="main-content">
          {activeTab === 'predict' && (
            <div className="prediction-tab">
              {selectedAsset && (
                <button 
                  className="predict-button" 
                  onClick={handlePredict}
                  disabled={loading}
                >
                  {loading ? 'Analizando...' : 'Obtener Predicción'}
                </button>
              )}
              
              {prediction && (
                <div className="prediction-result">
                  <h2>Predicción para {prediction.symbol}</h2>
                  <div className="prediction-details">
                    <div className="price-info">
                      <div className="current-price">
                        <span className="label">Precio Actual:</span>
                        <span className="value">${prediction.current_price.toFixed(2)}</span>
                      </div>
                      <div className="predicted-price">
                        <span className="label">Precio Predicho:</span>
                        <span className="value">${prediction.predicted_price.toFixed(2)}</span>
                      </div>
                      <div className="change-percent">
                        <span className="label">Cambio Esperado:</span>
                        <span className={`value ${prediction.change_percent >= 0 ? 'positive' : 'negative'}`}>
                          {prediction.change_percent >= 0 ? '+' : ''}{prediction.change_percent.toFixed(2)}%
                        </span>
                      </div>
                    </div>
                    
                    <div className="recommendation" style={{ backgroundColor: getRecommendationColor(prediction.recommendation) }}>
                      <div className="trend">Se espera que el precio <strong>{prediction.trend}</strong></div>
                      <div className="action">Recomendación: <strong>{prediction.recommendation.toUpperCase()}</strong></div>
                      <div className="confidence">Confianza: <strong>{(prediction.confidence * 100).toFixed(1)}%</strong></div>
                      <div className="model">Modelo: <strong>{prediction.model}</strong></div>
                    </div>
                    
                    <div className="dates">
                      <div>Fecha de predicción: {new Date(prediction.prediction_date).toLocaleString()}</div>
                      <div>Fecha objetivo: {new Date(prediction.target_date).toLocaleDateString()}</div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
          
          {activeTab === 'backtest' && (
            <div className="backtest-tab">
              <h2>Backtesting</h2>
              
              <div className="backtest-form">
                <div className="form-group">
                  <label>Activo:</label>
                  <select 
                    value={backtestForm.symbol} 
                    onChange={(e) => setBacktestForm({...backtestForm, symbol: e.target.value})}
                  >
                    <option value="">Seleccionar activo</option>
                    {assets.map(asset => (
                      <option key={asset.id} value={asset.simbolo}>{asset.simbolo} - {asset.nombre}</option>
                    ))}
                  </select>
                </div>
                
                <div className="form-group">
                  <label>Tipo de Activo:</label>
                  <select 
                    value={backtestForm.assetType} 
                    onChange={(e) => setBacktestForm({...backtestForm, assetType: e.target.value})}
                  >
                    <option value="stock">Acción</option>
                    <option value="crypto">Criptomoneda</option>
                  </select>
                </div>
                
                <div className="form-group">
                  <label>Modelo:</label>
                  <select 
                    value={backtestForm.modelType} 
                    onChange={(e) => setBacktestForm({...backtestForm, modelType: e.target.value})}
                  >
                    <option value="lstm">LSTM</option>
                    <option value="random_forest">Random Forest</option>
                    <option value="xgboost">XGBoost</option>
                  </select>
                </div>
                
                <div className="form-group">
                  <label>Fecha Inicio:</label>
                  <input 
                    type="date" 
                    value={backtestForm.startDate} 
                    onChange={(e) => setBacktestForm({...backtestForm, startDate: e.target.value})}
                  />
                </div>
                
                <div className="form-group">
                  <label>Fecha Fin:</label>
                  <input 
                    type="date" 
                    value={backtestForm.endDate} 
                    onChange={(e) => setBacktestForm({...backtestForm, endDate: e.target.value})}
                  />
                </div>
                
                <div className="form-group">
                  <label>Balance Inicial:</label>
                  <input 
                    type="number" 
                    value={backtestForm.initialBalance} 
                    onChange={(e) => setBacktestForm({...backtestForm, initialBalance: parseFloat(e.target.value)})}
                  />
                </div>
                
                <div className="form-group">
                  <label>Días de Entrenamiento:</label>
                  <input 
                    type="number" 
                    value={backtestForm.trainPeriodDays} 
                    onChange={(e) => setBacktestForm({...backtestForm, trainPeriodDays: parseInt(e.target.value)})}
                  />
                </div>
                
                <div className="form-group">
                  <label>Intervalo de Reentrenamiento (días):</label>
                  <input 
                    type="number" 
                    value={backtestForm.retrainInterval} 
                    onChange={(e) => setBacktestForm({...backtestForm, retrainInterval: parseInt(e.target.value)})}
                  />
                </div>
                
                <button 
                  className="predict-button" 
                  onClick={handleBacktest}
                  disabled={loading}
                >
                  {loading ? 'Ejecutando Backtest...' : 'Ejecutar Backtest'}
                </button>
              </div>
              
              <h3>Resultados Anteriores</h3>
              <div className="backtest-results">
                {backtestResults.length > 0 ? (
                  <table>
                    <thead>
                      <tr>
                        <th>Activo</th>
                        <th>Modelo</th>
                        <th>Periodo</th>
                        <th>Retorno Total</th>
                        <th>Retorno Anualizado</th>
                        <th>Sharpe Ratio</th>
                        <th>Max Drawdown</th>
                        <th>Win Rate</th>
                      </tr>
                    </thead>
                    <tbody>
                      {backtestResults.map(result => (
                        <tr key={result.id}>
                          <td>{result.symbol}</td>
                          <td>{result.model_type}</td>
                          <td>{formatDate(result.start_date)} - {formatDate(result.end_date)}</td>
                          <td className={result.total_return >= 0 ? 'positive' : 'negative'}>
                            {result.total_return.toFixed(2)}%
                          </td>
                          <td className={result.annualized_return >= 0 ? 'positive' : 'negative'}>
                            {result.annualized_return.toFixed(2)}%
                          </td>
                          <td>{result.sharpe_ratio.toFixed(2)}</td>
                          <td className="negative">{result.max_drawdown.toFixed(2)}%</td>
                          <td>{result.win_rate.toFixed(2)}%</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                ) : (
                  <p>No hay resultados de backtesting disponibles.</p>
                )}
              </div>
            </div>
          )}
          
          {activeTab === 'risk' && (
            <div className="risk-tab">
              <h2>Gestión de Riesgos</h2>
              
              <div className="risk-form">
                <h3>Calcular Tamaño de Posición</h3>
                
                <div className="form-group">
                  <label>Activo:</label>
                  <select 
                    value={riskForm.symbol} 
                    onChange={(e) => setRiskForm({...riskForm, symbol: e.target.value})}
                  >
                    <option value="">Seleccionar activo</option>
                    {assets.map(asset => (
                      <option key={asset.id} value={asset.simbolo}>{asset.simbolo} - {asset.nombre}</option>
                    ))}
                  </select>
                </div>
                
                <div className="form-group">
                  <label>Precio Actual:</label>
                  <input 
                    type="number" 
                    step="0.01"
                    value={riskForm.currentPrice} 
                    onChange={(e) => setRiskForm({...riskForm, currentPrice: parseFloat(e.target.value)})}
                  />
                </div>
                
                <div className="form-group">
                  <label>Balance de la Cuenta:</label>
                  <input 
                    type="number" 
                    value={riskForm.accountBalance} 
                    onChange={(e) => setRiskForm({...riskForm, accountBalance: parseFloat(e.target.value)})}
                  />
                </div>
                
                <div className="form-group">
                  <label>Volatilidad (opcional):</label>
                  <input 
                    type="number" 
                    step="0.01"
                    value={riskForm.volatility} 
                    onChange={(e) => setRiskForm({...riskForm, volatility: parseFloat(e.target.value)})}
                  />
                </div>
                
                <button 
                  className="predict-button" 
                  onClick={handleCalculatePositionSize}
                  disabled={loading}
                >
                  {loading ? 'Calculando...' : 'Calcular Tamaño de Posición'}
                </button>
                
                {positionSize && (
                  <div className="position-size-result">
                    <h4>Resultado:</h4>
                    <p>Tamaño de la posición: <strong>{positionSize.position_size.toFixed(4)}</strong> unidades</p>
                    <p>Valor de la posición: <strong>${positionSize.position_value.toFixed(2)}</strong></p>
                    <p>Riesgo por operación: <strong>{positionSize.risk_percentage.toFixed(2)}%</strong></p>
                  </div>
                )}
              </div>
              
              <div className="portfolio-risk">
                <h3>Riesgo del Portafolio</h3>
                
                <button 
                  className="predict-button" 
                  onClick={handleCalculatePortfolioRisk}
                  disabled={loading}
                >
                  {loading ? 'Calculando...' : 'Calcular Riesgo del Portafolio'}
                </button>
                
                {portfolioRisk && (
                  <div className="portfolio-risk-result">
                    <h4>Resultado:</h4>
                    <p>Riesgo actual del portafolio: <strong>{portfolioRisk.risk_percentage.toFixed(2)}%</strong></p>
                    <p>Riesgo máximo permitido: <strong>{portfolioRisk.max_portfolio_risk * 100}%</strong></p>
                    <p>Estado: <strong className={portfolioRisk.portfolio_risk <= portfolioRisk.max_portfolio_risk ? 'positive' : 'negative'}>
                      {portfolioRisk.portfolio_risk <= portfolioRisk.max_portfolio_risk ? 'Dentro de los límites' : 'Excede los límites'}
                    </strong></p>
                  </div>
                )}
              </div>
            </div>
          )}
          
          {activeTab === 'notifications' && (
            <div className="notifications-tab">
              <h2>Preferencias de Notificación</h2>
              
              <div className="notification-form">
                <div className="form-group">
                  <label>
                    <input 
                      type="checkbox" 
                      checked={notificationPreferences.emailNotifications}
                      onChange={(e) => setNotificationPreferences({
                        ...notificationPreferences, 
                        emailNotifications: e.target.checked
                      })}
                    />
                    Notificaciones por Email
                  </label>
                </div>
                
                {notificationPreferences.emailNotifications && (
                  <div className="form-group">
                    <label>Email:</label>
                    <input 
                      type="email" 
                      value={notificationPreferences.email} 
                      onChange={(e) => setNotificationPreferences({
                        ...notificationPreferences, 
                        email: e.target.value
                      })}
                    />
                  </div>
                )}
                
                <div className="form-group">
                  <label>
                    <input 
                      type="checkbox" 
                      checked={notificationPreferences.telegramNotifications}
                      onChange={(e) => setNotificationPreferences({
                        ...notificationPreferences, 
                        telegramNotifications: e.target.checked
                      })}
                    />
                    Notificaciones por Telegram
                  </label>
                </div>
                
                {notificationPreferences.telegramNotifications && (
                  <div className="form-group">
                    <label>ID de Chat de Telegram:</label>
                    <input 
                      type="text" 
                      value={notificationPreferences.telegramChatId} 
                      onChange={(e) => setNotificationPreferences({
                        ...notificationPreferences, 
                        telegramChatId: e.target.value
                      })}
                    />
                  </div>
                )}
                
                <div className="form-group">
                  <label>
                    <input 
                      type="checkbox" 
                      checked={notificationPreferences.webhookNotifications}
                      onChange={(e) => setNotificationPreferences({
                        ...notificationPreferences, 
                        webhookNotifications: e.target.checked
                      })}
                    />
                    Notificaciones por Webhook
                  </label>
                </div>
                
                {notificationPreferences.webhookNotifications && (
                  <div className="form-group">
                    <label>URL del Webhook:</label>
                    <input 
                      type="text" 
                      value={notificationPreferences.webhookUrl} 
                      onChange={(e) => setNotificationPreferences({
                        ...notificationPreferences, 
                        webhookUrl: e.target.value
                      })}
                    />
                  </div>
                )}
                
                <button 
                  className="predict-button" 
                  onClick={handleNotificationPreferences}
                  disabled={loading}
                >
                  {loading ? 'Guardando...' : 'Guardar Preferencias'}
                </button>
              </div>
            </div>
          )}
          
          {activeTab === 'simulation' && (
            <div className="simulation-tab">
              <h2>Simulación de Trading</h2>
              
              <div className="simulation-accounts">
                <h3>Cuentas de Simulación</h3>
                
                <div className="new-account-form">
                  <h4>Crear Nueva Cuenta</h4>
                  <div className="form-group">
                    <label>Nombre:</label>
                    <input 
                      type="text" 
                      value={newAccountForm.name} 
                      onChange={(e) => setNewAccountForm({...newAccountForm, name: e.target.value})}
                    />
                  </div>
                  <div className="form-group">
                    <label>Balance Inicial:</label>
                    <input 
                      type="number" 
                      value={newAccountForm.initialBalance} 
                      onChange={(e) => setNewAccountForm({...newAccountForm, initialBalance: parseFloat(e.target.value)})}
                    />
                  </div>
                  <button 
                    className="predict-button" 
                    onClick={handleCreateSimulationAccount}
                    disabled={loading || !newAccountForm.name}
                  >
                    {loading ? 'Creando...' : 'Crear Cuenta'}
                  </button>
                </div>
                
                <div className="accounts-list">
                  {simulationAccounts.length > 0 ? (
                    <div className="account-cards">
                      {simulationAccounts.map(account => (
                        <div 
                          key={account.id} 
                          className={`account-card ${selectedSimulationAccount && selectedSimulationAccount.id === account.id ? 'selected' : ''}`}
                          onClick={() => handleSelectSimulationAccount(account)}
                        >
                          <div className="account-name">{account.account_name}</div>
                          <div className="account-balance">${account.current_balance.toFixed(2)}</div>
                          <div className="account-date">Creada: {new Date(account.created_at).toLocaleDateString()}</div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p>No hay cuentas de simulación. Crea una para empezar.</p>
                  )}
                </div>
              </div>
              
              {selectedSimulationAccount && (
                <div className="account-details">
                  <h3>Detalles de la Cuenta: {selectedSimulationAccount.account_name}</h3>
                  
                  {simulationPerformance && (
                    <div className="performance-summary">
                      <div className="performance-item">
                        <span className="label">Balance Inicial:</span>
                        <span className="value">${simulationPerformance.initial_balance.toFixed(2)}</span>
                      </div>
                      <div className="performance-item">
                        <span className="label">Balance Actual:</span>
                        <span className="value">${simulationPerformance.current_balance.toFixed(2)}</span>
                      </div>
                      <div className="performance-item">
                        <span className="label">Valor del Portafolio:</span>
                        <span className="value">${simulationPerformance.portfolio_value.toFixed(2)}</span>
                      </div>
                      <div className="performance-item">
                        <span className="label">Retorno Total:</span>
                        <span className={`value ${simulationPerformance.total_return >= 0 ? 'positive' : 'negative'}`}>
                          {simulationPerformance.total_return >= 0 ? '+' : ''}{simulationPerformance.total_return.toFixed(2)}%
                        </span>
                      </div>
                    </div>
                  )}
                  
                  <div className="trade-section">
                    <h4>Ejecutar Operación Basada en Predicción</h4>
                    
                    <div className="trade-form">
                      <div className="form-group">
                        <label>Activo:</label>
                        <select 
                          value={tradeForm.symbol} 
                          onChange={(e) => setTradeForm({...tradeForm, symbol: e.target.value})}
                        >
                          <option value="">Seleccionar activo</option>
                          {assets.map(asset => (
                            <option key={asset.id} value={asset.simbolo}>{asset.simbolo} - {asset.nombre}</option>
                          ))}
                        </select>
                      </div>
                      
                      <div className="form-group">
                        <label>Tipo de Activo:</label>
                        <select 
                          value={tradeForm.assetType} 
                          onChange={(e) => setTradeForm({...tradeForm, assetType: e.target.value})}
                        >
                          <option value="stock">Acción</option>
                          <option value="crypto">Criptomoneda</option>
                        </select>
                      </div>
                      
                      <div className="form-group">
                        <label>Modelo:</label>
                        <select 
                          value={tradeForm.modelType} 
                          onChange={(e) => setTradeForm({...tradeForm, modelType: e.target.value})}
                        >
                          <option value="lstm">LSTM</option>
                          <option value="random_forest">Random Forest</option>
                          <option value="xgboost">XGBoost</option>
                        </select>
                      </div>
                      
                      <button 
                        className="predict-button" 
                        onClick={handleExecuteTrade}
                        disabled={loading || !tradeForm.symbol}
                      >
                        {loading ? 'Ejecutando...' : 'Ejecutar Operación'}
                      </button>
                    </div>
                  </div>
                  
                  <div className="simulation-section">
                    <h4>Simular Período de Trading</h4>
                    
                    <div className="simulation-form">
                      <div className="form-group">
                        <label>Activo:</label>
                        <select 
                          value={simulationForm.symbol} 
                          onChange={(e) => setSimulationForm({...simulationForm, symbol: e.target.value})}
                        >
                          <option value="">Seleccionar activo</option>
                          {assets.map(asset => (
                            <option key={asset.id} value={asset.simbolo}>{asset.simbolo} - {asset.nombre}</option>
                          ))}
                        </select>
                      </div>
                      
                      <div className="form-group">
                        <label>Tipo de Activo:</label>
                        <select 
                          value={simulationForm.assetType} 
                          onChange={(e) => setSimulationForm({...simulationForm, assetType: e.target.value})}
                        >
                          <option value="stock">Acción</option>
                          <option value="crypto">Criptomoneda</option>
                        </select>
                      </div>
                      
                      <div className="form-group">
                        <label>Modelo:</label>
                        <select 
                          value={simulationForm.modelType} 
                          onChange={(e) => setSimulationForm({...simulationForm, modelType: e.target.value})}
                        >
                          <option value="lstm">LSTM</option>
                          <option value="random_forest">Random Forest</option>
                          <option value="xgboost">XGBoost</option>
                        </select>
                      </div>
                      
                      <div className="form-group">
                        <label>Días a Simular:</label>
                        <input 
                          type="number" 
                          min="1"
                          max="365"
                          value={simulationForm.days} 
                          onChange={(e) => setSimulationForm({...simulationForm, days: parseInt(e.target.value)})}
                        />
                      </div>
                      
                      <button 
                        className="predict-button" 
                        onClick={handleSimulateTrading}
                        disabled={loading || !simulationForm.symbol}
                      >
                        {loading ? 'Simulando...' : 'Simular Trading'}
                      </button>
                    </div>
                  </div>
                  
                  <div className="positions-section">
                    <h4>Posiciones Actuales</h4>
                    
                    {simulationPositions.length > 0 ? (
                      <table>
                        <thead>
                          <tr>
                            <th>Activo</th>
                            <th>Cantidad</th>
                            <th>Precio Promedio</th>
                            <th>Última Actualización</th>
                          </tr>
                        </thead>
                        <tbody>
                          {simulationPositions.map(position => (
                            <tr key={position.id}>
                              <td>{position.asset_symbol}</td>
                              <td>{position.quantity}</td>
                              <td>${position.average_price.toFixed(2)}</td>
                              <td>{new Date(position.updated_at).toLocaleString()}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    ) : (
                      <p>No hay posiciones abiertas.</p>
                    )}
                  </div>
                  
                  <div className="operations-section">
                    <h4>Historial de Operaciones</h4>
                    
                    {simulationOperations.length > 0 ? (
                      <table>
                        <thead>
                          <tr>
                            <th>Fecha</th>
                            <th>Activo</th>
                            <th>Tipo</th>
                            <th>Cantidad</th>
                            <th>Precio</th>
                          </tr>
                        </thead>
                        <tbody>
                          {simulationOperations.map(operation => (
                            <tr key={operation.id}>
                              <td>{new Date(operation.timestamp).toLocaleString()}</td>
                              <td>{operation.asset_symbol}</td>
                              <td className={operation.operation_type === 'buy' ? 'positive' : 'negative'}>
                                {operation.operation_type === 'buy' ? 'Compra' : 'Venta'}
                              </td>
                              <td>{operation.quantity}</td>
                              <td>${operation.price.toFixed(2)}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    ) : (
                      <p>No hay operaciones registradas.</p>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;