import discord
import os

from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

owner_user_id = os.getenv('OWNER_USER_ID')


intents = discord.Intents.members
client = commands.Bot(command_prefix='!', intents=intents)


def check_user_id(ctx):
    return str(ctx.message.author.id) == owner_user_id

@client.event
async def on_ready():
    print('online')
    await client.change_presence(status=discord.Status.online, activity=None)


@client.command(name='wiggle', help='try and findout')
@commands.dm_only()
@commands.check(check_user_id)
async def wiggle(ctx):
    await ctx.message.author.send('wiggly')


try:
    client.run(TOKEN)
except Exception as e:
    print(str(e))
