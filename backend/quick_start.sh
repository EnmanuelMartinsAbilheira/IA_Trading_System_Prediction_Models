#!/bin/bash

# 🚀 Inicio Rápido del Sistema de Trading con IA (Linux/Mac)

echo "🚀 Inicio Rápido del Sistema de Trading con IA"
echo "========================================"

echo ""
echo "📋 Este script configurará todo automáticamente"
echo "Presiona Enter para continuar o Ctrl+C para cancelar..."
read

echo ""
echo "🗄️ Paso 1: Configurando PostgreSQL..."
python3 setup_postgresql.py

echo ""
echo "⏳ Esperando a que PostgreSQL esté listo..."
sleep 5

echo ""
echo "🔌 Paso 2: Probando conexión..."
python3 test_db_connection.py

echo ""
echo "🏗️ Paso 3: Inicializando base de datos..."
python3 init_db.py

echo ""
echo "🚀 Paso 4: Iniciando servidor backend..."
echo "El servidor se iniciará y se mantendrá en ejecución"
echo "Presiona Ctrl+C para detenerlo"
echo ""

python3 main.py

echo ""
echo "🎉 ¡Sistema configurado!"
echo ""
echo "📝 Para usar el sistema:"
echo "1. Backend: python3 main.py"
echo "2. Frontend: cd frontend && npm start"
echo "3. Acceder a: http://localhost:3000"