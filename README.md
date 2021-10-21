# flask_sync_async
Tutorial showing scenarios about synchronous and asynchronous requests in Python

## Getting started
First install virtualenv by `pip install virtualenv`
If pip is not configured on your syste please refer to https://pip.pypa.io/en/stable/installation/

Setup your virtualenv in the root of the project by calling:
```
$ virtualenv -p python3 venv
```
**NOTE: if python3 is not installed please install and make it available**

Once your virtualenv is setup you can source it and install dependencies:
```
$ . venv/bin/activate
$ pip install -r requirements
```

## Running the app
**NOTE: requires redis installed and running on localhost, else change the connection string in the config files**

Open two terminal sessions and in each source the virtuelenv as above.  One will be used to run the Celery daemon, and another the app.

In one run:
```
$ celery -A tasks worker --loglevel=DEBUG
```

In the other run:
```
$ python app_async3.py
```

You may run other app*.py files for other tests, but the app_async3 is the one instrumented for OTEL today
