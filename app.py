from flask import Flask
from flask_cors import CORS
from src.routes import init_routes
import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from binance.client import Client
import json
from datetime import datetime

app = Flask(__name__)

# Configura la aplicación y la base de datos
init_routes(app)

# Configura CORS para permitir solicitudes desde cualquier origen (*)
CORS(app)

# Configura la secret_key desde la variable de entorno
app.config['JWT_SECRET_KEY'] = os.environ.get('SECRET_KEY')


# Configura las credenciales de la API de Binance desde las variables de entorno
binance_api_key = os.environ.get('BINANCE_API_KEY')
binance_api_secret = os.environ.get('BINANCE_API_SECRET')
client = Client(binance_api_key, binance_api_secret)

# Objeto JSON con el contenido del precio de las criptomonedas
criptos_price_json_data = {
    "BTCUSDT": {
        "precio": "0.00000000",
        "fecha_hora": ""
    },
    "ETHUSDT": {
        "precio": "0.00000000",
        "fecha_hora": ""
    },
    "SOLUSDT": {
        "precio": "0.00000000",
        "fecha_hora": ""
    },
    "DOTUSDT": {
        "precio": "0.00000000",
        "fecha_hora": ""
    },
    "ADAUSDT": {
        "precio": "0.00000000",
        "fecha_hora": ""
    }
}

# Función para obtener y actualizar el precio de cada criptomoneda en el objeto JSON
def obtener_y_actualizar_precios():
  try:
    for symbol in criptos_price_json_data:
      # Realiza la solicitud para obtener el precio de la criptomoneda
      ticker = client.get_symbol_ticker(symbol=symbol)
      precio_cripto = ticker['price']
      # print(f"Precio de {symbol}: {precio_cripto}")

      # Actualiza el precio y la fecha y hora en el objeto JSON
      criptos_price_json_data[symbol]["precio"] = precio_cripto
      criptos_price_json_data[symbol]["fecha_hora"] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    # Guarda el objeto JSON actualizado en un archivo
    with open('criptos_price.json', 'w') as archivo:
      json.dump(criptos_price_json_data, archivo, indent=2)

  except Exception as e:
    print(f"Error al obtener y actualizar precios: {e}")

# Configura la tarea programada con APScheduler
scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(
    obtener_y_actualizar_precios,
    trigger=IntervalTrigger(seconds=1),
    id='obtener_y_actualizar_precios',
    name='Obtener y actualizar precios cada 5 segundos',
    replace_existing=True
)

# Iniciar todas las tareas
if __name__ == "__main__":
    # Iniciar aplicación Flask
    # app.run(debug=True, threaded=True)
    app.run(host='0.0.0.0', port=5173)