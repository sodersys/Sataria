import hikari, lightbulb, os, json, firebase_admin, requests, math, time, miru
from   hikari         import intents, permissions, embeds, guilds, colors
from   firebase_admin import db, credentials
from   roblox         import Client
import BotFolder.Classes.log as Log

SatarianDiscordIDs = [1293772677781262336]
SatarianJoinChannels = {1293772677781262336:1299174327995994203}

def GetPath(Path:str):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), Path)

def GetGroupIDsAndRanks(RobloxID:int) -> dict:
    GroupRoles = requests.get(f'https://groups.roblox.com/v1/users/{RobloxID}/groups/roles?includeLocked=false').json()['data']
    RoleDict = {}
    for Group in GroupRoles:
        RoleDict[Group['group']['id']] = Group['role']['rank']
    return RoleDict

async def SetRobloxRank(GroupID:int, RobloxID:int, RankID:int):
    try:
        await RobloxClient.get_base_group(group_id=GroupID).set_rank(RobloxID, RankID)
    except:
        return False
    return True

async def AcceptIntoGroup(GroupID:int, RobloxID:int):
    try:
        await RobloxClient.get_base_group(group_id=GroupID).accept_user(RobloxID)
    except:
        return False
    return True

firebase_admin.initialize_app(credentials.Certificate(GetPath("Classes/Data/credentials.json")), {'databaseURL':os.environ["FIREBASE_URL"]})

DiscordBot = lightbulb.BotApp(os.environ["DISCORDTOKEN"], help_slash_command=False, intents=hikari.Intents.ALL)

RobloxClient = Client(os.environ["ROBLOXTOKEN"])

with open(GetPath("Classes/Data/RankData.json")) as json_file:
    RankData = json.load(json_file)

async def MemberUpdate(DiscordID, RobloxID, ServerID):
    GuildData = RankData[str(ServerID)]
    NameFormat = "{username}"
    RankName = "Guest"
    RankGrants = {}
    NameFormatPriority = -1
    RobloxAccount = await RobloxClient.get_user(RobloxID)

    if GuildData == None:
        FormatedName = str.format(NameFormat, username=RobloxAccount.name)
        await DiscordBot.rest.edit_member(ServerID, nickname=FormatedName)
        Embed = embeds.Embed(title="Sataria Verification", description="This discord is not currently set up to give roles.", color=7677476)
        Embed.add_field(name="Name Updated", value=FormatedName)
        return {"Verified":True, "RobloxID":RobloxID, "Embeds":[Embed]}
    
    DiscordUser = await DiscordBot.rest.fetch_member(ServerID, DiscordID)
    CurrentRoles = DiscordUser.get_roles()
    RolesToGrant = [GuildData['Verified']]
    RolesToRemove = []
    RobloxGroups = GetGroupIDsAndRanks(RobloxID)
    for Group in GuildData['Binds']:
        Group = int(Group)
        if not Group in RobloxGroups:
            RobloxGroups[Group] = 0
        for Condition in GuildData['Binds'][str(Group)]:
            if Condition[:2] == "<=":
                if not RobloxGroups[Group] <= int(Condition[2:]):
                    continue
            elif Condition[:2] == ">=": 
                if not RobloxGroups[Group] >= int(Condition[2:]):
                    continue
            elif Condition[:2] == "==": 
                if not RobloxGroups[Group] == int(Condition[2:]):
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
        if not Group in RobloxGroups:
            continue
        if RobloxGroups[Group] >= 12:
            continue
        if RobloxGroups[Group] == RankGrants[Group]:
            continue
        await SetRobloxRank(Group, RobloxAccount.id, int(RankGrants[Group]))
        await Log.LogGroupRankChange(DiscordUser.id, RobloxAccount.id, await RobloxClient.get_base_group(Group).get_roles(), int(RobloxGroups[Group]), int(RankGrants[Group]))
        RobloxGroups[Group] = RankGrants[Group]
    
    for Group in GuildData['Binds']:
        Group = int(Group)

        if not Group in RobloxGroups:
            RobloxGroups[Group] = 0
        for Condition in GuildData['Binds'][str(Group)]:
            if Condition[:2] == "<=":
                if not RobloxGroups[Group] <= int(Condition[2:]):
                    continue
            elif Condition[:2] == ">=": 
                if not RobloxGroups[Group] >= int(Condition[2:]):
                    continue
            elif Condition[:2] == "==": 
                if not RobloxGroups[Group] == int(Condition[2:]):
                    continue
            else:
                print("issue !!!")
                continue
            PassedData = GuildData['Binds'][str(Group)][Condition]
            if PassedData['Priority'] > NameFormatPriority:
                NameFormatPriority = PassedData['Priority']
                NameFormat = PassedData['UserNameFormat']
                RankName = PassedData['RankName']
            RolesToGrant.extend(PassedData['Roles'])

    for Roles in CurrentRoles:
        if not str(Roles.id) in GuildData['Roles']:
            continue
        if str(Roles.id) in RolesToGrant:
            RolesToGrant = [i for i in RolesToGrant if i != str(Roles.id)] 
            continue
        RolesToRemove.append(str(Roles.id))

    Embed = embeds.Embed(title="Update Complete", description=f"Welcome, {RankName} {RobloxAccount.name}.", color=colors.Color(4367920),url="https://www.roblox.com/groups/35016156/SATARIA#!/about")
    if len(RolesToGrant) >= 1: Embed.add_field(name="Roles Added", value="<@&"+(">\n<@&".join(RolesToGrant))+">")
    if len(RolesToRemove) >= 1: Embed.add_field(name="Roles Removed", value="<@&"+(">\n<@&".join(RolesToRemove))+">")
    for Role in RolesToGrant:
        try:
            await DiscordUser.add_role(int(Role))
            Log.LogRoleAdded(DiscordUser.id, RobloxAccount.id, Role)

        except:
            print(DiscordUser.id, ServerID, Role)
    for Role in RolesToRemove:
        try:
            await DiscordUser.remove_role(int(Role))
            Log.LogRoleRemoved(DiscordUser.id, RobloxAccount.id, Role)  
        except:
            print(DiscordUser.id, ServerID, Role)
    FormatedName = str.format(NameFormat, username=RobloxAccount.name)
    if FormatedName != DiscordUser.nickname and FormatedName != DiscordUser.username:
        try:
            await DiscordUser.edit(nickname=FormatedName)
            Embed.add_field(name="Nickname Changed", value=FormatedName)
            Log.LogNicknameChange(DiscordID, RobloxAccount.id, DiscordUser.nickname or DiscordUser.username, FormatedName)  
        except:
            Embed.add_field(name="Nickname Changed", value="Unable to change nickname due to an error.")
    return {"Verified":True, "RobloxID":RobloxID, "Embeds":Embed}

async def MemberVerify(DiscordID, RobloxName, ServerID) -> None:
    RobloxID = db.reference(f"/DiscordIDToRobloxID/{DiscordID}").get()
    if RobloxID != None:
        return await MemberUpdate(DiscordID, RobloxID, ServerID)
    if RobloxName == 0:
        await DiscordBot.rest.create_message(channel=SatarianJoinChannels[ServerID], content=f"Thank you for joining. In order to get access to the rest of the server, please run /verify [robloxname].")
        await DiscordBot.rest.add_role_to_member(ServerID, DiscordID, RankData[str(ServerID)]['Unverified'])
        return {"Verified":False, "RobloxID":0}
    if RobloxName == None:
        try:
            await DiscordBot.rest.add_role_to_member(ServerID, DiscordID, RankData[str(ServerID)]['Unverified'])
        except:
            print("error !!!! omg")
        return {"Verified":False, "RobloxID":0, "ResponseMessage":f"<@{DiscordID}> needs to verify before they can be updated."}
    try:
        RobloxAccount = await RobloxClient.get_user_by_username(RobloxName)
    except:
        return {"Verified":False, "RobloxID":0, "ResponseMessage":f"`{RobloxName}` is not a valid account on roblox."}
    
    AlreadyVerified = db.reference(f"/RobloxIDtoDiscordID/{RobloxAccount.id}")
    if AlreadyVerified.get() != None:
        return {"Verified":False, "RobloxID":0, "ResponseMessage":f"`{RobloxAccount.name}` is already verified to <@{AlreadyVerified.get()}>."}
   
    DiscordName = await DiscordBot.rest.fetch_user(DiscordID)
    ExistingVerification = db.reference(f"/PendingVerifications/{RobloxAccount.id}")
    ExistingVerification.update({
        'DiscordID':str(DiscordID),
        'Username': DiscordName.username
        })
    return {"Verified":False, "RobloxID":False, "ResponseMessage":"A verification request has been created. Join here https://www.roblox.com/games/84342663532399/Verification-Game"}


@DiscordBot.listen(hikari.MemberCreateEvent)
async def on_member_create(event: hikari.MemberCreateEvent) -> None:
    Info = await MemberVerify(event.user_id, 0, event.guild_id) 
    if "ResponseMessage" in Info or "Embeds" in "ResponseMessage":
        DiscordBot.rest.create_message(SatarianJoinChannels[event.guild_id], content="ResponseMessage" in Info and Info["ResponseMessage"] or None, embeds="Embeds" in Info and Info["Embeds"] or None)
    if not Info["Verified"]:
        NotVerified = RankData[str(event.guild_id)]["Unverified"]
        User = await DiscordBot.rest.fetch_member(event.guild_id, event.user.id)
        await User.add_role(NotVerified)
        Log.LogRoleAdded(event.user_id, 0, NotVerified)
    Log.LogMemberJoined(event.user_id, event.user.username, str(event.user.avatar_url), "https://www.roblox.com/users/{}/profile".format(Info['RobloxID']) if Info['Verified'] else "Not verified.")
    


@lightbulb.option(name="robloxusername", description="Your roblox username.", type=str, required=False)
@lightbulb.command("verify", "Verify your roblox account.", guilds=SatarianDiscordIDs)
@lightbulb.implements(lightbulb.SlashCommand)
async def verify_command(ctx:lightbulb.SlashContext) -> None:
    await ctx.respond(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
    Info = await MemberVerify(ctx.user.id, ctx.options.robloxusername, ctx.guild_id)
    await ctx.respond("Embeds" in Info and Info["Embeds"] or "ResponseMessage" in Info and Info["ResponseMessage"])
    
    return
DiscordBot.command(verify_command)

@lightbulb.option(name="discorduser", description="The person you want to update.", type=hikari.OptionType.USER, required=False)
@lightbulb.command("update", "Update your roles.", guilds=SatarianDiscordIDs)
@lightbulb.implements(lightbulb.SlashCommand)
async def update_command(ctx:lightbulb.SlashContext) -> None:
    await ctx.respond(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
    User = await DiscordBot.rest.fetch_member(ctx.guild_id, ctx.user.id)
    if ctx.options.discorduser != None and 1295111342688043140 in User.role_ids:
        Info = await MemberVerify(ctx.options.discorduser.id, None, ctx.guild_id)
    else:
        Info = await MemberVerify(ctx.user.id, None, ctx.guild_id)
    await ctx.respond("Embeds" in Info and Info["Embeds"] or "ResponseMessage" in Info and Info["ResponseMessage"] or None)
    return
DiscordBot.command(update_command)

@lightbulb.add_checks(lightbulb.has_role_permissions(permissions.Permissions.BAN_MEMBERS))
@lightbulb.option("discorduser", "Discord user of the person you want to verify.", type=hikari.OptionType.USER)
@lightbulb.option("robloxname", "Roblox name of the person you want to verify.", type=str)
@lightbulb.command("forceverify", "Force verify someone!", guilds=SatarianDiscordIDs)
@lightbulb.implements(lightbulb.SlashCommand)
async def ForceVerify(ctx:lightbulb.SlashContext):
    try:
        SelectedRobloxAccount = await RobloxClient.get_user_by_username(ctx.options.robloxname)
    except:
        await ctx.respond("No roblox account with the name `"+ctx.options.robloxname+"` exists.")
    await ctx.respond(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
    Embed = embeds.Embed(title="Account Force Verified", description="<@"+str(ctx.options.discorduser.id)+"> / https://www.roblox.com/users/"+str(SelectedRobloxAccount.id)+"/profile", color=colors.Color(7110962))
    CurrentRobloxAccount = db.reference(f"/DiscordIDToRobloxID/{ctx.options.discorduser.id}").get()
    if CurrentRobloxAccount != None:
        if CurrentRobloxAccount == SelectedRobloxAccount.id:
            await ctx.respond("<@"+str(ctx.options.discorduser.id)+"> / https://www.roblox.com/users/"+str(SelectedRobloxAccount.id)+"/profile is already bound.")
            return
        Embed.add_field("Account unbound", "<@"+str(ctx.options.discorduser.id)+"> / https://www.roblox.com/users/"+CurrentRobloxAccount+"/profile")
        db.reference(f"/DiscordIDToRobloxID/{ctx.options.discorduser.id}").delete()
        db.reference(f"/RobloxIDToDiscordID/{CurrentRobloxAccount}").delete()
    db.reference("/DiscordIDToRobloxID").update({
        str(ctx.options.discorduser.id):SelectedRobloxAccount.id,
        })
    db.reference("/RobloxIDToDiscordID").update({
        SelectedRobloxAccount.id:str(ctx.options.discorduser.id),
        })
    await ctx.respond(Embed)
DiscordBot.command(ForceVerify)

Branches = {35076880, 35076877, 35076896}

@lightbulb.option("branch", "What branch you'd like to join.", type=int, required = True, choices=[
    hikari.CommandChoice(name="Marines", value=35076880),
    hikari.CommandChoice(name="Navy", value=35076877),
    #hikari.CommandChoice(name="Police", value=35076896)
    ])
@lightbulb.command("enlist", "Enlist in a branch.", guilds=SatarianDiscordIDs)
@lightbulb.implements(lightbulb.SlashCommand)
async def Enlist(ctx:lightbulb.SlashContext):
    await ctx.respond(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
    RobloxID = db.reference(f"/DiscordIDToRobloxID/{ctx.user.id}").get()
    if RobloxID == None:
        await ctx.respond("You're not verified. Run /verify in order to enlist.")
        return
    
    RobloxGroups = GetGroupIDsAndRanks(RobloxID)

    RobloxID = db.reference(f"/DiscordIDToRobloxID/{ctx.user.id}").get()

    if RobloxID == None:
        await ctx.respond("You must be verified to enlist.")

    if not 35016156 in RobloxGroups:
        await ctx.respond("You must join Sataria to join a branch of its military. https://www.roblox.com/groups/35016156")

    if ctx.options.branch in RobloxGroups:
        await ctx.respond("You've already enlisted into this branch.")
        return
    for Branch in Branches:
        if Branch in RobloxGroups:
            await ctx.respond("You've already enlisted into a branch. If you wish to change your branch, leave this group. \n-# All rank data regarding this branch will be removed when you leave." + f"\nhttps://www.roblox.com/groups/{Branch}")
            return
    if not ctx.options.branch in Branches:
        await ctx.respond(f"{ctx.options.branch} is not a valid option.")
        return
    InGroup = await AcceptIntoGroup(ctx.options.branch, RobloxID)
    if InGroup:
        Approved = await SetRobloxRank(ctx.options.branch, RobloxID, 2)
        if Approved:
            Log.LogGroupRankChange(ctx.user.id, RobloxID, ctx.options.branch, 0, 2)
        else:
            await ctx.respond(f"There was an issue ranking you. Contact a member of your branch's HR to resolve the issue.")  
            return
    else:
        await ctx.respond(f"You're not pending for https://www.roblox.com/groups/{ctx.options.branch}. Please pend and rerun the command.")
        return

    await ctx.respond("You have succesfully enlisted. Run /update to get your roles.")
DiscordBot.command(Enlist)

def run():
    DiscordBot.run()