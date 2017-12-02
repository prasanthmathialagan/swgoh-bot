import discord
import asyncio
import syslog
from commands.interpreter import CommandInterpreter
from inventory import Inventory
import utils
import time
import os.path

html_cache_dir = "/media/pi/KINGSTON/html_cache"
timestamp_file = "last_updated_timestamp.bot"

# Inventory refresh interval (6 hours)
inventory_refresh_interval = 6*60*60

interpreter = CommandInterpreter()
inventory = Inventory(html_cache_dir, False)
client = discord.Client()

def get_last_updated_time():
    if os.path.isfile(timestamp_file):
        return int(open(timestamp_file, 'r').read())

    return None

last_updated_time = get_last_updated_time()

def update_last_updated_time():
    global last_updated_time

    last_updated_time = int(time.time())
    f = open(timestamp_file, 'w+')
    f.write(str(last_updated_time))
    f.close()

if last_updated_time is None:
    update_last_updated_time()

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
    global inventory

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

    # Refresh the inventory
    current_time = int(time.time())
    if current_time > (last_updated_time + inventory_refresh_interval):
        try:
            yield from client.send_typing(message.channel)
            new_inv = Inventory(html_cache_dir, True)
            inventory = new_inv
        except Exception as e:
            syslog.syslog(str(e))
            syslog.syslog("Unable to refresh the data. Will try during the next refresh period")
        finally:
            update_last_updated_time()

    yield from command_handler.execute(client, utils.strip_spaces_and_join(words[1:]), inventory, message.channel)

client.run('MzYwNTA3NTM5OTc4MzIxOTIw.DKWkWA.yx-yMLKqkEegLnthB3wYkNmvXS8')