from commands.help import HelpCommand
from commands.ping import PingCommand
from commands.hello import HelloCommand
from commands.toons import ToonsCommand
from commands.members import MembersCommand
from commands.guild_member import GuildMemberCommand
from commands.member_toon import MemberToonCommand
from commands.zetas import ZetasCommand


class CommandInterpreter(object):

    def __init__(self):
        self.commands = {}
        self.populate_commands()

    def populate_commands(self):
        self.commands['help'] = HelpCommand('help')
        self.commands['ping'] = PingCommand('ping')
        self.commands['hello'] = HelloCommand('hello')
        self.commands['toons'] = ToonsCommand('toons')
        self.commands['members'] = MembersCommand('members')
        self.commands['guild-member'] = GuildMemberCommand('guild-member')
        self.commands['member-toon'] = MemberToonCommand('member-toon')
        self.commands['zetas'] = ZetasCommand('zetas')

    def interpret(self, name):
        try:
            return self.commands[name]
        except KeyError:
            return self.commands['help']
