from commands.command import Command
import asyncio
import utils

class ToonsCommand(Command):

	@asyncio.coroutine
	def execute(self, client, input, inventory, channel):
		toons_str = ""
		i = 0
		for name in inventory.toons_name_list:
			toons_str = toons_str + name + "\n"
			i = i + 1
			if i == 100:
				yield from utils.embed_and_send(client, channel, 'Toons', toons_str)
				i = 0
				toons_str = ""

		if i > 0:
			yield from utils.embed_and_send(client, channel, 'Toons', toons_str)
		