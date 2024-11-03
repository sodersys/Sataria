from Emperor.Classes import firebase
from Emperor.Classes import guild
from Emperor.Classes import group
from Emperor.Classes import user

import hikari
import lightbulb

GroupManagement = lightbulb.Plugin("groupmanagement", "Group management plugin")

async def GetUserAndManagementPermissions(Member, Group):
    User = await firebase.GetVerifiedUser(Member)
    User.CanManage(Group, 10)
    return User

import string
import random

ALL_CHARS = string.ascii_letters + string.digits


async def autocomplete_callback(ctx: lightbulb.AutocompleteContext[str]) -> None:
    current_value: str = ctx.focused.value or ""
    values_to_recommend = [
        current_value + "".join(random.choices(ALL_CHARS, k=5)) for _ in range(10)
    ]
    await ctx.respond(values_to_recommend)


class RandomCharacters(
    lightbulb.SlashCommand,
    name="randomchars",
    description="autocomplete demo command"
):
    text = lightbulb.string("text", "autocompleted option", autocomplete=autocomplete_callback)

    @GroupManagement.invoke
    async def invoke(self, ctx: lightbulb.Context) -> None:
        await ctx.respond(self.text)

#class UserGroupsAutoComplete(lightbulb.SlashCommand, name="ManageGroup"):
    
def run(bot:lightbulb.BotApp):
    bot.add_plugin(GroupManagement)