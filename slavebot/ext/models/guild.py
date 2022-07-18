from typing import List

from mongoengine import *

from invite import Invite
from user import User


class Guild(Document):
	__slots__ = (
		'guild',
		'master',
		'members',
		'invites',
		'add_member',
		'add_invite',
	)

	_guild = StringField(
		max_length=30,
		unique=True,
	)

	_master = ReferenceField(User, null=True, default=None)

	_members = ListField(field=ReferenceField('User'), default=[])
	_invites = ListField(field=ReferenceField('Invite'), default=[])

	def __str__(self):
		return str(self.guild)

	@property
	def guild(self) -> str:
		return str(self.guild)

	@property
	def master(self) -> User:
		return self.master

	@property
	def members(self) -> List[User]:
		return list(self.members)

	@property
	def invites(self) -> List[Invite]:
		return list(self.invites)

	@guild.setter
	def guild(self, guild: str) -> None:
		self.guild = guild
		self.save()

	@master.setter
	def master(self, master: User) -> None:
		self.master = master
		self.save()

	@members.setter
	def members(self, members: List[User]) -> None:
		self.members = members
		self.save()

	@invites.setter
	def invites(self, invites: List[Invite]) -> None:
		self.invites = invites
		self.save()

	def add_member(self, member: User) -> None:
		members = self.members
		members.append(member)
		self.invites = members

	def add_invite(self, invite: Invite) -> None:
		invites = self.invites
		invites.append(invite)
		self.invites = invites

def main():
	u = User(
		_discord_id=1,
		_guild=None
	)
	u.save()
	g = Guild(
		guild='pyro',
		master=u
	)
	g.save()

	u.guild = g

if __name__ == '__main__':
	main()
