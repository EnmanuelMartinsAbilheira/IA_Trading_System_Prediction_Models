# test_sqlite.py - Script para probar el sistema SQLite
import requests
import time
import subprocess
import sys
import os

def test_server():
    """Probar si el servidor está funcionando"""
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor funcionando")
            return True
        else:
            print(f"❌ Servidor respondió con código {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servidor")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_assets():
    """Probar el endpoint de activos"""
    try:
        response = requests.get("http://localhost:8000/assets", timeout=5)
        if response.status_code == 200:
            assets = response.json()
            print(f"✅ Activos disponibles: {len(assets)}")
            for asset in assets[:3]:  # Mostrar primeros 3
                print(f"   - {asset['simbolo']}: {asset['nombre']}")
            return True
        else:
            print(f"❌ Error en /assets: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error al probar /assets: {e}")
        return False

def test_prediction():
    """Probar el endpoint de predicción"""
    try:
        response = requests.get("http://localhost:8000/predict?symbol=AAPL&asset_type=stock&model_type=lstm", timeout=30)
        if response.status_code == 200:
            prediction = response.json()
            print(f"✅ Predicción para AAPL:")
            print(f"   - Precio actual: ${prediction['current_price']:.2f}")
            print(f"   - Precio predicho: ${prediction['predicted_price']:.2f}")
            print(f"   - Recomendación: {prediction['recommendation']}")
            print(f"   - Confianza: {prediction['confidence']:.2%}")
            return True
        else:
            print(f"❌ Error en /predict: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error al probar /predict: {e}")
        return False

def main():
    print("🧪 Probando Sistema de Trading con IA - SQLite")
    print("=" * 50)
    
    # Verificar si el servidor está corriendo
    if not test_server():
        print("\n🚀 Iniciando servidor...")
        # Iniciar el servidor en segundo plano
        import threading
        import time
        
        def run_server():
            subprocess.run([sys.executable, "main_sqlite.py"])
        
        server_thread = threading.Thread(target=run_server)
        server_thread.daemon = True
        server_thread.start()
        
        # Esperar a que el servidor inicie
        print("⏳ Esperando a que el servidor inicie...")
        time.sleep(10)
        
        # Probar nuevamente
        if not test_server():
            print("❌ No se pudo iniciar el servidor")
            return
    
    # Probar endpoints
    print("\n📋 Probando endpoints...")
    
    if test_assets():
        print("✅ Endpoint /assets funciona")
    
    if test_prediction():
        print("✅ Endpoint /predict funciona")
    
    print("\n🎉 Pruebas completadas!")
    print("\n🌐 Accede a:")
    print("   - API: http://localhost:8000")
    print("   - Documentación: http://localhost:8000/docs")
    print("   - Frontend: http://localhost:3000 (ejecuta: cd frontend && npm start)")

if __name__ == "__main__":
    main()