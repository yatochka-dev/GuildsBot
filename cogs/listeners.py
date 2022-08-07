import nextcord
from nextcord import Interaction, slash_command, Message
from nextcord.ext.commands import Bot, Cog

from slavebot import *
from _config import Config

config = Config()

logger = config.get_logger


class AbyssRegistrationListenerCog(DataMixin, CommandsMixin, Cog):
	def __init__(self, bot: Bot):
		self.bot = bot
		self.listen_channel = 988149498775760916
		self.active = False

	@Cog.listener(
		name="on_ready"
	)
	async def on_ready(self) -> None:
		logger.info(f"{self.__class__.__name__} is ready and {self.active and 'active' or 'not active'}")

	async def hasnt_attachment(self, message: Message) -> None:
		user = message.author
		logger.info(f"Message sent by {user} hasn't attachment: \n{message.content}")

		if not user.bot:
			await message.delete()
			embed = ResponseEmbed(
				embed=nextcord.Embed(
					title="Ошибка",
					description="В вашем сообщении обязательно должно быть прикреплено изображение."
				),
				user=user
			).error

			try:
				await user.send(embed=embed)
			except Exception as e:
				logger.error("Message sending error: %s", e)


	@Cog.listener(
		name="on_message"
	)
	async def on_message(self, message: Message) -> None:
		if self.active:
			if message.channel.id == self.listen_channel:
				if self.MessageData(message).has_attachments is None:
					await self.hasnt_attachment(message)
				else:
					await message.add_reaction("✅")
			else:
				pass  # do nothing
		else:
			pass # do nothing

	@slash_command(
		name="register_abyss",

	)
	async def register(self, inter: Interaction) -> None:
		if await self.has_perms(inter=inter):
			self.active = not self.active
			embed = ResponseEmbed(
				embed=nextcord.Embed(
					title=f"Статус процесса {self.active and 'включен' or 'отключен'}",
					description=f"Процесс зарегистрирован в чате <#{self.listen_channel}>"
				),
				user=inter.user
			).normal

			await inter.send(
				embed=embed
			)

def setup(bot: Bot):
	bot.add_cog(AbyssRegistrationListenerCog(bot))
