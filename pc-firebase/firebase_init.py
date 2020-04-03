from firebase_admin import initialize_app,credentials,db

cred = credentials.Certificate('serviceKey.json') 

initialize_app(cred, {
    'databaseURL': 'https://laxz-test.firebaseio.com/',
    'databaseAuthVariableOverride': {
        'uid': 'service-writer' 
        }
})

