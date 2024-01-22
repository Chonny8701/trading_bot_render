# Pasos para Configurar y Ejecutar el Proyecto con Docker

## 1. Navegar a la Ruta Raíz del Proyecto TradingBot_Docker
Asegúrate de estar en la ruta raíz de la carpeta TradingBot_Docker antes de realizar cualquier acción.

## 2. Construir una imagen de Docker a partir del "Dockerfile"
En la terminal de comandos ejecuta el siguiente comando para construir una imagen de Docker a partir del "Dockerfile". El nombre de la imagen será imagen_trading_bot:

```bash
docker build -t imagen_trading_bot .
```

## 3. Crear y ejecutar contenedor de Docker
Finalmente, ejecuta el siguiente comando para crear y ejecutar un contenedor a partir de una imagen de Docker, vinculando el puerto 5000 del host al puerto 5000 del contenedor. El nombre del contenedor será contenedor_trading_bot

```bash
docker run -p 5173:5173 --name contenedor_trading_bot imagen_trading_bot
```

## 4. Acceder al proyecto desde el navegador web
Una vez se esté ejecutando el contenedor, podrás acceder al proyecto a través del nevegador web en la ruta http://localhost:5000/