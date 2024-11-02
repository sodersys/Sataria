from Emperor.Classes import firebase
from Emperor.Classes import guild
from Emperor.Classes import group
from Emperor.Classes import user

import hikari
import lightbulb
import crescent

GroupManagement = crescent.Plugin("groupmanagement", "Group management plugin")

async def GetUserAndManagementPermissions(Member, Group):
    User = await firebase.GetVerifiedUser(Member)
    User.CanManage(Group, 10)
    return User

@crescent.option("")
@crescent.command("setrank", "Sets a users rank.")


def run(bot:lightbulb.BotApp):
    bot.add_plugin(GroupManagement)