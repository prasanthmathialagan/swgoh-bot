import discord
import asyncio
from terminaltables import AsciiTable
import syslog
import web_pages_cache
import json
from bs4 import BeautifulSoup
from operator import itemgetter

html_cache_dir = "/media/pi/KINGSTON/html_cache"

member_to_toons_dict = {}
toon_to_members_dict = {}

toons = ""
toons_list = []
toons_obj_list = None
base_id_to_toon_name_dict = {}
def populate_toons():
    global toons, toons_list, toons_obj_list, base_id_to_toon_name_dict, toon_to_members_dict

    toons_url = "https://swgoh.gg/api/characters/?format=json"
    s = web_pages_cache.get_from_cache(html_cache_dir, "toons.json", toons_url)
    toons_obj_list = json.loads(s)
    for i in toons_obj_list:
        n = i['name']
        toons_list.append(n)
        toons = toons + n + "\n"
        base_id_to_toon_name_dict[i['base_id']] = n
        toon_to_members_dict[n] = []

populate_toons()

members_table = None
members_list = []
def populate_members():
    global members_table, members_list, member_to_toons_dict

    members_url = "https://swgoh.gg/g/11097/swgoh-guild-raiders/"
    s = web_pages_cache.get_from_cache(html_cache_dir, "guild_members.html", members_url)
    soup = BeautifulSoup(s, 'html.parser')

    base = "body > div.container.p-t-md > div.content-container > div.content-container-primary.character-list " \
           "> ul > li.media.list-group-item.p-0.b-t-0 > div > table > tbody > tr > td > a"

    members = soup.select(base)
    table_data = [['UserID', 'Name']]
    for m in members:
        user_id = m['href'].split("/")[2]
        name = m.find("strong").text
        table_data.append([user_id, name])
        members_list.append(name)
        member_to_toons_dict[name] = []

    members_table = AsciiTable(table_data)

populate_members()

zetas_data = []
def zetas():
    zetas_url = "https://swgoh.gg/g/11097/swgoh-guild-raiders/zetas/"
    s = web_pages_cache.get_from_cache(html_cache_dir, "zetas.html", zetas_url)
    soup = BeautifulSoup(s, 'html.parser')

    base = "body > div.container.p-t-md > div.content-container > div.content-container-primary.character-list " \
           "> ul > li.media.list-group-item.p-0.b-t-0 > div > table > tbody > tr"

    all_zetas = soup.select(base)
    # every <tr> --> 1 player
    for z in all_zetas:
        zeta_details_for_member = z.findAll('td')
        member_name = zeta_details_for_member[0].find("strong").text
        zetas_for_member = zeta_details_for_member[2].findAll("div", class_="guild-member-zeta")
        for zeta in zetas_for_member:
            toon = zeta.find('div', class_='guild-member-zeta-character').find('img')['alt']
            abilities = zeta.find('div', class_='guild-member-zeta-abilities').findAll('img')
            for ability in abilities:
                m_name = ""
                t_name = ""

                if member_name is not None:
                    m_name = member_name
                    member_name = None

                if toon is not None:
                    t_name = toon
                    toon = None

                zetas_data.append([m_name, t_name, ability['title']])

zetas()

def populate_guild_data():
    global base_id_to_toon_name_dict, member_to_toons_dict, toon_to_members_dict

    guild_toons_url = "https://swgoh.gg/api/guilds/11097/units/"
    s = web_pages_cache.get_from_cache(html_cache_dir, "guild_toons.dict", guild_toons_url)
    dict = eval(s)
    for key, values in dict.items():
        name = base_id_to_toon_name_dict.get(key, None)
        if name is None:
            print("Skipping " + key)
            continue

        for value in values:
            toon_to_members_dict[name].append({"gear_level": value['gear_level'], \
                                                "power": value['power'], \
                                                "level": value['level'], \
                                                "rarity": value['rarity'], \
                                                "player": value['player']})
            member_to_toons_dict[value['player']].append({"gear_level": value['gear_level'], \
                                               "power": value['power'], \
                                               "level": value['level'], \
                                               "rarity": value['rarity'], \
                                               "toon": name})

populate_guild_data()

def strip_spaces_and_join(args):
    output = ""
    for arg in args:
        arg = arg.strip()
        if len(arg) != 0:
            if len(output) == 0:
                output = arg
            else:
                output = output + " " + arg
    return output

def find_closest_match(name, list):
    for l in list:
        if name.lower() in l.lower():
            return l

    return None

def toons_for_member(name):
    table_data=[]

    list = member_to_toons_dict[name]
    list = sorted(list, key=itemgetter('power'), reverse=True)

    i = 1
    for elem in list:
        table_data.append([i, elem['toon'], elem['rarity'], elem['gear_level'], elem['power']])
        i = i + 1

    return table_data

def fn_players_with_toon(name):
    table_data=[]

    list = toon_to_members_dict[name]
    list = sorted(list, key=itemgetter('power'), reverse=True)

    i = 1
    for elem in list:
        table_data.append([i, elem['player'], elem['rarity'], elem['gear_level'], elem['power']])
        i = i + 1

    return table_data

@asyncio.coroutine
def send_as_table(data, headers, batch_size, channel):
    chunk = []
    for row in data:
        chunk.append(row)
        if len(chunk) == batch_size:
            chunk.insert(0, headers)
            ascii = AsciiTable(chunk)
            yield from client.send_message(channel, '```' + ascii.table + '```')
            chunk = []

    if len(chunk) > 0:
        chunk.insert(0, headers)
        ascii = AsciiTable(chunk)
        yield from client.send_message(channel, '```' + ascii.table + '```')

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

    cmd = words[0].lower()
    if cmd == 'help':
        output = "Command \n" \
                " **help** - Displays all the commands\n" \
                " **ping** - Responds with a Pong\n" \
                " **hello** - Greets you\n" \
                " **toons** - Lists all the toons\n" \
                " **members** - Lists all the Guild members\n" \
                " **zetas** - Lists all the zetas in the guild\n" \
                " **guild-member <name>** - Lists the toons for the member\n" \
                " **member-toon <toon name>** - Lists the members with the given toon\n" \
                # " **challenges** - Shows the daily guild challenges\n" \
                # " **activities** - Shows the daily guild activities\n" \
                # " **mods** - Shows some suggested mods for the specified character\n" \
                # " **raidteams** - Shows some teams that work well for each raid.\n"

        yield from client.send_message(message.channel, output)
    elif cmd == 'ping':
        yield from client.send_message(message.channel, "Pong!")
    elif cmd == 'hello':
        yield from client.send_message(message.channel, 'Hello <@' + str(message.author.id) + '>')
    elif cmd == 'toons':
        yield from client.send_message(message.channel, '```' + toons + '```')
    elif cmd == 'members':
        yield from client.send_message(message.channel, '```' + members_table.table + '```')
    elif cmd == 'zetas':
        yield from send_as_table(zetas_data, ['Member', 'Toon', 'Ability'], 20, message.channel)
    elif cmd == 'guild-member':
        member_name = strip_spaces_and_join(words[1:])
        if len(member_name) == 0:
            yield from client.send_message(message.channel, "Must supply a name. Usage: @greeter guild-member celessa")
            return

        closest_match = find_closest_match(member_name, members_list)
        if closest_match is None:
            yield from client.send_message(message.channel, 'No results found for ' + member_name + '. Check the supplied name. Use @greeter members to get correct name')
            return
        else:
            yield from client.send_message(message.channel, 'Closest match is ' + closest_match + '.')

        toons_for_player = toons_for_member(closest_match)
        if toons_for_player is None or len(toons_for_player) == 0:
            yield from client.send_message(message.channel, 'Toons information is not available for ' + member_name + '.')
            return
        else:
            yield from send_as_table(toons_for_player, ['No', 'Toon', 'Star', 'Gear', 'GP'], 30, message.channel)
    elif cmd == 'member-toon':
        toon_name = strip_spaces_and_join(words[1:])
        if len(toon_name) == 0:
            yield from client.send_message(message.channel, "Must supply a toon name. Usage: @greeter member-toon lobot")
            return

        closest_match = find_closest_match(toon_name, toons_list)
        if closest_match is None:
            yield from client.send_message(message.channel, 'No results found for ' + toon_name + '. Check the supplied name. Use @greeter toons to get correct name')
            return
        else:
            yield from client.send_message(message.channel, 'Closest match is ' + closest_match + '.')

        players_with_toon = fn_players_with_toon(closest_match)
        if players_with_toon is None or len(players_with_toon) == 0:
            yield from client.send_message(message.channel, 'Shame!! There is no player in the guild with ' + toon_name + '.')
            return
        else:
            yield from send_as_table(players_with_toon, ['No', 'Member', 'Star', 'Gear', 'GP'], 30, message.channel)
    elif cmd == 'stats':
        member_name = find_closest_match(words[1].strip(), members_list)
        toon_name = find_closest_match(words[2].strip(), toons_list)

        if member_name is None:
            yield from client.send_message(message.channel, 'Member name ' + words[1] + ' is not valid')
        elif toon_name is None:
            yield from client.send_message(message.channel, 'Toon name ' + words[2] + ' is not valid')
        else:
            # get the user id from user name
            # TODO
            url = "https://swgoh.gg/u/weldon/collection/finn"
            web_pages_cache.get_from_cache(html_cache_dir, "weldon_finn", url)
            yield from client.send_message(message.channel, 'It is a work in progress!!')
    elif cmd == 'challenges':
        yield from client.send_message(message.channel, ";challenges")
    elif cmd == 'activities':
        yield from client.send_message(message.channel, ";activities")
    elif cmd == 'mods':
        yield from client.send_message(message.channel, ";mods")
    elif cmd == 'raidteams':
        yield from client.send_message(message.channel, ";raidteams")

client.run('MzYwNTA3NTM5OTc4MzIxOTIw.DKWkWA.yx-yMLKqkEegLnthB3wYkNmvXS8')