import asyncio

import nextcord
from nextcord import Interaction, slash_command
from nextcord.ext.commands import Bot, Cog

from slavebot import *
from _config import Config

config = Config()
logger = config.get_logger

class Spam(DataMixin, Cog):
	def __init__(self, bot: Bot):
		self.bot = bot

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

def setup(bot: Bot):
	bot.add_cog(Spam(bot))
