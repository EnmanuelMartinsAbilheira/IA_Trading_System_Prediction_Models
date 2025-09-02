# simple_postgresql_fix.py
import subprocess
import time

def run_command(command):
    print(f"Ejecutando: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ Éxito: {result.stdout}")
        return True
    else:
        print(f"❌ Error: {result.stderr}")
        return False

def main():
    print("🔧 Solución Simple para PostgreSQL")
    print("=" * 40)
    
    # Opción 1: Recrear el contenedor (la solución más confiable)
    print("\n🔄 Opción 1: Recrear contenedor PostgreSQL...")
    
    commands = [
        'docker stop trading_db',
        'docker rm trading_db', 
        'timeout 2',
        'docker run --name trading_db -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -e POSTGRES_DB=trading_db -p 5432:5432 -d postgres:13'
    ]
    
    for cmd in commands:
        run_command(cmd)
        time.sleep(2)
    
    print("\n⏳ Esperando a que PostgreSQL esté listo (20 segundos)...")
    time.sleep(20)
    
    # Verificar que el contenedor está corriendo
    run_command('docker ps | grep trading_db', 'Verificando contenedor')
    
    # Probar conexión
    print("\n🧪 Probando conexión...")
    try:
        import psycopg2
        
        conn = psycopg2.connect(
            host="localhost",
            port="5432", 
            database="trading_db",
            user="user",
            password="password"
        )
        print("✅ ¡Conexión exitosa!")
        conn.close()
        
        print("\n🎉 ¡PostgreSQL está funcionando!")
        print("Ahora ejecuta:")
        print("python init_db_updated.py")
        print("python main.py")
        
    except Exception as e:
        print(f"❌ La conexión sigue fallando: {e}")
        print("\n💡 Intenta esto manualmente:")
        print("1. docker stop trading_db")
        print("2. docker rm trading_db") 
        print("3. docker run --name trading_db -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -e POSTGRES_DB=trading_db -p 5432:5432 -d postgres:13")
        print("4. Espera 20 segundos")
        print("5. python test_db_connection_fixed.py")

if __name__ == "__main__":
    main()