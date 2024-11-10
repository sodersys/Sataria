from Emperor.Classes import firebase
from Emperor.Classes import guild
from Emperor.Classes import group
from Emperor.Classes import user

import hikari
import lightbulb

GroupManagement = lightbulb.Plugin("groupmanagement", "Group management plugin")

Groups = {
    35076880:10,#mar
    35076877:10,#nav
    35076896:10,#pol
    35076890:10,#st
    35076899:10,#sp
    35076894:10,#ni
    35076888:10,#ig
    35097043:5,#ar
    35076904:6, #rg
    35076884:8, #mage
    35016156:12, # sat
}

Branches = {
    35076880, 35076877, 35076896
}

async def GetUserAndManagementPermissions(Member, Group):
    User = await firebase.GetVerifiedUser(Member)
    User.CanManage(Group, Groups[Group])
    return User

@lightbulb.option("branch", "What branch you'd like to join.", type=int, required = True, choices=[
    hikari.CommandChoice(name="Marines", value=35076880),
    hikari.CommandChoice(name="Navy", value=35076877),
    #hikari.CommandChoice(name="Police", value=35076896)
    ])
@lightbulb.command("enlist", "Enlist in a branch.")
@lightbulb.implements(lightbulb.SlashCommand)
async def Enlist(ctx:lightbulb.SlashContext):
    await ctx.respond(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
    VerifiedUser = await firebase.GetVerifiedUser(ctx.member)
    if VerifiedUser.RobloxUser == None:
        await ctx.respond("You're not verified. Run /verify in order to enlist.")
        return

    if VerifiedUser.GetGroupRank(35016156) == 0:
        await ctx.respond("You must join Sataria to join a branch of its military. https://www.roblox.com/groups/35016156")
        return

    if VerifiedUser.GetGroupRank(ctx.options.branch) != 0:
        await ctx.respond("You've already enlisted into this branch.")
        return
    
    for Branch in Branches:
        if VerifiedUser.GetGroupRank(Branch) != 0:
            await ctx.respond("You've already enlisted into a branch. If you wish to change your branch, leave this group. \n-# All rank data regarding this branch will be removed when you leave." + f"\nhttps://www.roblox.com/groups/{Branch}")
            return
        
    if not ctx.options.branch in Branches:
        await ctx.respond(f"{ctx.options.branch} is not a valid option.")
        return
    
    InGroup = await VerifiedUser.AcceptIntoGroup(ctx.options.branch)
    if InGroup:
        Approved = await VerifiedUser.SetRobloxRank(ctx.options.branch, 2)
        if not Approved:
            await ctx.respond(f"There was an issue ranking you. Contact a member of your branch's HR to resolve the issue.")  
            return
    else:
        await ctx.respond(f"You're not pending for https://www.roblox.com/groups/{ctx.options.branch}. Please pend and rerun the command.")
        return

    await ctx.respond("You have succesfully enlisted.")
    VerifiedUser.UpdateRanks()
    await VerifiedUser.UpdateRoles(VerifiedUser)
    await ctx.respond(VerifiedUser.Response)
GroupManagement.command(Enlist)

@lightbulb.option("group", "The group you want to", required=True, choices=[
    hikari.CommandChoice(name="Marines", value=35076880),
    hikari.CommandChoice(name="Navy", value=35076877),
    hikari.CommandChoice(name="Police", value=35076896),
    hikari.CommandChoice(name="Shock Troopers", value=35076890),
    hikari.CommandChoice(name="Secret Police", value=35076899),
    hikari.CommandChoice(name="Naval Intelligence", value=35076894),
    hikari.CommandChoice(name="Imperial Guard", value=35076888),
    hikari.CommandChoice(name="Artifact Reclamation", value=35097043),
    hikari.CommandChoice(name="Royal Guard", value=35076904),
    hikari.CommandChoice(name="Magicians", value=35076884),
    hikari.CommandChoice(name="Sataria", value=35016156)
], type=int)
@lightbulb.option("user", "The user you want to manage.", required=True, type=hikari.OptionType.USER)
@lightbulb.option("rank", "The rank you want to set for this user. 0 = exile, >1 = accept + rank.", required=True, type=int)
@lightbulb.command("setrank", "Set a user's rank in a group you manage.")
@lightbulb.implements(lightbulb.SlashCommand)
async def setrank_command(ctx:lightbulb.SlashContext) -> None:
    await ctx.respond(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
    if ctx.user.id == ctx.options.user.id:
        await ctx.respond("You can not rank yourself.")
        return
    RankingUser = await GetUserAndManagementPermissions(ctx.member, ctx.options.group)
    if not RankingUser.Verified:
        await ctx.respond("You're not verified. Run /verify robloxname to use setrank command.")
        return
    
    if RankingUser.MaxModifyRanks[ctx.options.group] == 0:
        await ctx.respond("You can not manage this group.")
        return
    
    if RankingUser.MaxModifyRanks[ctx.options.group] < ctx.options.rank:
        await ctx.respond(f"You can not set a user to this rank. The highest rank you can manage is {RankingUser.MaxModifyRanks[ctx.options.group]}.")
        return  

    TemporaryUser = await ctx.bot.rest.fetch_member(ctx.guild_id, ctx.options.user.id)

    RankedUser = await firebase.GetVerifiedUser(TemporaryUser)

    if not RankedUser.Verified:
        await ctx.respond(f"<@{RankedUser.DiscordUser.id}> is not verified.")
        return

    if ctx.options.group in RankedUser.Ranks:
        if RankedUser.Ranks[ctx.options.group] >= RankingUser.Ranks[ctx.options.group]:
            await ctx.respond(f"<@{RankedUser.DiscordUser.id}> is a higher rank than you and you can not manage them. The highest rank you can manage is {RankingUser.MaxModifyRanks[ctx.options.group]}")
            return
        if RankedUser.Ranks[ctx.options.group] == ctx.options.rank:
            await ctx.respond(f"<@{RankedUser.DiscordUser.id}> is already ranked {ctx.options.rank}.")
            return
    else:
        AcceptResult = await RankedUser.AcceptIntoGroup(ctx.options.group)
        if not AcceptResult:
            await ctx.respond(f"<@{RankedUser.DiscordUser.id}> is not pending for https://www.roblox.com/groups/{ctx.options.group}")
            return

    RankingResult = await RankedUser.SetRobloxRank(ctx.options.group, ctx.options.rank)
    if RankingResult:
        await RankedUser.UpdateRoles(RankingUser)
        await ctx.respond(f"<@{RankedUser.DiscordUser.id}> has been ranked successfully.")
        return
    await ctx.respond("There was an issue ranking <@{RankedUser.DiscordUser.id}>. Roblox APIs are down or something.")
GroupManagement.command(setrank_command)

def run(bot:lightbulb.BotApp):
    print("groupmanagement loaded")
    bot.add_plugin(GroupManagement)