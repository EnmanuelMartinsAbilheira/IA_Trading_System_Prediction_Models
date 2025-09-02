# install_deps.py
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
            return True
        else:
            print(f"❌ Error")
            if result.stderr.strip():
                print(f"Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ Excepción: {e}")
        return False

def main():
    print("📦 Instalador de Dependencias Faltantes")
    print("=" * 40)
    
    # Lista de dependencias críticas que podrían faltar
    critical_deps = [
        "PyJWT",
        "python-dotenv",
        "psycopg2-binary",
        "sqlalchemy",
        "fastapi",
        "uvicorn"
    ]
    
    installed_count = 0
    
    for dep in critical_deps:
        print(f"\n🔍 Verificando: {dep}")
        
        # Intentar importar el módulo
        try:
            __import__(dep.lower().replace('-', '_'))
            print(f"✅ {dep} ya está instalado")
            installed_count += 1
        except ImportError:
            print(f"❌ {dep} no está instalado")
            
            # Instalar la dependencia
            success = run_command(f"pip install {dep}", f"Instalando {dep}")
            
            if success:
                print(f"✅ {dep} instalado correctamente")
                installed_count += 1
            else:
                print(f"❌ No se pudo instalar {dep}")
    
    print(f"\n📊 Resumen: {installed_count}/{len(critical_deps)} dependencias instaladas")
    
    if installed_count == len(critical_deps):
        print("\n🎉 Todas las dependencias críticas están instaladas")
        print("\n📝 Siguientes pasos:")
        print("1. python setup_postgresql.py  # Configurar PostgreSQL")
        print("2. python test_db_connection.py # Probar conexión")
        print("3. python init_db.py            # Inicializar base de datos")
        print("4. python main.py               # Iniciar servidor")
    else:
        print(f"\n⚠️  Faltan {len(critical_deps) - installed_count} dependencias críticas")
        print("Por favor, instala las dependencias faltantes manualmente:")
        for dep in critical_deps:
            print(f"   pip install {dep}")

if __name__ == "__main__":
    main()