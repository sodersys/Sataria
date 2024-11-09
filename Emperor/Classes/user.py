from Emperor.Classes import firebase
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
    def __init__(self, DiscordUser:Member):
        self.DiscordUser = DiscordUser
        self.Response = "hi"
        self.MaxModifyRanks = {}


    async def GetRoblox(self, RobloxId):
        if RobloxId != None and RobloxUser != 0:
            self.Verified = True
            self.RobloxUser = await GetRobloxUser(RobloxId)
            self.Ranks = GetGroupIDsAndRanks(RobloxId)
            DiscordRoles = self.DiscordUser.get_roles()
            for Role in DiscordRoles:
                if Role.name == "Updater" or Role.permissions & Permissions.MANAGE_ROLES == Permissions.MANAGE_ROLES:
                    self.CanUpdate = True
                    break
            return
        self.Verified = False
        self.RobloxUser = None
        self.CanUpdate = False

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
    
    def CanManage(self, GroupId, GroupManagementLimit):
        self.MaxModifyRanks[GroupId] = 0
        if self.RobloxUser == None:
            return
        if GroupId in self.Ranks:
            print(self.Ranks[GroupId], GroupManagementLimit)
            if self.Ranks[GroupId] >= GroupManagementLimit:
                self.MaxModifyRanks[GroupId] = self.Ranks[GroupId]-1

    async def SetDiscordNickName(self, NewNickname):
        await self.DiscordUser.edit(nickname=NewNickname)

    async def AddDiscordRole(self, RoleId):
        await self.DiscordUser.add_role(RoleId)
    
    async def RemoveDiscordRole(self, RoleId):
        await self.DiscordUser.remove_role(RoleId)

    async def Verify(self, RobloxAccountName, Override):
        if self.RobloxUser != None and Override == False:
            self.Response = f"You're already verified to roblox account. If you want to override this, reverify with the `override` parameter set to true."
            return
        try:
            RequestedRobloxAccount = await RobloxUser.get_user_by_username(RobloxAccountName)
        except:
            self.Response = f"There is no roblox user associated with {RobloxAccountName}"
            return
        AlreadyVerified = firebase.Reference(f"/RobloxIDToDiscordID/{RequestedRobloxAccount.id}").get()
        if AlreadyVerified != None:
            self.Response = f"[{RequestedRobloxAccount.name}](https://www.roblox.com/users/{RequestedRobloxAccount.id}/profile) is already verified to a user."
            return

        firebase.Reference(f"/PendingVerifications/{RequestedRobloxAccount.id}").set({"DiscordID":self.DiscordUser.id, "Username":self.DiscordUser.username})
        self.Response = f"A verification request has been created between [{RequestedRobloxAccount.name}](https://www.roblox.com/users/{RequestedRobloxAccount.id}/profile) and <@{self.DiscordUser.id}>. Join https://www.roblox.com/games/84342663532399/Verification-Game to verify."

    def PromptVerify(self):
        self.Response = "You're not currently verified. Run /verify [roblox name] in order to get access to the server."
        return
    
    async def UpdateRoles(self, Updater):
        print("hi")
        self.Response = f"user <@{self.DiscordUser.id}> updated by <@{Updater.DiscordUser.id}>"    


        
    
