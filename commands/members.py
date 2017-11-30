from commands.command import Command
import asyncio

class MembersCommand(Command):

	@asyncio.coroutine
	def execute(self, client, input, inventory, channel):
	       yield from client.send_message(channel, '```' + inventory.members_table.table + '```')