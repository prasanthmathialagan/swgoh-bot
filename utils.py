import asyncio
from terminaltables import AsciiTable
import discord

def strip_spaces_and_join(args):
    output = ""
    for arg in args:
        arg = arg.strip()
        if len(arg) != 0:
            if len(output) == 0:
                output = arg
            else:
                output = output + " " + arg
    return output

def find_closest_match(name, list):
    for l in list:
        if name.lower() in l.lower():
            return l

    return None

def find_case_insensitive_exact_match(name, list):
    for l in list:
        if name.lower() == l.lower():
            return l

    return None

def find_alias_matches(name, aliases):
    return aliases.get(name.lower(), [])

@asyncio.coroutine
def send_as_table(data, headers, batch_size, channel, client):
    chunk = []
    for row in data:
        chunk.append(row)
        if len(chunk) == batch_size:
            chunk.insert(0, headers)
            ascii = AsciiTable(chunk)
            yield from client.send_message(channel, '```' + ascii.table + '```')
            chunk = []

    if len(chunk) > 0:
        chunk.insert(0, headers)
        ascii = AsciiTable(chunk)
        yield from client.send_message(channel, '```' + ascii.table + '```')


@asyncio.coroutine
def embed_and_send(client, channel, tit, desc, col=0xDEADBF):
    em = discord.Embed(title=tit, description=desc, color=col)
    yield from client.send_message(channel, embed=em)