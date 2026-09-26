from flask import Flask, render_template, request, jsonify
import requests

# Инициализируем Flask с папкой для скриншотов assets
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

        # Форматируем текст пуш-уведомления (чистая строка без байтов)
        push_message = (
            f"📦 Товар: {product_name}\n"
            f"👤 Контакт: {client_contact}\n"
            f"📝 ТЗ: {client_task}"
        )

        url = f"https://ntfy.sh/{NTFY_TOPIC}"

        # На серверах Render (Linux) заголовки должны быть СТРОГО обычными строками без .encode()
        headers = {
            "Title": f"New Order!",
            "Priority": "high",
            "Tags": "shopping_bags,bell"
        }

        # Кодируем в UTF-8 ТОЛЬКО само текстовое тело сообщения, чтобы не ломался русский язык
        response = requests.post(url, data=push_message.encode('utf-8'), headers=headers, timeout=10)

        if response.status_code == 200:
            print("✅ Успех! Заказ отправлен с сервера Render в ntfy.")
            return jsonify({"status": "success", "message": "Order sent successfully!"}), 200
        else:
            print(f"❗ Ошибка ntfy сервера. Код ответа: {response.status_code}")
            return jsonify({"status": "error", "message": "Failed to send notification"}), 500

    except Exception as e:
        print(f"❌ Критическая ошибка на сервере Flask: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
