web: gunicorn srestate.wsgi --log-file - --log-level debug
worker: celery -A srestate worker --pool=gevent --loglevel debug