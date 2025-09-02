# start_postgresql.py
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

def main():
    print("🚀 Iniciando PostgreSQL para el Sistema de Trading")
    print("=" * 50)
    
    # Verificar si Docker está disponible
    if not run_command('docker --version', 'Verificando Docker'):
        print("❌ Docker no está disponible. Por favor, instala Docker Desktop.")
        return
    
    # Verificar si el contenedor ya existe
    print("\n📋 Verificando contenedores existentes...")
    result = subprocess.run('docker ps -a', shell=True, capture_output=True, text=True)
    
    if 'trading_db' in result.stdout:
        print("✅ El contenedor 'trading_db' ya existe")
        
        # Verificar si está corriendo
        result_running = subprocess.run('docker ps', shell=True, capture_output=True, text=True)
        if 'trading_db' in result_running.stdout:
            print("✅ El contenedor 'trading_db' ya está en ejecución")
        else:
            # Iniciar el contenedor existente
            if not run_command('docker start trading_db', 'Iniciando contenedor existente'):
                return
    else:
        # Crear nuevo contenedor
        command = 'docker run --name trading_db -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -e POSTGRES_DB=trading_db -p 5432:5432 -d postgres:13'
        if not run_command(command, 'Creando nuevo contenedor PostgreSQL'):
            return
    
    # Esperar a que PostgreSQL esté listo
    print("\n⏳ Esperando a que PostgreSQL esté listo (10 segundos)...")
    time.sleep(10)
    
    # Verificar que el contenedor está corriendo
    if not run_command('docker ps | grep trading_db', 'Verificando que el contenedor está corriendo'):
        print("❌ El contenedor no está corriendo correctamente")
        return
    
    print("\n🎉 PostgreSQL está listo!")
    print("\n📝 Ahora puedes ejecutar:")
    print("1. python test_db_connection_fixed.py  # Para probar la conexión")
    print("2. python init_db_updated.py           # Para inicializar la base de datos")
    print("3. python main.py                      # Para iniciar el servidor backend")

if __name__ == "__main__":
    main()