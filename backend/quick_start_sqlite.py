# quick_start_sqlite.py - Inicio rápido con SQLite
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

def main():
    print("🚀 Inicio Rápido del Sistema de Trading con IA - SQLite")
    print("=" * 70)
    
    print("\n📋 Este script configurará todo usando SQLite (sin Docker)")
    print("SQLite es mucho más simple y no requiere configuración externa")
    
    response = input("\n¿Estás seguro de continuar? (escribe 'si' para continuar): ")
    
    if response.lower() != 'si':
        print("❌ Operación cancelada")
        return
    
    steps = [
        ("Inicializando base de datos SQLite", "python init_sqlite.py"),
        ("Iniciando servidor backend", "python main_sqlite.py")
    ]
    
    completed_steps = 0
    
    for step_name, command in steps:
        print(f"\n📋 Paso {completed_steps + 1}/{len(steps)}: {step_name}")
        print("-" * 50)
        
        if step_name == "Iniciando servidor backend":
            print("🚀 Iniciando servidor backend...")
            print("El servidor se iniciará y se mantendrá en ejecución")
            print("Presiona Ctrl+C para detenerlo")
            print()
            
            try:
                subprocess.run([sys.executable, 'main_sqlite.py'])
            except KeyboardInterrupt:
                print("\n🛑 Servidor detenido")
            
            completed_steps += 1
        else:
            # Para comandos Python, ejecutar directamente
            try:
                result = subprocess.run([sys.executable, command.split()[1]], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"✅ {step_name} completado")
                    completed_steps += 1
                else:
                    print(f"❌ Error en {step_name}")
                    print(f"Error: {result.stderr}")
                    break
            except Exception as e:
                print(f"❌ Excepción en {step_name}: {e}")
                break
    
    print(f"\n📊 Resumen: {completed_steps}/{len(steps)} pasos completados")
    
    if completed_steps == len(steps):
        print("\n🎉 ¡Sistema configurado exitosamente con SQLite!")
        print("\n🌐 Accede a:")
        print("  - Backend: http://localhost:8000")
        print("  - Documentación API: http://localhost:8000/docs")
        print("  - Frontend: http://localhost:3000 (ejecuta: cd frontend && npm start)")
    else:
        print(f"\n❌ La configuración se detuvo en el paso {completed_steps + 1}")
        print("\n💡 Puedes continuar manualmente:")
        print("1. python init_sqlite.py")
        print("2. python main_sqlite.py")

if __name__ == "__main__":
    main()