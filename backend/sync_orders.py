import requests
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# RetailCRM
RETAIL_CRM_URL = os.getenv('RETAIL_CRM_URL')
API_KEY = os.getenv('RETAIL_CRM_API_KEY')

# Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def create_table_in_supabase():
    sql = """
    CREATE TABLE IF NOT EXISTS orders (
        id SERIAL PRIMARY KEY,
        external_id TEXT UNIQUE,
        customer_name TEXT,
        phone TEXT,
        total_summ INTEGER,
        status TEXT,
        created_at TIMESTAMP
    );
    """
    try:
        print("Выполните этот SQL в Supabase SQL Editor один раз перед запуском:")
        print(sql)
    except Exception as e:
        print(e)

def sync_orders():
    url = f"{RETAIL_CRM_URL}/api/v5/orders"
    params = {
        'apiKey': API_KEY,
        'limit': 100
    }
    
    response = requests.get(url, params=params)
    orders_data = response.json()
    
    if not orders_data.get('success'):
        print("Не удалось получить заказы из RetailCRM")
        return

    orders = orders_data.get('orders', [])
    
    # отладка
    for order in orders[:5]:
        print(order.get('externalId'), order.get('summ'))
    # отладка
    
    for order in orders:
        name = f"{order.get('firstName', '')} {order.get('lastName', '')}".strip()
        if not name:
            name = "Unknown"
            
        data = {
            'external_id': order.get('externalId'),
            'customer_name': name,
            'phone': order.get('phone'),
            'total_summ': order.get('summ'),
            'status': order.get('status'),
            'created_at': order.get('createdAt')
        }
        
        try:
            supabase.table('orders').upsert(data, on_conflict='external_id').execute()
        except Exception as e:
            print(f"Ошибка вставки заказа {order.get('externalId')}: {e}")

    print(f"Синхронизировано {len(orders)} заказов")

if __name__ == "__main__":
    sync_orders()