import os
import discord
import logging
import json

from dotenv import load_dotenv
from discord.ext import commands

# logging set up 
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='bot.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# load enviromental variables from .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# the id need to be ints
admin_user_id = int(os.getenv('ADMIN_USER_ID'))
owner_user_id = int(os.getenv('OWNER_USER_ID'))
mute_role_id = int(os.getenv('MUTE_ROLE_ID'))
logging_server_id = int(os.getenv('LOGGING_SERVER_ID'))
dm_logging_channel_id = int(os.getenv('DM_LOGGING_CHANNEL_ID'))

dm_auto_response = str(os.getenv('DM_AUTO_RESPONSE'))

#set up the client
intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix='!', intents=intents)

#load the dictionary of bad users from file
f = open('bad_users.json')
bad_json = json.load(f)

# utility functions
async def send_dm(msg):
    receiver = await client.fetch_user(admin_user_id)
    await receiver.create_dm()
    await receiver.dm_channel.send(msg)

# part of the dm verification thing
def check_user_id(ctx):
    return str(ctx.message.author.id) == admin_user_id

def check_owner_id(ctx):
    return str(ctx.message.author.id) == owner_user_id

@client.event
async def on_ready():

    for guild in client.guilds:
        server_info = f'name: {guild.name} id: {guild.id}'
        print(f'{client.user} has connected to server: {server_info}')

    await send_dm(f'{client.user} has come online\n\nUse !list_commands')

@client.event
async def on_member_join(member):

    #give status message
    print(f'member join: user: {member.name} {member.id}')

    # check if the user id is in the bad list
    if str(member.id) in bad_json:

        # find the role
        role = discord.utils.get(member.guild.roles, id=mute_role_id)

        #add the role
        await member.add_roles(role, reason='were on list of bad users')

        #send the alert to the alert reciver
        receiver = await client.fetch_user(admin_user_id)
        await receiver.create_dm()
        await receiver.dm_channel.send(f'the user {member.name} is on the BLACK LIST with id {member.id} just was muted')


'''
    repost dms the bot gets into a server and responds with default message from .env
'''
@client.event
async def on_message(message):
    logging_server = client.get_guild(logging_server_id)
    repost_channel = logging_server.get_channel(dm_logging_channel_id)
    admin_user = await client.fetch_user(admin_user_id)

    if message.guild is None and message.author != admin_user and message.author != client.user:
        await repost_channel.send(f'{message.author} : {message.content}')

    if message.guild is None and message.author != admin_user and message.author != client.user:
        await message.author.send(dm_auto_response)

@client.command(name='list_commands', help='displays the help message')
@commands.dm_only()
@commands.check(check_user_id)
async def list_commands(ctx):
    command_list = []
    command_list.append('```')
    command_list.append('add:  adds a user to the list.  example !add 235345363523534 wraggle#3513\n')
    command_list.append('remove: removes a user from the list.  example !remove 2346235153456346 \n')
    command_list.append('list_users: list all the entries currently watched for. example !list_users \n')
    command_list.append('```')

    await send_dm('\n'.join(command_list))



@client.command(name='add', help='ex: !add 323467245 wraggle#7162  the name is arbitrary')
@commands.dm_only()
@commands.check(check_user_id)
async def add(ctx, user_id: int, user_name: str):

    bad_json[user_id] = user_name
    
    await send_dm(f'{user_name} was added')



@client.command(name='remove', help='ex: !remove 234353245324534')
@commands.dm_only()
@commands.check(check_user_id)
async def remove(ctx, user_id: int):

    user_id = str(user_id).strip()

    if user_id in bad_json:
        user_name = bad_json.get(user_id)
        del bad_json[user_id]
        await send_dm(f'removed {user_id} {user_name} from list')
    else:
        await send_dm('the user_id entered did not match anyting in the list')


@client.command(name='list_users', help='ex: !list_users')
@commands.dm_only()
@commands.check(check_user_id)
async def list_users(ctx):

    for pair in bad_json:
        await send_dm(f'{pair}  {bad_json.get(pair)}')


# run statement
try:
    client.run(TOKEN)

except Exception as e:
    print(str(e))

finally:
    # make sure the dict is written to the file before closing for any reason
    with open('bad_users.json', 'w+') as f:
        json.dump(bad_json, f)
