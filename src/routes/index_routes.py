from flask import Blueprint, send_from_directory
import os

index_blueprint = Blueprint('index', __name__)

# Permitir que el enrutamiento lo maneje la aplicación de React con React-Router
@index_blueprint.route('/', defaults={'path': ''})
@index_blueprint.route('/<path:path>')
def catch_all(path):
    return send_from_directory('dist', 'index.html')

# Estas líneas definen rutas adicionales para manejar archivos estáticos en las carpetas raíz, /assets, /images
@index_blueprint.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory(os.path.join('dist', 'assets'), filename)

@index_blueprint.route('/images/<path:filename>')
def serve_images(filename):
    return send_from_directory(os.path.join('dist', 'images'), filename)

@index_blueprint.route('/<path:filename>')
def serve_other_files(filename):
    return send_from_directory(os.path.join('dist'), filename)
  
