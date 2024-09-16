import random

qna = {
            "Role Earned by Killing Player Unwilling" : "outlaw",
            "Where Is PVP Allowed" : "pvp arena",
            "Can I Build Without Permission" : "no",
            "Whom To Ask Permission From Before Building" : ["duke", "admin"],
            "Who Has The Ultimate Authority" : "emperor"
        }

user = input(" + ")
if user.lower() in qna["Can I Build Without Permission"]:
    print("WOW")