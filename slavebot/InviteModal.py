# x = nextcord.SelectOption(label="Test", description="Test desc")
# y = nextcord.SelectOption(label="Test 2", description="Test desc 2")
#
# years = [nextcord.SelectOption(label=f"{number}", description=f"Мне {number} лет") for number in range(24)]
#
# class TestModal(nextcord.ui.Modal):
#
# 	def __init__(self):
# 		super(TestModal, self).__init__("Создание заявки типа вот так")
#
# 		self.t = nextcord.ui.Select(options=years, placeholder="Сколько вам лет?")
#
#
# 	async def callback(self, interaction: nextcord.Interaction):
# 		pass
import nextcord
from nextcord import Interaction, SelectOption, TextInputStyle  # NOQA
from nextcord.ext import commands
from nextcord.ui import Modal, Select, TextInput  # NOQA

from _config import Config
from slavebot import *
config = Config()

logger = config.get_logger


def do_create_years_list() -> list:
	MAX_YEARS = 23
	before = SelectOption(
		label="Не хочу говорить",
		description="Это уменьшает шанс на вступление в гильдию...",
		value="NONE",
	)

	years = [
		SelectOption(
			label=f"{num}",
			description=f"Мне {num} {get_year_end(num)}.",
			value=f"{num}"
		) for num in range(1, MAX_YEARS + 1)
	]

	after = SelectOption(
		label="Больше",
		description=f"Я подтверждаю, что мне больше {MAX_YEARS}-х лет.",
		value="MORE"
	)

	years.insert(0, before)
	years.append(after)

	return years


def do_get_genders_list():
	return [
		SelectOption(
			label=f"{gender}",
			description=f"Мой пол - {gender}",
			value=f"{gender}".lower()
		) for gender in ['Мужчина', "Женщина", "Lockheed/Boeing F-22 Raptor"]
	]


def do_get_activities_list():
	return [
		SelectOption(
			label=f"{activity}",
			description=f"Я активен {activity}",
			value=f"{activity}".lower()
		) for activity in ['в обычном чате', "в голосовом чате", "и там и там"]
	]


class InviteModal(Modal):
	WHY_ACCEPT_FIELD = TextInput(
		label="Почему?",
		style=TextInputStyle.paragraph,
		min_length=50,
		max_length=1024,
		required=True,
		placeholder="Почему гильдмастер должен прнять вас в гильдию?"
	)

	WANT_FIELD = TextInput(
		label="Чего вы хотите от гильдии?",
		style=TextInputStyle.paragraph,
		min_length=15,
		max_length=300,
		required=True,
		placeholder="Какие аспекты вы бы хотели видеть в гильдии? Например: Актив, Ивенты и т.п."
	)

	def __init__(self, mobile: bool, bot: commands.Bot, guild: str = ""):
		super(InviteModal, self).__init__(
			timeout=(30 * 60),  # 30 минут
			title=f"Вступление в гильдию {str(guild).lower().capitalize()}."
		)
		self.guild = guild
		self.mobile = mobile
		self.bot = bot

		if not self.mobile:
			self.AGE_FIELD = Select(
				custom_id="SELECT_AGE",
				placeholder="Сколько вам лет?",
				options=do_create_years_list(),
				min_values=0,
			)
			self.GENDER_FIELD = Select(
				custom_id="SELECT_GENDER",
				placeholder="Ваш пол",
				options=do_get_genders_list(),
				min_values=0
			)

			self.ACTIVITY_FIELD = Select(
				custom_id="SELECT_ACTIVITY",
				placeholder="Где вы активны?",
				options=do_get_activities_list(),
				min_values=0
			)
		else:
			# Если на мобилке
			self.AGE_FIELD = TextInput(
				label="Ваш возраст?",
				style=TextInputStyle.short,
				min_length=1,
				max_length=5,
				required=True,
				placeholder="Сколько вам лет?",
			)
			self.GENDER_FIELD = TextInput(
				label="Ваш пол?",
				style=TextInputStyle.short,
				min_length=1,
				max_length=150,
				required=True,
				placeholder="Какого вы пола?)",
			)

			self.ACTIVITY_FIELD = TextInput(
				label="Активность?",
				style=TextInputStyle.paragraph,
				min_length=10,
				max_length=150,
				required=True,
				placeholder="Где вы больше всего активны? (Обычный чат, Голосовой чат, И там и там?)",
			)

		self.add_item(self.AGE_FIELD)
		self.add_item(self.GENDER_FIELD)
		self.add_item(self.ACTIVITY_FIELD)

		self.add_item(self.WHY_ACCEPT_FIELD)
		self.add_item(self.WANT_FIELD)

	def __str__(self):
		return f"{self.mobile}"

	async def callback(self, interaction: Interaction) -> None:
		try:
			if self.mobile:
				age = self.AGE_FIELD.value
				gender = self.GENDER_FIELD.value
				activity = self.ACTIVITY_FIELD.value
			else:
				age = self.AGE_FIELD._selected_values  # NOQA
				gender = self.GENDER_FIELD._selected_values  # NOQA
				activity = self.ACTIVITY_FIELD._selected_values  # NOQA
		except Exception as exc:
			raise LookupError(f"Ошибка получения данных {exc}") from exc

		try:
			data = FormatData(
				age=age,
				gender=gender,
				activity=activity,
				why_accept=self.WHY_ACCEPT_FIELD.value,
				want=self.WANT_FIELD.value,
			).format()
		except Exception as exc:
			raise LookupError(f"Ошибка форматирования данных {exc}") from exc

		try:
			try:
				manager = InvitesManager(interaction.user.id)
			except Exception as exc:
				raise LookupError(f"Ошибка менеджера заявок {exc} ") from exc

			send = InviteSend(
				interaction=interaction,
				data=data,
				guild=self.guild,
				bot=self.bot,
				manager=manager
			)

			await send.send()
		except Exception as exc:
			raise LookupError(f"Ошибка отправки заявки {exc}") from exc

		self.stop()

	async def on_error(self, error: Exception, interaction: Interaction) -> None:
		embed = CustomEmbed(
			embed=nextcord.Embed(
				title="Ошибка",
				description=f"{error}",
			)
		).error

		self.stop()

		await interaction.send(embed=embed, ephemeral=True)
