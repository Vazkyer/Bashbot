# Bashbot
Un asistente interactivo de línea de comandos para aprender y usar comandos de Bash y conceptos de Linux. Incluye un diccionario local de comandos y búsqueda en línea con Python.
BashBot

BashBot es un asistente interactivo de terminal diseñado para ayudar a usuarios de Linux a aprender y utilizar comandos de Bash de manera eficiente. Busca respuestas en un diccionario local de comandos comunes (comandos_comunes.json) y, si es necesario, realiza búsquedas en línea utilizando Google para proporcionar información actualizada y relevante. BashBot utiliza colores para mejorar la legibilidad y guarda un historial de consultas en history.txt.

# Tabla de Contenidos
- Características
- Instalación
- Uso

# Características
Búsqueda local: Consulta un diccionario local (comandos_comunes.json) para respuestas rápidas sobre comandos de Bash.

Búsqueda en línea: Realiza búsquedas automáticas en Google con palabras clave como "comando bash linux ejemplo" si no encuentra información localmente.

Formato legible: Usa colores (verde para respuestas, azul para preguntas, rojo para errores) para una mejor experiencia en la terminal.

Historial de consultas: Registra preguntas, respuestas y fuentes en history.txt para referencia futura.

Interfaz interactiva: Tiene su propia interfaz gráfica con diferentes temas disponibles.

# Instalación
Sigue estos pasos para instalar y configurar BashBot en tu sistema:

Clona el repositorio:
git clone https://github.com/Vazkyer/Bashbot.git

Navega al directorio del proyecto:
cd bashbot

Instala las dependencias de Python: Asegúrate de tener Python 3 instalado. Luego, instala las librerías necesarias:
pip install -r requirements.txt

Las dependencias incluyen requests, googlesearch, beautifulsoup4, colorama, json, re y os.

Configura el archivo de comandos: Asegúrate de que el archivo comandos_comunes.json esté en el directorio raíz del proyecto. Puedes personalizarlo con tus propios comandos y descripciones.

# Uso

Para ejecutar BashBot, usa el siguiente comando desde el directorio del proyecto:
python bashbot.py

El historial de esta interacción se guardará en history.txt.

![Captura de BashBot](/bashbotimg.png)



