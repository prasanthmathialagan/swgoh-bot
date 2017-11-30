import web_pages_cache
import json
from bs4 import BeautifulSoup
from terminaltables import AsciiTable
from operator import itemgetter


class Inventory(object):
    toons_url = "https://swgoh.gg/api/characters/?format=json"
    members_url = "https://swgoh.gg/g/11097/swgoh-guild-raiders/"
    guild_toons_url = "https://swgoh.gg/api/guilds/11097/units/"
    zetas_url = "https://swgoh.gg/g/11097/swgoh-guild-raiders/zetas/"
    ships_url = "https://swgoh.gg/api/ships/?format=json"

    def __init__(self, html_cache_dir):
        self.html_cache_dir = html_cache_dir

        # ----------------------------------
        # Characters
        # ----------------------------------
        self.member_to_toons_dict = {}
        self.toon_to_members_dict = {}

        self.toons_str = ""
        self.toons_name_list = []
        self.toons_obj_list = []

        self.base_id_to_toon_name_dict = {}

        self.populate_toons()
        # ----------------------------------

        # ----------------------------------
        # Ships
        # ----------------------------------
        self.member_to_ships_dict = {}
        self.ship_to_members_dict = {}

        self.ships_str = ""
        self.ships_name_list = []
        self.ships_obj_list = []

        self.base_id_to_ship_name_dict = {}

        self.populate_ships()
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

    def populate_toons(self):
        s = web_pages_cache.get_from_cache(self.html_cache_dir, "toons.json", self.toons_url)
        self.toons_obj_list = json.loads(s)
        for i in self.toons_obj_list:
            n = i['name']
            self.toons_name_list.append(n)
            self.toons_str = self.toons_str + n + "\n"
            self.base_id_to_toon_name_dict[i['base_id']] = n
            self.toon_to_members_dict[n] = []

    def populate_ships(self):
        s = web_pages_cache.get_from_cache(self.html_cache_dir, "ships.json", self.ships_url)
        self.ships_obj_list = json.loads(s)
        for i in self.ships_obj_list:
            n = i['name']
            self.ships_name_list.append(n)
            self.ships_str = self.ships_str + n + "\n"
            self.base_id_to_ship_name_dict[i['base_id']] = n
            self.ship_to_members_dict[n] = []

    def populate_members(self):
        s = web_pages_cache.get_from_cache(self.html_cache_dir, "guild_members.html", self.members_url)
        soup = BeautifulSoup(s, 'html.parser')

        base = "body > div.container.p-t-md > div.content-container > div.content-container-primary.character-list " \
               "> ul > li.media.list-group-item.p-0.b-t-0 > div > table > tbody > tr > td > a"

        members = soup.select(base)
        table_data = [['UserID', 'Name']]
        for m in members:
            user_id = m['href'].split("/")[2]
            name = m.find("strong").text
            table_data.append([user_id, name])
            self.members_name_list.append(name)
            self.member_to_toons_dict[name] = []
            self.member_to_ships_dict[name] = []

        self.members_table = AsciiTable(table_data)

    def populate_guild_data(self):
        s = web_pages_cache.get_from_cache(self.html_cache_dir, "guild_toons.dict", self.guild_toons_url)
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

    def zetas(self):
        s = web_pages_cache.get_from_cache(self.html_cache_dir, "zetas.html", self.zetas_url)
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