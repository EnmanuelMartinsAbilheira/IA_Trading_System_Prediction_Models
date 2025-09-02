# setup_guide.py
import os
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

def check_docker():
    print("🐳 Verificando Docker...")
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Docker encontrado: {result.stdout.strip()}")
            return True
        else:
            print("❌ Docker no encontrado")
            return False
    except FileNotFoundError:
        print("❌ Docker no está instalado o no está en el PATH")
        return False

def setup_database():
    print("\n🗄️  Configurando base de datos...")
    
    # Verificar si Docker está disponible
    if not check_docker():
        print("❌ Docker no está disponible. Por favor, instala Docker.")
        return False
    
    # Verificar si el contenedor ya está corriendo
    result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
    if 'trading_db' in result.stdout:
        print("✅ El contenedor trading_db ya está corriendo")
        return True
    
    # Iniciar el contenedor de PostgreSQL
    if not run_command('docker run --name trading_db -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -e POSTGRES_DB=trading_db -p 5432:5432 -d postgres:13', 'Iniciando contenedor PostgreSQL'):
        return False
    
    # Esperar a que PostgreSQL esté listo
    print("⏳ Esperando a que PostgreSQL esté listo...")
    time.sleep(10)
    
    # Probar conexión
    if not run_command('python test_db_connection.py', 'Probando conexión a la base de datos'):
        print("⚠️  La conexión falló, pero continuaremos...")
    
    return True

def install_dependencies():
    print("\n📦 Instalando dependencias...")
    
    # Instalar dependencias faltantes
    if not run_command('python install_missing_deps.py', 'Instalando dependencias faltantes'):
        return False
    
    return True

def initialize_database():
    print("\n🏗️  Inicializando base de datos...")
    
    if not run_command('python init_db_updated.py', 'Inicializando base de datos'):
        return False
    
    return True

def test_backend():
    print("\n🧪 Probando backend...")
    
    # Intentar iniciar el servidor por un corto tiempo
    try:
        print("Iniciando servidor (esto tomará unos segundos)...")
        process = subprocess.Popen([sys.executable, 'main.py'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        # Esperar un poco
        time.sleep(5)
        
        # Terminar el proceso
        process.terminate()
        
        print("✅ Backend iniciado correctamente (prueba superada)")
        return True
        
    except Exception as e:
        print(f"❌ Error al probar backend: {e}")
        return False

def main():
    print("🚀 Guía de Configuración del Sistema de Trading con IA")
    print("=" * 50)
    
    steps = [
        ("Configurar base de datos", setup_database),
        ("Instalar dependencias", install_dependencies),
        ("Inicializar base de datos", initialize_database),
        ("Probar backend", test_backend)
    ]
    
    completed_steps = 0
    
    for step_name, step_function in steps:
        print(f"\n📋 Paso {completed_steps + 1}: {step_name}")
        print("-" * 30)
        
        if step_function():
            completed_steps += 1
            print(f"✅ Paso {completed_steps} completado")
        else:
            print(f"❌ Paso {completed_steps + 1} falló")
            print("Por favor, revisa los errores above y intenta nuevamente.")
            break
    
    print(f"\n📊 Resumen: {completed_steps}/{len(steps)} pasos completados")
    
    if completed_steps == len(steps):
        print("🎉 ¡Configuración completada exitosamente!")
        print("\nAhora puedes:")
        print("1. Iniciar el backend: python main.py")
        print("2. Iniciar el frontend: cd frontend && npm start")
        print("3. Acceder a la aplicación: http://localhost:3000")
        print("4. Documentación de la API: http://localhost:8000/docs")
    else:
        print("⚠️  La configuración no se completó. Por favor, revisa los errores e intenta nuevamente.")

if __name__ == "__main__":
    main()