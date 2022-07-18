from datetime import datetime
from typing import List

import nextcord
from nextcord import slash_command, Interaction
from nextcord.ext import commands, tasks

from slavebot import *
from _config import Config

config = Config()

logger = config.get_logger

timezone = config.get_timezone


class SpeechesList(commands.Cog):
	emoji = ''
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.default_server: nextcord.Guild or None = None
		self.bot.loop.create_task(self.assign_default_server())

		self.stopped = False

		self.send.start()

	async def assign_default_server(self):
		await self.bot.wait_until_ready()
		self.bot.add_view(GuildView(self.bot, check_device=CheckDevice, invite_modal=InviteModal))
		self.default_server = self.bot.get_guild(config.base_server)

	@commands.Cog.listener(
		name="on_ready"
	)
	async def define(self):
		logger.success("Invites cog loaded")

	async def get_role(self, roles: List[nextcord.Role], role_id: int) -> nextcord.Role or None:
		for role in roles:
			if role.id == role_id:
				return role

		return None

	@staticmethod
	async def __create_timings(now: datetime) -> List[datetime]:
		raw_timings = config.all_resets

		result = []
		for rt in raw_timings:
			result.append(
				datetime(
					year=now.year,
					month=now.month,
					day=now.day,
					hour=rt,
					minute=0,
					second=0,
					microsecond=0
				)
			)

		result.append(
			datetime(
				year=now.year,
				month=now.month,
				day=now.day,
				hour=2,
				minute=27,
				second=20,
				microsecond=0
			)
		)

		return result

	@classmethod
	async def generate_buttons_embed(cls) -> nextcord.Embed:
		embed = CustomEmbed(
			embed=nextcord.Embed(
				title="Итак вы прочли агитации..."

			)
		).normal

		return embed

	async def generate_guild_embed(self, guild: str) -> nextcord.Embed:

		manager = GuildsManager(guild)
		guild_data = manager.get_data()

		serv: nextcord.Guild = self.default_server

		cae = config.get_color_and_emoji(guild)

		color = cae['color']
		emoji = await serv.fetch_emoji(cae['emoji'])

		master = await self.get_guild_master(guild)

		fs = await tools.FormatSpeech(guild_data.speech, {"members": guild_data.users_count, "r": f"<@&{guild_data.role_id}>"}, bot=self.bot).format()
		fs = fs.speech
		speech = f"""\n\n\n{emoji} Агитация от главы гильдии {emoji} \n\n\n\n\n{fs}"""

		embed = CustomEmbed(
			embed=nextcord.Embed(
				title=f"{emoji} {guild.capitalize()} гильдия! {emoji}",
				description=speech
			)
		).color(color)

		fields: List[dict[str: str or bool]] = [
			{"name": f"{emoji} Глава гильдии:  {emoji}", "value": f"{master.mention}"},
			{"name": f"{emoji} Кол-во участников:  {emoji}", "value": f"{guild_data.users_count}"},
		]

		for f in fields:
			embed.add_field(**f)

		return embed

	async def get_all_guild_users(self, _guild: str or GuildsManager) -> List[nextcord.Member]:

		if isinstance(_guild, str):
			guild = GuildsManager(guild=_guild).get_data()
		else:
			guild = _guild.get_data()

		serv: nextcord.Guild = self.default_server

		roles = await serv.fetch_roles()

		role = nextcord.utils.get(roles, id=guild.role_id)

		members = role.members
		return members

	async def get_guild_master(self, _guild: str or GuildsManager) -> nextcord.Member:
		if isinstance(_guild, str):
			guild = GuildsManager(guild=_guild).get_data()
		else:
			guild = _guild.get_data()

		serv: nextcord.Guild = self.default_server

		roles = await serv.fetch_roles()

		role = await self.get_role(roles=roles, role_id=int(guild.master_role_id))

		members = role.members

		return members[0]

	async def __sort_guilds_by_members(self):
		return {i[0]: i[1] for i in sorted({_.lower(): int(GuildsManager(_).get_data().users_count) for _ in config.ALL_GUILDS}.items(), key=lambda para: (para[1]))}

	async def __clean_chat(self, chat: nextcord.TextChannel):
		await chat.purge(
			limit=200,
		)

	async def __update_messages(self, channel: nextcord.TextChannel):

		sorted_guilds = await self.__sort_guilds_by_members()
		guild_buttons = GuildView(self.bot, check_device=CheckDevice, invite_modal=InviteModal)

		self.bot.add_view(guild_buttons)

		for _ in sorted_guilds:
			_ = _.lower()
			embed = await self.generate_guild_embed(_)
			await channel.send(embed=embed)

		await channel.send(embed=await self.generate_buttons_embed(), view=guild_buttons)

	async def __update_db(self):
		logger.info("Updating DB")
		for _ in config.ALL_GUILDS:
			_ = _.lower()
			guild = GuildsManager(_)

			users = await self.get_all_guild_users(_)
			master = await self.get_guild_master(_)

			guild.change_row("users_count", len(users))
			guild.change_row("master", int(master.id))

		logger.success("Updated DB successfully!")

	@tasks.loop(seconds=0.00001)
	async def send(self):
		now = datetime.now(tz=timezone)

		now_time = datetime(year=now.year, month=now.month, day=now.day, hour=now.hour, minute=now.minute, second=now.second, microsecond=00)

		timings = await self.__create_timings(now)

		if now_time in timings:
			await self.__update_db()


# if not self.stopped:
# 	await self.__update_messages()


class InvitesCogManager(DataMixin, CommandsMixin, commands.Cog):
	emoji = ''
	def __init__(self, bot):
		self.bot = bot

	@slash_command(
		name="upd_db",
		description="Обновить базу данных в боте."
	)
	async def upd_db(self, inter: Interaction):
		await self.not_implemented_command(inter)

	@slash_command(
		name="upd_ms",
		description="Обновить сообщения."
	)
	async def upd_ms(self, inter: Interaction):
		await self.not_implemented_command(inter)

	@slash_command(
		name='test'
	)
	async def __test(self, inter: Interaction):
		await self.not_implemented_command(inter)


def setup(bot):
	bot.add_cog(SpeechesList(bot=bot))
	bot.add_cog(InvitesCogManager(bot=bot))
