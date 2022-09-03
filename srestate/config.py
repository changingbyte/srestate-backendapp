from .configenv import CONFIG_DB
import os
ENV = os.environ.get('ENV',"local")
CACHES  = CONFIG_DB.get(ENV).get("CACHES")