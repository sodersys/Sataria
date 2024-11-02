from Emperor.Classes import firebase
from Emperor.Classes import guild
from Emperor.Classes import group
from Emperor.Classes import user

import hikari
import lightbulb

Verification = lightbulb.Plugin("verification", "Verification plugin")

@lightbulb.option("robloxaccount", "Your Roblox Account name.", type=str, required=True)
@lightbulb.command("verify", "Verify your roblox account")
@lightbulb.implements(lightbulb.SlashCommand)
async def verify_command(ctx:lightbulb.SlashContext) -> None:
    User = await firebase.GetVerifiedUser(ctx.member)
    if User.Verified:
        await User.UpdateRoles()
    else:
        await User.Verify(ctx.options.robloxaccount)
    await ctx.respond(User.Response)

Verification.command(verify_command)


@lightbulb.option("user", "User to update", type=hikari.OptionType.USER, required=False)
@lightbulb.command("update", "Update a user or yourself.")
@lightbulb.implements(lightbulb.SlashCommand)
async def update_command(ctx:lightbulb.SlashContext) -> None:
    User = await firebase.GetVerifiedUser(ctx.Member)
    if User.Verified:
        if not "user" in ctx.options or ctx.options.user.id == User.DiscordUser.id:
            await User.UpdateRoles()
        elif User.CanUpdate:
            NewUser = await firebase.GetVerifiedUser(ctx.options.user.Member)
            NewUser.UpdateRoles(User)
    else:
        User.PromptVerify()
    await ctx.respond(User.Response)

Verification.command(update_command)

def run(bot:lightbulb.BotApp):
    bot.add_plugin(Verification)