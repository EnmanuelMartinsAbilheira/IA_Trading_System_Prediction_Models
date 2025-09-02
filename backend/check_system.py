# check_system.py
import subprocess
import sys

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
            return True, result.stdout
        else:
            print(f"❌ Error")
            if result.stderr.strip():
                print(f"Error: {result.stderr.strip()}")
            return False, result.stderr
    except Exception as e:
        print(f"❌ Excepción: {e}")
        return False, str(e)

def check_python():
    """Verificar instalación de Python"""
    print("🐍 Verificando Python...")
    
    success, output = run_command(f'{sys.executable} --version', 'Verificando versión de Python')
    if success:
        print(f"✅ Python: {output.strip()}")
        return True
    return False

def check_pip():
    """Verificar pip"""
    print("\n📦 Verificando pip...")
    
    success, output = run_command(f'{sys.executable} -m pip --version', 'Verificando pip')
    if success:
        print(f"✅ pip: {output.strip()}")
        return True
    return False

def check_docker():
    """Verificar Docker"""
    print("\n🐳 Verificando Docker...")
    
    success, output = run_command('docker --version', 'Verificando Docker')
    if success:
        print(f"✅ Docker: {output.strip()}")
        return True
    return False

def check_postgresql_container():
    """Verificar contenedor PostgreSQL"""
    print("\n🗄️ Verificando contenedor PostgreSQL...")
    
    success, output = run_command('docker ps -a', 'Listando contenedores')
    
    if 'trading_db' in output:
        print("✅ Contenedor 'trading_db' existe")
        
        success, output = run_command('docker ps', 'Verificando contenedores en ejecución')
        if 'trading_db' in output:
            print("✅ Contenedor 'trading_db' está en ejecución")
            return True
        else:
            print("⚠️  Contenedor 'trading_db' existe pero no está en ejecución")
            return False
    else:
        print("❌ Contenedor 'trading_db' no existe")
        return False

def check_python_packages():
    """Verificar paquetes Python necesarios"""
    print("\n📚 Verificando paquetes Python...")
    
    required_packages = [
        'fastapi', 'uvicorn', 'sqlalchemy', 'psycopg2',
        'pandas', 'numpy', 'tensorflow', 'xgboost',
        'yfinance', 'ccxt', 'PyJWT'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} (faltante)")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Paquetes faltantes: {', '.join(missing_packages)}")
        print(f"   Instalar con: pip install {' '.join(missing_packages)}")
        return False
    else:
        print("\n✅ Todos los paquetes necesarios están instalados")
        return True

def check_ports():
    """Verificar puertos necesarios"""
    print("\n🔌 Verificando puertos...")
    
    # Verificar puerto 5432 (PostgreSQL)
    success, output = run_command('netstat -an | findstr :5432', 'Verificando puerto 5432')
    if success and 'LISTENING' in output:
        print("✅ Puerto 5432 (PostgreSQL) está disponible")
    else:
        print("⚠️  Puerto 5432 (PostgreSQL) no está en uso")
    
    # Verificar puerto 8000 (Backend)
    success, output = run_command('netstat -an | findstr :8000', 'Verificando puerto 8000')
    if success and 'LISTENING' in output:
        print("⚠️  Puerto 8000 (Backend) está en uso")
    else:
        print("✅ Puerto 8000 (Backend) está disponible")
    
    # Verificar puerto 3000 (Frontend)
    success, output = run_command('netstat -an | findstr :3000', 'Verificando puerto 3000')
    if success and 'LISTENING' in output:
        print("⚠️  Puerto 3000 (Frontend) está en uso")
    else:
        print("✅ Puerto 3000 (Frontend) está disponible")

def main():
    print("🔍 Verificación del Sistema de Trading con IA")
    print("=" * 60)
    
    checks = [
        ("Python", check_python),
        ("pip", check_pip),
        ("Docker", check_docker),
        ("Contenedor PostgreSQL", check_postgresql_container),
        ("Paquetes Python", check_python_packages),
        ("Puertos", check_ports)
    ]
    
    results = []
    
    for check_name, check_function in checks:
        print(f"\n{'='*20} {check_name} {'='*20}")
        result = check_function()
        results.append((check_name, result))
    
    print("\n" + "="*60)
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("="*60)
    
    passed = 0
    for check_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{check_name:.<30} {status}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(results)} verificaciones pasaron")
    
    if passed == len(results):
        print("\n🎉 ¡Todo está listo para comenzar!")
        print("\n📝 Siguientes pasos:")
        print("1. python test_db_connection.py")
        print("2. python init_db.py")
        print("3. python main.py")
    else:
        print(f"\n⚠️  {len(results) - passed} verificaciones fallaron")
        print("\n💡 Soluciones:")
        print("- Si Docker falló: Instala Docker Desktop")
        print("- Si el contenedor falló: Ejecuta 'python setup_postgresql.py'")
        print("- Si paquetes faltan: Ejecuta 'pip install [paquetes_faltantes]'")
        print("- Si puertos están en uso: Cierra las aplicaciones que usan esos puertos")

if __name__ == "__main__":
    main()