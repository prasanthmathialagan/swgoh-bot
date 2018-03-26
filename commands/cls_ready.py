from commands.command import Command
import asyncio
import utils

class CLSReadyCommand(Command):

	@asyncio.coroutine
	def execute(self, client, input, inventory, channel):
		if len(input) == 0:
			yield from client.send_message(channel, "Must supply a name. Usage: @greeter cls-ready celessa")
			return

		closest_match = utils.find_closest_match(input, inventory.members_name_list)
		if closest_match is None:
			yield from client.send_message(channel, 'No results found for ' + input + '. Check the supplied name. Use @greeter members to get correct name')
			return
		else:
			yield from client.send_message(channel, 'Closest match is ' + closest_match + '.')

		# Actual logic for finding CLS readiness
		table_data = inventory.get_specific_toons_data_for_member(closest_match, ['Commander Luke Skywalker'])
		if len(table_data) == 1:
			yield from client.send_message(channel, closest_match + ' already has a 7* Commander Luke Skywalker')
			return

		req_toons = ['Princess Leia', 'Stormtrooper Han', 'Luke Skywalker (Farmboy)', 'R2-D2', 'Obi-Wan Kenobi (Old Ben)']
		table_data = inventory.get_specific_toons_data_for_member(closest_match, req_toons)
		copy_req_toons = list(req_toons)

		output = []
		satisfiedCount = 0
		for row in table_data:
			name = row[0]
			rarity = row[1]
			if rarity != 7:
				output.append([name, rarity])
			else:
				satisfiedCount = satisfiedCount + 1
			copy_req_toons.remove(name)

		if len(req_toons) > 0:
			for name in copy_req_toons:
				output.append([name, 'Locked'])

		if satisfiedCount == 5:
			yield from client.send_message(channel, closest_match + ' does not have Commander Luke Skywalker yet but has the toons required for unlocking him at 7*')
			return

		yield from client.send_message(channel, closest_match + ' does not have Commander Luke Skywalker and need to farm following toons to 7* for unlocking him at 7*')
		yield from utils.send_as_table(output, ['Toon', 'Current rarity'], 30, channel, client) 