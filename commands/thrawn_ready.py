from commands.command import Command
import asyncio
import utils

class ThrawnReadyCommand(Command):

	@asyncio.coroutine
	def execute(self, client, input, inventory, channel):
		if len(input) == 0:
			yield from client.send_message(channel, "Must supply a name. Usage: @greeter thrawn-ready celessa")
			return

		member_name = utils.find_closest_match(input, inventory.members_name_list)
		if member_name is None:
			yield from client.send_message(channel, 'No results found for ' + input + '. Check the supplied name. Use @greeter members to get correct name')
			return
		else:
			yield from client.send_message(channel, 'Closest match is ' + member_name + '.')

		# Actual logic for finding Thrawn readiness
		thrawn_rarity = None
		table_data = inventory.get_specific_toons_data_for_member(member_name, ['Grand Admiral Thrawn'])
		if len(table_data) == 1:
			thrawn_rarity = table_data[0][1]
			if thrawn_rarity == 7: #rarity 
				yield from client.send_message(channel, member_name + ' already has a 7* Thrawn')
				return

		req_toons = ['Ezra Bridger', 'Chopper', 'Garazeb "Zeb" Orrelios', 'Hera Syndulla', 'Kanan Jarrus', 'Sabine Wren']
		table_data = inventory.get_specific_toons_data_for_member(member_name, req_toons)
		copy_req_toons = list(req_toons)

		output = []
		satisfiedCount = 0
		for row in table_data:
			name = row[0]
			rarity = row[1]
			if rarity < 7:
				if thrawn_rarity is None and rarity >= 5: # if Thrawn is not there, 5* Phoenix is enough
					satisfiedCount = satisfiedCount + 1
				else:
					output.append([name, rarity])
			else:
				satisfiedCount = satisfiedCount + 1
			copy_req_toons.remove(name)

		if len(req_toons) > 0:
			for name in copy_req_toons:
				output.append([name, 'Locked'])

		if satisfiedCount >= 5:
			if thrawn_rarity is None:
				yield from client.send_message(channel, member_name + ' does not have Thrawn yet but has the toons required for unlocking him at 5*')
			else:
				yield from client.send_message(channel, member_name + ' has Thrawn at ' + str(thrawn_rarity) + ' and has the toons required for upgrading him to 7*')
			return

		if thrawn_rarity is None:
			yield from client.send_message(channel, member_name + ' does not have Thrawn and need to farm following toons to 5* for unlocking him at 5*')
		else:
			yield from client.send_message(channel, member_name + ' has Thrawn at ' + str(thrawn_rarity) + ' and need to farm following toons to 7* for upgrading him to 7*')

		yield from utils.send_as_table(output, ['Toon', 'Current rarity'], 30, channel, client) 