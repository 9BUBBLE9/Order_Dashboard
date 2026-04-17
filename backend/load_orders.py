import requests
import json
import os
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

RETAIL_CRM_URL = os.getenv('RETAIL_CRM_URL')
API_KEY = os.getenv('RETAIL_CRM_API_KEY')

def load_orders():
    with open('mock_orders.json', 'r', encoding='utf-8') as f:
        orders = json.load(f)

    url = f"{RETAIL_CRM_URL}/api/v5/orders/create"
    params = {'apiKey': API_KEY}
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    success_count = 0
    for idx, order in enumerate(orders):
        total_summ = sum(item.get('initialPrice', 0) * item.get('quantity', 1) for item in order.get('items', []))
        external_id = order.get('id', f"import_{idx}")

        # товары для RetailCRM
        items = []
        for item in order.get('items', []):
            items.append({
                'productName': item.get('productName'),
                'quantity': item.get('quantity', 1),
                'initialPrice': item.get('initialPrice'),
                'summ': item.get('initialPrice', 0) * item.get('quantity', 1)
            })

        # вычисление даты со сдвигом
        # Первый заказ (idx=0) - сегодня, второй (idx=1) - вчера и т.д.
        created_date = datetime.now() - timedelta(days=idx)
        created_at_str = created_date.strftime('%Y-%m-%d %H:%M:%S')

        order_payload = {
            'externalId': external_id,
            'firstName': order.get('firstName'),
            'lastName': order.get('lastName'),
            'phone': order.get('phone'),
            'email': order.get('email'),
            'status': order.get('status', 'new'),
            'summ': total_summ,
            'paymentType': 'cash',
            'items': items,
            'createdAt': created_at_str,
            'delivery': order.get('delivery'),
            'customFields': order.get('customFields')
        }

        order_payload = {k: v for k, v in order_payload.items() if v is not None}

        data = {'order': json.dumps(order_payload, ensure_ascii=False)}

        try:
            response = requests.post(url, params=params, data=data, headers=headers, timeout=30)
            
            print(f"Статус: {response.status_code} для заказа {external_id}")
            
            if response.status_code in (200, 201):
                result = response.json()
                if result.get('success'):
                    success_count += 1
                    print(f"✓ Заказ {external_id} загружен, сумма: {total_summ}, дата: {created_at_str}")
            else:
                print(f"✗ Ошибка для {external_id}: {response.text[:200]}")
                
        except Exception as e:
            print(f"✗ Исключение для {external_id}: {e}")

        time.sleep(1)

    print(f"\n Успешно загружено {success_count} из {len(orders)} заказов")

if __name__ == "__main__":
    load_orders()