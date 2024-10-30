from roblox import Client
import requests
import os
from hikari import Member

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
        if RobloxId != None and RobloxUser != 0:
            self.RobloxUser = await GetRobloxUser(RobloxId)
            self.Ranks = GetGroupIDsAndRanks(RobloxId)
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


        
    
