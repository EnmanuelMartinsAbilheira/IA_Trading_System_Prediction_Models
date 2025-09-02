🚀 Guía Rápida de Solución de Problemas
Problemas Actuales y Soluciones
1. Error: ModuleNotFoundError: No module named 'jwt'
Solución:
    
"""
# Instalar PyJWT
pip install PyJWT

# O ejecutar el script automático
python install_missing_deps.py
"""

2. Error: FATAL: password authentication failed for user "user"
Solución:

"""
# Opción A: Usar Docker (recomendado)
docker run --name trading_db -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -e POSTGRES_DB=trading_db -p 5432:5432 -d postgres:13

# Opción B: Verificar si PostgreSQL está corriendo
docker ps

# Opción C: Probar conexión
python test_db_connection.py
"""

3. Pasos Completos para Configurar el Sistema
Paso 1: Instalar dependencias faltantes

"""
python install_missing_deps.py
"""

Paso 2: Iniciar PostgreSQL con Docker
"""
docker run --name trading_db -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -e POSTGRES_DB=trading_db -p 5432:5432 -d postgres:13
"""

Paso 3: Probar conexión a la base de datos
"""
python test_db_connection.py
"""

Paso 4: Inicializar la base de datos
"""
python init_db_updated.py
"""

Paso 5: Iniciar el backend
"""
python main.py
"""

Paso 6: Iniciar el frontend (en otra terminal)
"""
cd frontend
npm start
"""

4. Configuración Automática (Recomendado)
Ejecuta el script de configuración automática:

"""
python setup_guide.py
"""

Este script te guiará a través de todos los pasos necesarios.

5. Verificación Final
Una vez configurado, verifica que todo funciona:

Backend: http://localhost:8000
Deberías ver: {"message": "Trading AI System API"}
Documentación: http://localhost:8000/docs
Frontend: http://localhost:3000
Deberías ver la interfaz del sistema de trading
Base de Datos:
El contenedor Docker debe estar corriendo: docker ps
Deberías ver el contenedor trading_db
6. Solución de Problemas Comunes
Problema: Docker no está instalado
Solución:

Descarga e instala Docker Desktop desde https://www.docker.com/products/docker-desktop
Problema: Puerto 5432 ya está en uso
Solución:

Cambia el puerto en el comando de Docker:

"""
docker run --name trading_db -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -e POSTGRES_DB=trading_db -p 5433:5432 -d postgres:13
"""

Actualiza la URL de la base de datos:
"""
DATABASE_URL=postgresql://user:password@localhost:5433/trading_db
"""

Problema: Contenedor ya existe
Solución:
"""
# Eliminar el contenedor existente
docker rm -f trading_db

# Crear uno nuevo
docker run --name trading_db -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -e POSTGRES_DB=trading_db -p 5432:5432 -d postgres:13
"""

Problema: Dependencias de Python
Solución:

"""
# Limpiar e reinstalar
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
pip install PyJWT python-dotenv
"""

7. Prueba Rápida
Si quieres probar rápidamente sin configurar todo, ejecuta:

"""
# 1. Instalar dependencias faltantes
python install_missing_deps.py

# 2. Iniciar PostgreSQL
docker run --name trading_db -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -e POSTGRES_DB=trading_db -p 5432:5432 -d postgres:13

# 3. Esperar 10 segundos y probar conexión
python test_db_connection.py

# 4. Inicializar base de datos
python init_db_updated.py

# 5. Iniciar backend
python main.py
"""


¡Y listo! Tu sistema de trading con IA debería estar funcionando.