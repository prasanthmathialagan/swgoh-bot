from commands.command import Command
import asyncio
import utils

class MemberShipCommand(Command):

	@asyncio.coroutine
	def execute(self, client, input, inventory, channel):
		if len(input) == 0:
			yield from client.send_message(channel, "Must supply a ship name. Usage: @greeter member-ship Scimitar")
			return

		closest_match = None

		alias_matches = utils.find_alias_matches(input, inventory.ships_aliases)
		if len(alias_matches) == 1:
			closest_match = alias_matches[0]
		elif len(alias_matches) > 1:
			yield from client.send_message(channel,
										   'Multiple results returned' + str(alias_matches) + '. Be specific.')
			return
		else:
			closest_match = utils.find_closest_match(input, inventory.ships_name_list)

		if closest_match is None:
			yield from client.send_message(channel, 'No results found for ' + input + '. Check the supplied name. Use @greeter ships to get correct name')
			return
		else:
			yield from client.send_message(channel, 'Closest match is ' + closest_match + '.')

		players_with_ship = inventory.players_with_ship(closest_match)
		if players_with_ship is None or len(players_with_ship) == 0:
			yield from client.send_message(channel, 'Shame!! There is no player in the guild with ' + input + '.')
			return
		else:
			yield from utils.send_as_table(players_with_ship, ['No', 'Member', 'Star', 'GP'], 30, channel, client)