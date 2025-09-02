🚀 Sistema de Trading con IA - Versión SQLite
📋 ¿Qué es SQLite?
SQLite es una base de datos ligera que no requiere servidor ni configuración externa. A diferencia de PostgreSQL, SQLite:

✅ No necesita Docker
✅ No necesita configuración externa
✅ Funciona directamente con Python
✅ Perfecto para desarrollo y pruebas
✅ Muy fácil de usar

🎯 Ventajas de usar SQLite
Simplicidad: No hay que configurar Docker ni PostgreSQL
Rapidez: La base de datos se crea instantáneamente
Portabilidad: Todo está en un solo archivo (trading.db)
Sin dependencias: Solo necesitas Python y las librerías ya instaladas
🚀 Inicio Rápido con SQLite

Opción A: Todo Automático (Recomendado)
"""
python quick_start_sqlite.py
"""

Opción B: Paso a Paso Manual
"""
# 1. Inicializar la base de datos
python init_sqlite.py

# 2. Iniciar el servidor backend
python main_sqlite.py
"""

📁 Archivos de la Versión SQLite
Archivo                     Propósito
main_sqlite.py              Servidor backend principal con SQLite
init_sqlite.py              Inicializador de base de datos SQLite
simulator_sqlite.py         Simulador de trading corregido
quick_start_sqlite.py       Inicio rápido automático


🔍 ¿Qué pasa con los archivos originales?
Los archivos originales siguen ahí:

main.py - Versión con PostgreSQL (requiere Docker)
init_db.py - Versión con PostgreSQL
simulator.py - Versión con problemas de importación
Puedes usar la versión SQLite para desarrollo y pruebas, y luego migrar a PostgreSQL cuando quieras.

🌐 Acceso al Sistema
Una vez que inicies el servidor con SQLite:

Backend API: http://localhost:8000
Documentación API: http://localhost:8000/docs
Frontend: http://localhost:3000 (ejecuta cd frontend && npm start)
🧪 Probando el Sistema

1. Probar la API
"""
# Iniciar el servidor
python main_sqlite.py

# En otra terminal, probar los endpoints
curl http://localhost:8000/
curl http://localhost:8000/assets
"""

2. Probar predicciones
"""
# Obtener predicción para Apple
curl "http://localhost:8000/predict?symbol=AAPL&asset_type=stock&model_type=lstm"
"""

3. Probar simulación
"""
# Crear cuenta de simulación
curl -X POST "http://localhost:8000/simulation/accounts" \
  -H "Content-Type: application/json" \
  -d '{"account_name": "Cuenta Prueba", "initial_balance": 10000}'

# Ejecutar operación de trading
curl -X POST "http://localhost:8000/simulation/accounts/1/trade" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "asset_type": "stock", "model_type": "lstm"}'
"""

🔧 Solución de Problemas
Problema: "ModuleNotFoundError"
Solución: Asegúrate de tener todas las dependencias instaladas
"""
pip install fastapi uvicorn sqlalchemy pandas numpy tensorflow xgboost yfinance ccxt PyJWT
"""

Problema: "ImportError: attempted relative import"
Solución: Usa los archivos _sqlite.py que ya están corregidos

Problema: "Database locked"
Solución: Es normal en SQLite, espera un momento y vuelve a intentarlo

Problema: El servidor no inicia
Solución: Verifica que no haya otro proceso usando el puerto 8000

📊 Características Disponibles
Con SQLite, tendrás todas las mismas características:

✅ Predicciones de trading con IA (LSTM, Random Forest, XGBoost)
✅ Backtesting de estrategias
✅ Simulación de trading con cuentas virtuales
✅ Gestión de riesgos
✅ Notificaciones (email, Telegram)
✅ API REST completa
✅ Documentación interactiva
🎉 ¡Listo para Usar!
Con SQLite, puedes:

Desarrollar y probar sin complicaciones
Experimentar con el sistema inmediatamente
Aprender a usar la API fácilmente
Migrar a PostgreSQL cuando quieras desplegar en producción
🔄 Migración a PostgreSQL (Opcional)
Cuando quieras pasar a producción, puedes:

Usar los archivos originales (main.py, init_db.py)
Configurar PostgreSQL con los scripts anteriores
Exportar datos de SQLite e importarlos a PostgreSQL
🚀 ¡Empieza Ahora!

"""
python quick_start_sqlite.py
"""

O si prefieres paso a paso:
"""
python init_sqlite.py
python main_sqlite.py
"""

¡Disfruta de tu Sistema de Trading con IA sin complicaciones! 🎉


🎉 ¡SOLUCIÓN COMPLETA!
He creado una solución completa que te permite elegir entre PostgreSQL y SQLite. Te recomiendo encarecidamente usar SQLite ya que es mucho más simple y no tiene los problemas de Docker que estás experimentando.

🚀 OPCIÓN RECOMENDADA: Usar SQLite (Simple y Rápido)
Paso 1: Ejecutar el selector de base de datos
"""
python choose_database.py
"""

Cuando te pregunte, elige la opción 2 (SQLite).

Paso 2: O si prefieres ir directamente a SQLite:
"""
# Inicializar la base de datos SQLite
python init_sqlite.py

# Iniciar el servidor
python main_sqlite.py
"""

Paso 3: O si quieres todo automático:
"""
python quick_start_sqlite.py
"""

📁 Archivos Creados para SQLite:
Archivo                 Propósito
main_sqlite.py          Servidor backend con SQLite
init_sqlite.py          Inicializador de base de datos SQLite
simulator_sqlite.py     Simulador corregido para SQLite
quick_start_sqlite.py   Inicio rápido automático
choose_database.py      Selector entre PostgreSQL y SQLite
README_SQLITE.md        Documentación completa

✅ Ventajas de SQLite:
🚀 No necesita Docker - ¡Adiós a los problemas de Docker!
⚡ Rápido - La base de datos se crea instantáneamente
🎯 Simple - Todo está en un archivo (trading.db)
🔧 Sin dependencias - Solo necesitas Python
📚 Perfecto para aprender - Puedes experimentar sin complicaciones
🌐 Acceso al Sistema:
Una vez que inicies python main_sqlite.py:

Backend API: http://localhost:8000
Documentación API: http://localhost:8000/docs
Frontend: http://localhost:3000 (ejecuta cd frontend && npm start)
🧪 Pruebas Rápidas:
"""
# 1. Iniciar el sistema
python init_sqlite.py
python main_sqlite.py

# 2. Probar la API (en otra terminal)
curl http://localhost:8000/
curl http://localhost:8000/assets

# 3. Obtener una predicción
curl "http://localhost:8000/predict?symbol=AAPL&asset_type=stock&model_type=lstm"
"""

🎯 ¿Qué hacer ahora?
Te recomiendo encarecidamente:
"""
python choose_database.py
"""

Y cuando te pregunte, elige la opción 2 (SQLite).

O si prefieres ir directamente:
"""
python quick_start_sqlite.py
"""

🔍 ¿Por qué SQLite es mejor para ti ahora?
No tienes problemas con Docker
No necesitas configurar nada externo
Puedes empezar inmediatamente
Tienes todas las mismas características (predicciones, backtesting, simulación)
Es perfecto para desarrollo y aprendizaje
🚨 Importante:
Los archivos originales (main.py, init_db.py, simulator.py) siguen ahí para PostgreSQL. Puedes usarlos más adelante si quieres, pero por ahora SQLite es la mejor opción para ti.

🎉 ¡Listo para empezar!
Ejecuta ahora mismo:
"""
python choose_database.py
"""

Y elige la opción 2 (SQLite). ¡Así podrás empezar a usar tu Sistema de Trading con IA inmediatamente sin complicaciones! 🚀