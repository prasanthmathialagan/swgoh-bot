from commands.command import Command
import asyncio
import utils

class ShipsCommand(Command):

	@asyncio.coroutine
	def execute(self, client, input, inventory, channel):
		yield from utils.embed_and_send(client, channel, 'Ships', inventory.ships_str)