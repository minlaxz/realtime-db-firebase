import firebase_init_laxz as laxz
import time
import oledDevice
def userDef_data():
    try:
        userDef = input("Enter Data to Update: ")
        database_ref = laxz.db.reference('restricted_access')
        database_ref.update({
            u'userData':userDef,
            u'Time': time.time()
            })
        ref = database_ref.get()
        for key , val in ref.items():
            if(key == 'userData'):
                print(val)  #TODO
                oledDevice.main(val)
    except KeyboardInterrupt:
        exit()
    except Exception as e:
        print (e)
        exit()