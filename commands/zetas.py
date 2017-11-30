from commands.command import Command
import asyncio
import utils

class ZetasCommand(Command):

	@asyncio.coroutine
	def execute(self, client, input, inventory, channel):
		yield from utils.send_as_table(inventory.zetas_data, ['Member', 'Toon', 'Ability'], 20, channel, client)