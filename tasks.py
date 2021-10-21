import time
from celery import Celery, signals
from celery.utils.log import get_task_logger
from flask_socketio import SocketIO
import config
#import common

import os
from opentelemetry import trace
from opentelemetry.instrumentation.celery import CeleryInstrumentor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from grpc import ssl_channel_credentials



# Setup the logger (compatible with celery version 4)
logger = get_task_logger(__name__)

# Setup the celery client
celery = Celery(__name__)
# Load celery configurations from celeryconfig.py
celery.config_from_object("celeryconfig")

# Setup and connect the socket instance to Redis Server
socketio = SocketIO(message_queue=config.BROKER_URL)

'''
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
'''


@signals.worker_process_init.connect(weak=False)
def initialize_honeycomb(**kwargs):
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
    CeleryInstrumentor().instrument()
    #common.otel_init()



###############################################################################
def long_sync_task(n):
    print(f"This task will take {n} seconds.")
    for i in range(n):
        print(f"i = {i}")
        time.sleep(1)
###############################################################################
@celery.task(name = 'tasks.long_async_task')
def long_async_task(n,session):
    print(f"The task of session {session}  will take {n} seconds.")
    for i in range(n):
        print(f"i = {i}")
        time.sleep(1)
###############################################################################
def send_message(event, namespace, room, message):
    print("Message = ", message)
    socketio.emit(event, {'msg': message}, namespace=namespace, room=room)

@celery.task(name = 'tasks.long_async_taskf')
def long_async_taskf(data):
    room      = data['sessionid']
    namespace = data['namespase']
    n         = data['waittime']

    #Send messages signaling the lifecycle of the task
    send_message('status', namespace, room, 'Begin')
    send_message('msg', namespace, room, 'Begin Task {}'.format(long_async_taskf.request.id))
    send_message('msg', namespace, room, 'This task will take {} seconds'.format(n))

    print(f"This task will take {n} seconds.")
    for i in range(n):
        msg = f"{i}"
        send_message('msg', namespace, room, msg )
        time.sleep(1)

    send_message('msg', namespace, room, 'End Task {}'.format(long_async_taskf.request.id))
    send_message('status', namespace, room, 'End')
###############################################################################
@celery.task(name = 'tasks.long_async_sch_task')
def long_async_sch_task(data):
    #with tracer.start_as_current_span('long-async-sch-task'):
    room      = data['sessionid']
    namespace = data['namespase']
    n         = data['waittime']

    send_message('status', namespace, room, 'Begin')
    send_message('msg'   , namespace, room, 'Begin Task {}'.format(long_async_sch_task.request.id))
    send_message('msg'   , namespace, room, 'This task will take {} seconds'.format(n))

    print(f"This task will take {n} seconds.")
    for i in range(n):
        msg = f"{i}"
        send_message('msg', namespace, room, msg )
        time.sleep(1)

    send_message('msg'   , namespace, room, 'End Task {}'.format(long_async_sch_task.request.id))
    send_message('status', namespace, room, 'End')
###############################################################################
