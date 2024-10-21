import requests, os

def ConvertRobloxID(RobloxId):
    if RobloxId == 0:
        return "Not Verified"
    else:
        return f"https://www.roblox.com/users/{RobloxId}/profile"
def LogMemberJoined(DiscordId, DiscordUsername, PictureURL, Profile):
    Log({
        "embeds": [
            {
                "title": "Member joined",
                "color": 28691,
                "fields": [
                    {
                        "name": DiscordUsername,
                        "value": DiscordId
                    },
                    {
                        "name": "Roblox Account",
                        "value": Profile
                    }
                ],
                "image": {
                    "url": str(PictureURL)
                }
            }
        ]
    })
def LogRoleAdded(DiscordId, RobloxId, RoleId):
        RobloxId = ConvertRobloxID(RobloxId)
        Log({
            "embeds": [
                {
                    "title": "Role Added",
                    "description": "<@" +str(DiscordId)+ ">",
                    "color": 2754678,
                    "fields": [
                        {
                            "name": "Roblox Account",
                            "value": RobloxId
                        },
                        {
                            "name": "Role Added",
                            "value": "<@&{}>".format(RoleId)
                        }
                    ]
                }
            ]
        })
def LogRoleRemoved(DiscordId, RobloxId, RoleId):
        RobloxId = ConvertRobloxID(RobloxId)
        Log({
            "embeds": [
                {
                    "title": "Role Removed",
                    "description": "<@" +str(DiscordId)+ ">",
                    "color": 14780566,
                    "fields": [
                        {
                            "name": "Roblox Account",
                            "value": RobloxId
                        },
                        {
                            "name": "Role Removed",
                            "value": "<@&{}>".format(RoleId)
                        }
                    ]
                }
            ]
        })
def LogNicknameChange(DiscordId, RobloxID, OldNickName, NewNickName):
    Log({
        "embeds": [
            {
                "title": "Nickname changed",
                "description": "<@" +str(DiscordId)+ ">",
                "color": 821710,
                "fields": [
                    {
                        "name": "Roblox Account",
                        "value": "https://www.roblox.com/users/{}/profile".format(RobloxID)
                    },
                    {
                        "name": "Old Nickname",
                        "value": OldNickName,
                        "inline": True 
                    },
                    {
                        "name": "New Nickname",
                        "value": NewNickName,
                        "inline": True
                    }
                ]
            }
        ]
    }) 
def Log(LogJson):
    response = requests.post(os.environ["WEBHOOK_URL"], json=LogJson)
    if response.status_code != 204:
        print("Error with webhook logging.")
        print(response.status_code)
        print(LogJson)