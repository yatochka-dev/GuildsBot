import os
from typing import List, Tuple

import nextcord
from nextcord.ext import commands

from _config import Config
from slavebot import *
from slavebot import __version__ as bot_version

config = Config()

bot = commands.Bot(command_prefix=commands.when_mentioned_or(
	config.get_prefix), intents=nextcord.Intents.all())
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
	logger.success(f"Logged in as {bot.user.name}")
	logger.info(f"Bot version: {bot_version}")
	logger.info(f"Bot ID: {bot.user.id}")
	logger.info(f"Bot guilds: {len(bot.guilds)}")

	if len(bot.guilds) > 2:
		logger.warning("More than 2 guilds connected")
		for g in bot.guilds:
			logger.info(f"Guild: {g.name}")

	logger.info(f"Bot users: {len(bot.users)}")
	logger.info(f"Bot voice channels: {len(bot.voice_clients)}")


@bot.slash_command(
	name="do",
	description="Админ команда"
)
async def admin_do(inter: nextcord.Interaction, predo: str, channel_id: str = None, role: nextcord.Role = None, member: nextcord.Member = None):
	f_do, f_rate = await AdminMixin.admin_do(
		predo
	)

	[callback, is_async] = await AdminMixin.admin_do_getCallback(f_do, bot=bot)

	kwargs = {
		f'{"channel" if isinstance(_, nextcord.TextChannel) else "role" if isinstance(_, nextcord.Role) else "member" if isinstance(_, nextcord.Member) else ""}':
			_ for _ in [inter.guild.get_channel(int(channel_id)), role, member] if _ is not None
	}

	view = CallbackCloseView(
		callback=callback,
		user=inter.user,
		is_async=is_async,
		**kwargs,

	)

	await inter.send(
		embed=ResponseEmbed(
			nextcord.Embed(
				title="Выполнить действие?",
				description=f"{predo} схожа с командой {f_do} на {f_rate}%"

			),
			inter.user
		).normal,
		ephemeral=True,
		view=view
	)


@logger.catch()
def run():
	load_cogs(config.get_allowed_cogs)
	bot.run(config.get_token)


if __name__ == '__main__':
	run()
