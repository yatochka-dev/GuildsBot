import asyncio
import random
import re
from typing import Tuple, List, Optional

import nextcord
from nextcord import Interaction, TextInputStyle
from nextcord.ext import commands
from nextcord.ui import Modal, TextInput

from _config import Config
from .GuildsManager import GuildsManager
from .embeds import CustomEmbed
from .tools import CheckUser
from .utils import DataMixin

config = Config()

logger = config.get_logger


class GuildView(DataMixin, nextcord.ui.View):

	def __init__(self, bot: commands.Bot, check_device, invite_modal):
		super().__init__(timeout=None)
		self.bot = bot
		self.CheckDevice = check_device
		self.InviteModal = invite_modal

	async def __check(self, inter: Interaction, _btn: nextcord.Button) -> Tuple[bool, str, any]:
		c = CheckUser(
			bot=self.bot,
			server=self.bot.get_guild(config.base_server),
			user=inter.user
		)

		res = True
		msg = ""

		hi = await c.has_invite
		ii = await c.in_invite
		im = await c.is_master()
		iig = await c.is_in_guild()

		if hi:
			res = False
			msg = "Вы уже отправили заявку, сейчас нужно дождатся пока вас примут в гильдию.\n\n**Если вас не примут - вы сможете отправить заявку снова**"

		elif ii:
			res = False
			msg = "Вы уже начали создавать заявку, если это не так, обратитесь к <@!686207718822117463>."

		elif im:
			res = False
			msg = "Вы являеетесь гильд-мастером, вы не можете сменить гильдию, пока не закончится ваш срок правления."

		elif iig:
			res = False
			msg = "Вы уже находитесь в гильдии, попросите вашего мастера изнать вас. \n\n Также вы можете написать /leave или +лив"

		return res, msg, c.manager

	async def __callback(self, inter: Interaction, btn: nextcord.Button):
		checked, message, manager = await self.__check(inter, btn)

		if not checked:
			return await self.bad_callback(interaction=inter, message=message)

		guild = str(btn.custom_id).strip().lower()

		if guild == "random":
			guild = random.choice(config.ALL_GUILDS).lower()

		manager.creating_invite(True)

		await inter.response.send_modal(
			self.CheckDevice(
				modal=self.InviteModal,
				guild=guild,
				bot=self.bot,
			)
		)

		await asyncio.sleep(30)

		manager.creating_invite(False)

	@nextcord.ui.button(label="Дендро", style=nextcord.ButtonStyle.blurple, custom_id="Dendro")
	async def dendro(self, button: nextcord.Button, interaction: nextcord.Interaction):
		await self.__callback(interaction, button)

	@nextcord.ui.button(label="Гидро", style=nextcord.ButtonStyle.blurple, custom_id="Hydro")
	async def hydro(self, button: nextcord.Button, interaction: nextcord.Interaction):
		await self.__callback(interaction, button)

	@nextcord.ui.button(label="Пиро", style=nextcord.ButtonStyle.blurple, custom_id="Pyro")
	async def pyro(self, button: nextcord.Button, interaction: nextcord.Interaction):
		await self.__callback(interaction, button)

	@nextcord.ui.button(label="Крио", style=nextcord.ButtonStyle.blurple, custom_id="Cryo")
	async def cryo(self, button: nextcord.Button, interaction: nextcord.Interaction):
		await self.__callback(interaction, button)

	@nextcord.ui.button(label="Анемо", style=nextcord.ButtonStyle.blurple, custom_id="Anemo")
	async def anemo(self, button: nextcord.Button, interaction: nextcord.Interaction):
		await self.__callback(interaction, button)

	@nextcord.ui.button(label="Электро", style=nextcord.ButtonStyle.blurple, custom_id="Electro")
	async def electro(self, button: nextcord.Button, interaction: nextcord.Interaction):
		await self.__callback(interaction, button)

	@nextcord.ui.button(label="Гео", style=nextcord.ButtonStyle.blurple, custom_id="Geo")
	async def geo(self, button: nextcord.Button, interaction: nextcord.Interaction):
		await self.__callback(interaction, button)

	@nextcord.ui.button(label="Случайная гильдия", style=nextcord.ButtonStyle.green, custom_id="random")
	async def random(self, button: nextcord.Button, interaction: nextcord.Interaction):
		await self.__callback(interaction, button)


class WithoutView(nextcord.ui.View):

	def __init__(self):
		super().__init__()


class InviteView(DataMixin, nextcord.ui.View):

	def __init__(self, wait_to: int, guild: str):
		super().__init__(timeout=wait_to)  # 259200 -> Три дня
		self.do = ""
		self.guild = guild

	async def __check(self, inter: Interaction) -> Tuple[bool, str]:
		gm_role_id = GuildsManager(self.guild.lower()).get_data().master_role_id
		role = inter.guild.get_role(gm_role_id)

		from tools import has_role

		if has_role(role, inter.user):
			res = True
			msg = ""
		else:
			res = False
			msg = "У вас нет прав на использование данного элемента!"

		return res, msg

	@nextcord.ui.button(label="Принять", style=nextcord.ButtonStyle.green, emoji="✔️")
	async def accept(self, _btn, inter: nextcord.Interaction) -> None:
		check, message = await self.__check(inter)

		if check:
			self.do = True
			self.stop()
		else:
			await self.bad_callback(interaction=inter, message=message)

	@nextcord.ui.button(label="Отклонить", style=nextcord.ButtonStyle.red, emoji="❌")
	async def decline(self, _btn, inter: nextcord.Interaction) -> None:
		check, message = await self.__check(inter)
		if check:
			self.do = False
			self.stop()
		else:
			await self.bad_callback(interaction=inter, message=message)

	async def on_timeout(self) -> None:
		self.do = None
		self.stop()


class YesCloseVIew(nextcord.ui.View):

	def __init__(self, wait_for: int, users_tc: nextcord.role, modal: callable, **kwargs):
		super(YesCloseVIew, self).__init__(timeout=wait_for)
		self.ans: bool = False
		self.data = ""
		self.inter: nextcord.Interaction or None = None
		self.rtc = users_tc
		self.modal = modal
		self.kw = kwargs

	@logger.catch()
	async def __check__(self, inter: nextcord.Interaction) -> Tuple[bool, str]:
		from tools import has_role

		if has_role(self.rtc, inter.user):
			res = True
			msg = ""
		else:
			res = False
			msg = "У вас нет прав на использование данного элемента!"

		return res, msg

	@logger.catch()
	async def __bad_callback(self, interaction: nextcord.Interaction, message: str):

		return await interaction.send(
			ephemeral=True,
			embed=CustomEmbed(
				embed=nextcord.Embed(
					title="Ошибка!",
					description=message
				)
			).error
		)

	@nextcord.ui.button(label="Да", style=nextcord.ButtonStyle.green)
	async def ya(self, _btn, inter: nextcord.Interaction) -> None:
		check, message = await self.__check__(inter)

		if check:
			modal = self.modal(**self.kw)

			await inter.response.send_modal(
				modal=modal
			)

			await modal.wait()

			self.ans = True
			self.data = modal.data
			self.stop()
		else:
			await self.__bad_callback(inter, message)

	@nextcord.ui.button(label="Нет", style=nextcord.ButtonStyle.green)
	async def close(self, _btn, inter: nextcord.Interaction) -> None:
		check, message = await self.__check__(inter)

		if check:
			self.ans = False
			self.inter = inter
			self.stop()
		else:
			await self.__bad_callback(inter, message)


class GetMessageView(Modal):
	message = TextInput(
		label="Текст",
		style=TextInputStyle.short,
		min_length=20,
		max_length=1024,
		required=True,
		placeholder="Введите текст"
	)

	def __init__(
			self,
			title: str = "Напишите сообщение",
			min_length: int = 20,
			max_length: int = 1024,
			label: str = "Текст",
			placeholder: str = "введите текст"
	):
		super(GetMessageView, self).__init__(
			title=title,
			timeout=(60 * 60)
		)
		self.message.min_length = min_length
		self.message.max_length = max_length
		self.message.label = label
		self.message.placeholder = placeholder

		if self.message.max_length > 30:
			self.message.style = TextInputStyle.paragraph

		self.add_item(self.message)
		self.data = ""

	async def callback(self, interaction: Interaction):
		self.data = self.message.value
		self.stop()


# class MasterView(nextcord.ui.View):
#
# 	def __init__(self, guild: str, speech: callable, topic: callable, message: nextcord.Message):
# 		super(MasterView, self).__init__(
# 			timeout=60
# 		)
# 		self.guild = guild
# 		self.sp = speech
# 		self.tp = topic
# 		self.msg = message
#
# 	async def __check__(self, inter: nextcord.Interaction) -> bool:
# 		_ = GuildsManager(self.guild.lower())
# 		role_id = _.get_data().master_role_id
#
# 		role = inter.guild.get_role(role_id)
#
# 		d = has_role(user=inter.user, role=role)
#
# 		if d:
# 			return d
# 		else:
# 			await inter.send(
# 				embed=CustomEmbed.no_perm(),
# 				ephemeral=True
# 			)
#
#
#
# 	@nextcord.ui.button(label="Изменить агитационную речь", style=nextcord.ButtonStyle.green)
# 	async def speech(self, _btn, inter: nextcord.Interaction) -> None:
# 		if await self.__check__(inter):
# 			await self.sp(inter)
# 			self.stop()
#
# 	@nextcord.ui.button(label="Изменить тему канала", style=nextcord.ButtonStyle.blurple)
# 	async def topic(self, _btn, inter: nextcord.Interaction) -> None:
# 		if await self.__check__(inter):
# 			self.stop()
#
# 	@nextcord.ui.button(label="Закрыть", style=nextcord.ButtonStyle.red)
# 	async def close(self, _btn, inter: nextcord.Interaction) -> None:
# 		if await self.__check__(inter):
# 			self.stop()

# class VotingView(
# 	nextcord.ui.View,
# 	utils.DataMixin
# ):
#
# 	def __init__(
# 			self,
# 			timeout: float = (60 * 60 * 24 * 3),
# 	):
# 		super(VotingView, self).__init__(
# 			timeout=timeout,
# 			auto_defer=False,
# 		)
# 		self.response = VotingMenu('end')
#
# 	@nextcord.ui.button(label="Выбрать победителя!", style=nextcord.ButtonStyle.green)
# 	async def start(self, _btn, inter: nextcord.Interaction) -> None:
# 		if await self.has_perms(inter=inter):
# 			self.response.change(
# 				to='start'
# 			)
# 			self.stop()

class MasterMembers(nextcord.ui.Select):

	def __init__(self, embeds: List[nextcord.Embed], user: nextcord.Member):
		self.embeds = embeds
		self.user = user

		if len(self.embeds) > 25:
			raise ValueError("Слишком много пользователей")

		pg = 1
		options = []

		for _emb in embeds:
			options.append(
				nextcord.SelectOption(
					label=f"#{pg}",
					description=f"Страница {pg}",
					value=str(pg),
				)
			)

			pg += 1

		super(MasterMembers, self).__init__(
			options=options,
			min_values=1,
			max_values=1,
			placeholder="Выберите страницу"
		)

		self.data: Optional[dict] = {}

	async def callback(self, interaction: Interaction):
		self.interaction = interaction
		if self.user == interaction.user:

			chosen = self.values[0]
			_id = int(re.findall(r"\d+", str(chosen))[0]) - 1

			embed = self.embeds[_id]

			await interaction.response.edit_message(
				content="",
				embed=embed,
			)
			self.data['embed'] = embed

		else:
			await interaction.send(
				embed=CustomEmbed.no_perm(),
				ephemeral=True
			)


class ListEmbedsView(nextcord.ui.View):
	def __init__(self, embeds: List[nextcord.Embed], user: nextcord.Member, base_embed: nextcord.Embed, button: bool = False, edit: callable = None):
		super(ListEmbedsView, self).__init__(timeout=300)  # 5 минут

		self.menu = MasterMembers(
			embeds=embeds,
			user=user
		)

		self.add_item(
			self.menu
		)

		if not button:
			self.clear_items()
			self.add_item(self.menu)

		self.embed: Optional[nextcord.Embed] = base_embed
		self.message: Optional[nextcord.Message] = None
		self.edit: Optional[callable] = edit

	@nextcord.ui.button(
		label="Отобразить пользователей",
		style=nextcord.ButtonStyle.blurple
	)
	@logger.catch()
	async def show(self, _btn, _inter: Interaction):
		msg = await _inter.send(
			embed=CustomEmbed.working_on(),
			ephemeral=True
		)
		try:
			self.embed: nextcord.Embed or None = self.menu.data.get('embed', self.embed)
			edit: callable = self.edit

			text = ""

			for f in self.embed.fields:
				text += f'\n{f.value}'

			await edit(
				content=text
			)
		except Exception as exc:
			await msg.edit(
				embed=CustomEmbed.has_error(exc)
			)
			raise exc from exc
		else:
			await msg.edit(
				embed=CustomEmbed.done()
			)

	async def on_timeout(self) -> None:
		self.clear_items()
		await self.message.edit(view=self)

	def add_msg(self, msg: nextcord.Message or nextcord.InteractionMessage):
		self.msg = msg

		return self
