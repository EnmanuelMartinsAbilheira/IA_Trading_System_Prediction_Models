# start_sqlite.py - Script simple para iniciar con SQLite
import subprocess
import sys
import os

def main():
    print("🚀 Iniciando Sistema de Trading con IA - SQLite")
    print("=" * 50)
    
    # Verificar si la base de datos existe
    if not os.path.exists("trading.db"):
        print("📋 La base de datos no existe. Inicializando...")
        result = subprocess.run([sys.executable, "init_sqlite.py"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Base de datos inicializada")
        else:
            print("❌ Error al inicializar la base de datos")
            print(result.stderr)
            return
    
    print("🚀 Iniciando servidor...")
    print("🌐 El servidor estará disponible en:")
    print("   - http://localhost:8000")
    print("   - http://localhost:8000/docs")
    print("🛑 Presiona Ctrl+C para detener")
    print()
    
    # Iniciar el servidor
    try:
        subprocess.run([sys.executable, "main_sqlite.py"])
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido")

if __name__ == "__main__":
    main()