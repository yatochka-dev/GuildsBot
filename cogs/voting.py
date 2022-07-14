import random
from typing import List

import nextcord
from nextcord import Interaction, slash_command
from nextcord.ext import commands

from slavebot import *
from _config import Config

config = Config()

logger = config.get_logger
timezone = config.get_timezone


class Voting(DataMixin, commands.Cog):

	def __init__(self, bot: commands.Bot):
		self.bot = bot

	async def get_rand_react(self, selected: List[nextcord.Emoji], list_to_choose: List[nextcord.Emoji] or any) -> nextcord.Emoji:
		r = random.choice(list_to_choose)
		blocked_reacts_ids = [
			config.get_color_and_emoji(_.lower())['emoji'] for _ in config.ALL_GUILDS
		]
		if r in selected and r.id not in blocked_reacts_ids and not r.name.startswith("Element"):
			return await self.get_rand_react(list_to_choose, list_to_choose)
		else:
			return r

	async def get_candidates(self, inter: Interaction, react_name: str, message_id):
		channel: nextcord.TextChannel = inter.channel  # type: ignore
		message: nextcord.Message = await channel.get_partial_message(int(message_id)).fetch()

		react = nextcord.utils.get(
			await inter.guild.fetch_emojis(),
			name=react_name
		)

		r = message.reactions
		res = """"""
		res_d: dict = {

		}

		selected_reacts: List[nextcord.Emoji] = []

		for _ in r:
			if _.emoji == react:
				async for member in _.users(limit=40):
					if member.id != 686207718822117463:
						rand = await self.get_rand_react(selected_reacts, inter.guild.emojis)
						selected_reacts.append(rand)
						res += f"\n{rand} -> {member.mention} -> {member.name}#{member.discriminator}\n"
						res_d[rand] = member.id

		return res_d, res, selected_reacts

	@slash_command(
		name='voting',

	)
	@logger.catch()
	async def voting(self, inter: Interaction, react_name: str, message_id, guild: str, add_member: nextcord.Member = None):
		# @ToDo Добавить пинг гильдии + добавление в закреп
		if await self.has_perms(inter=inter):
			x = await self.get_candidates(inter, react_name, message_id)
			candidates, text, selected_reacts = x
			if add_member:
				r = await self.get_rand_react(
					selected_reacts, inter.guild.emojis
				)
				candidates[r] = add_member.id
				text += f"\n{r} -> {add_member.mention} -> {add_member.name}#{add_member.discriminator}\n"
			emojis = [k for k, v in candidates.items()]

			embed = CustomEmbed(
				nextcord.Embed(
					title='Выборы!',
					description=f"Сегодня начинается второй этап выборов, закончится он {await self.get_timestamp((60 * 24), discord=True)}!\n\n**Вы должны выбрать ГМ-а который будет править до "
					            f"середины "
					            f"следующего "
					            f"месяца!**\n\n{text}\n\n\nВыберите кандидата из списка, и нажми на прилагающуюся к нему реакцию! "
				)
			).great

			msg = await inter.send(
				embed=embed,

			)

			msg = await msg.fetch()

			for e in emojis:
				try:
					await msg.add_reaction(e)
				except Exception as exc:
					logger.critical(
						f"Error in voting, {exc}"
					)
					await msg.delete(
						delay=0
					)
					await self.bad_callback(
						inter, f"Не удалось начать голосование, {exc}"
					)
					return

			manager = GuildsManager(guild.lower())
			data = manager.get_data()
			role = inter.guild.get_role(data.role_id)

			await msg.reply(
				content=f"{role.mention}",
			)

			await msg.pin()

	@slash_command(
		name='assign',

	)
	async def assign_master(self, inter: Interaction, master: nextcord.Member, guild: str):

		if await self.has_perms(
				inter=inter
		):
			if guild.lower() not in [_.lower() for _ in config.ALL_GUILDS]:
				await self.bad_callback(
					inter,
					"Неизвестная гильдия!"
				)
			else:
				c = tools.CheckUser(
					self.bot,
					self.bot.get_guild(config.base_server),
					master
				)

				manager = GuildsManager(guild.lower())

				data = manager.get_data()
				role = inter.guild.get_role(data.role_id)
				master_role = inter.guild.get_role(data.master_role_id)
				guild_channel = inter.guild.get_channel(data.chat_id)

				hi = await c.has_invite
				ii = await c.in_invite
				im = await c.is_master()
				niig = not tools.has_role(role, master)

				if hi or ii or im or niig:
					error = f"Невозможно назначить пользователя мастером: \n\nЕсть заявка - {hi}\n\nЗаполняет заявку - {ii}\n\nУже мастер - {im}\n\nНе является членом {guild.lower().capitalize()} гильдии -" \
					        f" {niig}"
					return await self.bad_callback(
						inter, error
					)

				await master.add_roles(
					master_role,
					reason="По приказу генерала гафса. \n"
					       "Назначение нового мастера"
				)

				new_embed = CustomEmbed(
					nextcord.Embed(
						title="Поздравляю",
						description=f"В {config.get_jp_guild(guild.lower()) or 'вашей гильдии'} назначен новый мастер!"
					)
				).great

				new_embed.set_image(url=self.get_img('sfw', 'kick'))

				new_embed.add_field(
					name="Новый мастер",
					value=f"{master.mention}"
				)

				msg = await guild_channel.send(
					embed=new_embed,
				)

				await msg.pin(
					reason="По приказу генерала гафса. \n"
					       "Новый мастер должен быть услышан!"
				)

				manager = GuildsManager(guild.lower())
				data = manager.get_data()
				role = inter.guild.get_role(data.role_id)

				await msg.reply(
					content=f"{role.mention}",
				)

				await inter.send(
					embed=CustomEmbed.done(),
					ephemeral=True
				)


def setup(bot: commands.Bot):
	bot.add_cog(Voting(bot))
