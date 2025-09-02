# choose_database.py - Elegir entre PostgreSQL y SQLite
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

def check_docker():
    """Verificar si Docker está disponible y funcionando"""
    print("🐳 Verificando Docker...")
    
    success = run_command('docker --version', 'Verificando Docker')
    if not success:
        print("❌ Docker no está instalado")
        return False
    
    success = run_command('docker ps', 'Verificando si Docker responde')
    if not success:
        print("❌ Docker no está respondiendo")
        print("💡 Asegúrate de que Docker Desktop esté iniciado")
        return False
    
    print("✅ Docker está funcionando")
    return True

def setup_postgresql():
    """Configurar PostgreSQL"""
    print("\n🗄️ Configurando PostgreSQL...")
    
    # Detener y eliminar contenedor existente
    run_command('docker stop trading_db', 'Deteniendo contenedor existente')
    run_command('docker rm trading_db', 'Eliminando contenedor existente')
    
    time.sleep(2)
    
    # Crear nuevo contenedor
    success = run_command(
        'docker run --name trading_db -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -e POSTGRES_DB=trading_db -p 5432:5432 -d postgres:13',
        'Creando contenedor PostgreSQL'
    )
    
    if not success:
        print("❌ No se pudo crear el contenedor")
        return False
    
    print("⏳ Esperando a que PostgreSQL esté listo (30 segundos)...")
    time.sleep(30)
    
    # Verificar que el contenedor está corriendo
    success, output = run_command('docker ps', 'Verificando contenedor')
    
    if success and 'trading_db' in output:
        print("✅ PostgreSQL está listo")
        return True
    else:
        print("❌ PostgreSQL no está listo")
        return False

def test_postgresql():
    """Probar conexión a PostgreSQL"""
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
        print("✅ Conexión a PostgreSQL exitosa")
        return True
    except Exception as e:
        print(f"❌ Error de conexión a PostgreSQL: {e}")
        return False

def setup_sqlite():
    """Configurar SQLite"""
    print("\n💾 Configurando SQLite...")
    
    success = run_command('python init_sqlite.py', 'Inicializando base de datos SQLite')
    
    if success:
        print("✅ SQLite está listo")
        return True
    else:
        print("❌ No se pudo configurar SQLite")
        return False

def main():
    print("🗄️ Selector de Base de Datos para el Sistema de Trading con IA")
    print("=" * 70)
    
    print("\n📋 Opciones disponibles:")
    print("1. PostgreSQL (recomendado para producción)")
    print("   - Requiere Docker")
    print("   - Más robusto y escalable")
    print("   - Configuración más compleja")
    print()
    print("2. SQLite (recomendado para desarrollo)")
    print("   - No requiere Docker")
    print("   - Fácil y rápido")
    print("   - Perfecto para aprender y probar")
    
    while True:
        try:
            choice = input("\n🤔 Elige una opción (1 o 2): ")
            
            if choice == '1':
                print("\n🚀 Has elegido PostgreSQL")
                print("Esta opción requiere Docker Desktop funcionando")
                
                # Verificar Docker
                if not check_docker():
                    print("\n❌ Docker no está disponible")
                    print("💡 Soluciones:")
                    print("1. Instala Docker Desktop")
                    print("2. Inicia Docker Desktop desde el menú de inicio")
                    print("3. Espera 1-2 minutos a que inicie completamente")
                    print("4. Vuelve a ejecutar este script")
                    print("\n🔄 O puedes elegir SQLite (opción 2) que es más simple")
                    continue
                
                # Configurar PostgreSQL
                if not setup_postgresql():
                    print("\n❌ No se pudo configurar PostgreSQL")
                    continue
                
                # Probar conexión
                if not test_postgresql():
                    print("\n❌ La conexión a PostgreSQL falló")
                    continue
                
                print("\n🎉 ¡PostgreSQL configurado exitosamente!")
                print("\n📝 Siguientes pasos:")
                print("1. python init_db.py")
                print("2. python main.py")
                print("3. Acceder a http://localhost:8000")
                
                break
                
            elif choice == '2':
                print("\n💾 Has elegido SQLite")
                print("Esta opción es simple y no requiere Docker")
                
                # Configurar SQLite
                if not setup_sqlite():
                    print("\n❌ No se pudo configurar SQLite")
                    continue
                
                print("\n🎉 ¡SQLite configurado exitosamente!")
                print("\n📝 Siguientes pasos:")
                print("1. python main_sqlite.py")
                print("2. Acceder a http://localhost:8000")
                print("3. Documentación: http://localhost:8000/docs")
                
                break
                
            else:
                print("❌ Opción no válida. Elige 1 o 2")
                
        except KeyboardInterrupt:
            print("\n❌ Operación cancelada")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            continue

if __name__ == "__main__":
    main()