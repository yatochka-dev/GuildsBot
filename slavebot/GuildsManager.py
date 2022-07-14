import sqlite3
from typing import List

import nextcord

from .errors import ThisFieldDoesNotExists, SQLError
from _config import Config

config = Config()

con = sqlite3.connect(config.DB_PATH)
cur = con.cursor()


class AbsGuild:

	def __init__(self, data: tuple):
		self.guild: str = data[0]
		self.speech: str = data[1]
		self.chat_topic: str = data[7]

		self.chat_id: int = data[2]
		self.role_id: int = data[3]
		self.users_count: int = data[4]
		self.master_role_id: int = data[5]
		self.master: int = data[6]

	def __str__(self):
		result = f"----------{self.guild}----------\n" \
		         f"----------{self.speech=}----------\n" \
		         f"----------{self.chat_topic=}----------\n" \
		         f"----------{self.chat_id=}----------\n" \
		         f"----------{self.role_id=}----------\n" \
		         f"----------{self.master_role_id=}----------\n" \
		         f"----------{self.master=}----------\n" \
		         f"----------{self.users_count=}----------\n"

		return result

	def parse_role(self, server: nextcord.Guild):
		return server.get_role(self.role_id)

	def parse_master_role(self, server: nextcord.Guild):
		return server.get_role(self.master_role_id)


class GuildsManager:
	FIELDS_LIST = ["guild", "speech", "chat", "role", "master_role", "chat_topic", "master", "users_count"]
	STR_FIELDS = ["guild", "speech", "chat_topic"]

	def __init__(
			self,
			guild: str
	):
		self.guild = guild.lower()

	def __str__(self):
		return self.guild

	def change_row(self, what: str, to_what: str or int):
		if what == 'guild':
			raise ValueError("You cannot change that field")

		if what not in self.FIELDS_LIST:
			raise ThisFieldDoesNotExists("Этого поля не существует")

		if what in self.STR_FIELDS and isinstance(to_what, int):
			raise TypeError("Expected type str")

		if what not in self.STR_FIELDS and isinstance(to_what, str):
			raise TypeError("Expected type int")

		if isinstance(to_what, str):
			to = f"'{to_what}'"
		else:
			to = to_what

		query = """
			UPDATE guild
			SET %(column)s = %(value)s
			WHERE
			    guild = '%(guild)s'
		""" % {
			"guild": self.guild,
			"column": what,
			"value": to
		}  # type: ignore

		cur.execute(query)
		con.commit()
		return self

	def get_data(self) -> AbsGuild:
		query = """
			SELECT * FROM guild WHERE guild = '%s'
		""" % self.guild.lower()
		cur.execute(
			query

		)

		data = cur.fetchone()
		return AbsGuild(data)

	def get_all_data(self) -> List[AbsGuild]:
		result = []
		for g in config.ALL_GUILDS:
			self.guild = g
			result.append(self.get_data())
		return result

	def create_row(self, speech: str, chat: int, role: int, master_role: int, chat_topic: str, master: int, users_count: int):
		query = f"""
			INSERT INTO guild (guild, speech, chat, role, master_role, chat_topic, master, users_count) VALUES ('{self.guild.lower()}', '{speech}', {chat}, {role}, {master_role},  
			'{chat_topic}', {master}, {users_count})
		"""  # NOQA

		cur.execute(
			query
		)
		con.commit()
		return self.get_data()


class DB:

	def __init__(self, sql: str):
		self.sql = sql

	def do(self) -> any:
		try:
			cur.execute(self.sql)

			con.commit()

			return cur.fetchone()
		except Exception as exc:
			raise SQLError(f"Ошибка {exc}")


if __name__ == '__main__':
	pass
	manager = GuildsManager('dendro')
	data = manager.change_row("master", 525388562951176222)
	print(data.get_data())

# d = manager.get_all_data()
# for x in d:
# 	print(x)
# print(d)

#
# 	data = manager.get_data()
#
# 	print(data.master)
# cur.execute("""
# create table "guild"
# (
#
#     guild VARCHAR(255) unique NOT NULL PRIMARY KEY,
#     speech TEXT NOT NULL,
#     chat INTEGER unique NOT NULL,
#     role INTEGER unique NOT NULL,
#     users_count INTEGER NOT NULL,
#     master_role INTEGER unique NOT NULL,
#     master INTEGER unique NOT NULL,
#     chat_topic TEXT
#
# );
# """)
#
# with open("additional_files/guilds.json", "r") as guild_file:
# 	guilds_json = json.load(guild_file)
#
# for g in config.ALL_GUILDS:
# 	gui = g.lower()
#
# 	data = guilds_json[f"guild_{gui.capitalize()}"]
# 	manager = GuildsManager(gui)
#
# 	manager.create_row(
# 		speech=data["campaign_speech"],
# 		chat=data["channel"],
# 		role=data["role"],
# 		master_role=data["guild_master_role"],
# 		chat_topic=data["guild_chat_description"],
# 		master=data["guild_president"],
# 		users_count=10
# 	)
