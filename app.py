from flask import Flask, render_template, request, jsonify
import requests

# Подключаем папку со скриншотами assets
app = Flask(__name__, static_folder='assets')

# ==========================================================================
# КОНФИГУРАЦИЯ УВЕДОМЛЕНИЙ NTFY (ТЕМА СИНХРОНИЗИРОВАНА)
# ==========================================================================
NTFY_TOPIC = "synapse-orders"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/submit-order', methods=['POST'])
def submit_order():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No data received"}), 400

        product_name = data.get('product_name', 'Unknown Product')
        client_contact = data.get('client_contact', 'Not provided')
        client_task = data.get('client_task', 'Not provided')

        # Форматируем текст пуш-уведомления для телефона и ПК
        push_message = (
            f"👤 Контакт: {client_contact}\n"
            f"📝 ТЗ: {client_task}"
        )

        # Отправляем запрос на официальный сервер ntfy
        url = f"https://ntfy.sh/{NTFY_TOPIC}"

        headers = {
            "Title": f"📦 Новый заказ: {product_name}".encode('utf-8'),
            "Priority": "high",  # Пробивает режим энергосбережения и беззвучный режим
            "Tags": "shopping_bags,bell"  # Добавит красивые эмодзи в пуш-уведомление
        }

        # Пересылаем текст заказа в кодировке utf-8, чтобы русский текст не ломался
        response = requests.post(url, data=push_message.encode('utf-8'), headers=headers, timeout=10)

        if response.status_code == 200:
            print("✅ Успех! Заказ отправлен, пуш летит на телефон и ПК.")
            return jsonify({"status": "success", "message": "Order sent successfully!"}), 200
        else:
            print(f"❗ Ошибка ntfy сервера. Код ответа: {response.status_code}")
            return jsonify({"status": "error", "message": "Failed to send notification"}), 500

    except Exception as e:
        print(f"❌ Критическая ошибка на сервере Flask: {str(e)}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500


if __name__ == '__main__':
    app.run(debug=True)
