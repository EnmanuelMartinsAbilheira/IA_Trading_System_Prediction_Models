# install_missing_deps.py
import subprocess
import sys

def install_package(package):
    try:
        print(f"Instalando {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} instalado correctamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al instalar {package}: {e}")
        return False

def main():
    print("Instalando dependencias faltantes...")
    
    # Lista de paquetes faltantes
    missing_packages = [
        "PyJWT",  # Para el módulo jwt
        "python-dotenv",  # Para variables de entorno
    ]
    
    success_count = 0
    for package in missing_packages:
        if install_package(package):
            success_count += 1
    
    print(f"\n📊 Resumen: {success_count}/{len(missing_packages)} paquetes instalados correctamente")
    
    if success_count == len(missing_packages):
        print("🎉 Todas las dependencias faltantes han sido instaladas")
        print("Ahora puedes ejecutar:")
        print("1. python test_db_connection.py  # Para probar la conexión a la DB")
        print("2. python init_db_updated.py     # Para inicializar la base de datos")
        print("3. python main.py                # Para iniciar el servidor")
    else:
        print("⚠️  Algunos paquetes no pudieron ser instalados. Revisa los errores above.")

if __name__ == "__main__":
    main()