from Emperor.Classes import firebase
from roblox import Client
from hikari import Member, Permissions, embeds, colors
import requests
import os
import time
import json

RankBinds = {}

with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../RankData.json")) as json_file:
    RankData = json.load(json_file)

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

    def UpdateRanks(self):
        if self.RobloxUser != None:
            self.Ranks = GetGroupIDsAndRanks(self.RobloxUser.id)

    async def GetRoblox(self, RobloxId):
        if RobloxId != None and RobloxId != 0 and RobloxId:
            self.Verified = True
            self.RobloxUser = await GetRobloxUser(RobloxId)
            self.UpdateRanks()
            self.DiscordRoles = self.DiscordUser.get_roles()
            for Role in self.DiscordRoles:
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
        
    def GetGroupRank(self, GroupId:int):
        if GroupId in self.Ranks:
            return self.Ranks[GroupId]
        return 0
    
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
        if AlreadyVerified:
            self.Response = f"[{RequestedRobloxAccount.name}](https://www.roblox.com/users/{RequestedRobloxAccount.id}/profile) is already verified to a <@{AlreadyVerified}>."
            return

        firebase.Reference(f"/PendingVerifications/{RequestedRobloxAccount.id}").set({"DiscordID":self.DiscordUser.id, "Username":self.DiscordUser.username})
        self.Response = f"A verification request has been created between [{RequestedRobloxAccount.name}](https://www.roblox.com/users/{RequestedRobloxAccount.id}/profile) and <@{self.DiscordUser.id}>. Join https://www.roblox.com/games/84342663532399/Verification-Game to verify."

    def PromptVerify(self):
        self.Response = "You're not currently verified. Run /verify [roblox name] in order to get access to the server."
        return
    
    async def UpdateRoles(self, Updater):
        if self.RobloxUser == None:
            Updater.Response = "You're not verified ^^"
            return
        
        GuildData = GetRankBinds(self.DiscordUser.guild_id)
        NameFormat = "{username}"
        RankName = "Guest"
        RankGrants = {}
        NameFormatPriority = -1

        if GuildData == False:
            FormatedName = str.format(NameFormat, username=self.RobloxAccount.name)
            await self.SetDiscordNickName(FormatedName)
            Embed = embeds.Embed(title="Sataria Verification", description="This discord is not currently set up to give roles.", color=7677476)
            Embed.add_field(name="Name Updated", value=FormatedName)
            Updater.Response = Embed
            return
        
        CurrentRoles = self.DiscordRoles
        RolesToGrant = [GuildData['Verified']]
        RolesToRemove = []
        for Group in GuildData['Binds']:
            Group = int(Group)
            if not Group in self.Ranks:
                self.Ranks[Group] = 0
            for Condition in GuildData['Binds'][str(Group)]:
                if Condition[:2] == "<=":
                    if not self.Ranks[Group] <= int(Condition[2:]):
                        continue
                elif Condition[:2] == ">=": 
                    if not self.Ranks[Group] >= int(Condition[2:]):
                        continue
                elif Condition[:2] == "==": 
                    if not self.Ranks[Group] == int(Condition[2:]):
                        continue
                else:
                    print("issue !!!")
                    continue
                PassedData = GuildData['Binds'][str(Group)][Condition]
                if "RankGrant" in PassedData:
                    for RankGroup in PassedData['RankGrant']:
                        if not RankGroup in RankGrants:
                            RankGrants[int(RankGroup)] = PassedData['RankGrant'][RankGroup]
                        if RankGrants[int(RankGroup)] > PassedData['RankGrant'][RankGroup]:
                            continue
                        RankGrants[int(RankGroup)] = PassedData['RankGrant'][RankGroup]
        for Group in RankGrants:
            if not Group in self.Ranks:
                continue
            if self.Ranks[Group] >= 12:
                continue
            if self.Ranks[Group] == RankGrants[Group]:
                continue
            await self.SetRobloxRank(Group, int(RankGrants[Group]))
            self.Ranks[Group] = RankGrants[Group]
        
        for Group in GuildData['Binds']:
            Group = int(Group)

            if not Group in self.Ranks:
                self.Ranks[Group] = 0
            for Condition in GuildData['Binds'][str(Group)]:
                if Condition[:2] == "<=":
                    if not self.Ranks[Group] <= int(Condition[2:]):
                        continue
                elif Condition[:2] == ">=": 
                    if not self.Ranks[Group] >= int(Condition[2:]):
                        continue
                elif Condition[:2] == "==": 
                    if not self.Ranks[Group] == int(Condition[2:]):
                        continue
                else:
                    print("issue !!!")
                    continue
                PassedData = GuildData['Binds'][str(Group)][Condition]
                if PassedData['Priority'] > NameFormatPriority:
                    NameFormatPriority = PassedData['Priority']
                    NameFormat = PassedData['UserNameFormat']
                    RankName = PassedData['RankName']
                if "Roles" in PassedData:
                    RolesToGrant.extend(PassedData['Roles'])

        for Roles in CurrentRoles:
            if not str(Roles.id) in GuildData['Roles']:
                continue
            if str(Roles.id) in RolesToGrant:
                RolesToGrant = [i for i in RolesToGrant if i != str(Roles.id)] 
                continue
            RolesToRemove.append(str(Roles.id))

        Embed = embeds.Embed(title="Update Complete", description=self.DiscordUser.id == Updater.DiscordUser.id and f"Welcome, {RankName} {self.RobloxUser.name}." or f"<@{self.DiscordUser.id}> was updated by <@{Updater.DiscordUser.id}>", color=colors.Color(4367920),url="https://www.roblox.com/groups/35016156/SATARIA#!/about")
        if len(RolesToGrant) >= 1: Embed.add_field(name="Roles Added", value="<@&"+(">\n<@&".join(RolesToGrant))+">")
        if len(RolesToRemove) >= 1: Embed.add_field(name="Roles Removed", value="<@&"+(">\n<@&".join(RolesToRemove))+">")
        for Role in RolesToGrant:
            try:
                await self.AddDiscordRole(int(Role))
            except:
                print(Role, "add")
        for Role in RolesToRemove:
            try:
                await self.RemoveDiscordRole(int(Role))
            except:
                print(Role, "remove")
        FormatedName = str.format(NameFormat, username=self.RobloxUser.name)
        if FormatedName != self.DiscordUser.nickname and FormatedName != self.DiscordUser.username:
            try:
                await self.SetDiscordNickName(FormatedName)
                Embed.add_field(name="Nickname Changed", value=FormatedName)
            except:
                Embed.add_field(name="Nickname Changed", value="Unable to change nickname due to an error.")
        Updater.Response = Embed
    
def GetRankBinds(GuildId:int):
    if GuildId in RankBinds:
        if os.environ["DATAMODE"] == "FIREBASE":
            if RankBinds[GuildId]["LastUpdate"]+1000 > int(time.time()):
                return RankBinds[GuildId]
        
            RankBinds[GuildId] = firebase.GetRankBinds(GuildId)
            RankBinds[GuildId]["LastUpdate"] = int(time.time())
    else:
        if str(GuildId) in RankData:
            RankBinds[GuildId] = RankData[str(GuildId)]


    return RankBinds[GuildId]
        
    
async def GetRobloxId(Name:str):
    try:
        return await RobloxUser.get_user_by_username(Name)
    except:
        return False