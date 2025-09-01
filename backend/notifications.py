# notifications.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import os
from datetime import datetime

class NotificationManager:
    def __init__(self, email_config=None, telegram_config=None, webhook_url=None):
        self.email_config = email_config
        self.telegram_config = telegram_config
        self.webhook_url = webhook_url
    
    def send_email(self, subject, message, to_email):
        """Enviar notificación por email"""
        if not self.email_config:
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config['from_email']
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'plain'))
            
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['from_email'], self.email_config['password'])
            
            text = msg.as_string()
            server.sendmail(self.email_config['from_email'], to_email, text)
            server.quit()
            
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def send_telegram(self, message):
        """Enviar notificación por Telegram"""
        if not self.telegram_config:
            return False
        
        try:
            bot_token = self.telegram_config['bot_token']
            chat_id = self.telegram_config['chat_id']
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(url, json=payload)
            return response.status_code == 200
        except Exception as e:
            print(f"Error sending Telegram message: {e}")
            return False
    
    def send_webhook(self, data):
        """Enviar notificación por webhook"""
        if not self.webhook_url:
            return False
        
        try:
            response = requests.post(self.webhook_url, json=data)
            return response.status_code == 200
        except Exception as e:
            print(f"Error sending webhook: {e}")
            return False
    
    def send_prediction_notification(self, prediction, user_preferences):
        """Enviar notificación de predicción según las preferencias del usuario"""
        symbol = prediction['symbol']
        current_price = prediction['current_price']
        predicted_price = prediction['predicted_price']
        change_percent = prediction['change_percent']
        trend = prediction['trend']
        recommendation = prediction['recommendation']
        confidence = prediction['confidence']
        model = prediction['model']
        
        # Formatear mensaje
        message = f"""
*Predicción de Trading para {symbol}*

- Precio Actual: ${current_price:.2f}
- Precio Predicho: ${predicted_price:.2f}
- Cambio Esperado: {change_percent:.2f}%
- Tendencia: {trend}
- Recomendación: {recommendation}
- Confianza: {confidence:.1%}
- Modelo: {model}
- Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        # Enviar notificaciones según las preferencias del usuario
        notifications_sent = []
        
        if user_preferences.get('email_notifications', False) and user_preferences.get('email'):
            email_sent = self.send_email(
                f"Predicción de Trading para {symbol}",
                message,
                user_preferences['email']
            )
            if email_sent:
                notifications_sent.append('email')
        
        if user_preferences.get('telegram_notifications', False):
            telegram_sent = self.send_telegram(message)
            if telegram_sent:
                notifications_sent.append('telegram')
        
        if user_preferences.get('webhook_notifications', False):
            webhook_sent = self.send_webhook({
                'type': 'prediction',
                'symbol': symbol,
                'current_price': current_price,
                'predicted_price': predicted_price,
                'change_percent': change_percent,
                'trend': trend,
                'recommendation': recommendation,
                'confidence': confidence,
                'model': model,
                'timestamp': datetime.now().isoformat()
            })
            if webhook_sent:
                notifications_sent.append('webhook')
        
        return notifications_sent