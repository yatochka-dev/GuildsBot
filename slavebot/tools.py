import re
from typing import List

import nextcord
from nextcord.ext import commands

from _config import Config
from slavebot import *
config = Config()
from  .InvitesManager import InvitesManager
from  .GuildsManager import GuildsManager
logger = config.get_logger


def get_year_end(year: int) -> str:
	if (year % 10 == 1) and (year != 11) and (year != 111):
		result = "год"
	elif (year % 10 > 1) and (year % 10 < 5) and (year != 12) and (year != 13) and (year != 14):
		result = f"года"
	else:
		result = f"лет"

	return result


def has_role(role: nextcord.Role, user: nextcord.Member) -> bool:
	return role in user.roles


def __create_guild(guild_name: str):
	g = Guild.create(
		guild=guild_name,
		guild_master_speech="",
		chat=0,
		role=0,
		master_role=0,
		chat_topic="",

	)
	g.save()
	return g


def get_or_create_guild(guild_name: str):
	try:
		return Guild.get(Guild.guild == guild_name)
	except:
		return __create_guild(guild_name)


class FormatData:

	def __init__(
			self,
			age: List[str] or str,
			gender: List[str] or str,
			activity: List[str] or str,

			why_accept: str,
			want: str,
	):
		self.age = age
		self.gender = gender
		self.activity = activity
		self.why = why_accept
		self.want = want

	def __str__(
			self
	):
		result = \
			f"""
			\t- {self.age}
			\t- {self.gender}
			\t- {self.activity}
			\t- {self.why}
			\t- {self.want}
			""".strip()
		return result

	def format(self):
		self.age = self.__format_age()
		self.why = self.__format_why()
		self.want = self.__format_want()
		self.gender = self.__format_gender()
		self.activity = self.__format_activity()

		return self

	def create_fields(self) -> list[dict]:
		age = {
			"name": "Возраст:",
			"value": f"{self.age}",
			"inline": False
		}

		gender = {
			"name": "Пол:",
			"value": f"{self.gender}",
			"inline": False
		}

		activity = {
			"name": "Активен:",
			"value": f"{self.activity}",
			"inline": False
		}

		why_accept = {
			"name": "Почему гильдмастер должен принять его/её:",
			"value": f"{self.why}",
			"inline": False
		}

		what_want = {
			"name": "Чего хочет от гильдии:",
			"value": f"{self.want}",
			"inline": False
		}

		return [age, gender, activity, why_accept, what_want]

	def __format_gender(self) -> str:
		"""
		["Male"] -> male
		"""
		try:
			if isinstance(self.gender, list):
				genders = self.gender
				result = genders[0].strip().lower()
			else:
				result = self.gender.strip().lower()

		except Exception as exc:
			logger.error(f"Format gender error {exc}")
			result = "Не удалось получить пол."

		return result

	def __format_age(self) -> str:
		"""
		["1"] or ["NONE"] or ["MORE"]
		:return:
		"""
		try:
			if isinstance(self.age, list):
				age = self.age[0]

				if age == "NONE":
					result: str = "Не указан"

				elif age == "MORE":
					result: str = "Более 23-х лет"
				else:
					try:
						_age: int = int(age)
						result: str = f"{_age} {get_year_end(_age)}"
					except (ValueError):
						result: str = "Не удалось форматировать фозраст пользователя!".strip()

				return result
			elif isinstance(self.age, str):
				format_str = str(self.age).strip().lower()
				ages: List = re.findall(r"\d+", format_str)
				if len(ages) > 0:
					age = sum([int(a) for a in ages])
					age = f"{age} {get_year_end(age)}"
				else:
					age = format_str

				return str(age)
			else:
				raise FormatError("Не удалось опеределить тип входных данных.")

		except Exception as exc:
			logger.error(f"Format age error {exc}")
			return "Не удалось получить возраст."

	def __format_why(self) -> str:
		return self.why.strip() or "Не удалось получить данное поле."

	def __format_want(self) -> str:
		return self.want.strip() or "Не удалось получить данное поле."

	def __format_activity(self):
		try:
			if isinstance(self.activity, list):
				activity = self.activity
				result = activity[0].strip().lower()
			else:
				result = self.activity.strip().lower()
		except Exception as exc:
			logger.error(f"Format activity error {exc}")
			result = "Не удалось получить предпочтительную активность."

		return result


class FormatSpeech:

	def __init__(
			self,
			speech: str,
			vars: dict,
			bot: commands.Bot
	):
		self.speech = speech
		self.vars = vars
		self.bot = bot
		self.server = self.bot.get_guild(config.base_server)

	async def format(self):
		await self.__apply_vars()
		await self.__apply_emojis()
		return self

	async def __apply_vars(self):
		try:
			sp = self.speech % self.vars
		except KeyError as exc:
			var_name = str(exc).replace("'", "").strip()
			self.vars.update({var_name: "#"})
			await self.__apply_vars()
			return
		except Exception as exc:
			logger.critical(f"Error in speech formatting {exc}")
			return self.speech

		self.speech = sp

	async def __apply_emojis(self):
		pattern = r'<e:\d\d\d\d\d\d\d\d\d\d\d\d\d\d\d\d\d\d:>'
		res = re.findall(pattern, self.speech)
		for _ in res:
			id = re.findall(r"\d+", str(_))[0]
			try:
				emoji = await self.server.fetch_emoji(int(id))
			except nextcord.NotFound:
				emoji = "#"

			self.speech = re.sub(_, str(emoji), self.speech)


class CheckUser:

	def __init__(
			self,
			bot: commands.Bot,
			server: nextcord.Guild,
			user: nextcord.Member
	):
		self.bot = bot
		self.server = server
		self.user = user
		self.manager = InvitesManager(self.user.id)

	async def is_in_guild(self) -> bool:
		all_roles = [self.server.get_role(GuildsManager(_.lower()).get_data().role_id) for _ in config.ALL_GUILDS]

		for r in all_roles:
			if has_role(role=r, user=self.user):
				return True

		return False

	async def is_master(self):
		all_roles = [self.server.get_role(GuildsManager(_.lower()).get_data().master_role_id) for _ in config.ALL_GUILDS]

		for r in all_roles:
			if has_role(role=r, user=self.user):
				return True

		return False

	@property
	async def has_invite(self) -> bool:
		return self.manager.has_invite()

	@property
	async def in_invite(self):
		return self.manager.creating_invite()

	@property
	async def is_clean(self):
		return await self.is_in_guild() or await self.is_master() or await self.has_invite or await self.in_invite

class UIResponse:
	responses_list: List[str] = [
		'close',
	]

	def __init__(self, response: str):
		self.response = self.get_resp(response)

	def change(self, to: str) -> None:
		if to in self.responses_list:
			self.response = to
		else:
			raise UIResponseError("Неизвестный ответ")

	@classmethod
	def get_resp(cls, resp: str):
		if resp in cls.responses_list:
			return resp
		else:
			raise UIResponseError("Неверный ответ")

	@property
	def close(self):
		return self.response == 'close'


class VotingMenu(UIResponse):
	responses_list = [
		'end',
		'start'
	]

	@property
	def end(self):
		return self.response == 'end'

	@property
	def start(self):
		return self.response == 'start'
