from datetime import datetime

import nextcord
from tortoise import fields as f
from tortoise.models import Model


# class UserCooldown(NamedTuple):
# 	is_: bool
# 	from_: datetime
# 	message_: str
#
#
# class User(Model):
# 	id = f.IntField(pk=True)
#
# 	invite = f.OneToOneField("models.Invite", related_name="user", null=True)
#
# 	is_on_cooldown = f.BooleanField(default=False)
# 	cooldown_from = f.DatetimeField(null=True)
# 	cooldown_message = f.TextField(blank=False, null=True)
#
# 	async def set_cooldown(
# 			self,
# 			until: datetime,
# 			message: str,
# 	):
# 		self.is_on_cooldown = True
# 		self.cooldown_from = until
# 		self.cooldown_message = str(message).strip()
# 		await self.save()
#
# 	async def remove_cooldown(self):
# 		self.is_on_cooldown = False
# 		self.cooldown_from = None
# 		self.cooldown_message = None
# 		await self.save()
#
# 	@property
# 	def cooldown(self):
# 		return UserCooldown(self.is_on_cooldown, self.cooldown_from,
# 		                    self.cooldown_message)
#
# 	class Meta:
# 		table = 'users'
#

class EventRole(Model):
	role_id = f.BigIntField(pk=True)

	until = f.DatetimeField(null=True)

	guild_object_original = f.ForeignKeyField("models.Guild")

	created_at = f.DatetimeField(auto_now_add=True)


class Guild(Model):
	code = f.CharField(max_length=30)

	#	invites = f.ManyToManyField("models.Invite", related_name="guild")

	event_roles = f.ManyToManyField(
		"models.EventRole",
		related_name="guild"
	)

	master_role = f.BigIntField(
		null=True
	)

	async def is_gm(
			self,
			user: nextcord.Member,
	) -> True:

		if user.guild_permissions.administrator or \
				user.guild_permissions.manage_guild or \
				user.guild_permissions.manage_roles:
			return True

		gm_role = user.guild.get_role(self.master_role)
		if gm_role is None:
			return False

		return gm_role in user.roles

	async def add_event_role(
			self,
			role_id: int,
			until: datetime,
	):
		event_role, _ = await EventRole.get_or_create(
			role_id=role_id,
			defaults=dict(until=until,
			              guild=self, )
		)

		event_roles = self.event_roles

		if event_role in await event_roles.all():
			return False
		else:
			await event_roles.add(event_role)

	class Meta:
		table = 'guilds'

# class Invite(Model):
#	user = f.OneToOneField('models.User', related_name='invite')
#
#	guild = f.ForeignKeyField("models.Guild", related_name="invites")


# # imports
# import asyncio
# import datetime
# import json
# # from imports
# import os
#
# import loguru
# import nextcord
# import peewee
# from nextcord.ext import commands
#
# #
# # Эмбеды
# #
# from utils import GuildDefense
#
# BASE_DIR = os.path.dirname(os.path.dirname(__file__))
#
#
# LOGGER = loguru.logger
#
# LOGGER.add(
# 	"logs/debug.json",
# 	level="DEBUG",
# 	format="{time} | {level}      | {message}",
# 	rotation="00:00",
# 	compression="zip",
# 	serialize=True,
# )
# LOGGER.add(
# 	"logs/info.json",
# 	level="INFO",
# 	format="{time} | {level}      | {message}",
# 	rotation="00:00",
# 	compression="zip",
# 	serialize=True,
# )
# LOGGER.add(
# 	"logs/error.json",
# 	level="ERROR",
# 	format="{time} | {level}      | {message}",
# 	rotation="00:00",
# 	compression="zip",
# 	serialize=True,
# )
# LOGGER.add(
# 	"logs/waring.json",
# 	level="WARNING",
# 	format="{time} | {level}      | {message}",
# 	rotation="00:00",
# 	compression="zip",
# 	serialize=True,
# )
# LOGGER.add(
# 	"logs/success.json",
# 	level="SUCCESS",
# 	format="{time} | {level}      | {message}",
# 	rotation="00:00",
# 	compression="zip",
# 	serialize=True,
# )
#
#
# def offset():
# 	fp = "./additional_files/config_file.json"
# 	with open(fp, "r") as file:
# 		j = json.load(fp=file)
#
# 	now = datetime.datetime.now()
#
# 	before = j["DATETIME"]["offset"]
#
# 	month = now.month
# 	day = now.day
#
# 	if 3 <= month < 10 and day >= 25:
# 		j["DATETIME"]["offset"] = 3
# 	elif 10 <= month < 3:
# 		j["DATETIME"]["offset"] = 2
#
# 	after = j["DATETIME"]["offset"]
#
# 	if before != after:
# 		with open(fp, "w") as file_w:
# 			json.dump(j, file_w, indent=4)
# 	else:
# 		pass
#
#
# def embed_stan(embed: nextcord.Embed = nextcord.Embed(title='Error
# EmptyEmbed 404', color=nextcord.Color.red())):
# 	offset()
#
# 	embed.set_author(name=f"Система управления гильдями!",
# 	icon_url="https://cdn.discordapp.com/attachments/862044149779529750
# 	/956595788979535902/256.png")
#
# 	if embed.colour == embed.Empty:
# 		embed.colour = nextcord.Colour.from_rgb(37, 244, 188)
#
# 	with open("additional_files/config_file.json") as file:
# 		j = json.load(fp=file)
#
# 	offset_ = j["DATETIME"]["offset"]
#
# 	israel_tz = datetime.timezone(offset=datetime.timedelta(hours=int(
# 	offset_)), name="UTC")
# 	dt_now = datetime.datetime.now(tz=israel_tz)
#
# 	embed.timestamp = dt_now
# 	return embed
#
#
# #
# #
# #
#
#
# async def get_info_about_user_gui(user: nextcord.Member):
# 	"""
# 	:param user: :nextcord.User:
# 	:return: Перебирает роли User и возвращает значение в зависимости от того,
# 	какие роли у него есть:
# 	1) NIG - не в гильдии
# 	2) IGM - Гильд-мастер
# 	3) IGV - Смотритель за гильдиями
# 	4) [List] - участник одной из гильдий, в списке возвращается роль гильдии
# 	+ её гильд-мастер
# 	"""
# 	try:
# 		try:
# 			guild_master_roles = [user.guild.get_role(role) for role in
# 			get_tags_by_type("TIME_ROLE", "guild-master")]
# 			guild_vision_roles = [user.guild.get_role(role) for role in
# 			get_tags_by_type("TIME_ROLE", "guild-vision")]
# 			guild_member_roles = [user.guild.get_role(role) for role in
# 			get_tags_by_type("ROLE", "role")]
# 			user_roles = user.roles
#
# 		except Exception as exc:
# 			LOGGER.error(f"ОШИБКА В ПОЛУЧЕНИИ РОЛЕЙ\n{exc}")
# 			raise LookupError(exc) from exc
# 		#
# 		else:
# 			#
# 			list_for_check = []
# 			#
# 			for r in user_roles:
# 				for r_v in guild_vision_roles:
# 					if r == r_v:
# 						list_for_check.append(r)
#
# 			if len(list_for_check) >= 1:
# 				return "IGV"
# 			else:
# 				for r in user_roles:
# 					for r_m in guild_master_roles:
# 						if r == r_m:
# 							list_for_check.append(r)
#
# 				if len(list_for_check) >= 1:
# 					return "IGM"
# 				else:
# 					for r in user_roles:
# 						for r_me in guild_member_roles:
# 							if r == r_me:
# 								list_for_check.append(r)
#
# 					if len(list_for_check) >= 1:
# 						gm = NEDOGUILD().get_one_tag(guild=list_for_check[
# 						0].name, tag="guild_president")
# 						gm = user.guild.get_member(gm)
#
# 						return [list_for_check[0].mention, gm.mention]
# 					else:
# 						return "NIG"
# 	except Exception as exc:
# 		LOGGER.error(f"ОШИБКА В ОПРЕДЕЛЕНИИ РОЛЕЙ\n{exc}")
# 		raise LookupError(exc) from exc
#
#
# #
# # КНОПКИ
# #
#
#
# class AlreadyInDatabase(Exception):
#
# 	def __init__(self, msg=None):
# 		super().__init__()
# 		self.msg = "Запись с этим ID уже находится в базе данных!" if msg is
# 		None else msg
#
# 	def __repr__(self):
# 		return f"The Exception Already in DataBase object, msg: {self.msg}"
#
# 	def __str__(self):
# 		return self.msg
#
#
# class NonInDatabase(Exception):
#
# 	def __init__(self, msg=None):
# 		super().__init__()
# 		self.msg = "Записи с этим ID нет в базе данных!" if msg is None else
# 		msg
#
# 	def __repr__(self):
# 		return f"The Exception Non in DataBase object, msg: {self.msg}"
#
# 	def __str__(self):
# 		return self.msg
#
#
# class InviteSend:
#
# 	def __init__(self, guild: str, interaction: nextcord.Interaction or
# 	nextcord.User, bot: commands.Bot, params: list, invite_data):
#
# 		# Данные для работы класса
# 		self.file_path = r"additional_files\invites.json"
# 		self.guild_id = 794987714310045727
# 		self.channel_id = 929059926641356850
# 		self.bot = bot
# 		self.idta = invite_data
#
# 		# Данные для обработки запросов
# 		self.user = interaction.user if isinstance(interaction,
# 		nextcord.Interaction) else interaction
# 		self.guild = guild
# 		self.params = params if isinstance(params, list) and len(params) >= 3
# 		else print()
#
# 		self.invite = {
# 			"user_id": self.user.id,
# 			"to_guild": self.guild,
# 			"params": self.params
# 		}
#
# 	async def send(self):
# 		try:
# 			guild = await self.bot.fetch_guild(self.guild_id)
# 			channel = await guild.fetch_channel(self.channel_id)
#
# 			gm_role = NEDOGUILD().get_one_tag(guild=self.guild,
# 			tag="guild_master_role")
# 			gm_role = guild.get_role(gm_role)
#
# 			bt = AcceptDicline(gm_role=gm_role, user=self.user)
#
# 			if not isinstance(self.params, list):
# 				raise TypeError("Неправильный тип данных!")
#
# 			def time(secs: int):
# 				try:
# 					timesta = datetime.datetime.now() + datetime.timedelta(
# 					seconds=secs)  # 259200 -> Три дня
#
# 					timestamp = str(timesta.timestamp()).split(".")[0]
# 					timestamp = f"<t:{timestamp}:R>"
# 					return timestamp
# 				except Exception as exception:
# 					LOGGER.error(f"{self.__class__.__name__} -> send ->
# 					timestamp exception {exception}")
# 					raise LookupError(exception) from exception
#
# 			a: list = self.params
#
# 			embed = nextcord.Embed(title=f"Заявка для {self.guild}.",
# 			                       description=f"{self.user.mention} возжелал
# 			                       вступить в гильдию {self.guild}, вот что он
# 			                       написал в заявку:\n\n\n"
# 			                                   f"Возраст: {a[0]}\n\n"
# 			                                   f"Почему ГМ {self.guild} должен
# 			                                   принять его: {a[1]}\n\n"
# 			                                   f"Любимые персонажи: {a[2]}\n\n"
# 			                                   f"Пол: {a[3]}\n\n"
# 			                                   f"Активность в: {a[4]}\n\n"
# 			                                   f"Что он хочет от {self.guild}:
# 			                                   {a[5]}\n\n\n\n"
# 			                                   f"**Срок действия заявки
# 			                                   истечёт:** {time(259200)}!",
# 			                       colour=nextcord.Color.from_rgb(80, 141,
# 			                       234))
# 			embed = embed_stan(embed)
#
# 			try:
# 				gm = gm_role.members[0].mention
# 			except Exception:
# 				gm = gm_role.mention
#
# 			gm += " " + str(self.user.mention)
# 			msg = await channel.send(gm, embed=embed, view=bt)
#
# 			await bt.wait()
#
# 			if bt.ans is True:
# 				pass  # give role
# 				role_id = NEDOGUILD().get_one_tag(guild=self.guild, tag="role")
# 				role = guild.get_role(role_id)
#
# 				await self.user.add_roles(role, reason="По приказу генерала
# 				гафса!")
#
# 				#
# 				# ---- message for user ----
# 				#
#
# 				embed_accepted = nextcord.Embed(
# 					title="Сведения о заявке.",
# 					description=f"Ваша заявка была рассмотренна и ГМ вынес
# 					решение о принятии вас в {self.guild}.✔️",
# 					color=nextcord.Color.green()
# 				)
#
# 				embed_accepted = embed_stan(embed_accepted)
#
# 				embed.title = "Заявка была принята | ✔"
# 				embed.description = f"{self.user.mention}"
# 				embed.colour = nextcord.Color.green()
#
# 				await msg.edit(embed=embed, view=NonBts())
#
# 				await self.user.send(embed=embed_accepted)
#
# 			elif bt.ans is False:
# 				x = GuildDefense(self.bot, server=guild, user=self.user.id,
# 				guild=self.guild)
# 				x.set_cooldown(30.0 * 60.0)
# 				embed_acc = nextcord.Embed(
# 					title="Сожалею!",
# 					description=f"Вы не смогли вступить в гильдию {
# 					self.guild}!\n\n\nВступить в гильдию снова можно будет {
# 					x.dc__timestamp}.",
#
# 					color=nextcord.Color.red()
# 				)
#
# 				embed_acc = embed_stan(embed_acc)
#
# 				embed.title = "Заявка была отклонена | ❌"
# 				embed.description = f"{self.user.mention}"
# 				embed.colour = nextcord.Color.red()
# 				await msg.edit(embed=embed, view=NonBts())
#
# 				await self.user.send(embed=embed_acc)
#
# 			else:
# 				#
# 				# NEEDS TO BE REWRITTEN
# 				#
# 				if bt.ans is None:
# 					await self.__ignored_invite(msg=msg)
# 					LOGGER.success("Ignored msg sent")
#
# 		except Exception as exc:
# 			LOGGER.error(f"{self.__class__.__name__} -> send exception" + str(
# 			exc))
# 			raise LookupError(exc) from exc
# 		try:
# 			self.idta.delete()
# 		except AlreadyInDatabase as exc:
# 			LOGGER.error(f"{self.__class__.__name__} -> send exception\n" +
# 			str(exc))
# 		except NonInDatabase as exc:
# 			LOGGER.error(f"{self.__class__.__name__} -> send exception\n" +
# 			str(exc))
#
# 	async def __ignored_invite(self, msg: nextcord.Message) -> None:
# 		"""
# 		:param msg: Message with invite in invites channel
# 		:return: None(type: None)
# 		"""
#
# 		# Получаем айди смотрителей за гильдиями из БД
# 		watchers_roles_id = get_tags_by_type("TIME_ROLE", 'guild-vision')
# 		# Из айди получаем объекты мемберов и помещаем в список
#
# 		# get
# 		# watchers = [print(watcher_id) and server.get_member(watcher_id) for
# 		watcher_id in watchers_id if len(str(watcher_id)) == 18 and
# 		isinstance(watcher_id, int)]
# 		# async fetch
#
# 		#
# 		# Message to self.user
# 		#
# 		embed_user = embed_stan(nextcord.Embed(
# 			title=f"Ваша заявка была проигнорирована",
# 			description=f"Смотрители уже уже знают об этом и работаеют над
# 			этим(читают морали ГМ-у {self.guild})",
# 			color=nextcord.Color.from_rgb(80, 141, 234)))
# 		try:
# 			await self.user.send(embed=embed_user)
# 		except Exception as exc:
# 			LOGGER.error("Cannot send message to user because " + str(exc))
# 		#
# 		# /* END /*
# 		#
#
# 		usr = ''
# 		for watcher_id in watchers_roles_id:
# 			usr += f"<@&{watcher_id}>"
#
# 		embed_edit = embed_stan(nextcord.Embed(title=f"Проигнорированная
# 		заявка в {self.guild}...", description=f"{self.user.mention}"))
# 		try:
# 			await msg.edit(content=f"{usr}", embed=embed_edit, view=NonBts())
# 		except Exception as exc:
# 			LOGGER.error("Cannot edit ignored invite message because " + str(
# 			exc))
#
#
# class WrongInvite(AlreadyInDatabase):
# 	pass
#
#
# class InviteData:
#
# 	def __init__(self, invite: dict = None):
#
# 		self.file_path = "additional_files/invites.json"
# 		self.file_open_set = (self.file_path, "w", "UTF-8")
#
# 		self.invite: dict = invite
#
# 	def __eq__(self, other):
# 		try:
# 			if isinstance(other, InviteData):
# 				return self.invite["user_id"] == other.invite["user_id"]
# 			else:
# 				return False
# 		except Exception:
# 			return False
#
# 	def __repr__(self):
# 		return f"Объект заявки в базе данных юзера (\\{self.invite[
# 		'user_id']}\\)"
#
# 	def __str__(self):
# 		return f"Объект заявки в базе данных юзера (\\{self.invite[
# 		'user_id']}\\)"
#
# 	def save(self):
# 		try:
# 			if isinstance(self.invite, dict) and len(self.invite) >= 3:
#
# 				with open(self.file_path, "r", encoding="UTF-8") as
# 				invites_file:
# 					invites_json = json.load(invites_file)
#
# 				self.invite["number"] = invites_json["invites_numbers"] + 1
#
# 				if self.invite["user_id"] in invites_json["ids_list"]:
# 					raise AlreadyInDatabase
#
# 				x = list(invites_json["ids_list"])
# 				x.append(self.invite["user_id"])
# 				invites_json["ids_list"] = x
#
# 				# invite
# 				invites_json[f"invite_{self.invite['user_id']}"] = self.invite
# 				invites_json["invites_numbers"] = invites_json[
# 				"invites_numbers"] + 1
#
# 				with open(self.file_path, "w", encoding="UTF-8") as file_w:
# 					json.dump(invites_json, file_w, indent=4)
# 			else:
# 				raise WrongInvite("инвайт гавно")
# 		except Exception as exc:
# 			LOGGER.error(self.__class__.__name__ + " -> save exception " +
# 			str(exc))
# 			raise LookupError(exc) from exc
#
# 	@property
# 	def inv(self):
# 		with open(self.file_path, "r", encoding="UTF-8") as invites_file:
# 			invites_json = json.load(invites_file)
#
# 		if f"invite_{self.invite['user_id']}" in invites_json.keys():
# 			inv = invites_json[f"invite_{self.invite['user_id']}"]
# 		else:
# 			raise NonInDatabase()
#
# 		return inv
#
# 	@inv.setter
# 	def inv(self, other):
# 		if isinstance(other, dict):
# 			if isinstance(other["user_id"], int):
# 				if isinstance(other["to_guild"], str):
# 					if isinstance(other["params"], list):
# 						self.invite = other
# 					else:
# 						raise ValueError
# 				else:
# 					raise ValueError
# 			else:
# 				raise ValueError
# 		else:
# 			raise ValueError
#
# 	def delete(self):
# 		with open(self.file_path, "r", encoding="UTF-8") as invites_file:
# 			invites_json = json.load(invites_file)
#
# 		invites_json = dict(invites_json)
#
# 		if f"invite_{self.invite['user_id']}" in invites_json.keys():
# 			inv = invites_json[f"invite_{self.invite['user_id']}"]
#
# 			invites_json.pop(f"invite_{self.invite['user_id']}")
#
# 			invites_json["ids_list"].sort()
# 			invites_json["ids_list"].remove(self.invite['user_id'])
#
# 			invites_json["invites_numbers"] = invites_json["invites_numbers"]
# 			- 1
#
# 			with open(self.file_path, "w", encoding="UTF-8") as inv_f_w:
# 				json.dump(invites_json, inv_f_w, indent=4)
# 		else:
# 			raise NonInDatabase()
#
# 	@classmethod
# 	def from_dict(cls, user, guild, params):
# 		invite = {
# 			"user_id": user.id,
# 			"to_guild": guild,
# 			"params": params
# 		}
# 		return cls(invite)
#
#
# class InviteParams:
#
# 	def __init__(self, bot: commands.Bot, interaction: nextcord.Interaction,
# 	button):
#
# 		self.bot = bot
# 		self.interaction = interaction
# 		self.button = button
#
# 	async def get_params(self) -> list or None:
#
# 		def change_status(status):
# 			with open("additional_files/invites.json", "r", encoding="UTF-8")
# 			as invites_file:
# 				invites_dict = json.load(invites_file)
#
# 			invites_dict[f"invite_{self.interaction.user.id}"] = {
# 				"in_creating_invite": status if isinstance(status, bool) else
# 				True
# 			}
#
# 			with open("additional_files/invites.json", "w", encoding="UTF-8")
# 			as invites_file_w:
# 				json.dump(invites_dict, invites_file_w, indent=4)
#
# 		def check_status() -> bool:
# 			with open("additional_files/invites.json", "r", encoding="UTF-8")
# 			as invites_file:
# 				invites_dict = json.load(invites_file)
#
# 			try:
# 				return invites_dict[f"invite_{self.interaction.user.id}"] if
# 				isinstance(invites_dict[f"invite_{self.interaction.user.id}"],
# 				bool) else True
# 			except Exception as exc:
# 				LOGGER.error(f"Error in InviteParams -> check_status: {exc}")
# 				return False
#
# 		def check_invite_status() -> bool:
# 			with open("additional_files/invites.json", "r", encoding="UTF-8")
# 			as invites_file:
# 				invites_dict = json.load(invites_file)
#
# 			try:
# 				if self.interaction.user.id in invites_dict["ids_list"]:
# 					return True
# 				else:
# 					return False
# 			except Exception as exc:
# 				LOGGER.error(f"Error in InviteParams -> check_invite_status: {
# 				exc}")
# 				return False
#
# 		def del_status():
# 			with open("additional_files/invites.json", "r", encoding="UTF-8")
# 			as invites_file:
# 				invites_dict = dict(json.load(invites_file))
#
# 			try:
# 				invites_dict.pop(f"invite_{self.interaction.user.id}")
# 			except Exception as exc:
# 				LOGGER.error(f"Error in InviteParams -> del_status: {exc}")
# 				raise LookupError() from exc
#
# 			with open("additional_files/invites.json", "w", encoding="UTF-8")
# 			as invites_file_w:
# 				json.dump(invites_dict, invites_file_w, indent=4)
#
# 		async def something_went_wrong(whats_wrong: str, exception: Exception
# 		= None):
# 			"""
# 			:param: whats_wrong: String object, with text about the exception
# 			"""
# 			try:
# 				await self.interaction.response.send_message(f"Что-то пошло не
# 				так, мы пытаемся выяснить что именно. \nПреждевременный анализ
# 				выявил, что причиной стал: {whats_wrong}",
# 				                                             ephemeral=True)
# 				LOGGER.error(f"Автоматическое расспространение ошибки:
# 				Exception Type: {type(exception)}\n\n Exception Desc: {
# 				exception}") if exception is not None else None
# 			except Exception as exc:
# 				raise LookupError() from exc
#
# 		try:
# 			async def create_channel(interaction: nextcord.Interaction) ->
# 			nextcord.TextChannel:
#
# 				try:
# 					guild = interaction.guild
# 					c = await guild.fetch_channel(929059781245808700)
# 					category = c.category
# 					yat = interaction.guild.get_member(686207718822117463)
# 					awa = interaction.guild.get_member(361198710551740428)
# 					overwrites = {
# 						guild.default_role: nextcord.PermissionOverwrite(
# 						view_channel=False, send_messages=False),
# 						self.interaction.user: nextcord.PermissionOverwrite(
# 						view_channel=True, send_messages=True),
# 						yat: nextcord.PermissionOverwrite(view_channel=True,
# 						send_messages=True),
# 						awa: nextcord.PermissionOverwrite(view_channel=True,
# 						send_messages=True),
# 						self.bot.user: nextcord.PermissionOverwrite(
# 						view_channel=True, send_messages=True)
# 					}
#
# 					channel = await guild.create_text_channel(
# 						position=0,
# 						category=category,
# 						name=f"Канал для создания заявки {
# 						self.interaction.user.name}",
# 						overwrites=overwrites,
# 						reason="По приказу генерала гафса",
# 						topic=f"Автоматически созданный канал для заполнения
# 						заявки пользователя под ником: {
# 						self.interaction.user.display_name}",
# 						slowmode_delay=1
#
# 					)
#
# 					return channel
#
# 				except Exception as exc:
# 					raise LookupError() from exc
#
# 			async def cancel(chat: nextcord.TextChannel):
# 				await chat.trigger_typing()
# 				await asyncio.sleep(0.3)
# 				await chat.send(embed=embed_stan(embed=nextcord.Embed(
# 				title="Заполнение заявки было отменено, удаляю канал...",
# 				color=nextcord.Color.red())))
# 				await asyncio.sleep(5)
# 				await chat.delete()
#
# 				await self.interaction.user.send(embed=embed_stan(
# 				embed=nextcord.Embed(title="Вы отменили заполнение заявки.",
# 				color=nextcord.Color.red())))
#
# 			defense = GuildDefense(self.bot, self.interaction.user.guild,
# 			self.interaction.user.id, self.button.custom_id if not None else
# 			self.button.label)
#
# 			if defense.is_on_cooldown[0]:
# 				props = defense.is_on_cooldown[1]
# 				time_until_2m = datetime.datetime.fromtimestamp(float(
# 				props.get("until", None))) + datetime.timedelta(seconds=120)
#
# 				timestamp_until = str(time_until_2m.timestamp()).split(".")[0]
#
# 				return await self.interaction.response.send_message(
# 					ephemeral=True,
# 					content=f"Недавно вы вышли из {props.get('guild',
# 					'(ошибка)')}, вы снова сможете вступить в гильдию <t:{
# 					timestamp_until}:R>."
# 				)
#
# 			if check_invite_status() is True:
# 				return await self.interaction.response.send_message(
# 				ephemeral=True,
# 				                                                    content="Вы уже отправили заявку на вступление в гильдию, если это не так - напишите нам с помощью команды +bug.")
#
# 			if check_status() is False:
# 				chat = await create_channel(interaction=self.interaction)
# 				change_status(True)
# 			else:
# 				return await self.interaction.response.send_message(
# 				ephemeral=True,
# 				                                                    content="Вы уже начали заполнять заявку, если это ошибка и у вас не создался канал - используйте +bug и отправьте нам отчет об ошибке.")
# 		except nextcord.Forbidden as excf:
# 			await something_went_wrong(whats_wrong="Недостаточно прав для
# 			создания канала", exception=excf)
# 		except nextcord.HTTPException as exch:
# 			await something_went_wrong(whats_wrong="Ошибка создания канала",
# 			exception=exch)
# 		except nextcord.InvalidArgument as exci:
# 			await something_went_wrong(whats_wrong="Неверно указаны параметры
# 			создания канала", exception=exci)
# 		except Exception as e:
# 			await something_went_wrong(whats_wrong="Ошибка создания канала",
# 			exception=e)
# 		else:
# 			try:
# 				await chat.send(self.interaction.user.mention)
#
# 				async def get_msg(wait: int, wait_for: nextcord.Embed,
# 				message: nextcord.Message = None) -> nextcord.Message or None:
# 					def check(m: nextcord.Message):
# 						# NEDOGUILD vision role user_id's
# 						counter = 0
# 						if m.channel == chat:
# 							g_v_r_i_s: list = get_tags_by_type("TIME_ROLE",
# 							"guild-vision")
# 							member: nextcord.Member =
# 							self.interaction.guild.get_member(m.author.id)
# 							author_roles = [role.id for role in member.roles]
#
# 							if member == self.interaction.user and m.channel
# 							== chat:
# 								result = True
# 							else:
# 								for rl in g_v_r_i_s:
# 									if rl in author_roles:
# 										counter += 1
#
# 								if counter >= 1 and str(m.content) ==
# 								"отменить-заполнение":
# 									result = True
# 								elif counter >= 1 and str(
# 								m.content).startswith("-=-"):
# 									result = True
# 								else:
# 									result = False
# 						else:
# 							result = False
# 						return result
#
# 					try:
# 						await chat.send(embed=wait_for) if message is None
# 						else await message.edit(embed=wait_for)
# 					except Exception as exc:
# 						LOGGER.error(f"get_msg error \n {exc}")
# 						raise LookupError() from exc
# 					try:
#
# 						wait_for_msg = await self.bot.wait_for("message",
# 						check=check, timeout=wait)
#
# 					except asyncio.exceptions.TimeoutError:
# 						return None
# 					else:
# 						return wait_for_msg
#
# 				embed_start = embed_stan(embed=nextcord.Embed(title="Сборщик
# 				данных <<Український хакер віталя>>",
# 				                                              description=f"Для вступления в гильдию "
# 				                                                          f"{
# 				                                                          self.button.custom_id if self.button.custom_id else self.button.label} "
# 				                                                          f"необходимо ответить на несколько простых вопросов, это не займет больше 5 "
# 				                                                          f"минут.\n**Когда будете готовы - напишите в чат любое сообщение**!\n\nP.S. Если "
# 				                                                          f"вы
# 				                                                          передумали - просто не отвечайте на это сообщение 30 секунд.",
# 				                                              color=nextcord.Color.from_rgb(47, 204, 142)))
#
# 				answer_wait = await get_msg(wait=30, wait_for=embed_start)
#
# 				if answer_wait is None:
# 					return await cancel(chat)
# 				else:
# 					async def delete():
# 						h = await chat.history(limit=100).flatten()
# 						for msg in h:
# 							await msg.delete()
#
# 					await delete()
#
# 					await chat.trigger_typing()
#
# 					await asyncio.sleep(2)
#
# 					embed_params = embed_stan(nextcord.Embed(title="Отлично!",
# 					description="Теперь начнём заполнение заявки.
# 					\n\n\n**Собираю данные...**",
# 					color=nextcord.Color.green()))
# 					mess = await chat.send(embed=embed_params)
# 					#
# 					await chat.trigger_typing()
# 					await asyncio.sleep(2)
#
# 					# Напишите в чат (элемент списка)
# 					params = ["ваш возраст, просто цифры.\n\nP.S. Опционально,
# 					можете написать белибирду типа: **sgjhblkzdrgb**. \nно
# 					учитывайте, что некоторые ГМ-ы очень сильно заостряют на
# 					этом "
# 					          "внимание.\n",
# 					          #
# 					          --------------------------------------------------------------------------------------------------------
# 					          f"причина по которой мастеру {
# 					          self.button.custom_id if self.button.custom_id
# 					          else self.button.label} будет интересно принять
# 					          вас.\n\n"
# 					          f"P.S. Это основная часть заявки, мастер будет
# 					          определять брать вас или нет в основном из этого
# 					          параметра.",
# 					          #
# 					          --------------------------------------------------------------------------------------------------------
# 					          "любимого/ых героя/ев из Genshin Impact.",
# 					          #
# 					          --------------------------------------------------------------------------------------------------------
# 					          "Какого вы пола.",
# 					          #
# 					          --------------------------------------------------------------------------------------------------------
# 					          "Где вы больше всего активны? (в текстовом чате
# 					          или в войсе(голосовой чат))",
# 					          #
# 					          --------------------------------------------------------------------------------------------------------
# 					          f"Что вы хотели бы от {self.button.custom_id if
# 					          self.button.custom_id else self.button.label}
# 					          если вас примут (ивенты, постоянный актив,
# 					          помощь)"
#
# 					          ]
#
# 					params_ac = []
# 					question = 1
# 					cancel_var = "отменить-заполнение"
# 					time_wait = 4  # minutes
# 					counter_of_none = 0
# 					for param in params:
# 						# УТРО ОБНОВИТЬ БОТА!!!
#
# 						embed_param = embed_stan(embed=nextcord.Embed(
# 						title=f"Сборщик данных <<Український хакер віталя>>,
# 						вопрос №{question}",
# 						                                              description=f"Напишите в чат **{param}**\n\n\n\nУ вас 4 минуты, "
# 						                                                          f"Если вы передумали заполнять заявку, и хотите начать сначала -> напишите в чат '{cancel_var}', "
# 						                                                          f"без кавычек. \n\nТакже если вы не успете - я подставлю сюда пустое значение.",
# 						                                              color=nextcord.Color.random()))
# 						p = await get_msg(wait=time_wait * 60,
# 						wait_for=embed_param, message=mess)
# 						if p.content.lower() == cancel_var.lower():
# 							await cancel(chat=chat)
# 						else:
# 							if p is None:
# 								counter_of_none += 1
# 								ap = "Не заполненное поле."
# 							else:
# 								ap = p.content
# 								await p.delete()
#
# 							params_ac.append(ap)
# 							question += 1
#
# 					await mess.delete()
#
# 					await chat.trigger_typing()
#
# 					embed_cool = embed_stan(embed=nextcord.Embed(
# 					title="Сборщик данных <<Український хакер віталя>>",
# 					description=f"Сбор данных завершён, заявка отправлена,
# 					она будет расмотренна в "
# 					                                                                                                              f"течении 72 часов. \n\n\nДанный чат будет удален через 5-4-3-2...",
# 					                                             color=nextcord.Color.green()))
# 					if params_ac[0] and params_ac[1] and params_ac[2] == "Не
# 					заполненное поле.":
#
# 						embed_bad = embed_stan(embed=nextcord.Embed(
# 						title="Ваша заявка не заполнена", description="Вы не
# 						ответили ни на один из вопросов, ваша заявка не будет
# 						отправлена никуда.",
# 						                                            color=nextcord.Color.red()))
#
# 						await chat.trigger_typing()
# 						await asyncio.sleep(2)
#
# 						await chat.send(embed=embed_bad)
#
# 						await asyncio.sleep(5)
# 						await chat.delete()
#
# 						# На всякий случай
# 						return None
#
# 					else:
# 						await chat.trigger_typing()
# 						await asyncio.sleep(2)
# 						await chat.send(embed=embed_cool)
# 						await asyncio.sleep(5)
# 						await chat.delete()
#
# 						return params_ac
#
# 			except Exception as exc:
# 				LOGGER.critical(f"Ошибка в сборе параметров для юзера {
# 				self.interaction.user}\n\n{exc}")
#
# 				await chat.trigger_typing()
# 				await chat.send(embed=embed_stan(embed=nextcord.Embed(
# 				title="ERROR", description="У нас произошла ошибка, данный
# 				канал будет удален через несколько секунд. \n\n\nСведения об
# 				ошибке: "
# 				                                                                                 f"\n {exc}", color=nextcord.Color.red())))
# 				await asyncio.sleep(6)
# 				await chat.delete()
# 				raise LookupError() from exc
# 			finally:
# 				del_status()
#
#
# #
# # ВЗАИМОДЕЙСТВИЕ С JSON КОНФИГОМ!
# #
#
#
# def config_roles_file_get_by_type(type: str, embed: nextcord.Embed):
# 	def inline(num):
# 		if 0 < num < 4:
# 			return True
# 		else:
# 			return False
#
# 	with open("additional_files/config_file.json", "r") as file:
# 		file = json.load(file)
#
# 	type_ = file[type]
#
# 	f = 1
#
# 	for x in type_:
# 		embed.add_field(name=f"**{x}**", value=f"`{type_[x]}`",
# 		inline=inline(f))
# 		f += 1
# 		if f == 1:
# 			pass
#
# 		elif f == 2:
# 			pass
#
# 		elif f == 3:
# 			pass
# 		else:
# 			if f >= 4:
# 				f = 1
#
# 	return embed
#
#
# def delete_tag_in_type(type, tag):
# 	with open("additional_files/config_file.json", "r") as conf:
# 		conf = json.load(conf)
#
# 	del conf[type][tag]
#
# 	with open("additional_files/config_file.json", "w") as conf_w:
# 		json.dump(conf, conf_w, indent=4)
#
#
# def check_tag_in_type(type, tag):
# 	with open("additional_files/config_file.json", "r") as conf:
# 		conf = json.load(conf)
#
# 	type_ = conf[type]
#
# 	for tag_e in type_:
# 		if tag_e == tag:
# 			return True
# 		else:
# 			pass
#
#
# def change_tag_in_type(type, tag, fill):
# 	with open("additional_files/config_file.json", "r") as conf:
# 		conf = json.load(conf)
#
# 	conf[type][tag] = int(fill)
#
# 	with open("additional_files/config_file.json", "w") as conf_w:
# 		json.dump(conf, conf_w, indent=4)
#
#
# def get_tag_value(type, tag):
# 	with open("additional_files/config_file.json", "r") as conf:
# 		conf = json.load(conf)
#
# 	val = conf[type][tag]
#
# 	return val
#
#
# def get_tags_by_type(type, s):
# 	with open("additional_files/config_file.json", "r") as conf:
# 		conf = json.load(conf)
#
# 	ty = conf[type]
#
# 	return [ty[val] for val in ty if val.startswith(s)]
#
#
# #
# # БАЗА ДАННЫХ
# #
# # Класс гильдии, общие данные и т.д.
#
#
#
# class NEDOGUILD:
#
# 	def __init__(self):
# 		self.file = "additional_files/guilds.json"
#
# 		# --_--_--_--_--_--_--_--_--_--_--_--_--_--_--_--_--_--
# 		self.guild = "guild"
# 		self.agi = "campaign_speech"
# 		self.users = "users"
# 		self.guild_master = "guild_president"
# 		self.guild_chat_desc = "guild_chat_description"
# 		self.channel = "channel"
# 		self.role = "role"
# 		self.guild_master_role = "guild_master_role"
#
# 		self.args = [self.guild, self.agi, self.users, self.guild_master,
# 		self.guild_chat_desc, self.channel, self.role, self.guild_master_role]
#
# 	def create_guild_settings(self, **kwargs):
# 		with open(self.file, "r") as guild_file:
# 			guild_json = json.load(guild_file)
#
# 		guild_json[f"guild_{kwargs.get('guild', 'fuuck')}"] = {
# 			self.agi: kwargs.get("agi", None),
# 			self.users: kwargs.get("users", 0),
# 			self.guild_master: kwargs.get("guild_master", 000000000000000000),
# 			self.guild_chat_desc: kwargs.get("guild_chat_description", ""),
# 			self.channel: kwargs.get("channel", 000000000000000000),
# 			self.role: kwargs.get("role", 000000000000000000),
# 			self.guild_master_role: kwargs.get("guild_master_role",
# 			000000000000000000)
#
# 		}
#
# 		with open(self.file, "w") as guild_file_w:
# 			json.dump(guild_json, guild_file_w, indent=4)
#
# 	def update_guild_settings(self, **kwargs):
# 		with open(self.file, "r") as guild_file:
# 			guild_json = json.load(guild_file)
#
# 		if f"guild_{kwargs.get('guild', 'fuuck')}" not in guild_json:
# 			raise KeyError("Не найдена гильдия")
#
# 		guild_json[f"guild_{kwargs.get('guild', 'fuuck')}"] = {
# 			self.agi: kwargs.get("agi", None),
# 			self.users: kwargs.get("users", 0),
# 			self.guild_master: kwargs.get("guild_master", 000000000000000000),
# 			self.guild_chat_desc: kwargs.get("guild_chat_description", ""),
# 			self.channel: kwargs.get("channel", 000000000000000000),
# 			self.role: kwargs.get("role", 000000000000000000),
# 			self.guild_master_role: kwargs.get("guild_master_role",
# 			000000000000000000)
#
# 		}
#
# 		with open(self.file, "w") as file_to_write:
# 			json.dump(guild_json, file_to_write, indent=4)
#
# 	def update_one_tag(self, guild, tag, new_value):
# 		with open(self.file, "r") as guild_file:
# 			guilds_json = json.load(guild_file)
#
# 		guilds_json[f"guild_{guild}"][tag] = new_value
#
# 		with open(self.file, "w") as file_to_write:
# 			json.dump(guilds_json, file_to_write, indent=4)
#
# 		return guilds_json[f"guild_{guild}"][tag]
#
# 	def get_one_tag(self, guild, tag):
# 		with open(self.file, "r") as guild_file:
# 			guilds_json = json.load(guild_file)
#
# 		return guilds_json[f"guild_{guild}"][tag]
#
# 	def get_all_tags(self, guild):
# 		with open(self.file, "r") as guild_file:
# 			guilds_json = json.load(guild_file)
#
# 		return guilds_json[f"guild_{guild}"]
#
#
# 	@classmethod
# 	def get_all_guilds(cls):
# 		with open("additional_files/guilds.json", "r") as guild_file:
# 			guilds_json = json.load(guild_file)
#
# 		return guilds_json # N NOQA
