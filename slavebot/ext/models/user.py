from mongoengine import *

from guild import Guild
from invite import Invite



class User(Document):
	__slots__ = (
		'discord_id',
		'guild',
		'invite'
	)

	_discord_id = IntField(

	)

	_guild = ReferenceField(Guild, null=True)

	_invite = ReferenceField(Invite, null=True)

	@property
	def discord_id(self) -> int:
		return int(self._discord_id)

	@property
	def guild(self) -> Guild:
		return self._guild

	@property
	def invite(self) -> Invite:
		return self._invite

	@discord_id.setter
	def discord_id(self, discord_id: int) -> None:
		self.discord_id = discord_id
		self.save()

	@guild.setter
	def guild(self, invite: Guild or None) -> None:
		self.invite = invite
		self.save()

	@invite.setter
	def invite(self, invite: Invite or None) -> None:
		self.invite = invite
		self.save()
