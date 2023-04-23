import discord
import configparser
import subprocess
import os
import logging
from logging.handlers import RotatingFileHandler
from subprocess import Popen, PIPE
from discord.ext import commands
import datetime
import time


# load config
config = configparser.ConfigParser()
config.read('config.ini')

TOKEN = config.get('BOT', 'TOKEN')
CHANNEL_ID = int(config.get('BOT', 'CHANNEL_ID'))
SOFTWARE_PATH = config.get('BOT', 'SOFTWARE_PATH')
DEBUG = config.getboolean('BOT', 'DEBUG')
LOG_FILENAME = 'logs/log.txt'
LOG_LEVEL = logging.DEBUG if DEBUG else logging.INFO

# set up logging
logging.basicConfig(level=LOG_LEVEL,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    handlers=[RotatingFileHandler(LOG_FILENAME, maxBytes=1000000, backupCount=1),
                              logging.StreamHandler()])

# set up intents
intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.guilds = True
intents.typing = True

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

@bot.event
async def on_ready():
    logging.info("Logged in as")
    logging.info(bot.user.name)
    logging.info(bot.user.id)
    logging.info("------")
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        logging.error("Error: Channel not found.")
    else:
        message = "Bot is now online and ready!"
        logging.info(message)
        await channel.send(message)

def start_software():
    software = os.path.abspath(SOFTWARE_PATH)
    Popen([software], stdout=PIPE, stdin=PIPE, stderr=PIPE)

def stop_software():
    logging.info('Stopping software...')
    subprocess.call('TASKKILL /F /IM DCS_server.exe /T')
    logging.info('Software stopped.')

def restart_software():
    logging.info('Restarting software...')
    subprocess.call('TASKKILL /F /IM DCS_server.exe /T')
    subprocess.Popen(SOFTWARE_PATH)
    logging.info('Software restarted.')

@bot.command()
async def start(ctx):
    start_software()
    await ctx.send('Software started.')

@bot.command()
async def stop(ctx):
    stop_software()
    await ctx.send('Software stopped.')

@bot.command()
async def restart(ctx):
    restart_software()
    await ctx.send('Software restarted.')

@bot.command()
async def status(ctx):
    # Check if software is running
    result = subprocess.run('TASKLIST', stdout=subprocess.PIPE, universal_newlines=True)
    if 'DCS_server.exe' in result.stdout:
        await ctx.send('Software is running.')
    else:
        await ctx.send('Software is not running.')

@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

bot.run(TOKEN)
