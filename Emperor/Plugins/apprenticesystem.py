from Emperor.Classes import firebase
from Emperor.Classes import guild
from Emperor.Classes import group
from Emperor.Classes import user

import hikari
import lightbulb

ApprenticeSystem = lightbulb.Plugin("apprenticesystem", "Apprentice System plugin")

@lightbulb.command("apprenticecoins", "Check your apprentice coins")
@lightbulb.implements(lightbulb.SlashCommand)
async def apprenticecoins_command(ctx:lightbulb.SlashContext):
    Coins = firebase.Reference(f"/ApprenticeCoins/{ctx.user.id}")
    GottenCoins = Coins.get()
    if GottenCoins:
        await ctx.respond(f"You have {GottenCoins['Coins']} <:apprenticecoin:1305245764401758361> and {GottenCoins['ExamKeys']} <:ExamKey:1305252720147697684>.")
        return
    Coins.set({"ExamKeys":0, "Coins":0})
    await ctx.respond("You have 0 <:apprenticecoin:1305245764401758361> and 0 <:ExamKey:1305252720147697684>")
    return
ApprenticeSystem.command(apprenticecoins_command)

@lightbulb.option("user", "The user you want to give coins to", required=True, type=hikari.OptionType.USER)
@lightbulb.option("coins", "The amount of coins you want to give.", required=True, type=int)
@lightbulb.command("addapprenticecoins", "Adds apprentice coins.")
@lightbulb.implements(lightbulb.SlashCommand)
async def addapprenticecoins_command(ctx:lightbulb.SlashContext):
    VerifiedUser = await firebase.GetVerifiedUser(ctx.member)
    if VerifiedUser.GetGroupRank(35076884) < 7:
        await ctx.respond("You can not manage Apprentice Coins.")
        return
    if ctx.options.coins >= 10:
        await ctx.respond("Do not cause inflation, noob.")
        return
    Coins = firebase.Reference(f"/ApprenticeCoins/{ctx.options.user.id}")
    GottenCoins = Coins.get()
    if GottenCoins:
        Coins.set({"ExamKeys":GottenCoins["ExamKeys"], "Coins":ctx.options.coins+GottenCoins['Coins']})
        await ctx.respond(f"<@{ctx.options.user.id}> now has {GottenCoins['Coins']+ctx.options.coins} <:apprenticecoin:1305245764401758361> and {GottenCoins['ExamKeys']} <:ExamKey:1305252720147697684>.")
        return
    Coins.set({"ExamKeys":0, "Coins":ctx.options.coins})
    await ctx.respond(f"<@{ctx.options.user.id}> now has {ctx.options.coins} <:apprenticecoin:1305245764401758361> and 0 <:ExamKey:1305252720147697684>")
    return
ApprenticeSystem.command(addapprenticecoins_command)

@lightbulb.option("user", "The user you want to give coins to", required=True, type=hikari.OptionType.USER)
@lightbulb.option("coins", "The amount of coins you want to give.", required=True, type=int)
@lightbulb.command("giveapprenticecoins", "Gives your apprentice coins to someone else.")
@lightbulb.implements(lightbulb.SlashCommand)
async def addapprenticecoins_command(ctx:lightbulb.SlashContext):
    if ctx.options.coins >= 10:
        await ctx.respond("You can not give more than 10 coins at a time.")
        return
    Coins = firebase.Reference(f"/ApprenticeCoins/{ctx.user.id}")
    GottenCoins = Coins.get()
    if GottenCoins:
        if GottenCoins["Coins"] < ctx.options.coins:
            await ctx.respond("You don't have enough coins to preform this action.")
            return
        
        Coins.set({"ExamKeys":GottenCoins["ExamKeys"], "Coins":GottenCoins['Coins']-ctx.options.coins})
        OtherCoins = firebase.Reference(f"/ApprenticeCoins/{ctx.user.id}")
        OtherGottenCoins = OtherCoins.get()
        if OtherGottenCoins:
            OtherCoins.set({"ExamKeys":OtherGottenCoins["ExamKeys"], "Coins":OtherGottenCoins['Coins']+ctx.options.coins})
        else:
            OtherCoins.set({"ExamKeys":0, "Coins":ctx.options.coins})
        await ctx.respond(f"<@{ctx.user.id}> has given {ctx.options.coins} to <@{ctx.options.user.id}>")
        return
    Coins.set({"ExamKeys":0, "Coins":ctx.options.coins})
    await ctx.respond(f"<@{ctx.options.user.id}> now has {ctx.options.coins} <:apprenticecoin:1305245764401758361> and 0 <:ExamKey:1305252720147697684>")
    return





def run(bot:lightbulb.BotApp):
    print("Apprentice System loaded")
    bot.add_plugin(ApprenticeSystem)