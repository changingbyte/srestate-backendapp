import urllib
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
mongo_uri = 'mongodb+srv://srestateapi:' + str(urllib.parse.quote("changingbyte@123"))  +'@cluster0.0zdkv.mongodb.net/myFirstDatabase?retryWrites=true&w=majority'

CONFIG_DB = {
"local" : {
        'default': {
            'ENGINE': 'djongo',
            'NAME': 'your-db-name',
            'ENFORCE_SCHEMA': False,
            'CLIENT': {
                'host': mongo_uri
            }  
        },
        'messagedb':{
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        },

        'db2': {
            'ENGINE': 'djongo',
            'NAME': 'your-db-name',
            'ENFORCE_SCHEMA': False,
            'CLIENT': {
                'host': mongo_uri
            }  
        },
        "CACHES" : {
    'default': {
        "host":"redis-10641.c301.ap-south-1-1.ec2.cloud.redislabs.com",
        "port":"10641",
        "password":"h9Wkb8znF8tcWquRFRr6NiuCBKPkpsw1"
     }
    },


},

    "DEV" : {
        'default': {
            'ENGINE': 'djongo',
            'NAME': 'your-db-name',
            'ENFORCE_SCHEMA': False,
            'CLIENT': {
                'host': mongo_uri
            }  
        },
        'messagedb':{
            'ENGINE': 'django.db.backends.postgresql',
                'NAME': os.environ.get('DATABASE_NAME'),
                'USER': os.environ.get('DATABASE_USER'),
                'PASSWORD': os.environ.get('DATABASE_PASSWORD'),
                'HOST': os.environ.get('DATABASE_HOST'),
                'PORT': '5432'
        },

        'db2': {
            'ENGINE': 'djongo',
            'NAME': 'your-db-name',
            'ENFORCE_SCHEMA': False,
            'CLIENT': {
                'host': mongo_uri
            }  
        },
        "CACHES" : {
    'default': {
        "host":"redis-10641.c301.ap-south-1-1.ec2.cloud.redislabs.com",
        "port":"10641",
        "password":"h9Wkb8znF8tcWquRFRr6NiuCBKPkpsw1"
     }
    },


} ,

    "PROD" : {
        'default': {
            'ENGINE': 'djongo',
            'NAME': 'srestateapiprod',
            'ENFORCE_SCHEMA': False,
            'CLIENT': {
                'host': mongo_uri
            }  
        },
        'messagedb':{
            
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': os.environ.get('DATABASE_NAME'),
                'USER': os.environ.get('DATABASE_USER'),
                'PASSWORD': os.environ.get('DATABASE_PASSWORD'),
                'HOST': os.environ.get('DATABASE_HOST'),
                'PORT': '5432'
            },

        'db2': {
            'ENGINE': 'djongo',
            'NAME': 'your-db-name',
            'ENFORCE_SCHEMA': False,
            'CLIENT': {
                'host': mongo_uri
            },
        
        "CACHES" : {
    'default': {
        "host":"redis-14152.c264.ap-south-1-1.ec2.cloud.redislabs.com",
        "port":"14152",
        "password":"93mHkCGxkxM0Wj2yjcO8bxkhlECCOCis"
     }
    },
        },
        


} ,

}
