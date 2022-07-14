import nextcord
from nextcord import Interaction, slash_command
from nextcord.ext.commands import Cog, Bot

from slavebot import *
from _config import Config

config = Config()

logger = config.get_logger


class MasterCommands(DataMixin, TextGetter, Cog):

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

		embed.add_field(name="Старая тема канала", value=str(old_topic), inline=True)
		embed.add_field(name="Новая тема канала", value=str(new_topic), inline=True)

		await inter.send(
			ephemeral=True,
			embed=embed
		)

	# async def __profile(self, inter: Interaction, guild: str or GuildsManager, msg: nextcord.Message = None):
	#
	# 	_ = guild.lower() if isinstance(guild, str) else guild.guild.lower()
	#
	# 	embed = \
	# 		CustomEmbed(
	# 			embed=nextcord.Embed(
	# 				title="マスタープロフィール！",
	# 				description=f"コニチワ, 主人 {config.get_jp_guild(_)}, 今日は美しい日ですね。?"
	# 			)
	# 		).normal
	#
	# 	buttons = MasterView(_)
	#
	# 	message = await inter.send(
	# 		embed=embed,
	# 		view=buttons
	# 	) if not msg else await msg.edit(
	# 		embed=embed,
	# 		view=buttons
	# 	)
	#
	# 	await buttons.wait()
	#
	# 	response = buttons.response
	#
	# 	logger.info(response.response)
	# 	logger.info(response.close)
	# 	logger.info(response.speech)
	# 	logger.info(response.topic)
	#
	# 	if response.close:
	# 		await message.delete()
	#
	# 	elif response.speech:
	# 		await self.change_speech(inter, _, message)
	#
	# 	elif response.topic:
	# 		await self.change_topic(inter, _, message)
	# 	else:
	# 		await message.delete()

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
