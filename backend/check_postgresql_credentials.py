# check_postgresql_credentials.py
import subprocess
import sys
import time

def run_command(command, description):
    print(f"\n🔄 {description}...")
    print(f"Comando: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completado exitosamente")
            if result.stdout:
                print(f"Salida: {result.stdout}")
            return True, result.stdout
        else:
            print(f"❌ Error en {description}")
            if result.stderr:
                print(f"Error: {result.stderr}")
            return False, result.stderr
    except Exception as e:
        print(f"❌ Excepción en {description}: {e}")
        return False, str(e)

def check_container_env():
    """Verificar las variables de entorno del contenedor"""
    print("🔍 Verificando variables de entorno del contenedor...")
    
    success, output = run_command('docker exec trading_db env', 'Verificando variables de entorno del contenedor')
    
    if success:
        print("\n📋 Variables de entorno encontradas:")
        env_vars = output.split('\n')
        for var in env_vars:
            if any(keyword in var.lower() for keyword in ['postgres', 'user', 'password', 'db']):
                print(f"  {var}")
    
    return success

def check_postgresql_users():
    """Verificar los usuarios en PostgreSQL"""
    print("\n👥 Verificando usuarios en PostgreSQL...")
    
    # Intentar conectarse como postgres y listar usuarios
    command = 'docker exec -u postgres trading_db psql -c "SELECT usename FROM pg_user;"'
    success, output = run_command(command, 'Listando usuarios de PostgreSQL')
    
    if success:
        print("✅ Usuarios encontrados:")
        print(output)
    
    return success

def check_postgresql_databases():
    """Verificar las bases de datos en PostgreSQL"""
    print("\n🗄️ Verificando bases de datos en PostgreSQL...")
    
    command = 'docker exec -u postgres trading_db psql -c "SELECT datname FROM pg_database;"'
    success, output = run_command(command, 'Listando bases de datos')
    
    if success:
        print("✅ Bases de datos encontradas:")
        print(output)
    
    return success

def test_connection_inside_container():
    """Probar conexión dentro del contenedor"""
    print("\n🔌 Probando conexión dentro del contenedor...")
    
    # Probar conexión como el usuario postgres
    command = 'docker exec trading_db psql -U postgres -d postgres -c "SELECT version();"'
    success, output = run_command(command, 'Probando conexión como postgres')
    
    if success:
        print("✅ Conexión como postgres exitosa")
    
    # Probar conexión como el usuario user
    command = 'docker exec trading_db psql -U user -d trading_db -c "SELECT version();"'
    success, output = run_command(command, 'Probando conexión como user')
    
    if success:
        print("✅ Conexión como user exitosa")
    else:
        print("❌ Conexión como user falló - esto explica el error")
    
    return success

def create_user_and_database():
    """Crear el usuario y la base de datos si no existen"""
    print("\n🏗️ Creando usuario y base de datos...")
    
    # Crear el usuario si no existe
    command = 'docker exec -u postgres trading_db psql -c "CREATE USER user WITH PASSWORD \'password\';"'
    success, output = run_command(command, 'Creando usuario')
    
    # Crear la base de datos si no existe
    command = 'docker exec -u postgres trading_db psql -c "CREATE DATABASE trading_db OWNER user;"'
    success, output = run_command(command, 'Creando base de datos')
    
    # Conceder permisos
    command = 'docker exec -u postgres trading_db psql -d trading_db -c "GRANT ALL PRIVILEGES ON DATABASE trading_db TO user;"'
    success, output = run_command(command, 'Concediendo permisos')
    
    return success

def reset_postgresql():
    """Reiniciar completamente PostgreSQL"""
    print("\n🔄 Reiniciando PostgreSQL...")
    
    # Detener el contenedor
    run_command('docker stop trading_db', 'Deteniendo contenedor')
    
    # Eliminar el contenedor
    run_command('docker rm trading_db', 'Eliminando contenedor')
    
    # Crear nuevo contenedor con configuración correcta
    command = 'docker run --name trading_db -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -e POSTGRES_DB=trading_db -p 5432:5432 -d postgres:13'
    success, output = run_command(command, 'Creando nuevo contenedor')
    
    if success:
        print("⏳ Esperando a que PostgreSQL esté listo...")
        time.sleep(15)  # Esperar más tiempo para que se inicialice completamente
    
    return success

def main():
    print("🔍 Herramienta de Diagnóstico de PostgreSQL")
    print("=" * 50)
    
    # Paso 1: Verificar variables de entorno
    check_container_env()
    
    # Paso 2: Verificar usuarios
    check_postgresql_users()
    
    # Paso 3: Verificar bases de datos
    check_postgresql_databases()
    
    # Paso 4: Probar conexión dentro del contenedor
    test_connection_inside_container()
    
    # Paso 5: Preguntar si quiere recrear el contenedor
    print("\n🤔 ¿La conexión falló? ¿Quieres recrear el contenedor PostgreSQL?")
    print("Esto eliminará el contenedor actual y creará uno nuevo.")
    response = input("Escribe 'si' para continuar o cualquier otra tecla para salir: ")
    
    if response.lower() == 'si':
        if reset_postgresql():
            print("\n🎉 Contenedor recreado exitosamente")
            print("Ahora prueba la conexión con: python test_db_connection_fixed.py")
        else:
            print("\n❌ Error al recrear el contenedor")
    else:
        print("\n👋 Saliendo sin hacer cambios")

if __name__ == "__main__":
    main()