import nextcord
from nextcord import slash_command
from nextcord.ext.commands import Cog, Bot

from slavebot import DataMixin
from slavebot.models import Guild


class Event(Cog, DataMixin):

	def __init__(self, bot: Bot):
		self.bot = bot

	@slash_command(
		name='create_event_role',

	)
	async def create_event_role(
			self,
			inter: nextcord.Interaction,
			role: nextcord.Role,
			until: int,
			guild: str = None
	):
		g = await Guild.get_or_create(code="hydro")
		print(g)
	# _guild = await self.define_guild(inter)
	#
	# if guild is None:
	# 	guild = _guild
	#
	# if guild is None:
	# 	await inter.send("Укажите гильдию")
	# 	return
	# until = datetime.datetime.fromtimestamp(until)
	#
	# x = await Guild.get_or_create(
	# 	code=guild
	# )
	#
	# print(x)
	#
	# if x is None:
	# 	await inter.send("Гильдия не найдена")
	# 	return
	#
	# g, _ = x
	#
	# _role = await g.add_event_role(
	# 	role_id=role.id,
	# 	until=until
	# )
	#
	# await inter.send(
	# 	embed=ResponseEmbed(
	# 		embed=nextcord.Embed(
	# 			title="Создана роль",
	# 			description=f"Роль {role.mention} была создана и будет "
	# 			            f"выдана всем пользователям, которые будут её "
	# 			            f"получать до "
	# 			            f"{until.strftime('%d.%m.%Y %H:%M')}"
	# 		),
	# 		user=inter.user,
	# 	).great,
	# )


def setup(bot: Bot):
	bot.add_cog(Event(bot))
