from flask import Blueprint, jsonify
from src.services.binance_services import generar_grafica_velas
from flask import send_file
import json

consultasBinance_blueprint = Blueprint('consultasBinance', __name__)

# Devolver todos los negocios de la base de datos
@consultasBinance_blueprint.route('/grafica-velas/<cripto>/<temporalidad>/<ema>/<rsi>', methods=['GET'])
def obtener_grafica_mercado(cripto, temporalidad, ema, rsi):
  try:    
    grafica = generar_grafica_velas(cripto, temporalidad, ema, rsi )
    return jsonify(grafica.to_json()), 200
  
  except Exception as e:
    # Manejo de errores si es necesario
    print ({str(e)})
    return jsonify({"error": f"Error en la ruta privada: {str(e)}"}), 500
  

# Devolver la informacion de una cripto especifica
@consultasBinance_blueprint.route('/cripto/<nombre>', methods=['GET'])
def obtener_informacion_cripto(nombre):
    try:
        # Lee el contenido del archivo criptos_price.json
        with open('criptos_price.json', 'r') as archivo:
            datos_criptos = json.load(archivo)

        # Verifica si la criptomoneda está en los datos
        if nombre in datos_criptos:
            informacion_cripto = datos_criptos[nombre]
            return jsonify(informacion_cripto), 200
        else:
            return jsonify({"error": f"Criptomoneda no encontrada: {nombre}"}), 404

    except Exception as e:
        # Manejo de errores si es necesario
        print(str(e))
        return jsonify({"error": f"Error al obtener informacion de la cripto: {str(e)}"}), 500
  
  
@consultasBinance_blueprint.route('/get_plotly_chart')
def get_plotly_chart():
    # Ruta al archivo plotly_chart.json en tu servidor
    file_path = 'plotly_chart.json'

    # Devolver el archivo como respuesta
    return send_file(file_path, mimetype='application/json')