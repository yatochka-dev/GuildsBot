from typing import List

import nextcord
from nextcord import slash_command, Interaction
from nextcord.ext.commands import Bot, Cog

from slavebot import *
from _config import Config

config = Config()

logger = config.get_logger

class Presence(Cog):
	emoji = "🎮"

	def __init__(self, bot: Bot):
		self.bot = bot
		self.presence_types: List[str] = [
			'game',
			'steam',
		]

	async def define_type(self, t: str):
		match t.lower():
			case 'game':
				return nextcord.Game
			case 'stream':
				return nextcord.Streaming

	async def set(self, text: str, _type: callable):
		return await self.bot.change_presence(
			activity=_type(name=text)
		)

	@slash_command(
		name="set_status"
	)
	async def set_status(self, inter: Interaction, text: str, type: str):
		logger.info(type.lower().strip() not in self.presence_types)
		if type.lower().strip() not in self.presence_types:
			return await inter.send(
				embed=ResponseEmbed.unable_to(
					unable_to=f", изменить статус, неизвестный тип {type}",
					user=inter.user
				)
			)

		await self.set(
			text=text,
			_type=await self.define_type(type)
		)

		await inter.send(
			embed=ResponseEmbed(
				nextcord.Embed(
					title="Успешно",
					description=f"Статус бота изменён на {text}, с типом {type}"
				),
				inter.user
			).great
		)



def setup(bot: Bot):
	bot.add_cog(Presence(bot))
