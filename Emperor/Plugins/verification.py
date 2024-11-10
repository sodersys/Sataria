from Emperor.Classes import firebase
from Emperor.Classes import user

import hikari
import lightbulb

Verification = lightbulb.Plugin("verification", "Verification plugin")

@lightbulb.option("robloxaccount", "Your Roblox Account name.", type=str, required=True)
@lightbulb.option("override", "Override your existing verification.", type=bool, required=False)
@lightbulb.command("verify", "Verify your roblox account")
@lightbulb.implements(lightbulb.SlashCommand)
async def verify_command(ctx:lightbulb.SlashContext) -> None:
    User: user.UserClass = await firebase.GetVerifiedUser(ctx.member)
    if User.Verified:
        await User.UpdateRoles(User)
    else:
        await User.Verify(ctx.options.robloxaccount, ctx.options.override != None and True or False)
    await ctx.respond(User.Response)

Verification.command(verify_command)


@lightbulb.option("user", "Discord user to update.", type=hikari.OptionType.USER, required=False)
@lightbulb.command("update", "Update a user or yourself.")
@lightbulb.implements(lightbulb.SlashCommand)
async def update_command(ctx:lightbulb.SlashContext) -> None:
    await ctx.respond(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
    User: user.UserClass = await firebase.GetVerifiedUser(ctx.member)
    if User.Verified:
        if ctx.options.user == None or ctx.options.user.id == User.DiscordUser.id:
            await User.UpdateRoles(User)
        elif User.CanUpdate:
            NewUser = await firebase.GetVerifiedUser(await ctx.bot.rest.fetch_member(ctx.guild_id, ctx.options.user.id))
            await NewUser.UpdateRoles(User)
    else:
        User.PromptVerify()
    await ctx.respond(User.Response)

Verification.command(update_command)

def run(bot:lightbulb.BotApp):
    print("verification `loaded")
    bot.add_plugin(Verification)