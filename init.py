from flask import Flask
#from opentelemetry.instrumentation.flask import FlaskInstrumentor
#from opentelemetry.instrumentation.celery import CeleryInstrumentor
import common

#Create a flask instance
app = Flask(__name__)
#Loads flask configurations from config.py
app.secret_key = app.config['SECRET_KEY']
app.config.from_object("config")

#Setup the Flask SocketIO integration (Required only for asynchronous scenarios)
from flask_socketio import SocketIO
socketio = SocketIO(app,logger=True,engineio_logger=True,message_queue=app.config['BROKER_URL'])

# Initialize otel for the application
common.otel_init()
