import asyncio

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

		self.stop_spam = False

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
		).normal

		await inter.send(
			embed=embed
		)

	@slash_command(
		name='t',
		description="testing embeds"
	)
	async def t(self, inter: Interaction):
		embeds = [
			ResponseEmbed.done(inter.user),
			ResponseEmbed.unable_to(inter.user),
			ResponseEmbed.has_error(user=inter.user, exc="Custom Error"),
			ResponseEmbed.no_perm(inter.user),
			ResponseEmbed.not_implemented(inter.user),
			ResponseEmbed.working_on(inter.user),
		]

		await inter.send(
			embeds=embeds,
			ephemeral=True
		)

	# get all bot guilds and invites to them
	@slash_command(
		name='get-guilds',
		description="Получает все приглашения бота в гильдии"
	)
	async def invites(self, inter: Interaction):
		# only for has perms users
		if await self.has_perms(inter=inter):
			invites = []
			for guild in self.bot.guilds:
				invites.append(
					{"guild": guild, "invite": await self.get_guild_invite(guild)}
				)

			embed = ResponseEmbed(
				nextcord.Embed(
					title="Приглашения",
					description="Все приглашения бота в гильдии",
				),
				inter.user
			).normal

			i = 0
			for invite in invites:
				embed.add_field(
					name=f"#{i} {invite['guild'].name}({invite['guild'].id})",
					value=f"Приглашение - {invite['invite']}",
					inline=False
				)
				i += 1

			await inter.send(
				embed=embed
			)


	# spamming gif to chats command


def setup(bot):
	bot.add_cog(Help(bot=bot))
