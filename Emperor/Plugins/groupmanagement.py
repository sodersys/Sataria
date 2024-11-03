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


async def _programming_language_autocomplete(
    option: hikari.CommandInteractionOption, interaction: hikari.AutocompleteInteraction
) -> list[str]:
    # The `option` argument is the current text that the user typed in.
    if not isinstance(option.value, str):
        # This will raise a TypeError if `option.value` cannot be converted
        option.value = str(option.value)

    # You can query a database, fetch an api, or return any list of strings
    # !!! You can return a max of 25 options !!!
    langs = [
        "C",
        "C++",
        "C#",
        "CSS",
        "Go",
        "HTML",
        "Java",
        "Javascript",
        "Kotlin",
        "Matlab",
        "NoSQL",
        "PHP",
        "Perl",
        "Python",
        "R",
        "Ruby",
        "Rust",
        "SQL",
        "Scala",
        "Swift",
        "TypeScript",
        "Zig",
    ]
    return [lang for lang in langs if option.value.lower() in lang.lower()]


@GroupManagement.command
@lightbulb.option(
    "language",
    "Your favorite programming language.",
    autocomplete=_programming_language_autocomplete,
)
@lightbulb.command("autocomplete_example", "Autocomplete example.")
@lightbulb.implements(lightbulb.SlashCommand)
async def autocomplete_example(ctx: lightbulb.SlashContext):
    """Autocomplete example."""
    await ctx.respond("Your favorite programming language is " + ctx.options.language)

#class UserGroupsAutoComplete(lightbulb.SlashCommand, name="ManageGroup"):
    
def run(bot:lightbulb.BotApp):
    print("groupmanagement loaded")
    bot.add_plugin(GroupManagement)