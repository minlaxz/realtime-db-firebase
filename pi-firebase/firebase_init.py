from firebase_admin import initialize_app,credentials,db
from sys import exit
cred = credentials.Certificate('serviceKey.json')

initialize_app(cred, {
    'databaseURL': 'https://laxz-test.firebaseio.com/',
    'databaseAuthVariableOverride': {
        'uid': 'service-writers'
        }
})
