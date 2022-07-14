import nextcord
import peewee as models
from nextcord.ext import commands

GUILDS_LIST = ["Dendro", "Hydro", "Pyro", "Cryo", "Anemo", "Electro", "Geo"]  # CONST # NOQA
from _config import Config

config = Config()
db = models.SqliteDatabase(config.DB_PATH)


class User(models.Model):
	_id = models.IntegerField(unique=True, primary_key=True)

	is_in_creating_invite = models.BooleanField(default=False)
	has_invite = models.BooleanField(default=False)

	class Meta:
		database = db

	def __str__(self):
		return f"- {self._id}\n- {self.is_in_creating_invite} \n- {self.has_invite}"

	def parse(self, bot: commands.Bot) -> nextcord.User:
		return bot.get_user(int(self._id))  # NOQA


class Guild(models.Model):
	guild = models.CharField(
		primary_key=True,
		max_length=40,
		unique=True,
		verbose_name="Название гильдии",  # NOQA
	)

	guild_master_speech = models.TextField(
		null=False,
		verbose_name="Речь гильдмастера"  # NOQA
	)

	chat = models.IntegerField(
		null=False,
		unique=True,
	)

	role = models.IntegerField(
		null=False,
		unique=True,
	)

	master_role = models.IntegerField(
		null=False,
		unique=True,
	)

	chat_topic = models.TextField(
		null=False,
		verbose_name="Тема канала"  # NOQA
	)

	users = models.ManyToManyField(model=User)

	master = models.ForeignKeyField(model=User, backref="guild master")

	def parse_master(self, bot: commands.Bot) -> nextcord.User:
		return bot.get_user(int(self.master._id))  # NOQA

	def parse_chat(self, server: nextcord.Guild) -> nextcord.TextChannel:
		return server.get_channel(int(self.chat))  # NOQA

	def parse_role(self, server: nextcord.Guild) -> nextcord.Role:
		return server.get_role(int(self.role))  # NOQA

	def parse_master_role(self, server: nextcord.Guild) -> nextcord.Role:
		return server.get_role(int(self.master_role))  # NOQA

	class Meta:
		database = db


if __name__ == '__main__':
	with db:
		db.create_tables([User])
#
# with open("additional_files/guilds.json", "r") as guild_file:
# 	guilds_json = json.load(guild_file)
#
# print(guilds_json)
#
# for g in config.ALL_GUILDS:
# 	gui = g.lower()
#
# 	data = guilds_json[f"guild_{gui.capitalize()}"]
#
# 	g = Guild.create(
# 		guild=gui,
# 		guild_master_speech=data["campaign_speech"],
# 		chat=data["channel"],
# 		role=data["role"],
# 		master_role=data["guild_master_role"],
# 		chat_topic=data["guild_chat_description"],
# 		master=data["guild_president"],
# 		users_count=6363
#
# 	)
# 	g.save()
