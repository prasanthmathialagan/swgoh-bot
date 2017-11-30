from commands.command import Command
import asyncio

class ToonsCommand(Command):

	@asyncio.coroutine
	def execute(self, client, input, inventory, channel):
	       yield from client.send_message(channel, '```' + inventory.toons_str + '```')