import datetime
import json
from datetime import *
from typing import Tuple, Any, Literal, Callable, Optional
import nextcord
import requests
from nextcord.ext import commands

from fuzzywuzzy import fuzz

from _config import Config
from .GuildsManager import GuildsManager
from .embeds import CustomEmbed
from .tools import has_role

config = Config()
logger = config.get_logger

timezone = config.get_timezone


class GuildDefense:
	COOLDOWN_FILE = "additional_files/users_cooldown.json"

	def __init__(self, bot: commands.Bot, server: nextcord.Guild, user: int, guild: str):
		self.bot, self.server = bot, server
		self.user = user
		self.guild = guild

	# def __init__(self, bot: str, server: str, user: int, guild: str):
	# 	self.bot, self.server = bot, server
	# 	self.user = user
	# 	self.guild = guild

	@property
	def is_on_cooldown(self) -> Tuple[bool, Any]:
		"""
		:return: Type: tuple, tuple[0] - bool, tuple[1](only if tuple[0] is True) - dict[str, timestamp]
		"""

		dt_now = datetime.now(tz=timezone)

		with open(self.COOLDOWN_FILE, "r") as cooldown_file:
			cooldown_json: dict = json.load(cooldown_file)

		result = cooldown_json.get("{}".format(self.user), None)

		if result is None:
			return (False, {})
		elif float(result["until"]) < dt_now.timestamp():
			return (False, {})

		return (True, result)

	def timestamp(self, add: int = 120) -> str:
		time_until_2m = datetime.fromtimestamp(float(self.is_on_cooldown[1].get("until", None))) + timedelta(seconds=add)

		timestamp_until: str = str(time_until_2m.timestamp()).split(".")[0]

		return timestamp_until

	@property
	def dc__timestamp(self):
		return "<t:{}:R>".format(self.timestamp())

	def remove_cooldown(self):
		with open(self.COOLDOWN_FILE, "r") as cooldown_file:
			json_after: dict = json.load(cooldown_file)

		json_after.pop("{}".format(self.user))

		with open(self.COOLDOWN_FILE, "w") as file_w:
			json.dump(json_after, file_w, indent=4)

	def set_cooldown(self, cooldown_seconds: float):
		dt_now = datetime.now(tz=timezone)
		until = (datetime(
			year=dt_now.year,
			month=dt_now.month,
			day=dt_now.day,
			hour=dt_now.hour,
			minute=dt_now.minute,
			second=dt_now.second,
			microsecond=dt_now.microsecond,
		) + timedelta(seconds=cooldown_seconds)).timestamp()

		cooldown = {
			"until": f"{until}",
			"guild": f"{self.guild}",
		}

		with open(self.COOLDOWN_FILE, "r") as cooldown_file:
			cooldown_json = json.load(cooldown_file)

		cooldown_json["{}".format(self.user)] = cooldown

		with open(self.COOLDOWN_FILE, "w") as file_w:
			json.dump(cooldown_json, file_w, indent=4)

		return cooldown


class DataMixin:

	@logger.catch()
	def to_bool(self, value: Any):
		if isinstance(value, int):
			if value == 1:
				return True
			else:
				return False

	@logger.catch()
	async def has_nt(self, inter: nextcord.Interaction) -> bool:
		await inter.send(
			embed=CustomEmbed.no_perm(),
			ephemeral=True
		)

		return False

	@logger.catch()
	async def has_perms(self, _user: nextcord.Member = None, inter: nextcord.Interaction = None) -> bool:
		bot_admins = (686207718822117463,)
		user = _user if _user else inter.user

		if user.id in bot_admins or user.guild_permissions.administrator or user.guild_permissions.manage_guild:
			return True

		return \
			await self.has_nt(
				inter
			)

	@logger.catch()
	def get_timestamp(self, days: int = 0, hours: int = 0, minutes: int = 0, seconds: int = 0, discord: bool = True, style: str = "R"):
		now = datetime.now(tz=timezone)
		days: timedelta = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)

		result = int(str((now + days).timestamp()).split(".")[0])

		if discord:
			return f"<t:{result}:{style if discord else 'R'}>"
		return result

	@logger.catch()
	def timestamp(self, dt: datetime):
		return f"<t:{int(str(dt.timestamp()).split('.')[0])}:R>"

	@logger.catch()
	def get_img(self, type, cat) -> str:
		url = f'https://api.waifu.pics/{type}/{cat}'

		response = requests.get(
			url=url
		)

		data: dict[str: str] = json.loads(response.text)

		return data['url']

	@logger.catch()
	async def define_guild(self, inter: nextcord.Interaction, master_or_user='master') -> str:

		for _ in config.ALL_GUILDS:
			r = GuildsManager(_.lower()).get_data().master_role_id if master_or_user == 'master' else GuildsManager(_.lower()).get_data().role_id
			if has_role(role=inter.guild.get_role(r), user=inter.user):
				return _.lower()

	@logger.catch()
	async def bad_callback(self, interaction: nextcord.Interaction or nextcord.Message, message: str):
		return await interaction.send(
			ephemeral=True,
			embed=CustomEmbed(
				embed=nextcord.Embed(
					title="Ошибка!",
					description=message
				)
			).error
		) if isinstance(interaction, nextcord.Interaction) else await interaction.reply(
			embed=CustomEmbed(
				embed=nextcord.Embed(
					title="Ошибка!",
					description=message
				)
			).error
		)


class CommandsMixin:

	@logger.catch()
	async def not_implemented_command(self, inter: nextcord.Interaction):
		return await inter.send(
			ephemeral=True,
			embed=CustomEmbed.not_implemented()
		)

	@logger.catch()
	async def get_guild_invite(self, guild: nextcord.Guild):
		try:
			for c in guild.channels:
				if isinstance(c, nextcord.TextChannel):
					return await c.create_invite(unique=False)
		except Exception as exc:
			logger.error("Ошибка при получении инвайта для гильдии {}\n\n{}".format(guild.name, exc))
			return ""

	class MessageData:

		def __init__(self, message: nextcord.Message):
			self.message = message

		@property
		def has_attachments(self) -> Optional[int]:
			return len(self.message.attachments) if self.message.attachments else None


class AdminMixin:
	ADMIN_DO_LIST: list = ['reload_messages', 'reload_database']
	ADMIN_DO_TYPE = Literal['reload_messages', 'reload_database']

	@classmethod
	async def admin_do(cls, do: str) -> Tuple[ADMIN_DO_TYPE, int]:
		for _ in cls.ADMIN_DO_LIST:
			rate = fuzz.WRatio(
				do, _
			)
			logger.info(f"{do} {_} {rate}")
			if rate >= 70:
				return _, rate
			else:
				continue

		raise ValueError("Не найдено ни одной команды с таким названием!")

	@classmethod
	async def admin_do_getCallback(cls, do: ADMIN_DO_TYPE, bot: commands.Bot) -> Tuple[Callable, bool]:
		cogs = bot.cogs

		for c in cogs:
			cog: commands.Cog = bot.get_cog(c) if isinstance(c, str) else c
			logger.info(str(cog))

			try:
				iic = cog.invites_cog  # type: ignore
			except AttributeError:
				iic = False

			logger.info("Is invites cog: {}".format(iic))
			if iic:
				if do == 'reload_messages':
					return cog.update_messages, True
				elif do == 'reload_database':
					return cog.update_db, True
				else:
					continue

		if do == 'reload_messages':
			return cls.reload_messages, True
		elif do == 'reload_database':
			return cls.reload_database, True

		raise ValueError("Не найдено ни одной команды с таким названием!")
