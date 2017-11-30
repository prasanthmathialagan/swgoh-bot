from commands.command import Command
import asyncio
import utils

class GuildMemberCommand(Command):

	@asyncio.coroutine
	def execute(self, client, input, inventory, channel):
		if len(input) == 0:
			yield from client.send_message(channel, "Must supply a name. Usage: @greeter guild-member celessa")
			return

		closest_match = utils.find_closest_match(input, inventory.members_name_list)
		if closest_match is None:
			yield from client.send_message(channel, 'No results found for ' + input + '. Check the supplied name. Use @greeter members to get correct name')
			return
		else:
			yield from client.send_message(channel, 'Closest match is ' + closest_match + '.')

		toons_for_player = inventory.toons_for_member(closest_match)
		if toons_for_player is None or len(toons_for_player) == 0:
			yield from client.send_message(channel, 'Toons information is not available for ' + input + '.')
			return
		else:
			yield from utils.send_as_table(toons_for_player, ['No', 'Toon', 'Star', 'Gear', 'GP'], 30, channel, client)
	       