trading-ai-system/
├── backend/
│   ├── main.py
│   ├── prediction_model.py
│   ├── backtesting.py
│   ├── notifications.py
│   ├── risk_management.py
│   ├── simulator.py
│   ├── init_db.py (nuevo archivo)
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── App.js
│   │   ├── App.css
│   │   └── index.js
│   ├── package.json
│   └── Dockerfile
├── models/
├── backtest_results/
├── docker-compose.yml
└── README.md

# Crear estructura de directorios principal
mkdir trading-ai-system
cd trading-ai-system
mkdir -p backend frontend models backtest_results

# Configurar Backend
cd backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Crear archivos principales
touch main.py prediction_model.py backtesting.py notifications.py risk_management.py simulator.py Dockerfile .env

# Crear requirements.txt
cat > requirements.txt << EOF
fastapi==0.68.0
uvicorn==0.15.0
sqlalchemy==1.4.23
pydantic==1.8.2
python-jose==3.3.0
passlib==1.7.4
bcrypt==3.2.0
python-multipart==0.0.5
tensorflow==2.6.0
numpy==1.19.5
pandas==1.3.3
scikit-learn==0.24.2
yfinance==0.1.63
ccxt==1.55.44
psycopg2-binary==2.9.1
xgboost==1.5.0
matplotlib==3.4.3
requests==2.26.0
EOF

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cat > .env << EOF
DATABASE_URL=postgresql://user:password@db:5432/trading_db
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
FROM_EMAIL=tu_email@gmail.com
EMAIL_PASSWORD=tu_contraseña
TELEGRAM_BOT_TOKEN=tu_token_bot
TELEGRAM_CHAT_ID=tu_chat_id
WEBHOOK_URL=tu_webhook_url
EOF

# Volver al directorio raíz
cd ..

# Configurar Frontend
cd frontend

# Crear aplicación React
npx create-react-app . --template minimal

# Instalar dependencias adicionales
npm install axios

# Reemplazar App.js y App.css
rm src/App.js src/App.css
touch src/App.js src/App.css

# Crear Dockerfile
cat > Dockerfile << EOF
FROM node:16-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
RUN npm install -g serve
EXPOSE 3000
CMD ["serve", "-s", "build", "-l", "3000"]
EOF

# Volver al directorio raíz
cd ..

# Crear docker-compose.yml
cat > docker-compose.yml << EOF
version: '3.8'

services:
  db:
    image: postgres:13
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: trading_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/trading_db
    volumes:
      - ./backend:/app
      - ./models:/app/models
      - ./backtest_results:/app/backtest_results

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  postgres_data:
EOF

# Copiar el contenido de los archivos principales desde las respuestas anteriores
# (main.py, prediction_model.py, backtesting.py, notifications.py, risk_management.py, simulator.py, App.js, App.css)

# Construir y levantar los contenedores
docker-compose up --build