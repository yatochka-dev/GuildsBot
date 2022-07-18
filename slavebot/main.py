# imports
import asyncio
import datetime as dt
import json
import os
import random
import re
import secrets
from asyncio import TimeoutError
from datetime import datetime
import loguru
import nextcord
import nextcord as discord
# from imports
from nextcord.ext import commands as com, tasks
from nextcord.ext.commands.errors import MissingPermissions, BotMissingPermissions

from slavebot.ext import models
from utils import GuildDefense

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

LOGGER = loguru.logger

ONE_DAY_IN_SECONDS = (60 * 60 * 24)

GUILDS = ["Dendro", "Hydro", "Pyro", "Cryo", "Anemo", "Electro", "Geo"]


settings = {
	'pre': "+",
	'token': "ODYxNjI2NDA1MzEzNzA4MDYy.YOMiHw.2xTxozTjeP6xan0sByy_8XaBRLc",
	"bot": "SlaveBot#5164",
	"user_id": "861626405313708062",
	"ag_ci": 929059781245808700,
	"bi_ci": 929059926641356850
}

# bot object
bot = com.Bot(shard_count=2, command_prefix=com.when_mentioned_or(f"{settings['pre']}"), intents=discord.Intents.all())
bot.remove_command(name="help")
standard_color = discord.Color.from_rgb(80, 141, 234)

DEBUG = True


# on-ready functions
@bot.event
async def on_ready():
	def upd_invites():
		invites_json = {
			"invites_numbers": 0,
			"ids_list": [],
		}

		with open('additional_files/invites.json', "w", encoding="UTF-8") as invites_file_w:
			json.dump(invites_json, invites_file_w, indent=4)

		with open("additional_files/users_cooldown.json", "w", encoding="UTF-8") as cooldown_file_w:
			json.dump({}, cooldown_file_w, indent=4)

	upd_invites()

	server = bot.get_guild(794987714310045727)

	chat = server.get_channel(929059781245808700)

	if DEBUG is False:
		st = await chat.history(limit=500).flatten()
		for msg in st:
			try:
				await msg.delete()
				LOGGER.debug(
					"One message was deleted"
				)
			except Exception as exc:
				LOGGER.error(
					f"Error in message clearing\n{exc}"
				)

		await update_the_database()
		await update_the_messages()

		UpdateTask.start()

	UpdatePresence.start()

	# Каждое реальное изменение +1 в первую цифру каждая команда +1 во вторую каждый баг фикс +1 в третью
	def version(big, medium, small) -> str:
		return ".".join([str(big), str(medium), str(small)])

	LOGGER.info("I-i-i am in the {} body! version {}".format(bot.user, version(1, 2, 5)))
	LOGGER.info("Now ping is {}".format(bot.latency))


@bot.event
async def on_command_error(ctx, error):
	if isinstance(error, com.MaxConcurrencyReached):
		embed = discord.Embed(title="Уупс...", description="потише, мальчик(или вуман), я запрещаю спамить эту команду.", color=discord.Color.red())
		await ctx.reply(embed=embed, view=models.NonBts(), delete_after=3.5)
		await ctx.message.add_reaction('❌')
	else:
		LOGGER.warning(
			f"something went wrong, but we don't saying it to users. \n\n\nError: \n{error}\n"
		)


@tasks.loop(minutes=5)
async def UpdatePresence():
	c = 0
	for g in bot.guilds:
		c += len(g.members)

	LOGGER.info(
		"Presence was started"
	)
	presences = ["подслушивает {count} разговоров...".format(count=round(int(c) / random.randint(2, 4), 0)), "Ваши крики о помощи...", "Опенинг Клинка Рассекающего демонов!", "Советы от недалёких "
	                                                                                                                                                                           "людей.",
	             "Мурлыканье Вики",
	             "Стоны Яты",
	             "Хохлятский совет"]
	for p in presences:
		await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=str(p)))
		await asyncio.sleep(60)

	UpdatePresence.restart()


async def update_the_database():
	async def get_Gmaster(guild):

		guild_master_role_id = models.get_tag_value("TIME_ROLE", f"guild-master_{guild}")

		guild_master_role = server.get_role(guild_master_role_id)
		try:
			guild_master_user = guild_master_role.members[0]
		except Exception as e:
			LOGGER.error(f"ОШИБКА В get_Gmaster в НЕ НАЙДЕН ГМ {guild}, ПОДСТАВЛЕН АВАКУСУ"
			             f"! \n" + str(e))

			guild_master_user = await server.fetch_member(361198710551740428)
		return {"role": guild_master_role, "user": guild_master_user}

	def get_channel(guild):
		return server.get_channel(models.get_tag_value("CHANNEL", f"channel_{guild}"))

	async def get_users_count(guild):
		server = await bot.fetch_guild(794987714310045727)
		guild_role = models.NEDOGUILD().get_one_tag(guild=guild, tag="role")
		guild_role = server.get_role(guild_role)
		count = len(guild_role.members)

		return count

	server = bot.get_guild(794987714310045727)
	guilds = ["Dendro", "Hydro", "Pyro", "Cryo", "Anemo", "Electro", "Geo"]

	for guild in guilds:
		LOGGER.info(f"[INFO] UPDATING {guild.upper()} GUILD")
		gm_and_role = await get_Gmaster(guild)
		models.NEDOGUILD().update_one_tag(guild=guild, tag="users", new_value=await get_users_count(guild))
		models.NEDOGUILD().update_one_tag(guild=guild, tag="guild_president", new_value=gm_and_role["user"].id)
		models.NEDOGUILD().update_one_tag(guild=guild, tag="guild_chat_description", new_value=get_channel(guild).topic)
		models.NEDOGUILD().update_one_tag(guild=guild, tag="guild_master_role", new_value=gm_and_role["role"].id)
		models.change_tag_in_type("GUILD", f"guild_{guild}", fill=gm_and_role["user"].id)
		LOGGER.info(f"[INFO] UPDATED {guild.upper()} GUILD")

	LOGGER.success("UPDATED THE DATABASE")


async def update_the_messages():
	global vars

	async def get_color(guild, server):
		if guild == "Dendro":
			return [discord.Color.from_rgb(60, 173, 79), await server.fetch_emoji(868084062668095549)]

		elif guild == "Anemo":
			return [discord.Color.from_rgb(102, 205, 170), await server.fetch_emoji(868084061510463538)]

		elif guild == "Hydro":
			return [discord.Color.from_rgb(154, 176, 229), await server.fetch_emoji(868084062693236827)]

		elif guild == "Pyro":
			return [discord.Color.from_rgb(204, 47, 47), await server.fetch_emoji(868083783457443860)]

		elif guild == "Cryo":
			return [discord.Color.from_rgb(0, 252, 255), await server.fetch_emoji(868084061929877594)]

		elif guild == "Electro":
			return [discord.Color.from_rgb(103, 88, 182), await server.fetch_emoji(868084063142035466)]

		elif guild == "Geo":
			return [discord.Color.from_rgb(255, 222, 60), await server.fetch_emoji(868084063003639889)]

	# 204, 47, 47 - страндарт цвет

	def get_users_count(guild):
		guild_role = models.NEDOGUILD().get_one_tag(guild=guild, tag="role")
		guild_role = server.get_role(guild_role)

		count = len(guild_role.members)

		return count

	server = bot.get_guild(794987714310045727)

	def sort_dict(dict):
		sorted_dict = {i[0]: i[1] for i in sorted(dict.items(), key=lambda para: (para[1]))}

		return sorted_dict

	guilds_list = ["Dendro", "Hydro", "Pyro", "Cryo", "Anemo", "Electro", "Geo"]

	guilds_dict_by_users = {g: get_users_count(g) for g in guilds_list}

	guilds_dict_by_users_sorted = sort_dict(guilds_dict_by_users)

	chat = server.get_channel(929059781245808700)

	# def clean_text(text: str, list: list) -> str:
	# 	res = text
	# 	for i in list:

	for guild in guilds_dict_by_users_sorted:
		color_and_emoji = await get_color(guild, server)
		text = models.NEDOGUILD().get_one_tag(guild=guild, tag="campaign_speech")

		guild_master = models.NEDOGUILD().get_one_tag(guild=guild, tag="guild_president")

		guild_master = await server.fetch_member(guild_master)

		users_count = get_users_count(guild)
		# speech = re.sub("\s*\}", "}", text)
		# speech = re.sub("{\s*", "{", speech)
		#
		# formatted_speech = speech
		#
		# vars: Dict = {"guild_name": guild,
		#               "users_count": users_count,
		#               "awakusu": "<@!361198710551740428>",
		#               "master": f"{guild_master.mention}"}
		#
		# try:
		# 	formatted_speech = speech.format(**vars)
		# except (
		# 		KeyError
		# ):
		# 	LOGGER.warning("В речи несуществующая переменная, удали пж")
		# except Exception:
		# 	LOGGER.error("Ошибка редактирования речи!")

		embed = discord.Embed(title=f"{color_and_emoji[1]}{guild} **гильдия**!{color_and_emoji[1]}",
		                      description=f"**{color_and_emoji[1]} Кол-во участников**: {users_count}{color_and_emoji[1]}\n"
		                                  f"**{color_and_emoji[1]} Глава гильдии**: {guild_master.mention}{color_and_emoji[1]}\n"
		                                  f"\n\n\n\n"
		                                  f"**{color_and_emoji[1]} Агитационная речь главы гильдии**:\n\n"
		                                  f"{text}", color=color_and_emoji[0])

		embed = models.embed_stan(embed)

		message = await chat.send(embed=embed)
		await message.add_reaction(color_and_emoji[1])

	server = bot.get_guild(794987714310045727)
	chat = await server.fetch_channel(settings["ag_ci"])
	bts = models.GuildView(bot=bot)

	embed_start = discord.Embed(
		title="Итак вы прочли агитации...",
		description="```diff\n-Если вы не прочли агитации - настоятельно рекомендую это сделать```\n\n\n\nИтак вы прочли агитации: \n\n**__1)__ выберите гильдию из 7 доступных**\n**__2)__ нажмите на "
		            "одну из кнопок ниже(на ту, на которой имя понравившейся вам гильдии)** \n**__3)__ заполните заявку, это не возьмёт много времени.** \n\n\n```diff\n-ПРИМЕЧАНИЕ! рекомендую при "
		            "составлении заявки писать реальные вещи и ничего не выдумывать, а ещё лучше подготовится: (Возраст, причина вступить в гильдию, Любимые персонажи Геншина).```",
		color=standard_color)

	await chat.send(embed=embed_start, view=bts)


@tasks.loop(seconds=0.00001)
async def UpdateTask():
	israel_tz = dt.timezone(offset=dt.timedelta(hours=2), name="UTC")
	dt_now = dt.datetime.now(tz=israel_tz)

	time_m = datetime(year=dt_now.year, month=dt_now.month, day=dt_now.day, hour=5, minute=00, second=00, microsecond=000000)
	time_e = datetime(year=dt_now.year, month=dt_now.month, day=dt_now.day, hour=17, minute=00, second=00, microsecond=000000)

	now = datetime(year=dt_now.year, month=dt_now.month, day=dt_now.day, hour=dt_now.hour, minute=dt_now.minute, second=dt_now.second, microsecond=00)

	if time_m == now:

		server = bot.get_guild(794987714310045727)

		chat = server.get_channel(929059781245808700)

		st = await chat.history(limit=500).flatten()
		for msg in st:
			try:
				await msg.delete()
				LOGGER.debug(
					"One message was deleted"
				)

			except Exception as exc:
				LOGGER.error(exc)
		await chat.purge(limit=100)

		await update_the_database()
		await update_the_messages()

	elif time_e == now:

		server = bot.get_guild(794987714310045727)

		chat = server.get_channel(929059781245808700)

		st = await chat.history(limit=500).flatten()
		for msg in st:
			try:
				await msg.delete()
				LOGGER.debug(
					"One message was deleted"
				)

			except Exception as exc:
				LOGGER.error(
					f"Error in message clearing\n{exc}"
				)

		await update_the_database()
		await update_the_messages()

	else:
		pass


@bot.command(name='пинг', aliases=["латентность", "ping"])
@com.cooldown(1, 5, com.BucketType.user)
async def ping(ctx):
	try:
		def dur(ping: float):
			if ping <= 5:
				return f"Пинг: {str(ping).split('.')[0]}ms: автоматическая оценка: Идеально."

			elif ping >= 5 and ping < 10:
				return f"Пинг: {str(ping).split('.')[0]}ms: автоматическая оценка: Хорошо."

			elif ping >= 10 and ping < 20:
				return f"Пинг: {str(ping).split('.')[0]}ms: автоматическая оценка: Нормально."

			elif ping >= 20 and ping < 30:
				return f"Пинг: {str(ping).split('.')[0]}ms: автоматическая оценка: Средне."

			elif ping >= 30:
				return f"Пинг: {str(ping).split('.')[0]}ms: автоматическая оценка: Плохо."

		embed = discord.Embed(title="Текущая латентность!", description=f"**{dur(round(bot.latency, 2) * 100)}**", color=standard_color)
		embed = models.embed_stan(embed)
		await ctx.send(embed=embed)
	except Exception as e:
		LOGGER.error(f"Exception in latency command, {e}")


# Мэйн страница админки и уровни доступа к ней.

# Main
async def main(ctx, msg=None):
	if await access_lvl(ctx) >= 1:
		apf = models.AdminPanelFunc(await ctx.guild.fetch_member(ctx.author.id))
		embed_admin_panel = discord.Embed(title='Админ-Панель;',
		                                  description="Выберите функцию которую небходимо возпроизвести, у все функций разный уровень доступа.",
		                                  color=discord.Colour.from_rgb(80, 141, 234))

		embed_admin_panel.set_author(name="NEDOGUILD's-System",
		                             icon_url="https://cdn.discordapp.com/attachments/845771501571539035/930127142367420447/250.png")

		dt_string = str(datetime.now())

		embed_admin_panel.set_footer(text=f"{dt_string[:-10]}")

		if msg is None:
			msg_ap = await ctx.send(embed_admin_panel, view=apf)
		else:
			msg_ap = await msg.edit(embed=embed_admin_panel, view=apf)

		await apf.wait()

		if apf.Func is None:
			await msg_ap.delete()

		elif apf.Func == "FUNC:JSON":
			if int(await access_lvl(ctx)) >= 2:
				await json_pan(ctx, msg_ap)
			else:
				await msg_ap.edit(embed=discord.Embed(title=f'Недостаточный уровень доступа, для этой функции нужен 2 уровень доступа, ваш равен {await access_lvl(ctx)}.'))
				await asyncio.sleep(2.5)
				await main(ctx, msg_ap)
	else:
		LOGGER.info("User haven't access to this command")


# Access

async def access_lvl(ctx=None, user_=None):
	# Три уровня доступа.
	# Первый - 0 - обычный юзер, без доступа в админку.
	# Второй - 1 - Гильд-Мастер, с доступом к некоторым функциям по управлению гильдией.
	# Третий - 2 - Ята, Авакусу и все смотрящие за гильдиями а также администрация, доступ ко всем функциям.

	user = await ctx.guild.fetch_member(ctx.author.id) if user_ is None else user_

	if user.bot:
		return 0
	else:
		access_lvl_2 = []
		access_lvl_1 = []
		# Получаем все роли первого и второго уровня из JSON'a

		with open("additional_files/config_file.json", "r") as file:
			file = json.load(file)

		for role in file['TIME_ROLE']:
			if role.startswith('guild-vision'):
				access_lvl_2.append(file['TIME_ROLE'][role])
			else:
				if role.startswith('guild-master'):
					access_lvl_1.append(file['TIME_ROLE'][role])
				else:
					pass

		# ----------------------------------------------------------------

		# Проверяем есть ли роли первого и второго уровня у юзера.
		try:
			if user.guild_permissions.administrator:
				return 2

			if user.id == 686207718822117463:
				return 2

		except Exception:
			return 0


		else:
			lvl_1 = 0
			lvl_2 = 0

			for role in access_lvl_1:
				for role_ in user.roles:
					if role == role_.id:
						lvl_1 += 1
					else:
						pass

			for role in access_lvl_2:
				for role_ in user.roles:
					if role == role_.id:
						lvl_2 += 1
					else:
						pass

			if lvl_1 == 0 and lvl_2 == 0:
				return 0

			if lvl_1 > lvl_2:
				return 1
			else:
				if lvl_2 > lvl_1:
					return 2
				else:
					if lvl_1 == lvl_2:
						return 2


# -----------------------------------------------------------------------------

# JSON раздел админки

async def last_page(str_name_last_page: str, ctx, msg):
	if str_name_last_page == "ROLE":
		await json_type_pan(ctx, msg, "ROLE")
	elif str_name_last_page == "CHANNEL":
		await json_type_pan(ctx, msg, "CHANNEL")
	elif str_name_last_page == "TIME_ROLE":
		await json_type_pan(ctx, msg, "TIME_ROLE")
	elif str_name_last_page == "GUILD":
		await json_type_pan(ctx, msg, "GUILD")
	else:
		await main(ctx, msg)


async def json_pan(ctx, msg):
	btc = models.Type(await ctx.guild.fetch_member(ctx.author.id))
	embed_type_chose = discord.Embed(title="Админ-Панель: JSON;",
	                                 description="Какой раздел в базе-данных надо отредактировать?",
	                                 color=discord.Colour.from_rgb(80, 141, 234))

	embed_type_chose.set_author(name="NEDOGUILD's-System",
	                            icon_url="https://cdn.discordapp.com/attachments/845771501571539035/930127142367420447/250.png")

	dt_string = str(datetime.now())

	embed_type_chose.set_footer(text=f"{dt_string[:-10]}")

	await msg.edit(embed=embed_type_chose, view=btc)

	await btc.wait()

	res = btc.Type

	if res == "BACK":
		await main(ctx=ctx, msg=msg)

	elif res == "ROLE":
		await json_type_pan(ctx, msg, "ROLE")
	elif res == "CHANNEL":
		await json_type_pan(ctx, msg, "CHANNEL")
	elif res == "TIME_ROLE":
		await json_type_pan(ctx, msg, "TIME_ROLE")
	elif res == "GUILD":
		await json_type_pan(ctx, msg, "GUILD")
	else:
		if res == "STOP" or res is None:
			await msg.delete()


async def edit_json_type(ctx, msg, type):
	def check(msg):
		return msg.author == ctx.author and msg.channel == ctx.channel

	embed_please_give_me_a_tag = discord.Embed(title=f"Админ-Панель: JSON: {type}: Edit: Tag;",
	                                           description="Введите Tag который надо изменить. Вводите тег с соблюдением всех символов и правильным размером символов.", )

	embed_please_give_me_a_tag = models.embed_stan(embed=embed_please_give_me_a_tag)

	embed_please_give_me_a_fill = discord.Embed(title=f"Админ-Панель: JSON: {type}: Edit: Fill;", description="Введите новое значение.")

	embed_please_give_me_a_fill = models.embed_stan(embed_please_give_me_a_fill)

	#
	#
	#

	embed_time_err = models.embed_stan(embed=discord.Embed(title=f"Админ-Панель: JSON: {type}: Edit: Error;", description="Вы не дали ответ, возвращаю вас на прежнюю страницу."))

	embed_none_err = models.embed_stan(embed=discord.Embed(title=f"Админ-Панель: JSON: {type}: Edit: Error;",
	                                                       description="Такого значения нет в базе данных, возвращаю вас на прежнюю страницу."))

	await msg.edit(embed=embed_please_give_me_a_tag, view=models.NonBts())
	try:
		tag = await bot.wait_for("message", check=check, timeout=20)
	except TimeoutError:
		await msg.edit(embed=embed_time_err, view=models.NonBts())
		await asyncio.sleep(2.5)
		await last_page(type, ctx, msg)
	else:
		che = models.check_tag_in_type(type=type, tag=tag.content)
		await tag.delete()
		if che is None:
			await msg.edit(embed=embed_none_err, view=models.NonBts())
			await asyncio.sleep(2.5)
			await last_page(type, ctx, msg)
		else:
			if che is True:
				try:
					await msg.edit(embed=embed_please_give_me_a_fill, view=models.NonBts())
					fill = await bot.wait_for("message", check=check, timeout=20)
				except TimeoutError:
					await msg.edit(embed=embed_time_err, view=models.NonBts())
					await asyncio.sleep(2.5)
					await last_page(type, ctx, msg)
				else:
					await fill.delete()
					models.change_tag_in_type(type, tag.content, fill.content)
					await msg.edit(embed=models.embed_stan(embed=discord.Embed(title=f'Админ-Панель: JSON: {type}: Edit: Success;', color=discord.Colour.from_rgb(80, 141, 234))), view=models.NonBts())
					await asyncio.sleep(1.5)
					await last_page(type, ctx, msg)


async def add_json_to_type(ctx, msg, type):
	def check(msg):
		return msg.author == ctx.author and msg.channel == ctx.channel

	embed_add_tag_give_me = discord.Embed(
		title=f"Админ-Панель: JSON: {type}: Add: Tag;",
		description=f"Напишите в чат название тега который надо добавить, он должен начинатся с {type.lower()}."
		            f"\n\nНапример: {type.lower()}_DendroRole", color=discord.Colour.from_rgb(80, 141, 234))

	embed_add_fill_give_me = discord.Embed(
		title=f"Админ-Панель: JSON: {type}: Add: fill;",
		description=f"Напишите в чат значение для этого тега, оно не должно содержать буквы или другие символы. **Только цифры**\n\nНапример: 123", color=discord.Colour.from_rgb(80, 141, 234))

	embed_add_fill_give_me = models.embed_stan(embed_add_fill_give_me)

	embed_time_err = models.embed_stan(embed=discord.Embed(title=f"Админ-Панель: JSON: {type}: Add: Error;",
	                                                       description="Вы не дали ответ, возвращаю вас на прежнюю страницу."))

	embed_true_err = models.embed_stan(embed=discord.Embed(title=f"Админ-Панель: JSON: {type}: Add: Error;",
	                                                       description="Такой тег уже записан в базу данных, невозможно иметь два одинаковых тега.", color=discord.Colour.from_rgb(80, 141, 234)))

	embed_add_tag_give_me = models.embed_stan(embed_add_tag_give_me)

	add_tag = models.change_tag_in_type

	await msg.edit(embed=embed_add_tag_give_me, view=models.NonBts())
	try:
		tagN = await bot.wait_for("message", check=check, timeout=30)
	except TimeoutError:
		await msg.edit(embed=embed_time_err)
		await asyncio.sleep(2.5)
		await last_page(type, ctx, msg)
	else:
		che = models.check_tag_in_type(type, tagN.content)
		if che is True:
			await msg.edit(embed=embed_true_err, view=models.NonBts())
			await asyncio.sleep(2.5)
			await last_page(type, ctx, msg)
		else:
			if che is None:
				await msg.edit(embed=embed_add_fill_give_me, view=models.NonBts())
				await tagN.delete()
				try:
					fillN = await bot.wait_for("message", check=check, timeout=30)
				except TimeoutError:
					await msg.edit(embed=embed_time_err)
					await asyncio.sleep(2.5)
					await last_page(type, ctx, msg)
				else:
					await fillN.delete()
					add_tag(type, tagN.content, fillN.content)
					await msg.edit(embed=models.embed_stan(
						embed=discord.Embed(title=f'Админ-Панель: JSON: {type}: Edit: Success;',
						                    color=discord.Colour.from_rgb(80, 141, 234))))
					await asyncio.sleep(1.5)
					await last_page(type, ctx, msg)


async def delete_json_to_type(type, ctx, msg):
	def check(msg):
		return msg.author == ctx.author and msg.channel == ctx.channel

	embed_give_me_a_tag_to_delete = discord.Embed(
		title=f"Адмни-Панель: JSON: {type}: Delete: Tag;",
		description="Отправьте в чат тег который надо удалить.",
		color=discord.Colour.from_rgb(80, 141, 234)
	)
	embed_give_me_a_tag_to_delete = models.embed_stan(embed_give_me_a_tag_to_delete)

	embed_none_err = models.embed_stan(embed=discord.Embed(title=f"Админ-Панель: JSON: {type}: Edit: Error;",
	                                                       description="Такого значения нет в базе данных, возвращаю вас на прежнюю страницу."))

	embed_time_err = models.embed_stan(embed=discord.Embed(title=f"Админ-Панель: JSON: {type}: Edit: Error;",
	                                                       description="Вы не дали ответ, возвращаю вас на прежнюю страницу."))

	await msg.edit(embed=embed_give_me_a_tag_to_delete, view=models.NonBts())
	try:
		tagN = await bot.wait_for("message", check=check, timeout=30)
	except TimeoutError:
		await msg.edit(embed=embed_time_err, view=models.NonBts())
		await asyncio.sleep(2.5)
		await last_page(type, ctx, msg)
	else:
		che = models.check_tag_in_type(type, tagN.content)
		if che is None:
			await msg.edit(embed=embed_none_err, view=models.NonBts())
			await asyncio.sleep(2.5)
			await last_page(type, ctx, msg)
		else:
			if che is True:
				models.delete_tag_in_type(type, tagN.content)
				await msg.edit(embed=models.embed_stan(
					embed=discord.Embed(title=f'Админ-Панель: JSON: {type}: Edit: Success;',
					                    color=discord.Colour.from_rgb(80, 141, 234))), view=models.NonBts())
				await asyncio.sleep(1.5)
				await last_page(type, ctx, msg)


async def json_type_pan(ctx, msg, type: str):
	edit = models.EditJson(au=await ctx.guild.fetch_member(ctx.author.id))
	embed_type = discord.Embed(title=f'Админ-Панель: JSON: {type};', description=f"Что надо сделать со всеми {type.lower()}?", color=discord.Color.from_rgb(80, 141, 234))
	embed_type = models.config_roles_file_get_by_type(type, embed_type)

	await msg.edit(embed=embed_type, view=edit)

	await edit.wait()

	if edit.value is None:
		await msg.delete()

	elif edit.value == "EDIT":
		await edit_json_type(ctx, msg, type)

	elif edit.value == "ADD":
		await add_json_to_type(ctx, msg, type)

	elif edit.value == "DELETE":
		await delete_json_to_type(type, ctx, msg)

	elif edit.value == "BACK":
		await json_pan(ctx, msg)

	elif edit.value == "STOP":
		await msg.delete()

	else:
		pass


# -----------------------------------------------------------------------------

# Админ-Команды

@bot.command(name="ap")
@com.max_concurrency(number=1, per=com.BucketType.user, wait=False)
async def admin_panel(ctx):
	await main(ctx)


# -----------------------------------------------------------------------------

# Юзер-Команды

# User-Profile

async def get_guild(ctx, need: int):
	user = ctx.author

	async def all_guilds():
		gs = ["Dendro", "Hydro", "Pyro", "Cryo", "Anemo", "Electro", "Geo"]

		obj = []

		guild = await bot.fetch_guild(794987714310045727)

		for gui in gs:
			r = models.get_tag_value("ROLE", f"role_{gui}")
			r = guild.get_role(r)

			obj.append(r.id)

		return obj

	async def all_Gmasters():
		gs = ["Dendro", "Hydro", "Pyro", "Cryo", "Anemo", "Electro", "Geo"]

		obj = []

		guild = await bot.fetch_guild(794987714310045727)

		for gui in gs:
			r = models.get_tag_value("TIME_ROLE", f"guild-master_{gui.lower()}")
			r = guild.get_role(r)
			obj.append(r.id)

		return obj

	async def all_Gvisions():
		gs = ["Dendro", "Hydro", "Pyro", "Cryo", "Anemo", "Electro", "Geo"]

		obj = []

		guild = await bot.fetch_guild(794987714310045727)

		for gui in gs:
			with open("additional_files/config_file.json", "r") as file:
				file = json.load(file)

			tim = file["TIME_ROLE"]

			for key in tim:
				if key.startswith("guild-vision"):
					obj.append(tim[key])
				else:
					pass

		return obj

	rol = await all_guilds()

	gms = await all_Gmasters()

	gvs = await all_Gvisions()

	lvl = await access_lvl(ctx=ctx)

	list = []

	if lvl != need:
		return "Error loading profile"
	else:
		if lvl and need == 0:
			for role in user.roles:
				for r in rol:
					if role.id == r:
						list.append(role)
					else:
						pass

			if len(list) == 0 or len(list) > 1:
				return "Error more than two user roles!"
			else:
				if len(list) == 1:
					return list[0]

		elif lvl and need == 1:
			for role in user.roles:
				for r in gms:
					if role.id == r:
						list.append(role)
					else:
						pass

			if len(list) == 0 or len(list) > 1:
				return "Error more than two guild-master roles!"
			else:
				if len(list) == 1:
					return list[0]

		elif lvl and need == 2:
			for role in user.roles:
				for r in gvs:
					if role.id == r:
						list.append(role)
					else:
						pass

			if len(list) == 0 or len(list) > 1:
				return "Error more than two guild-vision roles!"
			else:
				if len(list) == 1:
					return list[0]
		else:
			"Error in access lvl!"


# Профиль для первого уровня доступа.
async def user_profile(ctx=None, msg=None, user=None):
	await nope(ctx=ctx, msg=msg, page_name="Профили для всех!", what_will_be_on_this_page="Профили для всех юзеров.")


# Профиль для второго уровня доступа.


class GmasterNotDefined(Exception):

	def __init__(self, msg=None):
		self.msg = msg if msg else "Гильд мастер не обнаружен, требуется вмешательство в код или стороннее действие со стороны Client."

	def __str__(self):
		return self.msg

	def __repr__(self):
		return "Экземпляр класса GmasterNotDefined"


class GuildMaster:

	def __init__(self, ctx):

		self.ctx = ctx
		#
		self.user = ctx.author
		self.guild: str = self.define_master(self.user) if self.define_master(self.user) is not None else "Unknown"

	def __str__(self) -> str:
		return f"{self.user} -> {self.guild}-master"

	def __repr__(self):
		name = self.__class__.__name__
		# @ToDo master = self.user
		return (
			f"<{name} ctx={self.ctx} master={self.guild} guild={self.guild}>"
		)

	@classmethod
	def define_master(cls, user) -> str:
		all_guilds: dict = models.NEDOGUILD().get_all_guilds()

		for guild in all_guilds.keys():
			server = bot.get_guild(794987714310045727)
			#
			#
			role = all_guilds[guild]["guild_master_role"]
			#
			role = server.get_role(role)

			if role in user.roles:
				return str(guild.split("_")[1])

	async def __get_msg(self, wait: int, wait_for: discord.Embed, message: discord.Message = None) -> discord.Message or None:
		def check(message):
			return message.author == self.user and message.channel == self.ctx.channel

		try:

			dsc = wait_for.description

			w = f"\n\n\n\n**__Я буду ждать лишь {wait} секунд...__**"

			wait_for.description = dsc + w

			await message.edit(embed=wait_for, view=models.NonBts())
		except Exception as exc:
			LOGGER.error(f"Exception in get_msg \n {exc}")
			raise LookupError() from exc
		try:

			wait_for_msg = await bot.wait_for("message", check=check, timeout=wait)

		except asyncio.exceptions.TimeoutError:
			return None
		else:
			return wait_for_msg

	async def __define_user(self, msg: discord.Message) -> discord.User or discord.Member:

		embed_which_user_to_kick = discord.Embed(title="Кого?", description="@упомяни юзера которого надо которым надо произвести некие действа.", color=standard_color)
		embed_which_user_to_kick = models.embed_stan(embed_which_user_to_kick)

		user_: discord.Message = await self.__get_msg(wait=45, wait_for=embed_which_user_to_kick, message=msg)

		if user_ is None:

			await msg.delete()

		else:
			await user_.delete()
			try:
				user_id = re.findall(r"\d+", str(user_.content))[0]
				if len(str(user_id)) != 18:
					raise UserWarning

				else:
					user: discord.Member = await self.ctx.guild.fetch_member(int(user_id))
			except Exception as exc:
				raise UserWarning(exc) from exc
			else:
				return user

	@classmethod
	async def kick(cls, **kwargs):
		guild = kwargs.get("guild")
		ctx: com.Context = kwargs.get("ctx")
		gt = kwargs.get("gt")
		msg: discord.Message = kwargs.get("msg")

		user: discord.Member = await gt.__define_user(msg=msg) if kwargs.get("user", None) is None else kwargs.get("user", None)

		guild_role_id = models.NEDOGUILD().get_one_tag(guild=guild, tag="role")
		guild_role = ctx.guild.get_role(guild_role_id)

		await user.trigger_typing()

		if guild_role in user.roles:
			await user.remove_roles(guild_role, reason="По приказу генерала гафса")
			result = f"{user.mention} исключен из гильдии {guild}."
			col = discord.Color.green()

			defense = GuildDefense(bot=bot, server=ctx.guild, user=user.id, guild=guild)

			defense.set_cooldown(cooldown_seconds=ONE_DAY_IN_SECONDS * 2)  # кулдаун на 2 дня

		else:
			result = f"{user.mention} не был исключен из гильдии {guild}, так как в ней и не находился."
			col = discord.Color.red()

		embed_success = models.embed_stan(embed=discord.Embed(title="Готово", description=result, color=col))

		await msg.edit(embed=embed_success)
		await ctx.channel.trigger_typing()
		await asyncio.sleep(4)
		await gt.get_profile(msg)

	async def __chdc(self, msg):
		embed__ = discord.Embed(title="На что изменим?", description="Максимально напряги свои мозги и включи воображение, а затем напиши в чат то, что придумал.", color=standard_color)
		embed__ = models.embed_stan(embed__)

		new_topic: discord.Message = await self.__get_msg(wait=45, wait_for=embed__, message=msg)

		if new_topic is None:
			await msg.delete()
		else:
			await new_topic.delete()
			topic = f"{new_topic.content}"

			try:
				guild_channel: discord.TextChannel = await self.ctx.guild.fetch_channel(models.NEDOGUILD().get_one_tag(guild=self.guild, tag="channel"))
			except Exception as exc:
				await something_went_wrong(msg=msg, problem=str(exc))
				raise discord.Forbidden
			else:
				await guild_channel.edit(reason="По приказу генерала гафса!", topic=topic)

			if (str(new_topic.content) == str(models.NEDOGUILD().get_one_tag(guild=self.guild, tag="guild_chat_description"))):
				result = "Тема канала не была изменена, ведь новая <<{}>> идентична старой."
				color = discord.Color.red()
			else:
				result = "Тема канала успешно изменена на {}."
				color = discord.Color.green()

			embed_success = discord.Embed(title="Готово", description=result.format(topic), color=color)

			await msg.edit(embed=embed_success, view=models.NonBts())

			await self.ctx.channel.trigger_typing()

			await asyncio.sleep(5)

			await self.get_profile(msg)

	async def __chte(self, msg):
		embed__ = discord.Embed(title="На что изменим?", description="Максимально напряги свои мозги и включи воображение, а затем напиши в чат то, что придумал.", color=standard_color)
		embed__ = models.embed_stan(embed__)

		new_text: discord.Message = await self.__get_msg(wait=180, wait_for=embed__, message=msg)

		if new_text is None:
			await msg.delete()
		else:
			await new_text.delete()
			old_text: str = models.NEDOGUILD().get_one_tag(guild=self.guild, tag="campaign_speech")

			try:
				if (str(new_text.content).lower() == old_text.lower()):
					result: str = "**Агитационная речь не была изменена**\n" \
					              "**Старая речь идентична новой**: \n\n\n {}".format(new_text.content)
					color: discord.Color = discord.Color.red()
					time_wait: int = 5
				else:
					new_text: str = models.NEDOGUILD().update_one_tag(guild=self.guild, tag="campaign_speech", new_value=new_text.content)
					result: str = "**Агитационная речь была изменена на**: \n\n\n {}".format(new_text)
					color: discord.Color = discord.Color.green()
					time_wait: int = 10

				#
				# END
				#
				embed_ = discord.Embed(title="Готово", description=result, color=color)
				await msg.edit(embed=embed_, view=models.NonBts())

				await self.ctx.trigger_typing()

				await asyncio.sleep(time_wait)

				await self.get_profile(message=msg)

			except Exception as exc:
				await something_went_wrong(msg=msg, problem=str(exc))

	async def get_profile(self, message=None) -> None:
		if self.guild == "Unknown":
			raise GmasterNotDefined

		profile_embed = models.embed_stan(embed=discord.Embed(
			title="User-Profiles: Gmaster: Profile;",
			description=f"У меня есть много способов угандошить {self.guild}, какой хочешь применить?",
			color=standard_color))

		buttons = models.ButtonsForGmasters(au=self.user)

		if message is None:
			profile_message: discord.Message = await self.ctx.send(embed=profile_embed, view=buttons)
		else:
			profile_message: discord.Message = await message.edit(embed=profile_embed, view=buttons)

		await buttons.wait()
		buttons_value = buttons.value

		if buttons_value == "KICK":
			await self.kick(ctx=self.ctx, guild=self.guild, gt=self, msg=profile_message)

		elif buttons_value == "CHDC":
			await self.__chdc(message)

		elif buttons_value == "SPRA":
			await self.__chte(msg=message)

		else:
			try:
				await profile_message.delete()
			except Exception as exc:
				LOGGER.error(f"Deleting message exception {exc} GuildMaster -> get_profile")


# @bot.command()
# async def chncm(ctx: com.Context):
# 	overwrites = {
# 		ctx.author: discord.PermissionOverwrite(view_channel=True, send_messages=True),
# 		bot.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
# 		ctx.guild.default_role: discord.PermissionOverwrite(view_channel=False, send_messages=False),
# 	}
#
# 	c = await ctx.guild.create_text_channel(
# 		position=0,
# 		category=ctx.channel.category,
# 		name=f"Ливы",
# 		overwrites=overwrites,
# 		reason="По приказу генерала гафса",
# 		topic=f"Канал для юзеров по тихому ушедших из гильдии...",
# 		slowmode_delay=1
#
# 	)
#
# 	await c.send(f"{ctx.author.mention}")

@bot.command(
	name="leave",
	aliases=[
		"выйти",
		"покинуть",
		"аривидерчи",
		"бай",
		"лив",
		"люблю-гей-дорамы",

		# transcript
		"выйtи",
		"пokинуть",
		"aривидерчи",
		"бaй",
		"лNв",
		"люbлю-гeй-дoрaмы"
	]
)
async def leave(ctx):
	def define_guild(user: nextcord.Member):
		all_guilds: dict = models.NEDOGUILD().get_all_guilds()

		for guild in all_guilds.keys():
			server = bot.get_guild(794987714310045727)
			#
			#
			role = all_guilds[guild]["role"]
			#
			role = server.get_role(role)

			if role in user.roles:
				return str(guild.split("_")[1])

		return None

	guild = define_guild(ctx.author)
	ctx: com.Context = ctx

	user: discord.Member = ctx.author

	await user.trigger_typing()

	if guild is not None:
		guild_role_id = models.NEDOGUILD().get_one_tag(guild=guild, tag="role")
		guild_role = ctx.guild.get_role(guild_role_id)
		await user.remove_roles(guild_role, reason="По приказу генерала гафса")

		defense = GuildDefense(bot=bot, server=ctx.guild, user=user.id, guild=guild)

		defense.set_cooldown(cooldown_seconds=ONE_DAY_IN_SECONDS * 2)  # кулдаун на 2 дня

		await ctx.guild.get_channel(972510360710037564).send(
			content=f"{ctx.guild.get_role(models.NEDOGUILD().get_one_tag(guild=guild, tag='guild_master_role')).mention}",
			embed=models.embed_stan(
				embed=nextcord.Embed(
					title="ГМа предали!",
					description=f"Этот \*\*\*а\*\*\с -> {user.mention} <- решил уйти по-тихому из {guild}!",
					color=discord.Color.red()
				)
			)
		)

		result = f"{user.mention} исключен из гильдии {guild}."
		col = discord.Color.green()




	else:
		result = f"{user.mention} не был исключен из гильдии так как в ней и не находился."
		col = discord.Color.red()

	embed_success = models.embed_stan(embed=discord.Embed(title="Готово", description=result, color=col))

	await ctx.send(
		embed=embed_success,
		delete_after=60,
	)


@bot.command()
@com.has_any_role(929552483808858132)
async def update_guild_database_now(ctx):
	server = ctx.guild

	async def all_guilds():
		gs = ["Dendro", "Hydro", "Pyro", "Cryo", "Anemo", "Electro", "Geo"]

		guild = await bot.fetch_guild(794987714310045727)

		obj = {}

		for gui in gs:
			r = models.get_tag_value("ROLE", f"role_{gui}")
			r = guild.get_role(r)
			c = models.get_tag_value("CHANNEL", f"channel_{gui}")
			c = await guild.fetch_channel(c)

			obj[f"{gui}"] = {
				"r": r,
				"c": c
			}

		return obj

	async def get_Gmaster(guild) -> dict:

		guild_master_role_id = models.get_tag_value("TIME_ROLE", f"guild-master_{guild}")

		guild_master_role = server.get_role(guild_master_role_id)
		try:
			guild_master_user = guild_master_role.members[0]
		except Exception as e:
			LOGGER.error(f"ОШИБКА В get_Gmaster в НЕ НАЙДЕН ГМ {guild}, ПОДСТАВЛЕН АВАКУСУ"
			             f"! \n" + str(e))

			guild_master_user = server.get_member(361198710551740428)
		return {"role": guild_master_role, "user": guild_master_user}

	algs = await all_guilds()
	gs = ["Dendro", "Hydro", "Pyro", "Cryo", "Anemo", "Electro", "Geo"]
	g = models.NEDOGUILD()

	def get_channel(guild):
		return server.get_channel(models.get_tag_value("CHANNEL", f"channel_{guild}"))

	for guild in gs:
		gmstr: dict = await get_Gmaster(guild)
		chat = get_channel(guild)
		g.create_guild_settings(agi="#", guild=guild, users=len(algs[guild]['r'].members), role=algs[guild]['r'].id, guild_master=gmstr["user"].id, guild_chat_description=chat.topic, channel=chat.id,
		                        guild_master_role=gmstr["role"].id)


async def Gmaster_profile(ctx=None, msg=None) -> None:
	try:
		try:
			await ctx.message.delete()
		except discord.Forbidden:
			pass
		except discord.NotFound:
			pass
		except discord.HTTPException:
			pass

		master = GuildMaster(ctx=ctx)
		if master.guild.lower() == "Unknown".lower():
			LOGGER.info("G-master non defined")

		await master.get_profile(message=msg)

	except LookupError or Exception as exc:
		return await something_went_wrong(msg, f"{exc}")
	except UserWarning as exc:
		return await something_went_wrong(msg, f"Не удалось определить юзера {exc}")
	finally:
		LOGGER.debug("Called the G-master profile")


# Профиль для третьего уровня доступа.
async def Gvision_profile(ctx=None, msg=None, user=None):
	user = ctx.author if user is None else user == user
	if await access_lvl(user_=user) == 2:
		# Эмбед с выбором чё сделать типа
		embed_c_m_p = discord.Embed(title='User-Profiles: Gvision: Profile;', description="Выберите что вам необходимо с помощью кнопок ниже, все режимы представлены ниже.", color=standard_color)
		embed_c_m_p = models.embed_stan(embed_c_m_p)

		Gvision = models.Gvision(au=await ctx.guild.fetch_member(ctx.author.id))

		await msg.edit(embed=embed_c_m_p, view=Gvision)

		await Gvision.wait()

		res = Gvision.value

		if res == "LOGS":
			await logs(ctx, msg)

		elif res == "MSGS":
			await msgs(ctx, msg)

		elif res == "STAT":
			await stat(ctx, msg)

		elif res == "EDIT":
			await mana(ctx, msg)
		else:
			if res == "STOP" or res is None:
				await msg.delete()
	else:
		await something_went_wrong(msg=msg, problem="Ошибка определения уровня доступа.")


# ---------------------------------------------------------------------------

@bot.command()
@com.max_concurrency(number=1, per=com.BucketType.user, wait=False)
@com.cooldown(rate=1, per=5, type=com.BucketType.user)
async def members(ctx, role: discord.Role):
	acc_lvl = await access_lvl(ctx=ctx)
	cracks = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
	count = 1
	text = "\n"
	if acc_lvl >= 1:
		embed_users = discord.Embed(title="#", description="#", color=standard_color)

		for member in role.members:
			text += f"{count}. {member.mention}({member.id})\n"
			if count in cracks:
				text += "---"
			count += 1

		texts = text.split("---")

		for t in texts:
			await ctx.send(t)


@members.error
async def error(ctx, error):
	if isinstance(error, com.MissingRequiredArgument):
		await ctx.send("Не указана роль, пожалуйста укажите роль!")
	elif isinstance(error, com.CommandOnCooldown):
		await ctx.send(f"Команда откатывается, подожди {error.retry_after:.2f}с!")
	else:
		await ctx.send(str(error))


# Функции для третьего уровня доступа
async def logs(ctx, msg):
	await nope(ctx, msg, page_name="Логи", what_will_be_on_this_page="Логи")


async def msgs(ctx, msg):
	embed_guild_s_cho = discord.Embed(title='User-Profiles: Gvision: Profile: Msgs;', description="Нажмите на одну из кнопок представленных ниже.", color=standard_color)
	embed_guild_s_cho = models.embed_stan(embed_guild_s_cho)

	msgs = models.Msgs(au=await ctx.guild.fetch_member(ctx.author.id))

	await msg.edit(embed=embed_guild_s_cho, view=msgs)

	await msgs.wait()

	val = msgs.value

	if val == "ONEG":
		await msgs_one(ctx, msg)

	elif val == "ALLG":
		await msgs_many(ctx, msg)

	elif val == "BACK":
		await return_profile(ctx, msg)

	elif val == "STOP" or val is None:
		await msg.delete()


async def message(title, desc, ping, pin, guild_obj, ctx):
	if ping.lower() in ("yes", "да", "конечно", "ага"):
		ping_ = guild_obj['role'].mention
	else:
		ping_ = ""

	embed = discord.Embed(title=title, description=f"Уведомление для всех {guild_obj['role'].mention} от {ctx.author.mention}. **Читайте внимательно**!\n\n\n{desc}", color=standard_color)

	embed = models.embed_stan(embed)

	msg = await guild_obj['channel'].send(content=ping_, embed=embed)

	if pin.lower() in ("yes", "да", "конечно", "ага"):
		try:
			await msg.pin()
		except Exception:
			pass
	else:
		pass

	return {"title": title,
	        "desc": desc,
	        "ping": ping,
	        "pin:": pin,
	        "guild_obj": guild_obj,

	        }


async def msgs_one(ctx, msg):
	try:
		async def give_me_message(ctx, msg, sho: str, time_wait: int):
			def check(msg):
				return msg.author == ctx.author and msg.channel == ctx.channel

			embed_give_me = discord.Embed(title='Система сбора данных "Український хакер Вiталя"', description=f"Напишите в чат {sho}", color=standard_color)
			embed_give_me = models.embed_stan(embed_give_me)

			embed_you_do_not_s = discord.Embed(title='Система сбора данных', description=f"Вы не написали в чат '{sho}'. \nПереношу вас на прежнюю страницу.", color=standard_color)
			embed_you_do_not_s = models.embed_stan(embed_you_do_not_s)

			await msg.edit(embed=embed_give_me, view=models.NonBts())

			try:
				value = await bot.wait_for("message", check=check, timeout=time_wait)
			except TimeoutError:
				await msg.edit(embed=embed_you_do_not_s)
				await asyncio.sleep(2.5)
				await msgs(ctx, msg)
			else:
				await value.delete()
				return value.content

		async def return_guild(guild: str):
			list_of_guilds = ["Dendro", "Hydro", "Pyro", "Cryo", "Anemo", "Electro", "Geo"]

			guild_after_for = None

			for gui in list_of_guilds:
				if gui.lower() == guild.lower():
					guild_after_for = gui
				else:
					pass

			if guild_after_for is None:
				await something_went_wrong(msg, "была введена несуществующая гильдия, возможна ошибка внутри скрипта.")
			else:
				guild = await bot.fetch_guild(794987714310045727)
				guild_object = {
					"role": guild.get_role(models.get_tag_value("ROLE", f"role_{guild_after_for}")),
					"channel": await guild.fetch_channel(models.get_tag_value("CHANNEL", f"channel_{guild_after_for}"))

				}
				return guild_object

		guild_str = await give_me_message(ctx, msg, "гильдию в которую надо отправить сообщение.", 20)
		title_str = await give_me_message(ctx, msg, "заголовок для сообщения.", 20)
		mainTXT_str = await give_me_message(ctx, msg, "основной текст сообщения.", 300)
		pin_str = await give_me_message(ctx, msg, "надо ли закреплять сообщение.", 20)
		ping_str = await give_me_message(ctx, msg, "надо ли пинговать всю гильдию.", 20)

		message_returns = await message(ctx=ctx, title=title_str, guild_obj=await return_guild(guild_str), desc=mainTXT_str, pin=pin_str, ping=ping_str)

		await msgs(ctx, msg)

	except BotMissingPermissions as bmp:
		await something_went_wrong(msg=msg, problem=f"У бота отсутстсвуют нужные права для работы!\n{bmp}")
	except MissingPermissions as mp:
		await something_went_wrong(msg=msg, problem=f"У бота отсутстсвуют нужные права для работы!\n{mp}")
	except Exception as e:
		await something_went_wrong(msg=msg)
		LOGGER.error("-------------------------------------------------------------------------\n"
		             f"Ошибка в функции отправки сообщения в одну гильдию: {e}\n"
		             f"-------------------------------------------------------------------------")


async def msgs_many(ctx, msg):
	try:
		async def give_me_message(ctx, msg, sho: str, time_wait: int):
			def check(msg):
				return msg.author == ctx.author and msg.channel == ctx.channel

			embed_give_me = discord.Embed(title='Система сбора данных "Український хакер Вiталя"', description=f"Напишите в чат {sho}", color=standard_color)
			embed_give_me = models.embed_stan(embed_give_me)

			embed_you_do_not_s = discord.Embed(title='Система сбора данных', description=f"Вы не написали в чат '{sho}'. \nПереношу вас на прежнюю страницу.", color=standard_color)
			embed_you_do_not_s = models.embed_stan(embed_you_do_not_s)

			await msg.edit(embed=embed_give_me, view=models.NonBts())

			try:
				value = await bot.wait_for("message", check=check, timeout=time_wait)
			except TimeoutError:
				await msg.edit(embed=embed_you_do_not_s)
				await asyncio.sleep(2.5)
				await msgs(ctx, msg)
			else:
				await value.delete()
				return value.content

		try:
			title = await give_me_message(ctx, msg, "title.", 20)
			desc = await give_me_message(ctx, msg, "полное сообщение.", 300)
			pin = await give_me_message(ctx, msg, "надо закреплять сообщение?", 20)
			ping = await give_me_message(ctx, msg, "надо пинговать гильдию", 20)
		except Exception:
			await msgs(ctx, msg)
		else:

			async def all_guilds():
				gs = ["Dendro", "Hydro", "Pyro", "Cryo", "Anemo", "Electro", "Geo"]

				obj = []

				guild = await bot.fetch_guild(794987714310045727)

				for gui in gs:
					c = models.get_tag_value("CHANNEL", f"channel_{gui}")
					c = await guild.fetch_channel(c)
					r = models.get_tag_value("ROLE", f"role_{gui}")
					r = guild.get_role(r)

					obj.append({"role": r, "channel": c})

				return obj

			all_guilds = await all_guilds()

			all_mes = []

			for obj in all_guilds:
				mes = await message(title=title, desc=desc, ctx=ctx, pin=pin, ping=ping, guild_obj=obj)
				all_mes.append(mes)

			await msgs(ctx, msg)
	except KeyError as ke:
		await something_went_wrong(msg, f"Ошибка базы данных!\n {ke}")
		LOGGER.critical("-------------------------------------------------------------------------\n"
		                f"Ошибка в функции отправки сообщения в гильдии: {ke}\n"
		                f"-------------------------------------------------------------------------")
	except Exception as e:
		await something_went_wrong(msg, f"Неизвестная проблема, {e}")
		LOGGER.critical("-------------------------------------------------------------------------\n"
		                f"Ошибка в функции отправки сообщения в гильдии: {e}\n"
		                f"-------------------------------------------------------------------------")
	except BotMissingPermissions as bmp:
		await something_went_wrong(msg=msg, problem=f"У бота отсутстсвуют нужные права для работы!\n{bmp}")
		LOGGER.critical("-------------------------------------------------------------------------\n"
		                f"Ошибка в функции отправки сообщения в гильдии: {bmp}\n"
		                f"-------------------------------------------------------------------------")
	except MissingPermissions as mp:
		await something_went_wrong(msg=msg, problem=f"У бота отсутстсвуют нужные права для работы!\n{mp}")
		LOGGER.critical("-------------------------------------------------------------------------\n"
		                f"Ошибка в функции отправки сообщения в гильдии: {mp}\n"
		                f"-------------------------------------------------------------------------")
	finally:
		LOGGER.success("All guild message!")


# ---------------------------------------------------------------------------

# Не готовые функции

async def stat(ctx, msg):
	await nope(ctx, msg, page_name="Статистика гильдий", what_will_be_on_this_page="статистика сразу всех гильдий для ГМ-ов и смотрителей за гильдиями.")


async def mana(ctx, msg):
	await nope(ctx, msg, page_name="Управление гильдиями", what_will_be_on_this_page="возможность управлять гильдиями для ГМ-ов и смотрителей.")


# ---------------------------------------------------------------------------

# Вспомогательные функции

async def something_went_wrong(msg=None, problem: str = "Внутреняя ошибка скрипта", ctx: com.Context = None):
	embed = discord.Embed(title="О нет, что-то пошло не так!", description=f"В ходе выполнение определенных действий произошла ошибка, наши специалисты скорее всего уже решают её(они спят). \n"
	                                                                       f"Сведения об ошибке: {problem}", color=standard_color)

	embed = models.embed_stan(embed)
	if msg is not None:
		await msg.edit(embed=embed)
		await asyncio.sleep(10)
		await msg.delete()
	else:
		await ctx.send(embed=embed, view=models.NonBts(), delete_after=60)


async def guild_ret(guild: str, ctx):
	if guild.lower() == "dendro" or guild.lower() == "дендро":
		guild_name = "Dendro"

	elif guild.lower() == "hydro" or guild.lower() == "гидро":
		guild_name = "Hydro"

	elif guild.lower() == "pyro" or guild.lower() == "пиро":
		guild_name = "Pyro"

	elif guild.lower() == "cryo" or guild.lower() == "крио":
		guild_name = "Cryo"

	elif guild.lower() == "anemo" or guild.lower() == "анемо":
		guild_name = "Anemo"

	elif guild.lower() == "electro" or guild.lower() == "электро":
		guild_name = "Electro"

	elif guild.lower() == "geo" or guild.lower() == "гео":
		guild_name = "Geo"
	else:
		return [None, None]

	guild = await bot.fetch_guild(ctx.guild.id)

	role = guild.get_role(models.get_tag_value("ROLE", f"role_{guild_name}"))

	channel = await bot.fetch_channel(models.get_tag_value("CHANNEL", f"channel_{guild_name}"))

	return {"role": role, "channel": channel}


# ---------------------------------------------------------------------------

# Функции профилей

async def return_profile(ctx=None, msg=None):
	acc = await access_lvl(ctx)
	if acc == 0:
		return await user_profile(ctx, msg)
	elif acc == 1:
		return await Gmaster_profile(ctx, msg)
	else:
		if acc == 2:
			return await Gvision_profile(ctx, msg)
		else:
			LOGGER.warning("Undefined lvl")


async def get_stats_profile(user_id, msg, ctx):
	await nope(ctx, msg, "stats profile", "")


async def nope(ctx, msg, page_name, what_will_be_on_this_page):
	embed_with_nope_page = discord.Embed(title=f'{page_name}',
	                                     description=f"Этой страницы ещё не существует. Когда-нибудь тут будет {what_will_be_on_this_page}\n\n"
	                                                 f"{ctx.author.nick}, эта страница будет закрыта через несколько секунд...",
	                                     color=standard_color)

	embed_with_nope_page = models.embed_stan(embed_with_nope_page)

	await msg.edit(embed=embed_with_nope_page, view=models.NonBts())
	await asyncio.sleep(10)
	await msg.delete()


# ---------------------------------------------------------------------------

@bot.command(name="prof", aliases=["проф", "п", "p", "з"])
@com.max_concurrency(number=1, per=com.BucketType.user, wait=False)
async def user_profile_Gmember_or_Gmaster_or_Gvision(ctx):
	try:
		loading = discord.Embed(title="Загрузка", description="Определяю уровень доступа...\n\n Загружаю данные...", color=standard_color)
		loading = models.embed_stan(loading)
		#
		#
		#
		msg = await ctx.send(embed=loading)
		await return_profile(ctx, msg)
	except Exception as exc:
		LOGGER.error(f"Profile exception {exc}")
		await something_went_wrong(problem=str(exc), ctx=ctx)


@bot.command(
	name="bug",
	aliases=["баг", "ошибка"],
	brief="Сообщение о баге на сервер поддержки бота",
	usage="+bug [сообщение]"
)
async def bug_report(ctx, *, message=None):
	try:
		server = bot.get_guild(856964290777972787)
		bugs_channel = server.get_channel(875032089756577882)
		session = secrets.token_hex(2)
	except Exception as exc:
		LOGGER.error(f"Bug report command error \n{exc}")
	else:
		try:
			at_count = 0
			atts = [models.embed_stan(discord.Embed(title=f"New bug...(session={session})", description=f"**Новый баг от {ctx.author.mention} Сообщение**: \n\n\n "
			                                                                                            f"{message if message is not None else 'Не указано описание, скорее всего есть только фото.'}",
			                                        color=discord.Color.red(

			                                        )))]

			for attach in ctx.message.attachments:
				at_count += 1
				if at_count == 9:
					continue
				else:
					atts.append(discord.Embed(title=f"session={session}", color=discord.Color.red()).set_image(url=attach.url))

			async def send():
				c = 0
				if at_count >= 1:
					c += 1
				elif message is not None:
					c += 1

				if c >= 1:
					await bugs_channel.send(embeds=atts)
					await ctx.reply(embed=models.embed_stan(embed=discord.Embed(title="Отправлено", color=discord.Color.green())), delete_after=5)

					await asyncio.sleep(5)
					return True
				else:
					return False

			x = await send()
			if x is False:
				await something_went_wrong(ctx=ctx, problem="Вы не указали ничего, что можно было-бы переслать хозяину.")
			else:
				pass
			await ctx.message.delete()
		except Exception as exc:
			LOGGER.error(f"Bug report command error \n{exc}")
			await something_went_wrong(ctx=ctx, problem=str(exc))
			raise ConnectionError(str(exc)) from exc


@bug_report.error
async def error_handler(ctx, error):
	await something_went_wrong(ctx=ctx, problem=str(error))


# @bot.command(
#     name="тех",
#     aliases=["tech"],
#     usage='+tech date_wait="now", time_wait="now", *, reason=None'
# )
# @com.cooldown(1, 20, type=com.BucketType.user)
# @com.is_owner()
# async def tech_stop(ctx, date_wait="now", time_wait="now", *, reason=None):
#     async def get_date(date=None, cooldown_seconds=None):
#         timezone = dt.timezone(offset=dt.timedelta(hours=2), name="UTC")
#         dt_now = dt.datetime.now(tz=timezone)
#
#         if type(date) is not str or type(cooldown_seconds) is not str:
#             raise NotImplementedError
#
#         try:
#             if date is None and cooldown_seconds == 'now':
#                 return dt_now
#             else:
#                 if cooldown_seconds is None and date == 'now':
#                     return dt_now
#                 else:
#                     if date is None and cooldown_seconds is None:
#                         return dt_now
#                     else:
#                         if date == 'now' and cooldown_seconds == 'now':
#                             return dt_now
#                         else:
#                             if date == 'now' and cooldown_seconds != 'now':
#                                 year = dt_now.year
#                                 month = dt_now.month
#                                 day = dt_now.day
#
#                                 hour = cooldown_seconds.split('.', -1)[0]
#                                 minute = cooldown_seconds.split('.', -1)[1]
#                                 second = cooldown_seconds.split('.', -1)[2]
#
#                                 time_ret = datetime(year=int(year), month=int(month), day=int(day),
#                                                     hour=int(hour), minute=int(minute), second=int(second), tzinfo=timezone)
#
#                                 return time_ret
#
#                             elif cooldown_seconds == 'now' and date != 'now':
#                                 year = date.split('/', -1)[2]
#                                 month = date.split('/', -1)[1]
#                                 day = date.split('/', -1)[0]
#
#                                 hour = dt_now.hour
#                                 minute = dt_now.minute
#                                 second = dt_now.second
#
#
#
#                                 time_ret: datetime = datetime(year=int(year), month=int(month), day=int(day),
#                                                               hour=int(hour), minute=int(minute), second=int(second), tzinfo=timezone)
#
#                                 return time_ret
#
#                             elif cooldown_seconds and date != "now":
#                                 year = date.split('/', -1)[2]
#                                 month = date.split('/', -1)[1]
#                                 day = date.split('/', -1)[0]
#
#                                 hour = cooldown_seconds.split('.', -1)[0]
#                                 minute = cooldown_seconds.split('.', -1)[1]
#                                 second = cooldown_seconds.split('.', -1)[2]
#
#                                 time_ret: datetime = datetime(year=int(year), month=int(month), day=int(day),
#                                                               hour=int(hour), minute=int(minute), second=int(second), tzinfo=timezone)
#                                 return time_ret
#
#         except Exception as exc:
#             print(exc)
#             await ctx.send
#
#     if date_wait and time_wait == "now":
#         return await ctx.send(ctx.command.usage)
#
#     if reason is None:
#         reason = "Технический перерыв"
#     else:
#         reason = reason
#
#     join_guild_channel = ctx.guild.get_channel(settings["ag_ci"])
#
#     if isinstance(join_guild_channel, discord.TextChannel):
#         pass
#     else:
#         await ctx.send("Не определился канал", delete_after=5)
#     h = await join_guild_channel.history(limit=500).flatten()
#     for msg in h:
#         await msg.delete()
#
#     async def get_time_stamp(date, cooldown_seconds) -> list[str | datetime] | str:
#         try:
#             cooldown_seconds: datetime = await get_date(date, cooldown_seconds)
#             times = cooldown_seconds.timestamp()
#             times = str(times).split(".")[0]
#             timestamp: str = f"<t:{times}:R>"
#             return [timestamp, cooldown_seconds]
#         except Exception as exc:
#             print(f"Timestamp exception {exc}")
#             return [f"<t:{datetime.now().timestamp()}:R>", datetime.now()]
#
#     base_roles_1 = join_guild_channel.guild.get_role(794994804018642965)
#     base_roles_2 = join_guild_channel.guild.get_role(933746139264610314)
#
#     await join_guild_channel.set_permissions(target=base_roles_1, overwrite=nextcord.PermissionOverwrite(view_channel=False))
#     await join_guild_channel.set_permissions(target=base_roles_2, overwrite=nextcord.PermissionOverwrite(view_channel=False))
#
#     overwrites = {
#         join_guild_channel.guild.default_role: discord.PermissionOverwrite(view_channel=False, send_messages=False),
#         base_roles_1: discord.PermissionOverwrite(view_channel=True, send_messages=False),
#         base_roles_2: discord.PermissionOverwrite(view_channel=True, send_messages=False),
#         bot.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
#         ctx.author: discord.PermissionOverwrite(view_channel=True, send_messages=True)
#     }
#
#     channel = await join_guild_channel.guild.create_text_channel(
#         position=0,
#         category=join_guild_channel.category,
#         name=f"Технический перерыв",
#         overwrites=overwrites,
#         reason="По приказу генерала гафса",
#         topic=f"Тех перерыв",
#         slowmode_delay=1
#
#     )
#     tms = await get_time_stamp(date_wait, time_wait)
#     tech_s_embed = discord.Embed(title="Технический перерыв", description=f"Временно приостановленна деятельность канала {join_guild_channel.mention} по причине:\n**{reason}**\n\n\n\nКанал "
#                                                                           f"откроется {tms[0]}.", color=discord.Color.red())
#     tech_s_embed = models.embed_stan(embed=tech_s_embed)
#     await channel.send(embed=tech_s_embed)
#     x: datetime = tms[1]
#
#     x = dt.timedelta(h)
#
#     await asyncio.wait()

@bot.command(
	name="тех",
	aliases=["tech"],
	usage='+tech date_wait="now", time_wait="now", *, reason=None'
)
@com.cooldown(1, 20, type=com.BucketType.user)
@com.is_owner()
async def tech_stop(ctx, date_wait="now", time_wait="now", *, reason=None):
	async def get_date(date=None, time=None):
		israel_tz = dt.timezone(offset=dt.timedelta(hours=2), name="UTC")
		dt_now = dt.datetime.now(tz=israel_tz)

		if type(date) is not str or type(time) is not str:
			raise NotImplementedError

		try:
			if date is None and time == 'now':
				return dt_now
			else:
				if time is None and date == 'now':
					return dt_now
				else:
					if date is None and time is None:
						return dt_now
					else:
						if date == 'now' and time == 'now':
							return dt_now
						else:
							if date == 'now' and time != 'now':
								year = dt_now.year
								month = dt_now.month
								day = dt_now.day

								hour = time.split('.', -1)[0]
								minute = time.split('.', -1)[1]
								second = time.split('.', -1)[2]

								time_ret = datetime(year=int(year), month=int(month), day=int(day),
								                    hour=int(hour), minute=int(minute), second=int(second), tzinfo=israel_tz)

								return time_ret

							elif time == 'now' and date != 'now':
								year = date.split('/', -1)[2]
								month = date.split('/', -1)[1]
								day = date.split('/', -1)[0]

								hour = dt_now.hour
								minute = dt_now.minute
								second = dt_now.second

								time_ret: datetime = datetime(year=int(year), month=int(month), day=int(day),
								                              hour=int(hour), minute=int(minute), second=int(second), tzinfo=israel_tz)

								return time_ret

							elif time and date != "now":
								year = date.split('/', -1)[2]
								month = date.split('/', -1)[1]
								day = date.split('/', -1)[0]

								hour = time.split('.', -1)[0]
								minute = time.split('.', -1)[1]
								second = time.split('.', -1)[2]

								time_ret: datetime = datetime(year=int(year), month=int(month), day=int(day),
								                              hour=int(hour), minute=int(minute), second=int(second), tzinfo=israel_tz)
								return time_ret

		except Exception as exc:
			LOGGER.error(
				f"TECH command error \n {exc}"
			)
			await ctx.send(exc)

	if date_wait and time_wait == "now":
		return await ctx.send(ctx.command.usage)

	if reason is None:
		reason = "Технический перерыв"
	else:
		reason = reason

	join_guild_channel = ctx.guild.get_channel(settings["ag_ci"])

	if isinstance(join_guild_channel, discord.TextChannel):
		pass
	else:
		await ctx.send("Не определился канал", delete_after=5)
	h = await join_guild_channel.history(limit=500).flatten()
	for msg in h:
		await msg.delete()

	async def get_time_stamp(date, time) -> str:
		try:
			time: datetime = await get_date(date, time)
			times = time.timestamp()
			times = str(times).split(".")[0]
			timestamp: str = f"<t:{times}:R>"
			return timestamp
		except Exception as exc:
			LOGGER.error(f"get timestamp exception {exc}")
			return f"<t:{datetime.now().timestamp()}:R>"

	tech_s_embed = discord.Embed(title="Технический перерыв", description=f"Временно приостановленна деятельность канала {join_guild_channel.mention} по причине:\n**{reason}**\n\n\n\nКанал "
	                                                                      f"откроется {await get_time_stamp(date_wait, time_wait)}.", color=discord.Color.red())
	tech_s_embed = models.embed_stan(embed=tech_s_embed)
	await join_guild_channel.send(embed=tech_s_embed)


@tech_stop.error
async def err(ctx, exception):
	if isinstance(exception, com.NotOwner):
		await ctx.send("Недостаточно прав", delete_after=15)
	elif isinstance(exception, com.CommandOnCooldown):
		await ctx.send(f"Подожди {exception.retry_after:.2f}", delete_after=15)


async def is_in_guild(ctx, guilds, member) -> tuple[str, bool]:
	for g in guilds:
		role_id = models.NEDOGUILD().get_one_tag(guild=g, tag="role")
		role = ctx.guild.get_role(role_id)

		if role in member.roles:
			return g, True

	return "None", False


class UnknownGuild(GmasterNotDefined):
	msg = "Гильдия не определена"


@bot.command(
	name="гильдия",
	aliases=[
		"guild",
		"g",
		"г"
	]
)
# @com.cooldown(1, 20, type=com.BucketType.user)
async def get_into(ctx, member: nextcord.Member):
	invite_state = False
	guild_master = GuildMaster(
		ctx=ctx
	)

	guild_name, user_in_guild = await is_in_guild(ctx, GUILDS, member=member)

	LOGGER.info(f"{guild_name} === {user_in_guild}")

	if guild_master.guild.lower() == 'unknown':
		raise GmasterNotDefined

	defense = GuildDefense(bot, ctx.guild, member.id, guild_master.guild)

	with open("additional_files/invites.json", "r", encoding="UTF-8") as invites_file:
		invites_dict = json.load(invites_file)

	try:
		if member.id in invites_dict["ids_list"]:
			invite_state = True
		elif invites_dict[f"invite_{member.id}"]["in_creating_invite"]:
			invite_state = True

	except Exception as exc:
		invite_state = False
		LOGGER.error(f"Error in get_into -> invite creating check: {exc}")

	def do(defence: GuildDefense, invite_state: bool, guild_master: GuildMaster, user_in_guild: bool, guild_name: str) -> str or None:
		if defence.is_on_cooldown[0]:
			if user_in_guild:
				return "kick"

			return "on_cooldown"

		elif invite_state:
			return "has_invite"

		elif user_in_guild:
			if guild_master.guild.strip().lower() == guild_name.strip().lower():
				return "kick"

			return "other_guild"

		return "add"

	case: str = do(defence=defense, invite_state=invite_state, guild_master=guild_master, user_in_guild=user_in_guild, guild_name=guild_name)

	LOGGER.success(case)
	if case == "on_cooldown":
		props = defense.is_on_cooldown[1]
		time_until_2m = datetime.fromtimestamp(float(props.get("until", None))) + dt.timedelta(seconds=120)

		timestamp_until = str(time_until_2m.timestamp()).split(".")[0]

		embed_error = models.embed_stan(
			nextcord.Embed(
				title="Не вышло!",
				description=f"{member.mention} недавно покинул {props.get('guild', '(ошибка)')}, он снова сможет вступить в гильдию <t:{timestamp_until}:R>!",
				color=nextcord.Color.red(),
			)
		)
		return await ctx.send(embed=embed_error)
	elif case == "has_invite":
		embed_error = models.embed_stan(
			nextcord.Embed(
				title="Не вышло!",
				description=f"На имя {member.mention} уже отправлена заявка в одну из гильдий, невозможно его принять!",
				color=nextcord.Color.red(),
			)
		)
		LOGGER.warning(f"Warning in get_into -> invite has check")
		return await ctx.send(embed=embed_error)
	elif case == "kick":
		role_id = models.NEDOGUILD().get_one_tag(guild=guild_name, tag="role")
		role = ctx.guild.get_role(role_id)

		await member.remove_roles(
			role, reason="По приказу генерала гафса!"
		)

		embed_error = models.embed_stan(
			nextcord.Embed(
				title="Ура!",
				description=f"{member.mention} был исключен из гильдии {guild_name}!",
				color=nextcord.Color.red(),
			)
		)
		LOGGER.debug(f"Kicked user from {guild_name}")

		defense.set_cooldown(cooldown_seconds=ONE_DAY_IN_SECONDS * 7)  # 2 days
		return await ctx.send(embed=embed_error)
	elif case == "other_guild":
		embed_error = models.embed_stan(
			nextcord.Embed(
				title="Не вышло!",
				description=f"Мастер гильдии {guild_master.guild} не может исключить пользователя из гильдии {guild_name}!\n\n\n\n***User collegium magistri variant!***",
				color=nextcord.Color.red(),
			)
		)
		LOGGER.debug(f"User collegium magistri variant")
		return await ctx.send(embed=embed_error)
	elif case == "add":
		role_id = models.NEDOGUILD().get_one_tag(guild=guild_master.guild, tag="role")
		role = ctx.guild.get_role(role_id)

		await member.add_roles(
			role, reason="По приказу генерала гафса!"
		)

		embed = models.embed_stan(
			nextcord.Embed(
				title="Ура!",
				description=f"{member.mention} был принят в гильдию {guild_master.guild}!"
			)
		)
		LOGGER.success(f"Successfully initiated {member.mention} into {guild_master.guild}")
		await ctx.send(embed=embed)
	else:
		embed = models.embed_stan(
			nextcord.Embed(
				title="Не вышло!",
				description=f"Неизвестный сценарий выполнения команды"
			)
		)
		LOGGER.success(f"Неизвестный сценарий match case into guild")
		await ctx.send(embed=embed)


# if defense.is_on_cooldown[0]:
# 	props = defense.is_on_cooldown[1]
# 	time_until_2m = datetime.fromtimestamp(float(props.get("until", None))) + dt.timedelta(seconds=120)
#
# 	timestamp_until = str(time_until_2m.timestamp()).split(".")[0]
#
# 	embed_error = models.embed_stan(
# 		nextcord.Embed(
# 			title="Не вышло!",
# 			description=f"{member.mention} вышел из {props.get('guild', '(ошибка)')}, он снова сможет вступить в гильдию <t:{timestamp_until}:R>.",
# 			color=nextcord.Color.red(),
# 		)
# 	)
# 	return await ctx.send(embed=embed_error)
# # 	Типа если заявку делает.
# elif invite_state:
# 	embed_error = models.embed_stan(
# 		nextcord.Embed(
# 			title="Не вышло!",
# 			description=f"У {member.mention} уже есть заявка!",
# 			color=nextcord.Color.red(),
# 		)
# 	)
# 	LOGGER.warning(f"Warning in get_into -> invite has check")
# 	return await ctx.send(embed=embed_error)
# elif user_in_guild:
#
# 	role_id = models.NEDOGUILD().get_one_tag(guild=guild_name, tag="role")
# 	role = ctx.guild.get_role(role_id)
#
# 	await member.remove_roles(
# 		role, reason="По приказу генерала гафса!"
# 	)
#
# 	embed_error = models.embed_stan(
# 		nextcord.Embed(
# 			title="Ура!",
# 			description=f"У {member.mention} успешно покинул гильдию {guild_name}!",
# 			color=nextcord.Color.red(),
# 		)
# 	)
# 	LOGGER.debug(f"Warning in get_into -> user already has guild")
#
# 	defense.set_cooldown(cooldown_seconds=(60 * 60 * 24 * 2))  # 2 days
# 	return await ctx.send(embed=embed_error)
#
# else:
# 	LOGGER.debug(invite_state)
# 	role_id = models.NEDOGUILD().get_one_tag(guild=guild_master.guild, tag="role")
# 	role = ctx.guild.get_role(role_id)
#
# 	await member.add_roles(
# 		role, reason="По приказу генерала гафса!"
# 	)
#
# 	embed = models.embed_stan(
# 		nextcord.Embed(
# 			title="Ура!",
# 			description=f"{member.mention} был принят в гильдию {guild_master.guild}!"
# 		)
# 	)
# 	LOGGER.success(f"Successfully initiated {member.mention} into {guild_master.guild}")
# 	await ctx.send(embed=embed)


@get_into.error
async def get_into_error_handler(ctx, exception):
	try:
		raise exception
	except GmasterNotDefined as exc:
		await something_went_wrong(problem=f"Гильд мастер не определен! \n {exc}", ctx=ctx)

		LOGGER.error(
			f"Ошибка в досрочном принятии пользователя в гильдию! \n {exc}"
		)
	except Exception as exc:
		await something_went_wrong(problem=f"Неизвестная ошибка! \n {exc}", ctx=ctx)

		LOGGER.error(
			f"Ошибка в досрочном принятии пользователя в гильдию! \n {exc}"
		)


if __name__ == '__main__':
	bot.run(token=settings['token'])
