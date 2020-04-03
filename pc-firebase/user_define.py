import firebase_init_laxz as laxz
from sys import exit
import time


def userDef_data():
    databaseRef = laxz.db.reference('restricted_access')
    ref = getData(databaseRef)
    for key , val in ref.items():
        if(key == 'userData'):
            print('Current Data is: ' + val)
    try:
        userDef = input("Enter Data to Update: ")
        databaseRef.update({
            u'userData': userDef,
            u'Time': time.time() 
        })# TODO
    except KeyboardInterrupt:
        print("Canceled by user..")
        exit()
    except Exception as e:
        print(e)
        exit()
def getData(databaseRef):
     return databaseRef.get()
