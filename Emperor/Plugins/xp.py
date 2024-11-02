from Emperor.Classes import firebase
from Emperor.Classes import guild
from Emperor.Classes import group
from Emperor.Classes import user

import hikari
import lightbulb

XP = lightbulb.Plugin("xp", "XP plugin")

@lightbulb.option("user", "The person who's XP you want to check.", type=hikari.OptionType.USER, required=True)
@lightbulb.command("xp", "Check your XP.")
@lightbulb.implements(lightbulb.SlashCommand)
async def xp_command(ctx:lightbulb.SlashContext):
    print("hi")