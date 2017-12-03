from commands.command import Command
import asyncio
import utils

class ToonsCommand(Command):

	@asyncio.coroutine
	def execute(self, client, input, inventory, channel):
		yield from utils.embed_and_send(client, channel, 'Toons', inventory.toons_str)