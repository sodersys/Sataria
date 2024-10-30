import roblox.users
from roblox import Client
import os
import firebase_admin
from  firebase_admin import db, credentials

def GetPath(Path:str):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), Path)

firebase_admin.initialize_app(credentials.Certificate(GetPath("Classes/Data/credentials.json")), {'databaseURL':os.environ["FIREBASE_URL"]})

RobloxUser = Client(os.environ["ROBLOXTOKEN"])

def GetRobloxUser(DiscordId):

class User:
    def __init__(self, **kwargs):
        if "DiscordId" in kwargs:
           self.DiscordId = kwargs["DiscordId"]
           self.RobloxUser = GetRobloxUser(kwargs["DiscordId"])
        elif "RobloxId" in kwargs:
            self = BuildUser.FromRobloxId()

        if self == None:
            raise Exception("we woo no user data provided")
            
        return self
    
    def SetRobloxRank(Group, Rank):


        
    
