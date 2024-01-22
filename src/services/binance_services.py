import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
from binance.client import Client
from decouple import config

# Configuración de la API de Binance
binance_api_key = config('BINANCE_API_KEY')
binance_secret_key = config('BINANCE_SECRET_KET')
client = Client(api_key=binance_api_key, api_secret=binance_secret_key)

# Funcion que genera grafica de velas recibiendo como parametros el par ejemplo BTCUSDT y la temporalidad ejemplo 1h
def generar_grafica_velas(symbol, interval, ema_visible, rsi_visible):
    # Obtención de datos de velas (klines) desde Binance
    now = datetime.now()
    
    # Calcular para que la fecha de inicio de la grafica sea variable en dependencia de la temporalidad
    if interval == '1h':
      fecha_inicio_grafica = now - timedelta(hours=500)
    elif interval == '4h':
      fecha_inicio_grafica = now - timedelta(hours=500*4)
    else:
      fecha_inicio_grafica = now - timedelta(hours=500*8)

    # Obtener datos de las velas
    klines = client.get_klines(symbol=symbol, interval=interval, startTime=int(fecha_inicio_grafica.timestamp()) * 1000)

    # Extracción de fechas, aperturas, cierres, máximos y mínimos de las velas
    dates = [datetime.fromtimestamp(kline[0] / 1000) for kline in klines]
    opens = [float(kline[1]) for kline in klines]
    highs = [float(kline[2]) for kline in klines]
    lows = [float(kline[3]) for kline in klines]
    closes = [float(kline[4]) for kline in klines]

    # Cálculo de las EMAs de 20, 50 y 100 periodos --------------------------
    df = pd.DataFrame({'Date': dates, 'Close': closes})
    df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
    df['EMA_100'] = df['Close'].ewm(span=100, adjust=False).mean()

    # Cálculo del RSI -------------------------------------------------------
    delta = pd.Series(closes).diff(1)
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.ewm(span=14, min_periods=1).mean()
    avg_loss = loss.ewm(span=14, min_periods=1).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    # Convertir la serie de pandas 'rsi' a un arreglo de numpy
    rsi_array = np.array(rsi)
    # print(rsi_array)

    # Inicialización de la variable 'buy' en False
    buy = False

    # Variable que almacenará los puntos donde se realizarán compras o ventas
    puntos_trade = []

    # Recorrer lista rsi_array para obtener los puntos de compra y venta
    for i in range(len(rsi_array)):
      if i>1 and rsi_array[i]>20 and rsi_array[i-1]<20 and not buy:
        # print(f"Índice: {i}, Valor: {rsi_array[i]}")
        puntos_trade.append([dates[i], closes[i], lows[i], "Comprar"])
        buy = True
      
      if i>1 and rsi_array[i]<80 and rsi_array[i-1]>80 and buy:
        puntos_trade.append([dates[i], closes[i], highs[i], "Vender"])
        buy = False
    # print(puntos_trade)

    # Configuración de la gráfica --------------------------------------------
    height = int(0.8 * 1080)  # Ajusta según tus preferencias
    width = int(0.8 * 1920)   # Ajusta según tus preferencias
    height_candlestick = int(0.75 * height)
    height_rsi = height - height_candlestick

    # Creación de subgráficos (Un Gráfico contendrá la velas y las EMAs y el otro el RSI)
    # Configurar un solo grafico si rsi_visible = false
    if rsi_visible == "false":
      fig = make_subplots(rows=1, cols=1, shared_xaxes=True, row_heights=[height_candlestick],
                          subplot_titles=(f'Candlestick Chart - {symbol} ({interval})'))
    else:
      fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                      row_heights=[height_candlestick, height_rsi],
                      subplot_titles=(f'Candlestick Chart with EMAs - {symbol} ({interval})', 'RSI'))

    # Añadir trazados de todas las graficas ---------------------------------------------------------------------------
    # Añadir el trazado de las velas al objeto fig
    fig.add_trace(go.Candlestick(x=dates, open=opens, high=highs, low=lows, close=closes), row=1, col=1)

    # Añadir el trazado de las EMAs al objeto fig
    if ema_visible== "true":
      fig.add_trace(go.Scatter(x=df['Date'], y=df['EMA_20'], name='EMA 20', line=dict(color='blue')), row=1, col=1)
      fig.add_trace(go.Scatter(x=df['Date'], y=df['EMA_50'], name='EMA 50', line=dict(color='orange')), row=1, col=1)
      fig.add_trace(go.Scatter(x=df['Date'], y=df['EMA_100'], name='EMA 100', line=dict(color='red')), row=1, col=1)
    
    # Añadir el trazado de RSI asi como los limites superior e inferior y el sombreado interior ------------------------------------------------
    if rsi_visible == "true":
      # Gráfica del RSI
      fig.add_trace(go.Scatter(x=df['Date'], y=rsi, line=dict(color='purple', width=2), name='RSI'), row=2, col=1)

      # Líneas horizontales para los valores 20 y 80 en el RSI
      fig.add_trace(go.Scatter(x=df['Date'], y=[20] * len(df), mode='lines', line=dict(color='green', width=2), name='RSI 20'), row=2, col=1)
      fig.add_trace(go.Scatter(x=df['Date'], y=[80] * len(df), mode='lines', line=dict(color='red', width=2), name='RSI 80'), row=2, col=1)

      # Área sombreada entre las líneas
      fig.add_trace(go.Scatter(x=df['Date'], y=[20] * len(df), fill='tonexty', fillcolor='rgba(0, 128, 0, 0.2)', line=dict(color='rgba(0, 0, 0, 0)'), showlegend=False), row=2, col=1)
      fig.add_trace(go.Scatter(x=df['Date'], y=[80] * len(df), fill='tonexty', fillcolor='rgba(255, 0, 0, 0.2)', line=dict(color='rgba(0, 0, 0, 0)'), showlegend=False), row=2, col=1)
    
    # Visualizar puntos compras
    for index in range(0, len(puntos_trade), 2):
      # Agregar el texto en el punto especificado
      fig.add_annotation(
          x=puntos_trade[index][0],
          y=puntos_trade[index][2],
          text=f'{puntos_trade[index][3]}: {puntos_trade[index][1]}',
          showarrow=True,
          arrowhead=2,
          ax=0,
          ay=40
      )
      
    # Visualizar puntos venta
    for index in range(1, len(puntos_trade), 2):
      # Agregar el texto en el punto especificado
      fig.add_annotation(
          x=puntos_trade[index][0],
          y=puntos_trade[index][2],
          text=f'{puntos_trade[index][3]}: {puntos_trade[index][1]}',
          showarrow=True,
          arrowhead=2,
          ax=0,
          ay=-40
      )
    
    # Configuración final del diseño del gráfico-----------------------------------------------------------------------------------------------
    fig.update_layout(height=height, width=width,
                      title_text=f'Candlestick Chart - {symbol} ({interval})',
                      xaxis_title='Fecha',
                      yaxis_title='Precio (USDT)')

    # # Convertir el objeto Figure a un formato serializable
    # fig_json = pio.to_json(fig)

    # # Guardar el gráfico en un archivo JSON
    # with open('plotly_chart.json', 'w') as json_file:
    #     json.dump(fig_json, json_file)
    
    # # # Mostrar el gráfico
    # fig.show()
    return fig



# # Funcion que genera grafica de velas recibiendo como parametros el par ejemplo BTCUSDT y la temporalidad ejemplo 1h
# def generar_grafica_indicadores(symbol, interval):
#   # Obtención de datos de velas (klines) desde Binance
#   now = datetime.now()
#   fecha_inicio_grafica = now - timedelta(days=30)
#   klines = client.get_klines(symbol=symbol, interval=interval, startTime=int(fecha_inicio_grafica.timestamp()) * 1000)
#   # print(klines)


#   # Extracción de fechas, aperturas, cierres, máximos y mínimos de las velas
#   dates = [datetime.fromtimestamp(kline[0] / 1000) for kline in klines]
#   opens = [float(kline[1]) for kline in klines]
#   highs = [float(kline[2]) for kline in klines]
#   lows = [float(kline[3]) for kline in klines]
#   closes = [float(kline[4]) for kline in klines]

#   # Cálculo de las EMAs de 20, 50 y 100 periodos
#   df = pd.DataFrame({'Date': dates, 'Close': closes})
#   df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
#   df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
#   df['EMA_100'] = df['Close'].ewm(span=100, adjust=False).mean()

#   # Cálculo del RSI
#   delta = pd.Series(closes).diff(1)
#   gain = delta.where(delta > 0, 0)
#   loss = -delta.where(delta < 0, 0)
#   avg_gain = gain.ewm(span=14, min_periods=1).mean()
#   avg_loss = loss.ewm(span=14, min_periods=1).mean()
#   rs = avg_gain / avg_loss
#   rsi = 100 - (100 / (1 + rs))

#   # Convertir la serie de pandas 'rsi' a un arreglo de numpy
#   rsi_array = np.array(rsi)
#   # print(rsi_array)

#   # Inicialización de la variable 'buy' en False
#   buy = False

#   # Variable que almacenará los puntos donde se realizarán compras o ventas
#   puntos_trade = []

#   # Recorrer lista rsi_array para obtener los puntos de compra y venta
#   for i in range(len(rsi_array)):
#     if i>1 and rsi_array[i]>20 and rsi_array[i-1]<20 and not buy:
#       # print(f"Índice: {i}, Valor: {rsi_array[i]}")
#       puntos_trade.append([dates[i], closes[i], lows[i], "Comprar"])
#       buy = True
    
#     if i>1 and rsi_array[i]<80 and rsi_array[i-1]>80 and buy:
#       puntos_trade.append([dates[i], closes[i], highs[i], "Vender"])
#       buy = False
#   # print(puntos_trade)

#   # Configuración de la gráfica
#   height = int(0.8 * 1080)  # Ajusta según tus preferencias
#   width = int(0.8 * 1920)   # Ajusta según tus preferencias
#   height_candlestick = int(0.75 * height)
#   height_rsi = height - height_candlestick

#   # Creación de subgráficos
#   fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
#                       row_heights=[height_candlestick, height_rsi],
#                       subplot_titles=(f'Candlestick Chart with EMAs - {symbol} ({interval})', 'RSI'))

#   # Velas y EMAs
#   fig.add_trace(go.Candlestick(x=dates, open=opens, high=highs, low=lows, close=closes), row=1, col=1)
#   fig.add_trace(go.Scatter(x=df['Date'], y=df['EMA_20'], name='EMA 20', line=dict(color='blue')), row=1, col=1)
#   fig.add_trace(go.Scatter(x=df['Date'], y=df['EMA_50'], name='EMA 50', line=dict(color='orange')), row=1, col=1)
#   fig.add_trace(go.Scatter(x=df['Date'], y=df['EMA_100'], name='EMA 100', line=dict(color='red')), row=1, col=1)

#   # Visualizar puntos compras
#   for index in range(0, len(puntos_trade), 2):
#     # Agregar el texto en el punto especificado
#     fig.add_annotation(
#         x=puntos_trade[index][0],
#         y=puntos_trade[index][2],
#         text=f'{puntos_trade[index][3]}: {puntos_trade[index][1]}',
#         showarrow=True,
#         arrowhead=2,
#         ax=0,
#         ay=40
#     )
    
#   # Visualizar puntos venta
#   for index in range(1, len(puntos_trade), 2):
#     # Agregar el texto en el punto especificado
#     fig.add_annotation(
#         x=puntos_trade[index][0],
#         y=puntos_trade[index][2],
#         text=f'{puntos_trade[index][3]}: {puntos_trade[index][1]}',
#         showarrow=True,
#         arrowhead=2,
#         ax=0,
#         ay=-40
#     )

#   # Gráfica del RSI
#   fig.add_trace(go.Scatter(x=df['Date'], y=rsi, line=dict(color='purple', width=2), name='RSI'), row=2, col=1)

#   # Líneas horizontales para los valores 20 y 80 en el RSI
#   fig.add_trace(go.Scatter(x=df['Date'], y=[20] * len(df), mode='lines', line=dict(color='green', width=2), name='RSI 20'), row=2, col=1)
#   fig.add_trace(go.Scatter(x=df['Date'], y=[80] * len(df), mode='lines', line=dict(color='red', width=2), name='RSI 80'), row=2, col=1)

#   # Área sombreada entre las líneas
#   fig.add_trace(go.Scatter(x=df['Date'], y=[20] * len(df), fill='tonexty', fillcolor='rgba(0, 128, 0, 0.2)', line=dict(color='rgba(0, 0, 0, 0)'), showlegend=False), row=2, col=1)
#   fig.add_trace(go.Scatter(x=df['Date'], y=[80] * len(df), fill='tonexty', fillcolor='rgba(255, 0, 0, 0.2)', line=dict(color='rgba(0, 0, 0, 0)'), showlegend=False), row=2, col=1)

#   # Configuración final del diseño del gráfico
#   fig.update_layout(height=height, width=width,
#                     title_text=f'Candlestick Chart with EMAs and RSI - {symbol} ({interval})',
#                     xaxis_title='Fecha',
#                     yaxis_title='Precio (USDT)')

#   print(type(fig))
#   # Mostrar el gráfico
#   fig.show()