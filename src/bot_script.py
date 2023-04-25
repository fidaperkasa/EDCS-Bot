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
import asyncio


# load config
config = configparser.ConfigParser()
config.read('config.ini')

TOKEN = config.get('BOT', 'TOKEN')
CHANNEL_ID = int(config.get('BOT', 'CHANNEL_ID'))
SOFTWARE_PATH = config.get('BOT', 'SOFTWARE_PATH')
DEBUG = config.getboolean('BOT', 'DEBUG')
LOG_FILENAME = 'logs/log.txt'
LOG_LEVEL = logging.DEBUG if DEBUG else logging.INFO
AUTO_RESTART = config.getboolean('BOT', 'AUTO_RESTART')

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

async def start_software():
    software = os.path.abspath(SOFTWARE_PATH)
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="DCS Server"))
    process = Popen([software], stdout=PIPE, stdin=PIPE, stderr=PIPE)
    return process

def stop_software():
    logging.info('Stopping software...')
    subprocess.call('TASKKILL /F /IM DCS_server.exe /T')
    logging.info('Software stopped.')
    bot.loop.create_task(bot.change_presence(activity=None))

async def restart_software():
    logging.info('Restarting software...')
    stop_software()
    await asyncio.sleep(5)
    process = await start_software()
    logging.info('Software restarted.')
    return process

async def auto_restart():
    while True:
        await asyncio.sleep(6 * 60 * 60)  # Wait 6 hours
        # await asyncio.sleep(2 * 60)  # Wait 2 minutes # this one for checking
        await restart_software()
        auto_restart_chnl = bot.get_channel(CHANNEL_ID)
        if auto_restart_chnl is None:
            auto_restart_msg = "Performing automatic restart..."
            logging.info(auto_restart_msg)
            await auto_restart_chnl.send(auto_restart_msg)
        

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
    if AUTO_RESTART:
        bot.loop.create_task(auto_restart())

@bot.command()
async def start(ctx):
    await start_software()
    await ctx.send('Software started.')

@bot.command()
async def stop(ctx):
    stop_software()
    await ctx.send('Software stopped.')

@bot.command()
async def restart(ctx):
    process = await restart_software()
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
