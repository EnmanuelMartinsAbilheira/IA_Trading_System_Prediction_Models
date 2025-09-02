# status_check.py
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

def check_python_deps():
    """Verificar dependencias de Python"""
    print("🐍 Verificando dependencias de Python...")
    
    critical_deps = [
        ("fastapi", "FastAPI"),
        ("sqlalchemy", "SQLAlchemy"),
        ("psycopg2", "psycopg2"),
        ("jwt", "PyJWT"),
        ("dotenv", "python-dotenv"),
        ("uvicorn", "uvicorn"),
        ("pandas", "pandas"),
        ("numpy", "numpy"),
        ("tensorflow", "TensorFlow"),
        ("sklearn", "scikit-learn"),
        ("xgboost", "XGBoost"),
        ("yfinance", "yfinance"),
        ("ccxt", "ccxt")
    ]
    
    ok_count = 0
    for module_name, display_name in critical_deps:
        try:
            __import__(module_name)
            print(f"✅ {display_name}")
            ok_count += 1
        except ImportError:
            print(f"❌ {display_name}")
    
    print(f"\n📊 Dependencias Python: {ok_count}/{len(critical_deps)} OK")
    return ok_count == len(critical_deps)

def check_docker():
    """Verificar Docker"""
    print("\n🐳 Verificando Docker...")
    
    success, output = run_command('docker --version', 'Verificando Docker')
    if not success:
        print("❌ Docker no está instalado")
        return False
    
    success, output = run_command('docker ps', 'Verificando contenedores')
    if not success:
        print("❌ Docker no funciona correctamente")
        return False
    
    print("✅ Docker está funcionando")
    return True

def check_postgresql():
    """Verificar PostgreSQL"""
    print("\n🗄️ Verificando PostgreSQL...")
    
    success, output = run_command('docker ps -a', 'Listando contenedores')
    
    if 'trading_db' in output:
        print("✅ Contenedor 'trading_db' existe")
        
        success, output = run_command('docker ps', 'Verificando si está corriendo')
        if 'trading_db' in output:
            print("✅ Contenedor 'trading_db' está corriendo")
            
            # Probar conexión
            success, output = run_command(
                'docker exec trading_db psql -U user -d trading_db -c "SELECT 1;"',
                'Probando conexión interna'
            )
            
            if success:
                print("✅ Conexión interna funciona")
                return True
            else:
                print("❌ Conexión interna falla")
                return False
        else:
            print("❌ Contenedor 'trading_db' no está corriendo")
            return False
    else:
        print("❌ Contenedor 'trading_db' no existe")
        return False

def check_external_connection():
    """Verificar conexión externa a PostgreSQL"""
    print("\n🌐 Verificando conexión externa...")
    
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
        print("✅ Conexión externa funciona")
        return True
    except Exception as e:
        print(f"❌ Conexión externa falla: {e}")
        return False

def main():
    print("🔍 Verificador de Estado del Sistema")
    print("=" * 40)
    
    checks = [
        ("Dependencias Python", check_python_deps),
        ("Docker", check_docker),
        ("PostgreSQL", check_postgresql),
        ("Conexión Externa", check_external_connection)
    ]
    
    results = []
    
    for check_name, check_func in checks:
        print(f"\n📋 {check_name}:")
        print("-" * 30)
        result = check_func()
        results.append((check_name, result))
    
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE ESTADO:")
    print("=" * 50)
    
    all_ok = True
    for check_name, result in results:
        status = "✅ OK" if result else "❌ ERROR"
        print(f"{check_name}: {status}")
        if not result:
            all_ok = False
    
    print("\n" + "=" * 50)
    
    if all_ok:
        print("🎉 ¡Todo está listo para usar!")
        print("\n📝 Siguientes pasos:")
        print("1. python init_db.py  # Inicializar base de datos")
        print("2. python main.py     # Iniciar servidor")
        print("3. cd frontend && npm start  # Iniciar frontend")
    else:
        print("❌ Hay problemas que necesitan solucionarse")
        print("\n💡 Soluciones recomendadas:")
        print("1. Para dependencias: python install_deps.py")
        print("2. Para PostgreSQL: python setup_postgresql.py")
        print("3. Para diagnóstico: python test_db_connection.py")

if __name__ == "__main__":
    main()