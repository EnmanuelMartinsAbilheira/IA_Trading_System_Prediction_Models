# fix_postgresql_connection.py
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
            return True
        else:
            print(f"❌ Error en {description}")
            if result.stderr:
                print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Excepción en {description}: {e}")
        return False

def recreate_postgresql_container():
    """Recrear el contenedor PostgreSQL completamente"""
    print("🔄 Recreando contenedor PostgreSQL...")
    
    # Detener el contenedor si existe
    run_command('docker stop trading_db 2>/dev/null', 'Deteniendo contenedor existente')
    
    # Eliminar el contenedor si existe
    run_command('docker rm trading_db 2>/dev/null', 'Eliminando contenedor existente')
    
    # Esperar un momento
    time.sleep(2)
    
    # Crear nuevo contenedor
    command = 'docker run --name trading_db -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -e POSTGRES_DB=trading_db -p 5432:5432 -d postgres:13'
    if not run_command(command, 'Creando nuevo contenedor PostgreSQL'):
        return False
    
    # Esperar a que PostgreSQL esté completamente listo
    print("⏳ Esperando a que PostgreSQL esté listo (15 segundos)...")
    time.sleep(15)
    
    # Verificar que el contenedor está corriendo
    if not run_command('docker ps | grep trading_db', 'Verificando que el contenedor está corriendo'):
        return False
    
    return True

def test_connection():
    """Probar la conexión a la base de datos"""
    print("\n🔌 Probando conexión a PostgreSQL...")
    
    # Importar aquí para evitar errores si no están instaladas las librerías
    try:
        import psycopg2
        
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="trading_db",
            user="user",
            password="password"
        )
        print("✅ Conexión exitosa con psycopg2")
        conn.close()
        return True
        
    except ImportError:
        print("❌ psycopg2 no está instalado")
        return False
    except psycopg2.OperationalError as e:
        print(f"❌ Error de conexión: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def main():
    print("🔧 Herramienta de Reparación de Conexión PostgreSQL")
    print("=" * 60)
    
    print("Este script recreará el contenedor PostgreSQL para solucionar problemas de conexión.")
    print("¡Advertencia: Esto eliminará todos los datos existentes en el contenedor!")
    
    response = input("\n¿Estás seguro de continuar? (escribe 'si' para continuar): ")
    
    if response.lower() != 'si':
        print("❌ Operación cancelada")
        return
    
    # Paso 1: Recrear el contenedor
    if not recreate_postgresql_container():
        print("\n❌ No se pudo recrear el contenedor PostgreSQL")
        return
    
    # Paso 2: Probar la conexión
    if test_connection():
        print("\n🎉 ¡Conexión reparada exitosamente!")
        print("\n📝 Siguientes pasos:")
        print("1. python init_db_updated.py  # Inicializar la base de datos")
        print("2. python main.py                # Iniciar el servidor backend")
    else:
        print("\n❌ La conexión sigue fallando")
        print("Por favor, verifica:")
        print("1. Que Docker esté funcionando correctamente")
        print("2. Que el puerto 5432 esté disponible")
        print("3. Que no haya firewalls bloqueando la conexión")

if __name__ == "__main__":
    main()