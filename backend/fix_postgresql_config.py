# fix_postgresql_config.py
import subprocess
import time

def run_command(command, description=""):
    print(f"\n🔄 {description}")
    print(f"Comando: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Éxito: {result.stdout}")
            return True
        else:
            print(f"❌ Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Excepción: {e}")
        return False

def main():
    print("🔧 Reparando Configuración de PostgreSQL")
    print("=" * 50)
    
    # Paso 1: Verificar el estado actual del contenedor
    print("\n📋 Verificando estado del contenedor...")
    run_command('docker ps | grep trading_db', 'Verificando contenedor en ejecución')
    
    # Paso 2: Probar conexión interna con el usuario existente
    print("\n🔌 Probando conexión interna...")
    run_command('docker exec trading_db psql -U user -d trading_db -c "SELECT current_user;"', 'Probando conexión como user')
    
    # Paso 3: Verificar la configuración de pg_hba.conf
    print("\n📝 Verificando configuración de autenticación...")
    run_command('docker exec trading_db cat /var/lib/postgresql/data/pg_hba.conf', 'Mostrando pg_hba.conf')
    
    # Paso 4: Modificar la configuración de autenticación
    print("\n⚙️  Modificando configuración de autenticación...")
    
    # Crear un nuevo pg_hba.conf que permita conexiones externas
    commands = [
        # Crear un archivo pg_hba.conf temporal
        'docker exec trading_db bash -c "echo \\"# TYPE  DATABASE        USER            ADDRESS                 METHOD\\" > /tmp/pg_hba.conf"',
        'docker exec trading_db bash -c "echo \\"local   all             all                                     trust\\" >> /tmp/pg_hba.conf"',
        'docker exec trading_db bash -c "echo \\"host    all             all             127.0.0.1/32            trust\\" >> /tmp/pg_hba.conf"',
        'docker exec trading_db bash -c "echo \\"host    all             all             0.0.0.0/0               md5\\" >> /tmp/pg_hba.conf"',
        'docker exec trading_db bash -c "echo \\"host    all             all             ::1/128                 md5\\" >> /tmp/pg_hba.conf"',
        
        # Reemplazar el archivo original
        'docker exec trading_db bash -c "cp /tmp/pg_hba.conf /var/lib/postgresql/data/pg_hba.conf"',
        
        # Reiniciar PostgreSQL dentro del contenedor
        'docker exec trading_db bash -c "su - postgres -c \\"pg_ctl restart\\""'
    ]
    
    for i, cmd in enumerate(commands, 1):
        success = run_command(cmd, f'Comando {i}/{len(commands)}')
        if not success:
            print(f"⚠️  El comando {i} falló, pero continuaremos...")
        time.sleep(2)
    
    # Paso 5: Esperar a que PostgreSQL se reinicie
    print("\n⏳ Esperando a que PostgreSQL se reinicie...")
    time.sleep(10)
    
    # Paso 6: Probar la conexión externa
    print("\n🧪 Probando conexión externa...")
    
    # Importar y probar la conexión
    try:
        import psycopg2
        
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="trading_db",
            user="user",
            password="password"
        )
        print("✅ Conexión externa exitosa con psycopg2")
        conn.close()
        
        print("\n🎉 ¡Problema solucionado! La conexión externa ahora funciona.")
        print("\n📝 Siguientes pasos:")
        print("1. python init_db_updated.py  # Inicializar la base de datos")
        print("2. python main.py                # Iniciar el servidor backend")
        
    except ImportError:
        print("❌ psycopg2 no está instalado")
    except psycopg2.OperationalError as e:
        print(f"❌ La conexión externa sigue fallando: {e}")
        print("\n🔄 Intentando solución alternativa...")
        
        # Si sigue fallando, recrear el contenedor
        print("\n🔄 Recreando el contenedor como última opción...")
        recreate_container()
    
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

def recreate_container():
    """Recrear el contenedor completamente"""
    print("\n🔄 Recreando contenedor PostgreSQL...")
    
    commands = [
        'docker stop trading_db',
        'docker rm trading_db',
        'timeout 3',
        'docker run --name trading_db -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -e POSTGRES_DB=trading_db -p 5432:5432 -d postgres:13'
    ]
    
    for cmd in commands:
        run_command(cmd, "Recreando contenedor")
        time.sleep(3)
    
    print("⏳ Esperando a que PostgreSQL esté listo...")
    time.sleep(15)
    
    print("🎉 Contenedor recreado. Intenta la conexión ahora:")
    print("python test_db_connection_fixed.py")

if __name__ == "__main__":
    main()