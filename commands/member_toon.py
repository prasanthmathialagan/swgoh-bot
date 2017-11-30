from commands.command import Command
import asyncio
import utils

class MemberToonCommand(Command):

	@asyncio.coroutine
	def execute(self, client, input, inventory, channel):
		if len(input) == 0:
			yield from client.send_message(channel, "Must supply a toon name. Usage: @greeter member-toon lobot")
			return

		closest_match = utils.find_closest_match(input, inventory.toons_name_list)
		if closest_match is None:
			yield from client.send_message(channel, 'No results found for ' + input + '. Check the supplied name. Use @greeter toons to get correct name')
			return
		else:
			yield from client.send_message(channel, 'Closest match is ' + closest_match + '.')

		players_with_toon = inventory.players_with_toon(closest_match)
		if players_with_toon is None or len(players_with_toon) == 0:
			yield from client.send_message(channel, 'Shame!! There is no player in the guild with ' + input + '.')
			return
		else:
			yield from utils.send_as_table(players_with_toon, ['No', 'Member', 'Star', 'Gear', 'GP'], 30, channel, client)   