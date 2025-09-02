# create_postgresql_user.py
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
    print("🔧 Configurando manualmente PostgreSQL...")
    
    # Conectarse al contenedor y configurar el usuario
    commands = [
        # Entrar al contenedor y acceder a PostgreSQL
        'docker exec -it trading_db bash -c "echo \\"CREATE USER user WITH PASSWORD \'password\';\\" | psql -U postgres"',
        'docker exec -it trading_db bash -c "echo \\"CREATE DATABASE trading_db OWNER user;\\" | psql -U postgres"',
        'docker exec -it trading_db bash -c "echo \\"GRANT ALL PRIVILEGES ON DATABASE trading_db TO user;\\" | psql -U postgres"',
        'docker exec -it trading_db bash -c "echo \\"ALTER USER user CREATEDB;\\" | psql -U postgres"'
    ]
    
    for cmd in commands:
        run_command(cmd)
        time.sleep(2)

if __name__ == "__main__":
    main()