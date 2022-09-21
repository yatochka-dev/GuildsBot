from typing import Tuple

import nextcord
from nextcord.ext import commands

from _config import Config
from .GuildsManager import GuildsManager
from .InvitesManager import InvitesManager
from .embeds import CustomEmbed
from .tools import FormatData, CheckUser
from .utils import DataMixin
from .views import YesCloseVIew, GetMessageView, InviteView, WithoutView

config = Config()
timezone = config.get_timezone
logger = config.get_logger


class InviteAnswer:

	def __init__(
			self, inter: nextcord.Interaction, guild: str,
			message: nextcord.Message
	):
		self.inter = inter
		self.guild = guild.lower()
		self.role = self.inter.guild.get_role(
			GuildsManager(self.guild.lower()).get_data().master_role_id)

		self.message = message

	async def __get_ans__(self) -> Tuple[bool, str]:
		yc = YesCloseVIew(
			60,
			self.role,
			modal=GetMessageView
		)

		msg = await self.message.reply(
			view=yc,
			embed=CustomEmbed(
				embed=nextcord.Embed(
					title="Отклонена ли...?",
					description="Вы отклонили заявку, хотите ответить почему, "
					            "чтобы пользователь знал, почему его не "
					            "приняли?"
				)
			).normal,

		)

		await yc.wait()

		await msg.delete()

		return yc.ans, yc.data

	async def send(self):
		w, message = await self.__get_ans__()

		logger.info(f"Data: {w} '{message}'")

		if w:
			user_embed = CustomEmbed(
				embed=nextcord.Embed(
					title="Сожалеем | {}".format(self.guild),
					description=f"Ваша заявка отправленная в гильдию "
					            f"{self.guild} не была "
					            f"одобрена...\n\nПричина: "
					            f"{message}\n\n\nP.S. **Вы можете отправить "
					            f"заявку в другую гильдию!**"
				)
			).error
		else:
			user_embed = CustomEmbed(
				embed=nextcord.Embed(
					title="Сожалеем | {}".format(self.guild),
					description=f"Ваша заявка отправленная в гильдию "
					            f"{self.guild} не была одобрена...\n\n\nP.S. "
					            f"**Вы можете отправить заявку в другую "
					            f"гильдию!**"
				)
			).error

		await self.inter.user.send(
			embed=user_embed
		)


class InviteSend(DataMixin):

	def __init__(
			self,
			interaction: nextcord.Interaction,
			data: FormatData,
			manager: InvitesManager,
			guild: str,
			bot: commands.Bot
	):
		self.interaction = interaction
		self.data = data
		self.guild = guild
		self.bot = bot
		self.manager = manager
		self.state = "INITIALIZATION"

	@property
	@logger.catch()
	def create_embed(self) -> nextcord.Embed:
		try:
			self.state = "CREATING_EMBED"
			_raw_embed = nextcord.Embed(
				title="Новая заявка в {}.".format(str(self.guild).strip()
				                                  .lower().capitalize()),
				description=f"Заявка истечёт "
				            f"{self.get_timestamp(days=3, discord=True)}"
				            f", за 3 пропущенные заявки - снятие с поста "
				            f"ГМ-а.",
			)

			embed = CustomEmbed(
				embed=_raw_embed
			).normal

			fields = self.data.create_fields()
			fields.insert(0,
			              {
				              "name": "Автор заявки:",
				              "value": f"{self.interaction.user.mention}",
				              "inline": False
			              }
			              )

			for field in fields:
				embed.add_field(**field)

			return embed
		except Exception as exc:
			logger.error(f"Ошибка создание эмбеда {exc}")
			raise LookupError(f"Ошибка создание эмбеда {exc}") from exc

	@logger.catch()
	async def send(self):
		try:

			self.manager.creating_invite(False)

			server = self.bot.get_guild(config.base_server)

			invites_channel = server.get_channel(config.invites_channel)

			master_role_id = GuildsManager(
				self.guild.lower()).get_data().master_role_id

			master_role = self.interaction.guild.get_role(master_role_id)

			try:
				buttons = InviteView(
					259200,
					self.guild
				)
			except Exception as exc:
				logger.error(f"Ошибка создания кнопок {exc}")
				raise LookupError(f"Ошибка создания кнопок {exc}") from exc

			try:
				try:
					emb = self.create_embed
				except Exception as exc:
					logger.error(f"Получения эмбеда {exc}")
					raise LookupError(f"Получения эмбеда {exc}") from exc

				message = await invites_channel.send(
					content=f"{self.interaction.user.mention}---"
					        f"{master_role.mention}",
					embed=emb,
					view=buttons,
				)

				await self.interaction.send(
					ephemeral=True,
					embed=CustomEmbed(
						embed=nextcord.Embed(
							title="Отправлена",
							description=f"Заявка в гильдию {self.guild} "
							            f"отправлена."
						)
					).great
				)

				self.manager.has_invite(True)

				logger.info(self.manager.has_invite())

				await buttons.wait()

				logger.info(buttons.do)

				if buttons.do is True:
					cu = CheckUser(self.bot, server, self.interaction.user)
					if await cu.is_master():
						return await self.bad_callback(
							message,
							"Невозможно принять пользователя в гильдию т.к. "
							"у него есть роль мастера одной из гильдий.",
							delete_after=10,
						)
					elif await cu.is_in_guild():
						return await self.bad_callback(
							message,
							"Невозможно принять пользователя в гильдию т.к. "
							"он уже находится в гильдии.",
							delete_after=10,
						)
					await self.__accepted(message)
					self.manager.has_invite(False)
					self.manager.creating_invite(False)


				elif buttons.do is False:
					await self.__declined(message)
					self.manager.has_invite(False)
					self.manager.creating_invite(False)
				else:
					await self.__out_of_time(message)
					self.manager.has_invite(False)
					self.manager.creating_invite(False)

			except Exception as exc:
				if isinstance(exc, TypeError):
					logger.error(f"Ошибка сообщения в канал {exc}")
				else:
					logger.error(f"Ошибка сообщения в канал {exc}")
					raise LookupError(
						f"Ошибка сообщения в канал {exc}") from exc


		except Exception as exc:
			logger.error(f"Ошибка отправки заявки {exc}")
			await self.interaction.send(
				ephemeral=True,
				embed=CustomEmbed(
					embed=nextcord.Embed(
						title="Ошибка",
						description=f"Ошибка отправки заявки в гильдию "
						            f"{self.guild.capitalize()}.\n\n\n"
						            f"Ошибка: ```{exc}```"
					)
				).error
			)
			raise LookupError(f"Ошибка отправки заявки {exc}") from exc

	@logger.catch()
	async def __accepted(self, message: nextcord.Message):
		guild_role_id = GuildsManager(self.guild.lower()).get_data().role_id

		role = message.guild.get_role(guild_role_id)

		new_embed = CustomEmbed(
			embed=nextcord.Embed(
				title="Заявка принята | {}".format(self.guild.capitalize()),
				description="Заявка принята!"
			)
		).great

		user_embed = CustomEmbed(
			embed=nextcord.Embed(
				title="Поздравляю | {}".format(self.guild.capitalize()),
				description=f"Ваша заявка отправленна"
				            f"я в гильдию {self.guild.capitalize()} была "
				            f"одобрена!"
			)
		).great

		await self.interaction.user.add_roles(
			role
		)

		await message.edit(embed=new_embed, view=WithoutView())
		await self.interaction.user.send(
			embed=user_embed
		)

		logger.success(
			f"Принята заявка в {self.guild} от {self.interaction.user.mention}"
		)

	@logger.catch()
	async def __declined(self, message: nextcord.Message):

		new_embed = CustomEmbed(
			embed=nextcord.Embed(
				title="Заявка отклонена | {}".format(self.guild.capitalize()),
				description="Заявка отклонена!"
			)
		).error

		aus = InviteAnswer(
			self.interaction,
			self.guild,
			message
		)

		await aus.send()

		await message.edit(embed=new_embed, view=WithoutView())

		logger.success(
			f"Отклонена заявка в {self.guild} от "
			f"{self.interaction.user.mention}"
		)

	@logger.catch()
	async def __out_of_time(self, message: nextcord.Message):
		logger.critical(
			f"Пропущена заявка в {self.guild.capitalize()} от "
			f"{self.interaction.user.mention}"
		)

		new_embed = CustomEmbed(
			embed=nextcord.Embed(
				title="Время вышло | {}".format(self.guild.capitalize()),
				description="Время действия заявки вышло!"
			)
		).color(nextcord.Color.dark_grey())

		user_embed = CustomEmbed(
			embed=nextcord.Embed(
				title="Время вышло | {}".format(self.guild),
				description=f"Ваша заявка отправленная в гильдию {self.guild} "
				            f"была проигнорирована...\n\n\n\nP.S. **Мы "
				            f"сделаем "
				            f"всё, возможное, чтобы это больше не "
				            f"повторилось**"
			)
		).normal

		new_content = f"{self.interaction.user.mention}---<@!686207718822117463>---<@!361198710551740428>"

		await message.edit(content=new_content, embed=new_embed,
		                   view=WithoutView())
		await self.interaction.user.send(
			embed=user_embed
		)
