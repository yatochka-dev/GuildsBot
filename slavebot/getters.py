import nextcord

from slavebot import GetMessageView


class TextGetter:
	async def get_text(self, inter: nextcord.Interaction, min_length: int = 1, max_length: int = 1024, label: str = "Текст", placeholder: str = "Введите текст") -> str:
		modal = GetMessageView(
			min_length=min_length,
			max_length=max_length,
			label=label,
			placeholder=placeholder,
		)
		await inter.response.send_modal(
			modal=modal
		)
		await modal.wait()
		data = str(modal.data)

		if len(data) <= 1:
			return ""
		return data
