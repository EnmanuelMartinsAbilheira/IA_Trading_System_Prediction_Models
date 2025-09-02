README_SCRIPTS.md
📚 Guía de Scripts para el Sistema de Trading con IA
🚀 Scripts Disponibles
1. install_deps.py - Instalador de Dependencias
Propósito: Instala todas las dependencias críticas de Python que puedan faltar.

Uso:

"""
  python install_deps.py
"""

Qué hace:

Verifica e instala: PyJWT, python-dotenv, psycopg2-binary, SQLAlchemy, FastAPI, uvicorn
Muestra un resumen de lo que se instaló
2. setup_postgresql.py - Configurador de PostgreSQL
Propósito: Configura PostgreSQL desde cero usando Docker.

Uso:
"""
  python setup_postgresql.py
"""

Qué hace:

Detiene y elimina cualquier contenedor existente
Crea un nuevo contenedor PostgreSQL con la configuración correcta
Espera a que PostgreSQL esté listo
Verifica que la conexión interna funcione
3. test_db_connection.py - Probador de Conexión
Propósito: Diagnostica completamente el estado de PostgreSQL y las conexiones.

Uso:
"""
  python test_db_connection.py
"""

Qué hace:

Verifica Docker
Verifica el contenedor PostgreSQL
Prueba conexión interna al contenedor
Prueba conexión externa desde el host
Muestra diagnóstico completo
4. init_db.py - Inicializador de Base de Datos
Propósito: Crea las tablas y carga los datos iniciales en la base de datos.

Uso:
"""
  python init_db.py
"""

Qué hace:

Prueba la conexión antes de intentar inicializar
Crea todas las tablas necesarias
Agrega activos iniciales (acciones y criptomonedas)
Crea un usuario de prueba
Muestra resumen de lo que se hizo
5. status_check.py - Verificador de Estado
Propósito: Verifica el estado completo del sistema.

Uso:
"""
  python status_check.py
"""

Qué hace:

Verifica todas las dependencias de Python
Verifica Docker
Verifica PostgreSQL
Verifica conexión externa
Muestra resumen completo del estado
6. quick_start.py - Inicio Rápido
Propósito: Guía paso a paso para configurar todo el sistema.

Uso:
"""
  python quick_start.py
"""

Qué hace:

Ejecuta setup_postgresql.py
Ejecuta test_db_connection.py
Ejecuta init_db.py
Inicia el servidor main.py
Guía interactiva
🎯 Flujo de Trabajo Recomendado
Opción A: Inicio Rápido (Recomendado para principiantes)

"""
  1. Ejecutar el inicio rápido (todo automático)
  python quick_start.py
"""

Opción B: Paso a Paso Manual

"""
  # 1. Verificar estado actual
  python status_check.py

  # 2. Instalar dependencias si es necesario
  python install_deps.py

  # 3. Configurar PostgreSQL
  python setup_postgresql.py

  # 4. Probar conexión
  python test_db_connection.py

  # 5. Inicializar base de datos
  python init_db.py

  # 6. Iniciar servidor
  python main.py                                
"""

Opción C: Diagnóstico y Reparación
"""
  # Si tienes problemas, primero diagnostica
  python status_check.py

  # Luego prueba la conexión específica
  python test_db_connection.py

  # Si PostgreSQL tiene problemas, reconfigúralo
  python setup_postgresql.py
"""

🔍 Solución de Problemas Comunes
Problema: "ModuleNotFoundError: No module named 'jwt'"
Solución:
  
"""
  python install_deps.py
"""

Problema: "FATAL: password authentication failed for user 'user'"
Solución:

"""
  python setup_postgresql.py
"""

Problema: Docker no funciona
Solución:

Instalar Docker Desktop
Reiniciar el equipo
Ejecutar: python status_check.py
Problema: Contenedor PostgreSQL no inicia
Solución:
  
"""
  # Limpiar y recrear
  docker stop trading_db
  docker rm trading_db
  python setup_postgresql.py
"""


Problema: Conexión externa falla pero interna funciona
Solución:

"""
  # Generalmente se soluciona recreando el contenedor
  python setup_postgresql.py
"""

📝 Notas Importantes
Orden de ejecución: Siempre ejecuta setup_postgresql.py antes de init_db.py
Esperar tiempos: Los scripts incluyen tiempos de espera necesarios para que PostgreSQL se inicialice
Docker necesario: Todos los scripts asumen que Docker está instalado y funcionando
Puerto 5432: Asegúrate de que el puerto 5432 esté disponible
🎉 ¡Listo para Usar!
Una vez que todos los scripts se ejecuten correctamente, tendrás:

✅ PostgreSQL corriendo en Docker
✅ Base de datos inicializada con tablas y datos
✅ Todas las dependencias de Python instaladas
✅ Conexión externa funcionando
Entonces podrás:

"""
  # Iniciar el backend
  python main.py

  # En otra terminal, iniciar el frontend
  cd frontend
  npm start

  # Acceder a la aplicación
  http://localhost:3000
"""