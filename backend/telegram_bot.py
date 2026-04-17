import telebot
import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()

RETAIL_CRM_URL = os.getenv('RETAIL_CRM_URL')
API_KEY = os.getenv('RETAIL_CRM_API_KEY')
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

bot = telebot.TeleBot(BOT_TOKEN)

# Множество для хранения ID уже отправленных заказов
sent_orders = set()

def check_orders():
    print("Проверка заказов...")
    
    url = f"{RETAIL_CRM_URL}/api/v5/orders"
    params = {
        'apiKey': API_KEY,
        'limit': 100
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        data = response.json()
        orders = data.get('orders', [])
        
        for order in orders:
            summ = order.get('summ', 0)
            order_id = order.get('externalId')
            
            if summ > 50000 and order_id not in sent_orders:
                msg = f"**Крупный заказ**\nКлиент: {order.get('firstName')}\nСумма: {summ} ₸\nСтатус: {order.get('status')}"
                bot.send_message(CHAT_ID, msg, parse_mode='Markdown')
                sent_orders.add(order_id)
                print(f"Уведомление отправлено о заказе {order_id}")
            elif order_id in sent_orders:
                print(f"Заказ {order_id} уже был отправлен ранее, пропускаем")
                
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == '__main__':
    print("Бот запущен...")
    while True:
        check_orders()
        time.sleep(60)