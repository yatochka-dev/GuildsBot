import nextcord
from nextcord import slash_command, Interaction
from nextcord.ext import commands

from slavebot import *
from _config import Config

config = Config()

logger = config.get_logger


class AdminPanel(DataMixin, commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@slash_command(
		name='sql',
		description="Выполняет запрос указаный при вызове команды в базе данных"
	)
	async def do_sql(self, inter: Interaction, sql: str):
		if await self.has_perms(inter=inter):
			db = DB(sql)
			try:
				result = db.do()
				embed = CustomEmbed(
					embed=nextcord.Embed(
						title="Завершена",
						description=f"Запрос в базу данных был завершён успешно:\n {result}"
					)
				).great
			except SQLError as exc:
				embed = CustomEmbed(
					embed=nextcord.Embed(
						title="Завершена",
						description=f"Запрос в базу данных был завершён с ошибкой:\n {exc}"
					)
				).error
			except Exception as exc:
				embed = CustomEmbed(
					embed=nextcord.Embed(
						title="Завершена",
						description=f"Запрос в базу не был произведен из-за ошибки:\n {exc}"
					)
				).error
			await inter.send(
				embed=embed
			)


def setup(bot):
	bot.add_cog(AdminPanel(bot=bot))
