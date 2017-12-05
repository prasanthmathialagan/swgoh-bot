import discord
import asyncio
import syslog
from commands.interpreter import CommandInterpreter
from inventory import Inventory
import utils
import time
import os.path
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import datetime

scheduler = AsyncIOScheduler()
scheduler.start()

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

notifications_channel = None
main_channel = None

@client.event
@asyncio.coroutine
def on_ready():
    global notifications_channel, main_channel

    syslog.syslog('Logged in as')
    syslog.syslog(client.user.name)
    syslog.syslog(client.user.id)
    syslog.syslog('------')
    for server in client.servers:
        print(str(server.id) + ", " + str(server.name))
        for channel in server.channels:
            print("----->" + str(channel.id) + ", " + str(channel.name))
            if server.name == 'Guild notifications' and channel.name == 'general':
                notifications_channel = channel
            elif server.name == 'SWGOH Guild Raiders' and channel.name == 'general':
                main_channel = channel

    # Notify guild activity reset every day at midnight and after reset
    scheduler.add_job(notify_guild_activity_midnight, trigger='cron', minute='0', hour="0")
    scheduler.add_job(notify_guild_activity_after_reset, trigger='cron', minute='30', hour="17")

    yield from utils.embed_and_send(client, notifications_channel, 'Welcome', 'Greeter is online!')

@asyncio.coroutine
def notify_guild_activity_after_reset():
    now = datetime.datetime.now()
    day = now.strftime("%A")

    activity=""
    if day == "Sunday":
        activity = "Spend Cantina energy\nSave Normal Energy"
    elif day == "Monday":
        activity = "Spend Normal energy on Light Side Battles"
    elif day == "Tuesday":
        activity = "Complete Galactic War Battles (24 with restart)\nSave Normal Energy"
    elif day == "Wednesday":
        activity = "Spend Normal energy on Hard Mode Battles"
    elif day == "Thursday":
        activity = "Complete Daily Challenges (10)\nSave Normal Energy"
    elif day == "Friday":
        activity = "Spend Normal energy on Dark Side Battles"
    elif day == 'Saturday':
        activity = "Complete Arena Battles (5)"

    syslog.syslog("Sending guild activity reminder after reset for %s, activity = %s!!!!" % (day, activity))
    yield from utils.embed_and_send(client, main_channel, 'Guild Activity Reminder after reset (' + day + ')', activity)

@asyncio.coroutine
def notify_guild_activity_midnight():
    now = datetime.datetime.now()
    day = now.strftime("%A")

    activity=""
    if day == "Sunday":
        activity = "Complete Arena Battles (5)\nSave Cantina energy"
    elif day == "Monday":
        activity = "Spend Cantina Energy\nSave Normal energy\nSave Galactic War (after restart)"
    elif day == "Tuesday":
        activity = "Spend Normal energy on Light Side Battles\nSave Galactic War (with restart available)"
    elif day == "Wednesday":
        activity = "Complete Galactic War Battles (12)\nSave Normal Energy"
    elif day == "Thursday":
        activity = "Spend Normal energy on Hard Mode Battles\nSave Daily Challenges"
    elif day == "Friday":
        activity = "Complete Daily Challenges (10)\nSave Normal energy"
    elif day == 'Saturday':
        activity = "Spend Normal energy on Dark Side Battles\nSave Arena Battles"

    syslog.syslog("Sending guild activity reminder before reset for %s, activity = %s!!!!" % (day, activity))
    yield from utils.embed_and_send(client, main_channel, 'Guild Activity Reminder before reset (' + day + ')', activity)

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