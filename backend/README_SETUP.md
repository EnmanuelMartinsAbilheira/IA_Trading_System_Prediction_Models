README_SETUP.md
🚀 Guía de Configuración del Sistema de Trading con IA
📋 Scripts Disponibles
1. check_system.py - Verificación del Sistema
Propósito: Verificar que todos los componentes necesarios estén instalados y funcionando.

"""
python check_system.py
"""

Qué verifica:

✅ Python y pip
✅ Docker
✅ Contenedor PostgreSQL
✅ Paquetes Python necesarios
✅ Puertos disponibles
2. setup_postgresql.py - Configuración de PostgreSQL
Propósito: Configurar PostgreSQL desde cero (eliminar contenedor existente y crear uno nuevo).

"""
python setup_postgresql.py
"""

Qué hace:

🗑️ Detiene y elimina el contenedor existente
🏗️ Crea un nuevo contenedor PostgreSQL
⏳ Espera a que esté listo
✅ Verifica que está corriendo
3. test_db_connection.py - Prueba de Conexión
Propósito: Probar la conexión a PostgreSQL (interna y externa).

"""
python test_db_connection.py
"""

Qué prueba:

🐳 Verifica Docker y el contenedor
🔌 Prueba conexión interna al contenedor
🌐 Prueba conexión externa desde el host
📊 Muestra resultados detallados
4. init_db.py - Inicialización de Base de Datos
Propósito: Crear las tablas y agregar datos iniciales.

"""
python init_db.py
"""

Qué hace:

📋 Crea tablas (usuarios, activos, etc.)
💰 Agrega 10 activos iniciales (5 acciones + 5 criptomonedas)
👤 Crea un usuario de prueba
✅ Verifica que todo se creó correctamente
5. quick_start.py - Configuración Automática Completa
Propósito: Realizar toda la configuración en un solo paso.

"""
python quick_start.py
"""

Qué hace:

🔄 Ejecuta todos los pasos automáticamente
🗑️ Limpia contenedores existentes
🏗️ Crea nuevo contenedor PostgreSQL
🧪 Prueba conexión
💾 Inicializa base de datos
🚀 Inicia el backend
🎯 Flujo de Trabajo Recomendado
Opción A: Verificación Paso a Paso (Recomendado para principiantes)

"""
# 1. Verificar que todo está instalado
python check_system.py

# 2. Configurar PostgreSQL
python setup_postgresql.py

# 3. Probar conexión
python test_db_connection.py

# 4. Inicializar base de datos
python init_db.py

# 5. Iniciar backend
python main.py
"""

Opción B: Configuración Automática (Recomendado para usuarios avanzados)

"""
# Todo en un solo paso
python quick_start.py
"""

Opción C: Solución de Problemas
Si tienes problemas, ejecuta en este orden:

"""
# 1. Verificar sistema
python check_system.py

# 2. Si hay problemas con PostgreSQL, configurarlo
python setup_postgresql.py

# 3. Probar conexión
python test_db_connection.py

# 4. Si la conexión funciona, inicializar
python init_db.py
"""


🔧 Solución de Problemas Comunes
Problema: "Docker no está instalado"
Solución: Instala Docker Desktop desde https://www.docker.com/products/docker-desktop

Problema: "El contenedor ya existe"
Solución: Ejecuta python setup_postgresql.py para limpiar y recrear

Problema: "Conexión fallida"
Solución:

python setup_postgresql.py
Espera 30 segundos
python test_db_connection.py
Problema: "Paquetes faltantes"
Solución:

"""
pip install fastapi uvicorn sqlalchemy psycopg2 pandas numpy tensorflow xgboost yfinance ccxt PyJWT
"""

Problema: "Puertos en uso"
Solución: Cierra las aplicaciones que usan los puertos 8000 y 3000

🌐 Acceso al Sistema
Una vez configurado, podrás acceder a:

Backend API: http://localhost:8000
Documentación API: http://localhost:8000/docs
Frontend: http://localhost:3000 (ejecuta cd frontend && npm start)
📝 Notas Importantes
Tiempo de espera: PostgreSQL puede tardar hasta 30 segundos en estar listo después de crear el contenedor.
Contenedores: Los scripts eliminarán y recrearán el contenedor trading_db cuando sea necesario.
Datos: Los datos en PostgreSQL se perderán si eliminas el contenedor.
Dependencias: Asegúrate de tener todas las dependencias instaladas (usa check_system.py).
🚀 ¡Listo para Usar!
Una vez que completes los pasos, tu sistema de trading con IA estará funcionando y podrás:

📈 Obtener predicciones de trading
🧪 Realizar backtesting
⚖️ Gestionar riesgos
🔔 Configurar notificaciones
🎮 Simular operaciones
¡Empieza con python check_system.py para verificar que todo está listo!