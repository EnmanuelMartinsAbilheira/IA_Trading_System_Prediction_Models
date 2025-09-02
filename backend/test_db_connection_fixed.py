# test_db_connection_fixed.py
import os
import sys
import subprocess
import psycopg2
from sqlalchemy import create_engine

def check_docker_status():
    """Verificar el estado de Docker y del contenedor"""
    print("🐳 Verificando Docker y contenedores...")
    
    try:
        # Verificar si Docker está instalado
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Docker no está instalado o no está en el PATH")
            return False
        
        print(f"✅ Docker encontrado: {result.stdout.strip()}")
        
        # Verificar contenedores en ejecución
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
        print("📋 Contenedores en ejecución:")
        print(result.stdout)
        
        # Verificar si el contenedor trading_db existe
        result = subprocess.run(['docker', 'ps', '-a'], capture_output=True, text=True)
        if 'trading_db' in result.stdout:
            print("✅ El contenedor 'trading_db' existe")
            
            # Verificar si está en ejecución
            result_running = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
            if 'trading_db' in result_running.stdout:
                print("✅ El contenedor 'trading_db' está en ejecución")
                return True
            else:
                print("⚠️  El contenedor 'trading_db' existe pero no está en ejecución")
                print("   Para iniciarlo: docker start trading_db")
                return False
        else:
            print("❌ El contenedor 'trading_db' no existe")
            print("   Para crearlo: docker run --name trading_db -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -e POSTGRES_DB=trading_db -p 5432:5432 -d postgres:13")
            return False
            
    except FileNotFoundError:
        print("❌ Docker no está instalado o no está en el PATH")
        return False
    except Exception as e:
        print(f"❌ Error al verificar Docker: {e}")
        return False

def start_postgresql_container():
    """Iniciar el contenedor de PostgreSQL"""
    print("\n🚀 Iniciando contenedor PostgreSQL...")
    
    try:
        # Verificar si el contenedor ya existe
        result = subprocess.run(['docker', 'ps', '-a'], capture_output=True, text=True)
        
        if 'trading_db' in result.stdout:
            # El contenedor existe, verificar si está corriendo
            result_running = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
            if 'trading_db' not in result_running.stdout:
                # Iniciar el contenedor existente
                result = subprocess.run(['docker', 'start', 'trading_db'], capture_output=True, text=True)
                if result.returncode == 0:
                    print("✅ Contenedor 'trading_db' iniciado")
                    return True
                else:
                    print(f"❌ Error al iniciar contenedor: {result.stderr}")
                    return False
            else:
                print("✅ Contenedor 'trading_db' ya está corriendo")
                return True
        else:
            # Crear nuevo contenedor
            command = 'docker run --name trading_db -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -e POSTGRES_DB=trading_db -p 5432:5432 -d postgres:13'
            print(f"Ejecutando: {command}")
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Contenedor 'trading_db' creado e iniciado")
                print("⏳ Esperando a que PostgreSQL esté listo...")
                import time
                time.sleep(10)  # Esperar a que PostgreSQL inicie
                return True
            else:
                print(f"❌ Error al crear contenedor: {result.stderr}")
                return False
                
    except Exception as e:
        print(f"❌ Excepción al iniciar contenedor: {e}")
        return False

def test_connection():
    """Probar la conexión a la base de datos"""
    DATABASE_URL = "postgresql://user:password@localhost:5432/trading_db"
    print(f"\n🔌 Probando conexión a: {DATABASE_URL}")
    
    try:
        # Primero probar con psycopg2 directamente
        print("📡 Probando con psycopg2...")
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="trading_db",
            user="user",
            password="password"
        )
        print("✅ Conexión exitosa con psycopg2")
        conn.close()
        
        # Luego probar con SQLAlchemy
        print("📡 Probando con SQLAlchemy...")
        engine = create_engine(DATABASE_URL)
        connection = engine.connect()
        print("✅ Conexión exitosa con SQLAlchemy")
        connection.close()
        
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Error de conexión (psycopg2): {e}")
        return False
    except Exception as e:
        print(f"❌ Error de conexión (general): {e}")
        return False

def main():
    print("🔍 Herramienta de Diagnóstico de Conexión a PostgreSQL")
    print("=" * 60)
    
    # Paso 1: Verificar Docker
    if not check_docker_status():
        print("\n❌ Docker no está disponible. Por favor, instala Docker.")
        return
    
    # Paso 2: Iniciar PostgreSQL si es necesario
    if not start_postgresql_container():
        print("\n❌ No se pudo iniciar el contenedor PostgreSQL")
        return
    
    # Paso 3: Probar conexión
    if test_connection():
        print("\n🎉 ¡Conexión exitosa! La base de datos está lista.")
        print("\n📝 Siguientes pasos:")
        print("1. python init_db_updated.py  # Inicializar la base de datos")
        print("2. python main.py                # Iniciar el servidor backend")
    else:
        print("\n❌ La conexión falló. Revisa los mensajes above.")

if __name__ == "__main__":
    main()