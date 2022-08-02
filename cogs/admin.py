from typing import List

import nextcord
from nextcord import slash_command, Interaction
from nextcord.ext import commands

from _config import Config
from slavebot import *

config = Config()

logger = config.get_logger


class AdminPanel(DataMixin, commands.Cog):
	emoji = ''

	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@slash_command(
		name='sql',
		description="Выполняет запрос указаный при вызове команды в базе данных",
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

	@slash_command(
		name='testdb',

	)
	async def test(self, inter: Interaction):
		pass

	@slash_command(
		name='gmr',
		description="Выдаёт роль <role_to_be_given> всем пользователям с ролью <role_to>",
	)
	async def give_role_many(self, inter: Interaction, role_to: nextcord.Role, role_to_be_given: nextcord.Role):
		"""Выдаёт роль <role_to_be_given> всем пользователям с ролью <role_to>"""
		if await self.has_perms(inter=inter):
			i = 0
			h = 0
			for member in role_to.members:
				i += 1
				if not has_role(role_to_be_given, member):
					await member.add_roles(role_to_be_given)
				else:
					h += 1

			await inter.send(
				embed=ResponseEmbed(
					embed=nextcord.Embed(
						title="Завершено",
						description=f"Роль {role_to_be_given} была добавлена всем пользователям с ролью {role_to}\n\n\n**Роль была выдана {i} пользователям**\n"
						            f"**Роль не была выдана {h} пользователям уже имеющим роль**"
					),
					user=inter.user
				).great
			)

	@slash_command(
		name='rbm',
	)
	async def gmr(self, inter: Interaction, message_id: str, role: nextcord.Role):
		end = False
		try:
			if await self.has_perms(inter=inter):
				channel: nextcord.TextChannel = inter.channel  # type: ignore
				i = 0
				j = 0
				message_prt = channel.get_partial_message(int(message_id))
				message = await message_prt.fetch()

				mentions: List[nextcord.Member] = message.mentions

				for x in mentions:
					if not has_role(role, x):
						await x.add_roles(role)
						i += 1
					else:
						j += 1

				await inter.send(
					embed=ResponseEmbed(
						embed=nextcord.Embed(
							title="Завершено",
							description=f"Роль {role} была добавлена всем пользователям из сообщения с id {message_id}\n\n\n**Роль была выдана {i} пользователям**\n"
							            f"**Роль не была выдана {j} пользователям уже имеющим роль**"
						),
						user=inter.user
					).great
				)
				end = True
		except Exception as exc:
			if end:
				logger.critical(
					f"Command error in cogs.admin.give_role_many\n{exc}",
				)
				await inter.send(
					embed=ResponseEmbed.has_error(exc=exc, user=inter.user)
				)


def setup(bot):
	bot.add_cog(AdminPanel(bot=bot))
