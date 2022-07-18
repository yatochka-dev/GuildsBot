from typing import List, Optional, Dict

import nextcord
from nextcord import SlashApplicationCommand, slash_command, Interaction, ApplicationCommandOption
from nextcord.ext.commands import Bot, Cog, MinimalHelpCommand

from _config import Config
from slavebot import *

config = Config()

logger = config.get_logger


class HelpCommand(MinimalHelpCommand):

	def get_command_signature(self, command: SlashApplicationCommand) -> str:
		return f'/{command.name} {command.options}'

	def get_full_command_signature(self, command: SlashApplicationCommand) -> str:
		return f"""/{command.name} {command.options}\n\n{command.description}"""


class HelpCommandCog(Cog, name='help'):
	"""Help command cog"""
	emoji = ''

	def __init__(self, bot: Bot):
		self.bot = bot

		self._original_help_command = bot.help_command
		bot.help_command = HelpCommand()
		bot.help_command.cog = self

	def cog_unload(self) -> None:
		self.bot.help_command = self._original_help_command

	def cog_embed(self, cog: Optional[Cog]) -> nextcord.Embed:
		logger.info(cog)
		if isinstance(cog, str): return CustomEmbed.unable_to()

		c: Cog = cog

		embed = CustomEmbed(
			embed=nextcord.Embed(
				title=f"Команды - {c.qualified_name}{c.emoji}",
				description=f"Категория команд - {c.qualified_name}:\n{c.description}\n\n\nПодробнее узнать о каждой команде, можно добавив её имя при вызове /help: /help help"
			)
		).normal

		for cm in c.application_commands:
			embed.add_field(
				name=f"{cm.name}",
				value=f"/{cm.name} {self.formate_options(cm.options)}",
				inline=False
			)

		return embed

	def formate_options(self, options: Dict[str, ApplicationCommandOption]):
		all_options = list(map(str.lower, options.keys()))
		return str(all_options)

	def cogs_embeds(self) -> List[nextcord.Embed]:
		return [self.cog_embed(self.bot.get_cog(name=str(cog))) for cog in self.bot.cogs]

	@slash_command(
		name='help',
		description="shows this message"
	)
	async def help_command(self, inter: Interaction, command_name: str = None):
		embeds = self.cogs_embeds()
		view = ListEmbedsView(
			embeds=embeds,
			user=inter.user
		)

		try:
			await inter.user.send(
				embed=embeds[0],
				view=view
			)


		except nextcord.Forbidden or nextcord.HTTPException:
			return await inter.send(
				embed=embeds[0],
				view=view,
				ephemeral=True
			)
		else:
			await inter.send(
				embed=CustomEmbed(
					embed=nextcord.Embed(
						title="Хелп",
						description="Я выслал список команд тебе в личку."
					)
				).great
			)


def setup(bot: Bot):
	bot.add_cog(HelpCommandCog(bot))
