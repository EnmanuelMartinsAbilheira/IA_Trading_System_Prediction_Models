# test_db_connection.py
import os
import sys
import subprocess
import psycopg2
from sqlalchemy import create_engine

def run_command(command, description=""):
    """Ejecutar un comando y mostrar el resultado"""
    print(f"\n🔄 {description}")
    print(f"Comando: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Éxito")
            if result.stdout.strip():
                print(f"Salida: {result.stdout.strip()}")
            return True, result.stdout
        else:
            print(f"❌ Error")
            if result.stderr.strip():
                print(f"Error: {result.stderr.strip()}")
            return False, result.stderr
    except Exception as e:
        print(f"❌ Excepción: {e}")
        return False, str(e)

def check_docker():
    """Verificar si Docker está disponible y funcionando"""
    print("🐳 Verificando Docker...")
    
    success, output = run_command('docker --version', 'Verificando instalación de Docker')
    if not success:
        print("❌ Docker no está instalado o no está en el PATH")
        return False
    
    success, output = run_command('docker ps', 'Verificando contenedores en ejecución')
    if not success:
        print("❌ No se puede listar contenedores")
        return False
    
    return True

def check_postgresql_container():
    """Verificar el estado del contenedor PostgreSQL"""
    print("\n🗄️ Verificando contenedor PostgreSQL...")
    
    # Verificar si el contenedor existe
    success, output = run_command('docker ps -a', 'Listando todos los contenedores')
    
    if 'trading_db' in output:
        print("✅ El contenedor 'trading_db' existe")
        
        # Verificar si está en ejecución
        success, output = run_command('docker ps', 'Verificando contenedores en ejecución')
        if 'trading_db' in output:
            print("✅ El contenedor 'trading_db' está en ejecución")
            return True
        else:
            print("⚠️  El contenedor 'trading_db' existe pero no está en ejecución")
            return False
    else:
        print("❌ El contenedor 'trading_db' no existe")
        return False

def test_internal_connection():
    """Probar conexión dentro del contenedor"""
    print("\n🔌 Probando conexión interna...")
    
    success, output = run_command(
        'docker exec trading_db psql -U user -d trading_db -c "SELECT current_user;"',
        'Probando conexión como usuario user dentro del contenedor'
    )
    
    if success and 'user' in output:
        print("✅ Conexión interna exitosa")
        return True
    else:
        print("❌ Conexión interna falló")
        return False

def test_external_connection():
    """Probar conexión externa desde el host"""
    print("\n🌐 Probando conexión externa...")
    
    try:
        # Probar con psycopg2
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="trading_db",
            user="user",
            password="password"
        )
        print("✅ Conexión externa exitosa con psycopg2")
        conn.close()
        
        # Probar con SQLAlchemy
        DATABASE_URL = "postgresql://user:password@localhost:5432/trading_db"
        engine = create_engine(DATABASE_URL)
        connection = engine.connect()
        print("✅ Conexión externa exitosa con SQLAlchemy")
        connection.close()
        
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Error de conexión (psycopg2): {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def main():
    print("🔍 Herramienta de Diagnóstico de PostgreSQL")
    print("=" * 50)
    
    # Paso 1: Verificar Docker
    if not check_docker():
        print("\n❌ Docker no está disponible. Por favor, instala Docker.")
        return
    
    # Paso 2: Verificar contenedor PostgreSQL
    container_ok = check_postgresql_container()
    
    if not container_ok:
        print("\n💡 El contenedor PostgreSQL no está disponible.")
        print("Ejecuta: python setup_postgresql.py")
        return
    
    # Paso 3: Probar conexión interna
    if not test_internal_connection():
        print("\n❌ La conexión interna falló. El contenedor podría estar dañado.")
        print("Ejecuta: python setup_postgresql.py")
        return
    
    # Paso 4: Probar conexión externa
    if test_external_connection():
        print("\n🎉 ¡Todo funciona correctamente!")
        print("\n📝 Siguientes pasos:")
        print("1. python init_db.py")
        print("2. python main.py")
    else:
        print("\n❌ La conexión externa falló.")
        print("💡 Soluciones:")
        print("1. Espera unos segundos y vuelve a intentarlo")
        print("2. Ejecuta: python setup_postgresql.py")
        print("3. Reinicia el contenedor: docker restart trading_db")

if __name__ == "__main__":
    main()