from mongoengine import *

from .guild import Guild
from .user import User
from .invite import Invite

from slavebot.tools import FormatData

connect(
	host='mongodb://127.0.0.1:27017/guilds'
)


class Manager:

	def __init__(self, user_id: int, guild: str):
		self.guild: Guild = self.__get_guild(guild)
		self.user: User = self.__get_user(user_id)

	def __get_user(self, user_id: int):
		try_ = User.objects(discord_id=user_id)

		if len(try_) > 0:
			return try_[0]
		else:
			user = User(
				discord_id=user_id,
				guild=self.guild
			)
			user.save()
			return user

	@staticmethod
	def __get_guild(guild: str):
		try_ = Guild.objects(guild=guild)

		if len(try_) > 0:
			return try_[0]
		else:
			guild_ = Guild(
				guild=guild,
			)
			guild_.save()
			return guild_

	def create_invite(self, invite_data: FormatData):
		invite = Invite.from_data(invite_data)

		invite.user = self.user
		invite.guild = self.guild

		invite.save()

		self.user.invite = invite

		invites: list = self.guild.invites

		invites.append(invite)

		self.guild.invites = invites

		self.guild.save()
		self.user.save()

		return invite.invite_id

	def delete_invite(self):
		invite = self.user.invite

		return invite.delete()

	def update_invite(self, new_data: FormatData):
		invite: Invite = self.user.invite
		return invite.update_from_data(new_data)

	def accept_invite(self):
		invite: Invite = self.user._invite

		self.user._invite = None

		self.guild._invites = [inv for inv in self.guild.invites if inv.id != invite.id]

		self.user.save()
		self.guild.save()


def main():

	u = User(
		_discord_id=686207718822117463
	)

	u.save()

	g = Guild(
		_guild='anemo',
		_master=u
	)

	g.save()



	# m = Manager(
	# 	99, 'cryo'
	# )
	#
	# data = FormatData(
	# 	age=19,
	# 	gender="female",
	# 	activity="voice",
	# 	why_accept="##########daw##########################################################################",
	# 	want="##################awdawd##################################################################"
	# )
	#
	# m.create_invite(
	# 	data
	# )


if __name__ == '__main__':
	main()
