from mongoengine import *

from user import User
from guild import Guild



from slavebot.tools import FormatData


class Invite(Document):
	__slots__ = (
		'invite_id',
		'user',
		'guild',

		'age',
		'gender',
		'activity',
		'why',
		'want',

		'from_data',
		'update_from_data',
	)

	_invite_id = SequenceField()

	_user = ReferenceField(User)
	_guild = ReferenceField(Guild)

	_age = IntField()
	_gender = StringField(max_length=40)
	_activity = StringField(max_length=40)

	_why = StringField(
		max_length=1024,
		min_length=50
	)

	_want = StringField(
		max_length=300,
		min_length=15
	)

	@property
	def invite_id(self) -> int:
		return int(self.invite_id)

	@property
	def user(self) -> User:
		return self.user

	@property
	def guild(self) -> Guild:
		return self.guild

	@property
	def age(self) -> int:
		return int(self.age)

	@property
	def gender(self) -> str:
		return str(self.gender)

	@property
	def activity(self) -> str:
		return str(self.activity)

	@property
	def why(self) -> str:
		return str(self.why)

	@property
	def want(self) -> str:
		return str(self.want)

	@user.setter
	def user(self, user: User) -> None:
		self.user = user
		self.save()

	@guild.setter
	def guild(self, guild: Guild) -> None:
		self.guild = guild
		self.save()

	@age.setter
	def age(self, age: int) -> None:
		self.age = age
		self.save()

	@gender.setter
	def gender(self, gender: str) -> None:
		self.gender = gender
		self.save()

	@activity.setter
	def activity(self, activity: str) -> None:
		self.activity = activity
		self.save()

	@why.setter
	def why(self, why: str) -> None:
		self.why = why
		self.save()

	@want.setter
	def want(self, want: str) -> None:
		self.want = want
		self.save()

	@classmethod
	def from_data(cls, data: FormatData):
		return cls(
			age=int(data.age),
			gender=data.gender,
			activity=data.activity,
			why=data.why,
			want=data.want
		)

	def update_from_data(self, data: FormatData):
		self.age = int(data.age)
		self.gender = data.gender
		self.activity = data.activity
		self.why = data.why
		self.want = data.want

		return self
