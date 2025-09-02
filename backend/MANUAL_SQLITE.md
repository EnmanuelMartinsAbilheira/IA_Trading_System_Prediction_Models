# MANUAL_SQLITE.md - Instrucciones manuales para SQLite

## 🚀 SOLUCIÓN MANUAL CON SQLITE

Dado que los scripts automáticos tienen problemas de codificación en Windows, aquí tienes las instrucciones manuales paso a paso.

### 📋 PASO A PASO:

#### Paso 1: Inicializar la base de datos SQLite
```bash
python init_sqlite_simple.py
```

Deberías ver:
```
Inicializando Base de Datos SQLite
==================================================
Creando tablas...
Tablas creadas exitosamente
Agregando activos iniciales...
  + AAPL - Apple Inc.
  + MSFT - Microsoft Corporation
  + GOOGL - Alphabet Inc.
  + AMZN - Amazon.com Inc.
  + TSLA - Tesla Inc.
  + BTC/USDT - Bitcoin
  + ETH/USDT - Ethereum
  + BNB/USDT - Binance Coin
  + ADA/USDT - Cardano
  + SOL/USDT - Solana
Agregando usuario de prueba...
  + Usuario: test
Base de datos SQLite inicializada exitosamente!
Resumen:
   - 10 activos agregados
   - Tablas creadas: usuarios, activos, y mas
   - Usuario de prueba: test
   - Archivo de base de datos: trading.db
Listo para iniciar el servidor!
Ejecuta: python main_sqlite.py
Accede a:
  - Backend: http://localhost:8000
  - Documentacion: http://localhost:8000/docs
```

#### Paso 2: Iniciar el servidor backend
```bash
python main_sqlite.py
```

Deberías ver algo como:
```
2025-09-02 11:21:47.329484: I tensorflow/core/util/port.cc:153] oneDNN custom operations are on...
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

#### Paso 3: Probar que el servidor funciona
Abre otra terminal y ejecuta:
```bash
python test_sqlite.py
```

Elige la opción 3 para probar la API.

#### Paso 4: Acceder al sistema
Una vez que el servidor esté corriendo, puedes acceder a:

- **Backend API**: http://localhost:8000
- **Documentación API**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000 (ejecuta `cd frontend && npm start` en otra terminal)

### 🔍 PROBAR ENDPOINTS MANUALMENTE:

Si no quieres usar el script de prueba, puedes probar los endpoints manualmente:

#### 1. Probar conexión básica
```bash
curl http://localhost:8000/
```
Deberías ver: `{"message":"Trading AI System API - SQLite Version"}`

#### 2. Probar obtener activos
```bash
curl http://localhost:8000/assets
```
Deberías ver una lista de activos.

#### 3. Probar predicción
```bash
curl "http://localhost:8000/predict?symbol=AAPL&asset_type=stock&model_type=lstm"
```

#### 4. Probar crear cuenta de simulación
```bash
curl -X POST "http://localhost:8000/simulation/accounts" \
  -H "Content-Type: application/json" \
  -d '{"account_name": "Cuenta Prueba", "initial_balance": 10000}'
```

### 📁 ARCHIVOS IMPORTANTES:

- `init_sqlite_simple.py` - Inicializador de base de datos (sin emojis)
- `main_sqlite.py` - Servidor backend corregido
- `simulator_sqlite.py` - Simulador corregido para SQLite
- `test_sqlite.py` - Probador de la API

### 🎯 SI ALGO FALLA:

#### Problema: "ModuleNotFoundError" o "ImportError"
**Solución:** Asegúrate de tener todas las dependencias:
```bash
pip install fastapi uvicorn sqlalchemy pandas numpy tensorflow xgboost yfinance ccxt PyJWT
```

#### Problema: "Database locked"
**Solución:** Es normal en SQLite. Cierra el servidor y vuelve a iniciarlo.

#### Problema: "Address already in use"
**Solución:** Cierra cualquier programa que esté usando el puerto 8000.

#### Problema: "No se puede conectar al servidor"
**Solución:** Asegúrate de que el servidor esté corriendo (debes ver el mensaje de Uvicorn).

### 🚀 INICIO RÁPIDO:

```bash
# 1. Inicializar base de datos
python init_sqlite_simple.py

# 2. Iniciar servidor
python main_sqlite.py

# 3. En otra terminal, probar
python test_sqlite.py
```

### 🎉 ¡LISTO PARA USAR!

Una vez que todo funcione, tendrás:

- ✅ **Base de datos SQLite** con 10 activos y usuario de prueba
- ✅ **Backend API** funcionando en http://localhost:8000
- ✅ **Predicciones de trading** con IA
- ✅ **Simulación de trading** con cuentas virtuales
- ✅ **Documentación interactiva** en http://localhost:8000/docs

### 🔄 PARA EL FUTURO:

Cuando quieras pasar a producción, puedes:

1. **Usar PostgreSQL** con los archivos originales
2. **Configurar Docker** para PostgreSQL
3. **Migrar los datos** de SQLite a PostgreSQL

¡Pero por ahora, SQLite es perfecto para desarrollar y aprender! 🚀