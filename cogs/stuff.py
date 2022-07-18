import nextcord
from nextcord import Interaction, slash_command
from nextcord.ext import commands

from slavebot import *
from _config import Config

config = Config()

logger = config.get_logger


class Help(DataMixin, CommandsMixin, commands.Cog):
	emoji = ''
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.enabled = False
		self.chat_id = 988149498775760916

	# @slash_command(
	# 	name="help",
	# 	description="Отправляет в личные сообщение текст с помощью."
	# )
	# async def help(self, inter: Interaction) -> None:
	# 	await self.not_implemented_command(inter)

	@slash_command(
		name="ping",
		description="Пинг бота"
	)
	async def ping(self, inter: Interaction) -> None:
		embed = ResponseEmbed(
			embed=nextcord.Embed(
				title="Pong!",
				description=f"Пинг бота: {self.bot.latency * 1000:.2f}мс"
			),
			user=inter.user
		).great

		await inter.send(
			embed=embed
		)


def setup(bot):
	bot.add_cog(Help(bot=bot))
