from typing import Literal, Tuple, Optional

import loguru
import nextcord
from nextcord.ext import commands

from slavebot import CustomEmbed

LOG_LEVELS = Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL', "SUCCESS"]


class BotLogger:
	ERROR_LEVELS: Tuple[LOG_LEVELS] = (
		'CRITICAL',
		'ERROR',
		'WARNING',
	)

	BASE_GUILD_ID: int = 794987714310045727
	LOG_CHANNEL_ID: int = 1000145537103835266

	def __init__(
			self,
			bot: Optional[commands.Bot],
			logger: loguru.logger
	):
		self.logger = logger
		self.bot = bot

	def log_embed(self, msg: str, level: LOG_LEVELS) -> nextcord.Embed:
		embed = CustomEmbed(
			embed=nextcord.Embed(
				title=f"{level.upper()}",
				description=msg

			))

		res = embed.normal

		if level == 'DEBUG':
			res = embed.color(
				nextcord.Color.from_rgb(0, 255, 0)
			)
		elif level == 'INFO':
			res = embed.normal
		elif level == 'WARNING':
			res = embed.color(
				nextcord.Color.from_rgb(255, 255, 0)
			)
		elif level == 'ERROR':
			res = embed.error
		elif level == 'CRITICAL':
			res = embed.color(
				nextcord.Color.from_rgb(255, 30, 0)
			)
		elif level == 'SUCCESS':
			res = embed.color(
				nextcord.Color.from_rgb(0, 255, 0)
			)

		return res

	async def __get_data(self, msg: str, level: LOG_LEVELS) -> dict:
		return {
			'content': "" if level not in self.ERROR_LEVELS else "<@!686207718822117463>",
			'embed': self.log_embed(msg, level)
		}

	async def __send_log(self, msg: str, level: LOG_LEVELS):
		if not self.bot.is_ready() or self.bot.is_closed() or not self.bot:
			self.logger.warning(
				"Bot is not ready, can't send log to channel"
			)
			return

		base_server = self.bot.get_guild(self.BASE_GUILD_ID)
		channel = base_server.get_channel(self.LOG_CHANNEL_ID)
		await channel.send(**await self.__get_data(msg, level))

	def send_log(self, msg, level: LOG_LEVELS):
		self.bot.loop.create_task(self.__send_log(msg, level), name="SendLog")
		pass 

	def debug(self, msg: str):
		self.logger.debug(msg)
		self.send_log(msg, 'DEBUG')

	def info(self, msg: str):
		self.logger.info(msg)
		self.send_log(msg, 'INFO')

	def warning(self, msg: str):
		self.logger.warning(msg)
		self.send_log(msg, 'WARNING')

	def error(self, msg: str):
		self.logger.error(msg)
		self.send_log(msg, 'ERROR')

	def critical(self, msg: str):
		self.logger.critical(msg)
		self.send_log(msg, 'CRITICAL')

	def success(self, msg: str):
		self.logger.success(msg)
		self.send_log(msg, 'SUCCESS')

	async def log(self, msg: str, level: LOG_LEVELS):
		self.logger.log(level, msg)
		await self.__send_log(msg, level)
