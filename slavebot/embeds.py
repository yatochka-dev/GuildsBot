import datetime
from typing import Tuple

import nextcord

from _config import Config

config = Config()

timezone = config.get_timezone


class CustomEmbed:
	BASE_COLOR: nextcord.Color = nextcord.Color.from_rgb(37, 244, 188)

	def __init__(self, embed: nextcord.Embed):
		self.embed: nextcord.Embed = embed

	def __repr__(self) -> str:
		return str(self.embed)

	@property
	def _base(self, color: nextcord.Color = BASE_COLOR) -> nextcord.Embed:
		self.embed.set_author(
			name=f"Система управления гильдями!",
			icon_url="https://cdn.discordapp.com/attachments/862044149779529750/956595788979535902/256.png",
		)

		self.embed._colour = color

		self.embed.timestamp = datetime.datetime.now(tz=timezone)

		return self.embed

	@property
	def normal(self) -> nextcord.Embed:
		self._base._colour = self.BASE_COLOR
		return self._base

	@property
	def error(self) -> nextcord.Embed:
		embed = self._base
		embed._colour = nextcord.Color.red()
		return embed

	@property
	def great(self) -> nextcord.Embed:
		embed = self._base
		embed._colour = nextcord.Color.green()
		return embed

	def color(self, _color: nextcord.Color | Tuple[int, int, int]) -> nextcord.Embed:
		if isinstance(_color, tuple):
			color = nextcord.Color.from_rgb(*_color)
		else:
			color = _color

		embed = self._base
		embed._colour = color

		return embed

	@classmethod
	def no_perm(cls) -> nextcord.Embed:
		return cls(
			nextcord.Embed(
				title="Ошибка",
				description="Недостаточно прав для этого взаимодействия!"
			)
		).error

	@classmethod
	def working_on(cls) -> nextcord.Embed:
		return cls(
			nextcord.Embed(
				title=". . .",
				description="Произвожу вычисления..."
			)
		).normal

	@classmethod
	def done(cls):
		return cls(
			nextcord.Embed(
				title="Успешно",
				description="Действие успешно выполнено!"
			)
		).great

	@classmethod
	def not_implemented(cls):
		return cls(
			embed=nextcord.Embed(
				title="Хелп",
				description="Этой команды ещё нет, обидно, правда?"
			)
		).error