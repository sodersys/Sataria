
import firebase_admin
from  firebase_admin import db, credentials
import os

def GetPath(Path:str):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), Path)

firebase_admin.initialize_app(credentials.Certificate(GetPath("../credentials.json")), {'databaseURL':os.environ["FIREBASE_URL"]})

#stuff