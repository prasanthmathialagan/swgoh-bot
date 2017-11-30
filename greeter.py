import discord
import asyncio
import syslog
from commands.interpreter import CommandInterpreter
from inventory import Inventory
import utils

html_cache_dir = "/media/pi/KINGSTON/html_cache"

interpreter = CommandInterpreter()
inventory = Inventory(html_cache_dir)
client = discord.Client()

@client.event
@asyncio.coroutine
def on_ready():
    syslog.syslog('Logged in as')
    syslog.syslog(client.user.name)
    syslog.syslog(client.user.id)
    syslog.syslog('------')

@client.event
@asyncio.coroutine
def on_message(message):
    bot_handle = '<@' + client.user.id + '>'
    if not message.content.startswith(bot_handle):
        return

    msg = message.content.replace(bot_handle, '').strip()
    words = msg.split(' ')
    if len(words) == 0:
        return

    # greeter assumes that the first word is always a command
    cmd = words[0].lower()
    command_handler = interpreter.interpret(cmd)
    yield from command_handler.execute(client, utils.strip_spaces_and_join(words[1:]), inventory, message.channel)

client.run('MzYwNTA3NTM5OTc4MzIxOTIw.DKWkWA.yx-yMLKqkEegLnthB3wYkNmvXS8')