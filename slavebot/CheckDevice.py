import nextcord
from nextcord import Interaction, TextInputStyle
from nextcord.ui import Modal, TextInput

from .embeds import CustomEmbed
from _config import Config

config = Config()

logger = config.get_logger


class LetsGoAfterCheckDevice(nextcord.ui.View):

	def __init__(self, modal: Modal):
		super().__init__(timeout=259200)  # 259200 -> Три дня
		self.state = None

		self.modal = modal

	@nextcord.ui.button(label="Вперёд!", style=nextcord.ButtonStyle.blurple, row=0)
	async def yes(self, _button, interaction: Interaction):
		await interaction.response.send_modal(
			self.modal
		)
		self.state = True
		await self.modal.wait()
		self.stop()


class CheckDevice(Modal):
	"""
		Modal for checking user device.
		Some other modal may need self.mobile attribute.
	"""
	DEVICE_FIELD = TextInput(
		custom_id="SELECT_AGE",
		label="Вы с мобильного телефона?",
		placeholder="Это очень важно т.к. неправдивый ответ может повлечь за собой неприятные последствия.",
		style=TextInputStyle.paragraph
	)

	def __init__(self, *args, modal: callable, **kwargs):
		super(CheckDevice, self).__init__(
			timeout=(30 * 60),  # 30 минут
			title=f"Да или Нет"
		)
		self.modal = modal
		self.args = args
		self.kwargs = kwargs

		self.mobile = None

		self.add_item(self.DEVICE_FIELD)

	async def callback(self, interaction: Interaction):
		self.mobile = await self.__check__device()

		modal = self.modal(*self.args, **self.kwargs, mobile=self.mobile)

		logger.success(f"{modal}")

		yn = LetsGoAfterCheckDevice(modal)

		response_embed = CustomEmbed(
			embed=nextcord.Embed(
				title="Отлично!",
				description="Теперь вы можете нажать на кнопку и получите доступ, к ожидаемому содержимому."
			)
		).great

		await interaction.send(
			embed=response_embed,
			view=yn,
			ephemeral=True,
		)

		# await self.callback(*self.callback_args, **self.callback_kwargs)

		self.stop()

	async def __check__device(self):
		value = self.DEVICE_FIELD.value.lower().strip()

		if value in ("yes", "да", "1", "+", "true", "ya", "of course", "hohoho yea"):
			return True
		else:
			return False
