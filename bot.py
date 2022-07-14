import os
from typing import List, Tuple
import nextcord
from nextcord.ext import commands
from slavebot import InvitesManager
from _config import Config
import sys
sys.setrecursionlimit(5000)
config = Config()

bot = commands.Bot(command_prefix=commands.when_mentioned_or(config.get_prefix), intents=nextcord.Intents.all())
logger = config.get_logger


def load_cogs(_allowed_cogs: List[str] or Tuple[str]) -> None:
	for file in os.listdir("./cogs"):
		if file.endswith(".py") and str(file[:-3]) in _allowed_cogs:
			bot.load_extension(f"cogs.{file[:-3]}")
	else:
		pass

	logger.success("Loaded cogs")

def reload_cogs(_allowed_cogs: List[str] or Tuple[str]) -> None:
	for file in os.listdir("./cogs"):
		if file.endswith(".py") and str(file[:-3]) in _allowed_cogs:
			bot.reload_extension(f"cogs.{file[:-3]}")
	else:
		pass

	logger.success("Loaded cogs")

async def app_commands():
	for guild_id in config.get_test_guilds:
		guild = bot.get_guild(guild_id)
		await guild.rollout_application_commands()


@bot.event
async def on_ready():

	InvitesManager.clear_invites()
	logger.success("Started bot inside {}!".format(bot.user))



@bot.slash_command(name="forme")
async def forme(_interaction: nextcord.Interaction):
	# device = check_device(
	# 	modal=invite_modal,
	# 	guild="Pyro",
	# 	bot=bot,
	# )
	# await interaction.response.send_modal(device)
	pass

@bot.slash_command(
	name="do",
	description="Админ команда"
)
async def admin_do(_inter: nextcord.Interaction, do: str):
	"""
	@ToDo Сделать типа команду, которая принимает аргумент, и на типа если написать в аргументе <selected do>reload_messages</selected> то бот перевышлет сообщения

	:param _inter: typeof: Interaction
	:return: None
	"""

if __name__ == '__main__':
	load_cogs(config.get_allowed_cogs)

	bot.run(config.get_token)
