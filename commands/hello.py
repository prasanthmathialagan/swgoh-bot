from commands.command import Command
import asyncio

class HelloCommand(Command):

	@asyncio.coroutine
	def execute(self, client, input, inventory, channel):
	       yield from client.send_message(channel, 'Hello <@' + str(input.author.id) + '>')