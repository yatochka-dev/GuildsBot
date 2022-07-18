from typing import List

import nextcord
from nextcord import Interaction, slash_command
from nextcord.ext.commands import Cog, Bot

from _config import Config
from slavebot import *

config = Config()

logger = config.get_logger


class MasterCommands(DataMixin, TextGetter, Cog):
	emoji = ''

	def __init__(self, bot: Bot):
		self.bot = bot

	async def change_speech(self, inter: nextcord.Interaction, guild: str or GuildsManager):
		new_speech = await self.get_text(
			inter=inter,
			min_length=100,
			max_length=1024,
			label="Новая агитация",
			placeholder="Введите вашу агитационную речь"
		)

		if isinstance(guild, str):
			guild = GuildsManager(
				guild.lower()
			)

		guild.change_row(
			'speech',
			new_speech
		)

		embed = CustomEmbed(
			embed=nextcord.Embed(
				title="Успешно",
				description=f"Успешно изменена агитационная речь! \n\nНовая речь: {new_speech}"
			)
		).great

		await inter.send(
			embed=embed,
			ephemeral=True
		)

	async def change_topic(self, inter: nextcord.Interaction, guild: str or GuildsManager):
		chat_id: int = guild.get_data().chat_id if isinstance(guild, GuildsManager) else GuildsManager(guild.lower()).get_data().chat_id

		chat: nextcord.TextChannel = inter.guild.get_channel(chat_id)

		old_topic = chat.topic
		topic: str = await self.get_text(
			inter=inter,
			min_length=0,
			max_length=1024,
			label="Новая тема канала",
			placeholder='Введите новую тему канала. чтобы убрать тему канала - напишите "1".'
		)

		ft = FormatSpeech(
			str(topic), {}, self.bot
		)

		await ft.format()

		new_topic: str = str(ft.speech)

		await chat.edit(
			topic=str(new_topic)
		)

		embed = \
			CustomEmbed(
				embed=nextcord.Embed(
					title="Всё супер!",
					description="Тема канал успешно изменена!"
				)
			).normal

		embed.add_field(name="Старая тема канала", value=f"{str(old_topic) if old_topic else '#'}", inline=True)
		embed.add_field(name="Новая тема канала", value=f"{str(new_topic) if new_topic else '#'}", inline=True)

		await inter.send(
			ephemeral=True,
			embed=embed
		)

	@staticmethod
	def divide_list(lst: list, n: int):
		for i in range(0, len(lst), n):
			yield lst[i:i + n]

	@slash_command(
		name='members'
	)
	async def get_users(self, inter: nextcord.Interaction, guild_role: nextcord.Role):

		divided_members: List[List[nextcord.Member]] = [
			d for d in self.divide_list(
				guild_role.members, 12
			)
		]

		if len(divided_members) > 25:
			return await inter.send(
				embed=CustomEmbed.has_error(exc="Слишком много пользователей имеют эту роль."),
				ephemeral=True,
			)

		embeds = []
		i = 1
		page = 1
		for l in divided_members:
			embed = CustomEmbed(
				embed=nextcord.Embed(
					title=f"Пользователи - {page}",
					description=f"Список из **{len(guild_role.members)}** пользователей с ролью {guild_role.mention}, страница **{page}**.\nВзаимодействие возможно до "
					            f"{self.get_timestamp(minutes=5, discord=True, style='T')}"
				)
			).normal

			for member in l:
				embed.add_field(
					name=f"#{i}",
					value=f"{member.mention} - {member.id}"
				)
				i += 1

			page += 1
			embeds.append(embed)

		if len(embeds) > 1:
			try:
				view = ListEmbedsView(
					embeds=embeds,
					user=inter.user,
					button=True,
					base_embed=embeds[0],

				)
			except ValueError as exc:
				return await self.bad_callback(
					inter,
					f"{exc}"
				)

			msg = await inter.send(
				embed=embeds[0],
				view=view,
				ephemeral=True
			)
			view.edit = msg.edit
			view.message = msg



		else:
			await inter.send(embed=embeds[0])



	@logger.catch()
	async def callback(self, do: str, inter: Interaction, guild: str):
		if do.lower() == 'речь':
			await self.change_speech(inter, guild)  # type: ignore

		elif do.lower() == 'тема':
			await self.change_topic(inter, guild)  # type: ignore

	@slash_command(
		name="gm",
		description="Профиль для гильд-мастера\nВарианты для использования: /gm речь, /gm тема"

	)
	async def call(self, inter: Interaction, do: str):

		scripts = ('тема', 'речь')

		guild = await self.define_guild(inter)
		error_message = """Невозможно определить мастера, если это ошибка обратитесь к <@!686207718822117463>."""

		if guild is None:
			return await self.bad_callback(
				interaction=inter,
				message=error_message
			)
		elif do.lower() in scripts:
			return await self.callback(do, inter, guild)
		else:
			await inter.send(
				str(await inter.guild.fetch_emoji(868084062668095549))
			)


def setup(bot: Bot):
	bot.add_cog(MasterCommands(bot))
