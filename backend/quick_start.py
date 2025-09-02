# quick_start.py
import subprocess
import time
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

def quick_setup():
    """Configuración rápida completa del sistema"""
    print("🚀 Configuración Rápida del Sistema de Trading con IA")
    print("=" * 70)
    
    steps = [
        ("Verificando Docker", 'docker --version'),
        ("Deteniendo contenedor existente", 'docker stop trading_db'),
        ("Eliminando contenedor existente", 'docker rm trading_db'),
        ("Esperando...", 'timeout 3'),
        ("Creando nuevo contenedor PostgreSQL", 'docker run --name trading_db -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -e POSTGRES_DB=trading_db -p 5432:5432 -d postgres:13'),
        ("Esperando a que PostgreSQL esté listo", 'timeout 30'),
        ("Verificando contenedor", 'docker ps | findstr trading_db'),
        ("Probando conexión", 'python test_db_connection.py'),
        ("Inicializando base de datos", 'python init_db.py'),
        ("Iniciando backend", 'python main.py')
    ]
    
    completed_steps = 0
    
    for step_name, command in steps:
        print(f"\n📋 Paso {completed_steps + 1}/{len(steps)}: {step_name}")
        print("-" * 50)
        
        if command.startswith('python'):
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
        else:
            # Para comandos del sistema
            if run_command(command, step_name):
                completed_steps += 1
            else:
                print(f"❌ Fallo en {step_name}")
                break
        
        # Pausa especial después de crear el contenedor
        if "Creando nuevo contenedor PostgreSQL" in step_name:
            print("\n⏳ Esto puede tardar hasta 30 segundos...")
            time.sleep(30)
    
    print(f"\n📊 Resumen: {completed_steps}/{len(steps)} pasos completados")
    
    if completed_steps == len(steps):
        print("\n🎉 ¡Sistema configurado exitosamente!")
        print("\n🌐 Accede a:")
        print("  - Backend: http://localhost:8000")
        print("  - Documentación API: http://localhost:8000/docs")
        print("  - Frontend: http://localhost:3000 (inicia con: cd frontend && npm start)")
    else:
        print(f"\n❌ La configuración se detuvo en el paso {completed_steps + 1}")
        print("\n💡 Puedes continuar manualmente:")
        print("1. python setup_postgresql.py")
        print("2. python test_db_connection.py")
        print("3. python init_db.py")
        print("4. python main.py")

def main():
    print("⚠️  Advertencia: Este script realizará una configuración completa del sistema.")
    print("   Eliminará cualquier contenedor PostgreSQL existente y creará uno nuevo.")
    
    response = input("\n¿Estás seguro de continuar? (escribe 'si' para continuar): ")
    
    if response.lower() == 'si':
        quick_setup()
    else:
        print("❌ Operación cancelada")

if __name__ == "__main__":
    main()