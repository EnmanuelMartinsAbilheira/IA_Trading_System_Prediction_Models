# fix_docker_issue.py - Versión corregida
import subprocess
import sys
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

def check_docker_status():
    """Verificar el estado de Docker"""
    print("\n🐳 Verificando estado de Docker...")
    
    # Verificar si Docker está instalado
    success = run_command('docker --version', 'Verificando Docker')
    if not success:
        print("❌ Docker no está instalado")
        return False
    
    # Verificar si Docker está funcionando
    success = run_command('docker ps', 'Verificando si Docker responde')
    if not success:
        print("❌ Docker no está respondiendo")
        print("\n💡 SOLUCIÓN:")
        print("1. Abre Docker Desktop desde el menú de inicio")
        print("2. Espera a que esté completamente iniciado (1-2 minutos)")
        print("3. Vuelve a ejecutar este script")
        return False
    
    print("✅ Docker está funcionando correctamente")
    return True

def setup_postgresql():
    """Configurar PostgreSQL"""
    print("\n🗄️ Configurando PostgreSQL...")
    
    # Detener y eliminar contenedor existente
    run_command('docker stop trading_db', 'Deteniendo contenedor existente')
    run_command('docker rm trading_db', 'Eliminando contenedor existente')
    
    # Esperar un momento
    time.sleep(2)
    
    # Crear nuevo contenedor
    success = run_command(
        'docker run --name trading_db -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -e POSTGRES_DB=trading_db -p 5432:5432 -d postgres:13',
        'Creando contenedor PostgreSQL'
    )
    
    if not success:
        print("❌ No se pudo crear el contenedor")
        return False
    
    # Esperar a que PostgreSQL esté listo
    print("⏳ Esperando a que PostgreSQL esté listo (30 segundos)...")
    time.sleep(30)
    
    # Verificar que el contenedor está corriendo
    success, output = run_command('docker ps', 'Verificando contenedor')
    
    if success and 'trading_db' in output:
        print("✅ Contenedor PostgreSQL está corriendo")
        return True
    else:
        print("❌ El contenedor no está corriendo")
        return False

def test_connection():
    """Probar la conexión a PostgreSQL"""
    print("\n🔌 Probando conexión a PostgreSQL...")
    
    try:
        import psycopg2
        
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="trading_db",
            user="user",
            password="password"
        )
        conn.close()
        print("✅ Conexión exitosa")
        return True
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def main():
    print("🔧 Solucionador de Problemas de Docker y PostgreSQL")
    print("=" * 60)
    
    if not check_docker_status():
        print("\n❌ No se puede continuar sin Docker funcionando")
        return
    
    if not setup_postgresql():
        print("\n❌ No se pudo configurar PostgreSQL")
        return
    
    if not test_connection():
        print("\n❌ La conexión a PostgreSQL falló")
        return
    
    print("\n🎉 ¡Todo configurado correctamente!")
    print("\n📝 Siguientes pasos:")
    print("1. python init_db.py")
    print("2. python main.py")

if __name__ == "__main__":
    main()