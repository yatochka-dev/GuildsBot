import asyncio

import nextcord
from nextcord.ext.commands import Bot

from .views import GetMessageView


class TextGetter:
    async def get_text(
            self, inter: nextcord.Interaction, min_length: int = 1,
            max_length: int = 1024, label: str = "Текст",
            placeholder: str = "Введите текст"
    ) -> str:
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

    async def get_chat_text(
            self,
            inter: nextcord.Interaction,
            bot: Bot,
    ):
        await inter.response.defer()

        await inter.send("Gimme message!\nYou have only 1000 seconds")

        def check(message: nextcord.Message):
            return inter.user.id == message.author.id and inter.channel_id == \
                   message.channel.id

        try:
            return await bot.wait_for(
                "message",
                check=check,
                timeout=1000
            )

        except asyncio.TimeoutError:
            await inter.edit_original_message(content="Oh fuck, i cannot wait too "
                                              "long!")
            return None
