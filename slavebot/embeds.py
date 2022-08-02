import datetime
from typing import Tuple, List

import nextcord
from nextcord.embeds import EmptyEmbed

from _config import Config

config = Config()

timezone = config.get_timezone


class CustomEmbed:
	BASE_COLOR: nextcord.Color = nextcord.Color.from_rgb(37, 244, 188)

	def __init__(self, embed: nextcord.Embed):
		self.embed: nextcord.Embed = embed

	def __repr__(self) -> str:
		return str(self.embed)

	def base(self, color: nextcord.Color) -> nextcord.Embed:
		self.embed.set_author(
			name=f"Система управления гильдями!",
			icon_url="https://cdn.discordapp.com/attachments/862044149779529750/956595788979535902/256.png",
		)

		self.embed._colour = color

		self.embed.timestamp = datetime.datetime.now(tz=timezone)

		return self.embed

	def color(self, _color: nextcord.Color | Tuple[int, int, int]) -> nextcord.Embed:
		if isinstance(_color, tuple):
			color = nextcord.Color.from_rgb(*_color)
		else:
			color = _color

		return self.base(
			color=color
		)

	@property
	def normal(self) -> nextcord.Embed:
		return self.base(self.BASE_COLOR)

	@property
	def error(self) -> nextcord.Embed:
		return self.base(nextcord.Color.red())

	@property
	def great(self) -> nextcord.Embed:
		return self.base(nextcord.Color.green())

	@classmethod
	def no_perm(cls, *args, **kwargs) -> nextcord.Embed:
		return cls(
			nextcord.Embed(
				title="Ошибка",
				description="Недостаточно прав для этого взаимодействия!"
			)
		).error

	@classmethod
	def unable_to(cls, *args, **kwargs) -> nextcord.Embed:
		return CustomEmbed(
			nextcord.Embed(
				title="Ошибка",
				description="Невозможно загрузить контент связанный с этим взаимодействием."
			)
		).error

	@classmethod
	def working_on(cls, *args, **kwargs) -> nextcord.Embed:
		return cls(
			nextcord.Embed(
				title=". . .",
				description="Произвожу вычисления..."
			)
		).normal

	@classmethod
	def done(cls, *args, **kwargs):
		return cls(
			nextcord.Embed(
				title="Успешно",
				description="Действие успешно выполнено!"
			)
		).great

	@classmethod
	def not_implemented(cls, *args, **kwargs):
		return cls(
			embed=nextcord.Embed(
				title="Хелп",
				description="Этой команды ещё нет, обидно, правда?"
			)
		).error

	@classmethod
	def has_error(cls, exc=None, *args, **kwargs) -> nextcord.Embed:
		exc = exc if exc else ""
		return cls(
			nextcord.Embed(
				title="Ошибка",
				description=f"Произошла неожиданная ошибка! \n {exc}"
			)
		).error


class ResponseEmbed(CustomEmbed):

	def __init__(self, embed: nextcord.Embed, user: nextcord.Member or nextcord.User):
		super(ResponseEmbed, self).__init__(embed)

		self.user = user

	def base(self, color: nextcord.Color) -> nextcord.Embed:
		embed = super(ResponseEmbed, self).base(color)

		footer = f"{self.user.display_name}" if self.user else EmptyEmbed
		icon_url = str(self.user.avatar.url) if self.user else EmptyEmbed

		embed.set_footer(
			text=footer,
			icon_url=icon_url

		)
		return embed

	@classmethod
	def no_perm(cls, user: nextcord.User or nextcord.Member) -> nextcord.Embed:
		return cls(
			nextcord.Embed(
				title="Ошибка",
				description="Недостаточно прав для этого взаимодействия!"
			),
			user
		).error

	@classmethod
	def unable_to(cls, user: nextcord.User or nextcord.Member, unable_to: str="загрузить контент связанный с этим взаимодействием") -> nextcord.Embed:
		unable_to = " " + unable_to
		unable_to = unable_to.strip()

		return cls(
			nextcord.Embed(
				title="Ошибка",
				description=f"Невозможно{unable_to}."
			),
			user
		).error

	@classmethod
	def working_on(cls, user: nextcord.User or nextcord.Member) -> nextcord.Embed:
		return cls(
			nextcord.Embed(
				title=". . .",
				description="Произвожу вычисления..."
			),
			user
		).normal

	@classmethod
	def done(cls, user: nextcord.User or nextcord.Member):
		return cls(
			nextcord.Embed(
				title="Успешно",
				description="Действие успешно выполнено!"
			),
			user
		).great

	@classmethod
	def not_implemented(cls, user: nextcord.User or nextcord.Member):
		return cls(
			nextcord.Embed(
				title="Ошибка",
				description="Этой команды ещё нет, обидно, правда?"
			),
			user
		).error

	@classmethod
	def has_error(cls, exc=None, *args, **kwargs) -> nextcord.Embed:
		exc = exc if exc else ""
		user = kwargs.get('user', None)
		return cls(
			nextcord.Embed(
				title="Ошибка",
				description=f"Произошла неожиданная ошибка! \n {exc}"
			),
			user
		).error


class EmbedWithUsers:

	def __init__(self, embed: CustomEmbed, users: List[nextcord.Member or nextcord.User]):
		super(EmbedWithUsers, self).__init__(embed=embed)

		self.users = users
		self.embed = embed.normal
