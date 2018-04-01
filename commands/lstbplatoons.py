from commands.command import Command
import asyncio
import utils

class LSTBPlatoonsCommand(Command):

	allowed_phases = ['P1', 'P2-1', 'P2-2', 'P3-1', 'P3-2', 'P3-3', 'P4-1', 'P4-2', 'P4-3', 'P5-1', 'P5-2', 'P5-3', 'P6-1', 'P6-2', 'P6-3']

	@asyncio.coroutine
	def execute(self, client, input, inventory, channel):
		if len(input) == 0:
			yield from utils.embed_and_send(client, channel, "Light Side TB Platoons", "Must supply a phase. Usage: @greeter lbtbplatoons P4-1")
			return

		phase = input.upper()
		if phase not in self.allowed_phases:
			yield from utils.embed_and_send(client, channel, "Light Side TB Platoons", "Not a valid phase. Valid phases = " + str(self.allowed_phases))
			return

		platoons_info = inventory.lstbplatoons_dict.get(phase, None)
		if platoons_info is None:
			yield from utils.embed_and_send(client, channel, "Light Side TB Platoons", "Information not available for " + phase + " from the last TB")
			return

		if len(platoons_info['items']) == 0:
			yield from utils.embed_and_send(client, channel, "Light Side TB Platoons", "All the platoons in " + phase + " were filled in the last TB")
			return

		rarity = platoons_info['rarity']
		items = platoons_info['items']
		yield from utils.embed_and_send(client, channel, "Light Side TB Platoons", "During last TB, we fell short of following toons/ships at " + str(rarity) + "* to complete the platoons in " + phase)

		headers = ['Toon/Ship', 'Deficit']
		table_data = []

		for i in items:
			table_data.append([i['name'], i['count']])

		yield from utils.send_as_table(table_data, headers, 20, channel, client)