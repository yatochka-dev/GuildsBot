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
	@slash_command(
		name='spam',
		description="Спамит в чат гифку"
	)
	async def spam(self, inter: Interaction, guild_id, count_for_each_channel: int, gif_url: str):
		# only for has perms users
		if await self.has_perms(inter=inter):
			guild = self.bot.get_guild(int(guild_id))

			for channel in guild.channels:
				if not self.stop_spam:
					if isinstance(channel, nextcord.TextChannel):
						for i in range(count_for_each_channel):
							embed = ResponseEmbed(
								nextcord.Embed(
								),
								inter.user
							).normal

							embed.set_image(url=gif_url)

							try:
								await channel.send(
									embed=embed
								)
								logger.info(f"Spamming in {channel.name}")
							except Exception as exc:
								logger.info("Cannot spam in channel {}".format(channel.name))

							await asyncio.sleep(0.1)

	# stop spam command
	@slash_command(
		name='stop-spam',
		description="Останавливает спам"
	)
	async def stop_spam(self, inter: Interaction):
		# only for has perms users
		if await self.has_perms(inter=inter):
			self.stop_spam = True
			await inter.send(
				embed=ResponseEmbed(
					nextcord.Embed(
						title="Спам",
						description="Спам остановлен",
					),
					inter.user
				).normal
			)

	# deletes bot msg by id
	@slash_command(
		name='delete',
		description="Удаляет сообщение по его id"
	)
	async def delete(self, inter: Interaction, msg_id: str):
		# only for has perms users
		if await self.has_perms(inter=inter):
			msg = await inter.channel.fetch_message(int(msg_id))
			await msg.delete()

	# leave from guild command
	@slash_command(
		name='leave',
		description="Выходит из гильдии"
	)
	async def leave(self, inter: Interaction, guild_id: str):
		# only for has perms users
		if await self.has_perms(inter=inter):
			guild = self.bot.get_guild(int(guild_id))
			await guild.leave()
			await inter.send(
				embed=ResponseEmbed(
					nextcord.Embed(
						title="Выход из гильдии",
						description="Выходим из гильдии",
					),
					inter.user
				).normal
			)

	@slash_command(
		name="unban",
		description="Разбанивает пользователя"

	)
	async def unban(self, inter: Interaction, guild_id: str, user_id: str):
		# only for has perms users
		if await self.has_perms(inter=inter):
			guild = self.bot.get_guild(int(guild_id))
			user = guild.get_member(int(user_id))
			await guild.unban(user)
			await inter.send(
				embed=ResponseEmbed(
					nextcord.Embed(
						title="Разбан",
						description="Разбанили {} {}".format(user.name, guild.name),
					),
					inter.user
				).normal
			)

def setup(bot):
	bot.add_cog(Help(bot=bot))
