"""
Created by Epic at 9/5/20
"""

import speedcord
from speedcord.ext.typing.context import MessageContext
from speedcord.http import Route
from os import environ as env
from logging import basicConfig, DEBUG
from pymongo import MongoClient
from random import choices
from string import ascii_letters, digits

client = speedcord.Client(intents=512)
mongo = MongoClient(env["MONGO_URI"])
database = mongo["BotConfig"]
bot_data_table = database["bot_data"]
bot_tokens_table = database["bot_tokens"]

basicConfig(level=DEBUG)

prefix = env["PREFIX"]
perms_role = env["PERMS_ROLE"]


@client.listen("MESSAGE_CREATE")
async def on_message(message, shard):
    ctx = MessageContext(client, message)
    if not ctx.content.startswith(prefix):
        return
    clean_content = ctx.content[len(prefix):]
    args = clean_content.split(" ")
    command = args[0]
    del args[0]

    if perms_role not in ctx.member["roles"]:
        await ctx.send(content="No permissions!")
    if command == "createbot":
        bot_id = args[0]
        route = Route("GET", "/users/{user_id}", user_id=bot_id)
        r = await client.http.request(route)
        if r.status == 404:
            return await ctx.send(content="Bot not found!")
        user_data = await r.json()
        if not user_data.get("bot", False):
            return await ctx.send(content="User is not a bot")

        avatar = f"https://cdn.discordapp.com/avatars/{bot_id}/{user_data['avatar']}"
        secret_key = "".join(choices(ascii_letters + digits, k=40))

        try:
            bot_data_table.insert_one({"_id": int(bot_id), "icon": avatar, "name": user_data["username"]})
            bot_tokens_table.insert_one({"_id": int(bot_id), "token": secret_key})
        except:
            return await ctx.send(content="Bot is already added")

        await ctx.send(content=f"Ok! Created bot. Token: ||{secret_key}||")


client.token = env["TOKEN"]
client.run()
