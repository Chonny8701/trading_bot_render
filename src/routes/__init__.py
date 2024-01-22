from src.routes.index_routes import index_blueprint
from src.routes.consultas_binance_routes import consultasBinance_blueprint

def init_routes(app):
  app.register_blueprint(index_blueprint)
  app.register_blueprint(consultasBinance_blueprint, url_prefix='/api/binance')

