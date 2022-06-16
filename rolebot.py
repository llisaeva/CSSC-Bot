# rolebot module
import discord
from discord import Message, RawReactionActionEvent
from discord.ext import commands
from discord.ext.commands import Context
from discord.utils import get
import modules.logger as logger
import modules.persistance as persistance
import modules.role_poll as role_poll
from tkn import MAKER, TOKEN

# 'Constants' ==============================================

CMDS_TEXT = "txt/cmds.txt"
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', owner_id=MAKER, intents=intents)

# Commands =================================================

# post the college year reaction poll ----------------------
@bot.command(pass_context=True)
async def collegeYearPoll(ctx: Context):
    await rolePoll(ctx, role_poll.COLLEGE_YEAR_POLL_KEY)

# post the college staff reaction poll ---------------------
@bot.command(pass_context=True)
async def collegeStaffPoll(ctx: Context):
    await rolePoll(ctx, role_poll.COLLEGE_STAFF_POLL_KEY)

# assign a role using a command ----------------------------
@bot.command(pass_context=True)
async def assign(ctx: Context, arg=None):
    if arg and ctx.author:
        if arg == "clear":
            await role_poll.clearAllRoles(ctx.author)
        
        elif ctx.guild:
            await role_poll.cmd(arg, ctx.guild, ctx.author)

# post a message that lists all of the commands ------------
@bot.command(pass_context=True)
async def cmds(ctx: Context):
    content = ""
    with open(CMDS_TEXT, "r") as file:
        content = file.read()

    if content:
        embed = discord.Embed(title="Command List", description=content)
        await ctx.send(embed=embed)

# Events ===================================================

# boot message ---------------------------------------------
@bot.event
async def on_ready():
    logger.setupLoggers()
    logger.log.info("BOOT")
    print('{0.user} is running'.format(bot))

# event is called when a reaction is added on the server ---
@bot.event
async def on_raw_reaction_add(payload: RawReactionActionEvent):
    # reaction was not created by bot and the 
    # author of the message is the bot
    if (payload and 
        payload.member and 
        payload.member != bot.user and
        payload.message_id):
            
            key = persistance.has(payload.message_id)
            guild = bot.get_guild(payload.guild_id)

            if key and guild:
                await role_poll.reaction(key, str(payload.emoji), guild, payload.member)

# Utilities & Helpers ======================================

# post a role reaction poll for ----------------------------
# the specified key
async def rolePoll(ctx: Context, key):
    msg: Message = await role_poll.post(ctx, key)
    persistance.save(key, msg.id)

# Run Rolebot ==============================================

bot.run(TOKEN)
logger.log.info("SHUTDOWN")