from commands.command import Command
import asyncio

class HelpCommand(Command):

	@asyncio.coroutine
	def execute(self, client, input, inventory, channel):
		output = "Command \n" \
                " **help** - Displays all the commands\n" \
                " **toons** - Lists all the toons\n" \
                " **ships** - Lists all the ships\n" \
                " **members** - Lists all the Guild members\n" \
                " **zetas** - Lists all the zetas in the guild\n" \
                " **guild-member <name>** - Lists the toons for the member\n" \
                " **cls-ready <member>** - Checks if the member is ready for CLS event\n" \
                " **thrawn-ready <member>** - Checks if the member is ready for Thrawn event\n" \
                " **jtr-ready <member>** - Checks if the member is ready for JTR event\n" \
                " **member-toon <toon name>** - Lists the members with the given toon\n" \
                " **member-ship <ship name>** - Lists the members with the given ship\n"
		yield from client.send_message(channel, output)