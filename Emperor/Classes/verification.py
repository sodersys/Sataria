from Emperor.Classes import firebase
from Emperor.Classes import guild
from Emperor.Classes import group
from Emperor.Classes import user

import hikari
import lightbulb

Verification = lightbulb.Plugin("verification", "Verification plugin")

@lightbulb.option("robloxaccount", "Your Roblox Account name.")
@lightbulb.command("verify", "Verify your roblox account")
@lightbulb.implements(lightbulb.SlashCommand)
async def verify_command(ctx:lightbulb.SlashContext) -> None:
    User = firebase.GetVerifiedUser(ctx.member)
    if User.Verified:
        User.UpdateRoles()
    else:
        User.Verify(ctx.options.robloxaccount)

    await ctx.respond(User.Response)

Verification.command(verify_command)

def run(bot:lightbulb.BotApp):
    bot.add_plugin(Verification)