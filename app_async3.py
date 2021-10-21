from gevent import monkey
monkey.patch_all()

from flask import render_template, jsonify, session, request
from random import randint
import uuid
import tasks
from init import app, socketio
from flask_socketio import join_room
import json

import os
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor
)
from opentelemetry.propagate import get_global_textmap
from opentelemetry.trace import set_span_in_context
from grpc import ssl_channel_credentials

resource = Resource(attributes={
    "service.name": 'celery'
    })

trace_provider = TracerProvider(resource=resource)

otlp_exporter = OTLPSpanExporter(
    endpoint="api.honeycomb.io:443",
    insecure=False,
    credentials=ssl_channel_credentials(),
    headers=(
        ("x-honeycomb-team", os.environ['HONEYCOMB_API_KEY']),
        ("x-honeycomb-dataset", 'celery')
    )
)

trace_provider.add_span_processor(
    BatchSpanProcessor(otlp_exporter)
)
trace.set_tracer_provider(trace_provider)

tracer = trace.get_tracer(__name__)

@app.route("/",methods=['GET'])
def index():
    # create a unique session ID
    if 'uid' not in session:
        sid = str(uuid.uuid4())
        session['uid'] = sid
        print("Session ID stored =", sid)
    return render_template('index3.html')


#Run a Post Scheduled Asynchronous Task With Automatic Feedback
@app.route("/runPSATask",methods=['POST'])
def long_async_sch_task():
    with tracer.start_as_current_span("runPSATask"):
        print("Running", "/runPSATask")
        # Generate a random number between MIN_WAIT_TIME and MAX_WAIT_TIME
        n = randint(app.config['MIN_WAIT_TIME'], app.config['MAX_WAIT_TIME'])
        span = trace.get_current_span()
        span.set_attribute("time_wait", n)

        data = {}
        data['sessionid'] = str(session['uid'])
        data['waittime']  = n
        data['namespase'] = '/runPSATask'
        data['duration']  = int(request.form['duration'])

        span.set_attribute("data", json.dumps(data))
        headers = {}
        get_global_textmap().inject(headers, set_span_in_context(span))

        #Countdown represents the duration to wait in seconds before running the task
        task = tasks.long_async_sch_task.apply_async(args=[data],countdown=data['duration'])

        return jsonify({ 'taskid':task.id
                        ,'sessionid':data['sessionid']
                        ,'waittime': data['waittime']
                        ,'namespace':data['namespase']
                        ,'duration':data['duration']
                        })


@socketio.on('connect', namespace='/runPSATask')
def socket_connect():
    print('Client Connected To NameSpace /runPSATask - ',request.sid)

@socketio.on('disconnect', namespace='/runPSATask')
def socket_connect():
    print('Client disconnected From NameSpace /runPSATask - ',request.sid)

@socketio.on('join_room', namespace='/runPSATask')
def on_room():
    room = str(session['uid'])
    print(f"Socket joining room {room}")
    join_room(room)

@socketio.on_error_default
def error_handler(e):
    print(f"socket error: {e}, {str(request.event)}")

if __name__ == "__main__":
    socketio.run(app,debug=True)