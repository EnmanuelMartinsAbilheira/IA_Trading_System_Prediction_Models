# setup_postgresql.py
import subprocess
import time

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
            return True
        else:
            print(f"❌ Error")
            if result.stderr.strip():
                print(f"Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ Excepción: {e}")
        return False

def setup_postgresql():
    """Configurar PostgreSQL desde cero"""
    print("🚀 Configurando PostgreSQL para el Sistema de Trading")
    print("=" * 60)
    
    # Paso 1: Verificar Docker
    print("\n🐳 Verificando Docker...")
    if not run_command('docker --version', 'Verificando Docker'):
        print("❌ Docker no está instalado")
        return False
    
    # Paso 2: Detener y eliminar contenedor existente
    print("\n🗑️  Limpiando contenedor existente...")
    run_command('docker stop trading_db', 'Deteniendo contenedor existente')
    run_command('docker rm trading_db', 'Eliminando contenedor existente')
    
    # Paso 3: Esperar un momento
    print("\n⏳ Esperando...")
    time.sleep(3)
    
    # Paso 4: Crear nuevo contenedor
    print("\n🏗️  Creando nuevo contenedor PostgreSQL...")
    command = 'docker run --name trading_db -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -e POSTGRES_DB=trading_db -p 5432:5432 -d postgres:13'
    
    if not run_command(command, 'Creando contenedor PostgreSQL'):
        print("❌ No se pudo crear el contenedor")
        return False
    
    # Paso 5: Esperar a que PostgreSQL esté listo
    print("\n⏳ Esperando a que PostgreSQL esté listo (30 segundos)...")
    print("Esto puede tardar un poco...")
    time.sleep(30)
    
    # Paso 6: Verificar que el contenedor está corriendo
    print("\n📋 Verificando estado del contenedor...")
    success, output = run_command('docker ps', 'Listando contenedores en ejecución')
    
    if 'trading_db' in output:
        print("✅ Contenedor PostgreSQL está corriendo")
        return True
    else:
        print("❌ El contenedor no está corriendo")
        return False

def main():
    if setup_postgresql():
        print("\n🎉 ¡PostgreSQL configurado exitosamente!")
        print("\n📝 Ahora ejecuta:")
        print("1. python test_db_connection.py")
        print("2. python init_db.py")
        print("3. python main.py")
    else:
        print("\n❌ Hubo un error al configurar PostgreSQL")
        print("💡 Revisa los mensajes above y asegúrate de que Docker esté funcionando")

if __name__ == "__main__":
    main()