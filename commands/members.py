from commands.command import Command
import asyncio
import utils

class MembersCommand(Command):

	@asyncio.coroutine
	def execute(self, client, input, inventory, channel):
		   headers = ['No', 'UserID', 'Name', 'GP']
		   yield from utils.send_as_table(inventory.members_table, headers, 25, channel, client)