from roblox import Client
from hikari import Member, Permissions
import requests
import os

RobloxUser = Client(os.environ["ROBLOXTOKEN"])

async def GetRobloxUser(RobloxId):
    try: 
        Account = await RobloxUser.get_user(RobloxId)
    except:
        return None
    return Account

def GetGroupIDsAndRanks(RobloxID:int) -> dict:
    GroupRoles = requests.get(f'https://groups.roblox.com/v1/users/{RobloxID}/groups/roles?includeLocked=false').json()['data']
    RoleDict = {}
    for Group in GroupRoles:
        RoleDict[Group['group']['id']] = Group['role']['rank']
    return RoleDict

class UserClass:
    async def __init__(self, DiscordUser:Member, RobloxId):
        self.DiscordUser = DiscordUser
        self.Verified = False
        self.CanUpdate = False
        self.Response = ""
        if RobloxId != None and RobloxUser != 0:
            self.RobloxUser = await GetRobloxUser(RobloxId)
            self.Verified = True
            self.Ranks = GetGroupIDsAndRanks(RobloxId)
            DiscordRoles = self.DiscordUser.get_roles()
            for Role in DiscordRoles:
                if Role.name == "Updater" or Role.permissions & Permissions.MANAGE_ROLES == Permissions.MANAGE_ROLES:
                    self.CanUpdate = True
                    break

        return self
    
    async def SetRobloxRank(self, Group, Rank):
        if self.RobloxUser == None:
            return False
        try:
           await RobloxUser.get_base_group(Group).set_rank(self.RobloxUser.id, Rank)
           return True
        except: 
            return False
        
    async def AcceptIntoGroup(self, Group):
        if self.RobloxUser == None:
            return False
        try:
           await RobloxUser.get_base_group(Group).accept_user(self.RobloxUser.id)
           return True
        except: 
            return False
        
    async def KickFromGroup(self, Group):
        if self.RobloxUser == None:
            return False
        try:
           await RobloxUser.get_base_group(Group).kick_user(self.RobloxUser.id)
           return True
        except: 
            return False
         
    async def SetDiscordNickName(self, NewNickname):
        await self.DiscordUser.edit(nickname=NewNickname)

    async def AddDiscordRole(self, RoleId):
        await self.DiscordUser.add_role(RoleId)
    
    async def RemoveDiscordRole(self, RoleId):
        await self.DiscordUser.remove_role(RoleId)


        
    
