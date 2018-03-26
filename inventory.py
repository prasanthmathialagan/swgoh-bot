import web_pages_cache
import json
from bs4 import BeautifulSoup
from terminaltables import AsciiTable
from operator import itemgetter
import csv
import os
import utils

class Inventory(object):
    toons_url = "https://swgoh.gg/api/characters/?format=json"
    members_url = "https://swgoh.gg/g/11097/swgoh-guild-raiders/"
    guild_toons_url = "https://swgoh.gg/api/guilds/11097/units/"
    zetas_url = "https://swgoh.gg/g/11097/swgoh-guild-raiders/zetas/"
    ships_url = "https://swgoh.gg/api/ships/?format=json"
    data_dir = "data"
    toons_aliases_url = "https://raw.githubusercontent.com/jmiln/SWGoHBot/master/data/characters.json"
    ships_aliases_url = "https://raw.githubusercontent.com/jmiln/SWGoHBot/master/data/ships.json"

    def __init__(self, html_cache_dir, refresh=False):
        self.refresh = refresh
        self.html_cache_dir = html_cache_dir

        # ----------------------------------
        # Characters
        # ----------------------------------
        self.member_to_toons_dict = {}
        self.toon_to_members_dict = {}

        self.toons_name_list = []
        self.toons_obj_list = []
        self.toons_aliases = {}

        self.base_id_to_toon_name_dict = {}

        self.populate_toons()
        self.populate_aliases("characters.json", self.toons_aliases_url, self.toons_aliases)

        # ----------------------------------

        # ----------------------------------
        # Ships
        # ----------------------------------
        self.member_to_ships_dict = {}
        self.ship_to_members_dict = {}

        self.ships_str = ""
        self.ships_name_list = []
        self.ships_obj_list = []
        self.ships_aliases = {}

        self.base_id_to_ship_name_dict = {}

        self.populate_ships()
        self.populate_aliases("ships.json", self.ships_aliases_url, self.ships_aliases)
        # ----------------------------------

        # ----------------------------------
        # Members
        # ----------------------------------
        self.members_table = None
        self.members_name_list = []

        self.populate_members()
        # ----------------------------------

        # ----------------------------------
        # Guild data
        # ----------------------------------
        self.populate_guild_data()
        # ----------------------------------

        # ----------------------------------
        # Zetas
        # ----------------------------------
        self.zetas_data = []

        self.zetas()
        # ----------------------------------

        self.refresh = False

    def populate_toons(self):
        s = web_pages_cache.get_from_cache(self.html_cache_dir, "toons.json", self.toons_url, self.refresh)
        self.toons_obj_list = json.loads(s)
        for i in self.toons_obj_list:
            n = i['name']
            self.toons_name_list.append(n)
            self.base_id_to_toon_name_dict[i['base_id']] = n
            self.toon_to_members_dict[n] = []

    def populate_aliases(self, aliases_data_file, aliases_url, output_dict):
        s = web_pages_cache.get_from_cache(self.data_dir, aliases_data_file, aliases_url, False)
        obj_list = json.loads(s)
        for obj in obj_list:
            name = obj['name']
            aliases = obj['aliases']
            for alias in aliases:
                alias = alias.lower()
                names = output_dict.get(alias, [])
                names.append(name)
                output_dict[alias] = names

    def populate_ships(self):
        s = web_pages_cache.get_from_cache(self.html_cache_dir, "ships.json", self.ships_url, self.refresh)
        self.ships_obj_list = json.loads(s)
        for i in self.ships_obj_list:
            n = i['name']
            self.ships_name_list.append(n)
            self.ships_str = self.ships_str + n + "\n"
            self.base_id_to_ship_name_dict[i['base_id']] = n
            self.ship_to_members_dict[n] = []

    def populate_members(self):
        s = web_pages_cache.get_from_cache(self.html_cache_dir, "guild_members.html", self.members_url, self.refresh)
        soup = BeautifulSoup(s, 'html.parser')

        base = "body > div.container.p-t-md > div.content-container > div.content-container-primary.character-list " \
               "> ul > li.media.list-group-item.p-0.b-t-0 > div > table > tbody > tr > td"

        members = soup.select(base)
        i = 1
        j = 1
        mem_local = []
        table_data = []
        for m in members:
            if i % 5 == 1:
                a = m.find('a')
                user_id = a['href'].split("/")[2]
                name = a.find("strong").text
                self.member_to_toons_dict[name] = []
                self.member_to_ships_dict[name] = []
                self.members_name_list.append(name)
                
                mem_local.append(j)
                mem_local.append(user_id)
                mem_local.append(name)

                j = j + 1
            if i % 5 == 2:
                mem_local.append(m.text)
                table_data.append(mem_local)
                mem_local = []

            i = i + 1

        # Manual entries
        with open('data/members.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                name = row[1]
                self.member_to_toons_dict[name] = []
                self.member_to_ships_dict[name] = []
                self.members_name_list.append(name)
                table_data.append([j, row[0], row[1], ""])
                j = j + 1

        self.members_table = table_data

    def populate_guild_data(self):
        s = web_pages_cache.get_from_cache(self.html_cache_dir, "guild_toons.dict", self.guild_toons_url, self.refresh)
        dict = eval(s)
        for key, values in dict.items():
            name = self.base_id_to_toon_name_dict.get(key, None)
            if name is not None:
                for value in values:
                    self.toon_to_members_dict[name].append({"gear_level": value['gear_level'], \
                                                            "power": value['power'], \
                                                            "level": value['level'], \
                                                            "rarity": value['rarity'], \
                                                            "player": value['player']})
                    self.member_to_toons_dict[value['player']].append({"gear_level": value['gear_level'], \
                                                                       "power": value['power'], \
                                                                       "level": value['level'], \
                                                                       "rarity": value['rarity'], \
                                                                       "toon": name})
            # ship
            else:
                ship = self.base_id_to_ship_name_dict.get(key, None)
                if ship is None:
                    print("Skipping")
                    continue

                for value in values:
                    self.ship_to_members_dict[ship].append({"power": value['power'], \
                                                            "level": value['level'], \
                                                            "rarity": value['rarity'], \
                                                            "player": value['player']})
                    self.member_to_ships_dict[value['player']].append({"power": value['power'], \
                                                                       "level": value['level'], \
                                                                       "rarity": value['rarity'], \
                                                                       "ship": ship})

        # Manually added data
        with open('data/members.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                user = row[0]
                if os.path.isfile('data/' + user + '.csv'):
                    print('Fetching data for the user ' + user)
                    with open('data/' + user + '.csv', 'r') as user_file:
                        user_reader = csv.reader(user_file)
                        for user_reader_row in user_reader:
                            name = self.base_id_to_toon_name_dict[user_reader_row[0]];
                            self.toon_to_members_dict[name].append({"gear_level": "-", \
                                                                    "power": 0, \
                                                                    "level": "-", \
                                                                    "rarity": user_reader_row[1], \
                                                                    "player": row[1]})
                            self.member_to_toons_dict[row[1]].append({"gear_level": "-", \
                                                                               "power": 0, \
                                                                               "level": "-", \
                                                                               "rarity": user_reader_row[1], \
                                                                               "toon": name})
                else:
                    print('Data not available for the user ' + user)


    def toons_for_member(self, name):
        table_data = []

        list = self.member_to_toons_dict[name]
        list = sorted(list, key=itemgetter('power'), reverse=True)

        i = 1
        for elem in list:
            table_data.append([i, elem['toon'], elem['rarity'], elem['gear_level'], elem['power']])
            i = i + 1

        return table_data

    def players_with_toon(self, name):
        table_data = []

        list = self.toon_to_members_dict[name]
        list = sorted(list, key=itemgetter('power'), reverse=True)

        i = 1
        for elem in list:
            table_data.append([i, elem['player'], elem['rarity'], elem['gear_level'], elem['power']])
            i = i + 1

        return table_data

    def players_with_ship(self, name):
        table_data = []

        list = self.ship_to_members_dict[name]
        list = sorted(list, key=itemgetter('power'), reverse=True)

        i = 1
        for elem in list:
            table_data.append([i, elem['player'], elem['rarity'], elem['power']])
            i = i + 1

        return table_data

    def get_specific_toons_data_for_member(self, member, toons_names):
        toons_list = self.member_to_toons_dict[member]

        table_data = []
        for elem in toons_list:
            name = elem['toon']
            if utils.find_case_insensitive_exact_match(name, toons_names) is None:
                continue
            rarity = elem['rarity']
            table_data.append([name, rarity])

        return table_data

    def zetas(self):
        s = web_pages_cache.get_from_cache(self.html_cache_dir, "zetas.html", self.zetas_url, self.refresh)
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

                    self.zetas_data.append([m_name, t_name, ability['title']])
