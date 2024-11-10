import hikari
import lightbulb
import os

from Emperor.Plugins import groupmanagement, verification, xp, apprenticesystem

if __name__ == "__main__":
    bot = lightbulb.BotApp(os.environ["DISCORDTOKEN"])
    groupmanagement.run(bot)
    verification.run(bot)
    apprenticesystem.run(bot)
    bot.run()
    #xp.run(bot)