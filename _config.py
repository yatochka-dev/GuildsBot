import json
import os
from datetime import timezone, timedelta
from pathlib import Path
from typing import List, Tuple

import loguru
import nextcord
from pymongo import MongoClient

LOGGER = loguru.logger
TIMEZONE = timezone(offset=timedelta(hours=3), name="UTC")

LOGGER.add(
	"logs/debug.json",
	level="DEBUG",
	format="{time} | {level}      | {message}",
	rotation="00:00",
	compression="zip",
	serialize=True,
)
LOGGER.add(
	"logs/info.json",
	level="INFO",
	format="{time} | {level}      | {message}",
	rotation="00:00",
	compression="zip",
	serialize=True,
)
LOGGER.add(
	"logs/error.json",
	level="ERROR",
	format="{time} | {level}      | {message}",
	rotation="00:00",
	compression="zip",
	serialize=True,
)
LOGGER.add(
	"logs/warning.json",
	level="WARNING",
	format="{time} | {level}      | {message}",
	rotation="00:00",
	compression="zip",
	serialize=True,
)
LOGGER.add(
	"logs/success.json",
	level="SUCCESS",
	format="{time} | {level}      | {message}",
	rotation="00:00",
	compression="zip",
	serialize=True,
)


# @TODO сделать дискорд логгер типа создаю лог как обычно, а он и в дискорд и в файл и в консоль.

class BaseConfig:
	BASE_DIR = Path(__file__).resolve().parent


class InvitesConfig:
	ALL_GUILDS: List[str] = ["DENDRO", "HYDRO", "PYRO", "CRYO", "ANEMO", "ELECTRO", "GEO"]

	logs_channel: int = 1
	invites_channel: int = 929059926641356850
	speeches_channel: int = 929059781245808700

	base_server = 794987714310045727

	morning_reset = 6
	day_reset = 12
	evening_reset = 18
	night_reset = 00

	all_resets = (morning_reset, day_reset, evening_reset, night_reset)

	color_and_emoji: dict[str: Tuple[Tuple[int, int, int], int]] = {
		"dendro": ((60, 173, 79), 868084062668095549),
		"hydro": ((154, 176, 229), 868084062693236827),
		"pyro": ((204, 47, 47), 868083783457443860),
		"cryo": ((0, 252, 255), 868084061929877594),
		"anemo": ((102, 205, 170), 868084061510463538),
		"electro": ((103, 88, 182), 868084063142035466),
		"geo": ((255, 222, 60), 868084063003639889),
	}


class SecureConfig(BaseConfig):

	def __init__(self):
		self.TOKEN = self.get_key('DISCORD_TOKEN')
		self.MONGO_URI = self.get_key('MONGO_URI')

	def get_key(self, key_name: str) -> str:
		with open(
				file=self.BASE_DIR / '.env',
				mode='r',
				encoding='UTF-8'
		) as config_file:
			config_json = json.load(config_file)

		os.environ[key_name] = config_json[key_name]

		return os.environ[key_name]


class Config(InvitesConfig, SecureConfig, BaseConfig):
	GO_TO_ME_TEXT: str = """Ублюдок мать твою а ну иди сюда говно собачье а ну решил ко мне лезть ты засранец вонючий мать твою а ну иди сюда попробуй меня трахнуть я тебя сам трахну ублюдок онанист чертов будь ты проклят иди идиот трахать тебя и всю твою семью говно собачье жлоб вонючий дерьмо сука падла иди сюда мерзавец негодяй гад иди сюда ты говно жопа"""

	DB_PATH = BaseConfig.BASE_DIR / 'DB/models.sqlite3'

	DEBUG = False

	PREFIX = "+"
	TEST_PREFIX = ")"
	# add cog to ALLOWED_COGS

	ALLOWED_COGS = ("master", 'voting', 'help', 'admin', 'stuff', 'spam',
	                'invites', "events")
	LOGGER = LOGGER

	TIMEZONE = TIMEZONE

	CHANNELS = InvitesConfig

	TEST_GUILDS = (856964290777972787,)

	jp_master = {
		'dendro': 'デンドロ',
		'hydro': 'ハイドロ',
		'pyro': 'パイロ',
		'cryo': 'クライオ',
		'anemo': 'アネモ',
		'electro': 'エレクトロ',
		'geo': 'ジオ',
	}

	def __init__(self):
		super(Config, self).__init__()
		self.MONGO_CLIENT = None # MongoClient(self.MONGO_URI)
		if self.DEBUG:
			self.logs_channel = 875032054469894195
			self.invites_channel = 898642365017890836
			self.speeches_channel = 900075754153443358
			self.base_server = 856964290777972787

	@property
	def get_prefix(self) -> str:
		return self.PREFIX if not self.DEBUG else self.TEST_PREFIX

	@property
	def get_token(self) -> str:
		return self.TOKEN

	@property
	def get_allowed_cogs(self) -> tuple:
		return self.ALLOWED_COGS

	@property
	def get_logger(self) -> loguru.logger:
		return self.LOGGER

	@get_logger.setter
	def get_logger(self, logger):
		self.LOGGER = logger

	@property
	def get_timezone(self):
		return self.TIMEZONE

	@property
	def get_test_guilds(self):
		return self.TEST_GUILDS

	@property
	def get_go_to_me(self):
		return self.GO_TO_ME_TEXT

	@classmethod
	def get_color_and_emoji(cls, guild: str) -> dict[str: nextcord.Color or int]:
		if guild.lower() not in [g.lower() for g in cls.ALL_GUILDS]:
			raise ValueError(f"{guild} it's non known guild")

		return {"color": nextcord.Color.from_rgb(*cls.color_and_emoji[guild][0]), "emoji": cls.color_and_emoji[guild][1]}

	@classmethod
	def get_jp_guild(cls, guild: str):
		if guild.lower() not in [g.lower() for g in cls.ALL_GUILDS]:
			raise ValueError(f"{guild} it's non known guild")

		return cls.jp_master[guild.lower()]


def main() -> None:
	pass


if __name__ == '__main__':
	main()
