
import firebase_admin
from  firebase_admin import db, credentials
import os

def GetPath(Path:str):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), Path)

firebase_admin.initialize_app(credentials.Certificate(GetPath("../credentials.json")), {'databaseURL':os.environ["FIREBASE_URL"]})

class Reference():
    def __init__(self, reference):
        self.Database = db.reference()
        return self
    
    def get(self):
        if self.Database.get() == None:
            return False
        return self.Database.get()
    
    def set(self, data):
        try:
            self.Database.set(data)
            return True
        except:
            return False
    
    def 