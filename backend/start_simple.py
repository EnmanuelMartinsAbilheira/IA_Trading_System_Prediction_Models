# start_simple.py - Inicio simple sin caracteres especiales
import subprocess
import sys
import time

def run_command(command, description=""):
    """Ejecutar un comando y mostrar el resultado"""
    print(f"\n{description}...")
    print(f"Comando: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Exito!")
            if result.stdout.strip():
                print(f"Salida: {result.stdout.strip()}")
            return True
        else:
            print(f"Error!")
            if result.stderr.strip():
                print(f"Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"Excepcion: {e}")
        return False

def main():
    print("Inicio Simple del Sistema de Trading con IA")
    print("=====================================")
    
    print("Este script te ayudara a iniciar el sistema con SQLite")
    print("SQLite es simple y no requiere Docker")
    
    response = input("\n¿Estas seguro de continuar? (escribe 'si' para continuar): ")
    
    if response.lower() != 'si':
        print("Operacion cancelada")
        return
    
    # Paso 1: Inicializar base de datos
    print("\nPaso 1: Inicializando base de datos SQLite...")
    if not run_command('python init_sqlite_simple.py', 'Inicializando base de datos'):
        print("No se pudo inicializar la base de datos")
        return
    
    # Paso 2: Iniciar servidor
    print("\nPaso 2: Iniciando servidor backend...")
    print("El servidor se iniciara y se mantendra en ejecucion")
    print("Presiona Ctrl+C para detenerlo")
    print()
    
    try:
        subprocess.run([sys.executable, 'main_sqlite.py'])
    except KeyboardInterrupt:
        print("\nServidor detenido")
    
    print("\nSistema configurado exitosamente!")
    print("Accede a:")
    print("  - Backend: http://localhost:8000")
    print("  - Documentacion: http://localhost:8000/docs")
    print("  - Frontend: http://localhost:3000 (ejecuta: cd frontend && npm start)")

if __name__ == "__main__":
    main()