from typing import List

import nextcord
from nextcord import Interaction, slash_command
from nextcord.ext.commands import Cog, Bot

from _config import Config
from slavebot import *

config = Config()

logger = config.get_logger


class MasterCommands(DataMixin, TextGetter, Cog):
    emoji = ''

    def __init__(self, bot: Bot):
        self.bot = bot

    async def change_speech(
            self, inter: nextcord.Interaction, guild: str or GuildsManager
            ):
        new_speech = await self.get_text(
            inter=inter,
            min_length=100,
            max_length=1024,
            label="Новая агитация",
            placeholder="Введите вашу агитационную речь"
        )

        if isinstance(guild, str):
            guild = GuildsManager(
                guild.lower()
            )

        guild.change_row(
            'speech',
            new_speech
        )

        embed = CustomEmbed(
            embed=nextcord.Embed(
                title="Успешно",
                description=f"Успешно изменена агитационная речь! \n\nНовая "
                            f"речь: {new_speech}"
            )
        ).great

        await inter.send(
            embed=embed,
            ephemeral=True
        )

    async def change_topic(
            self, inter: nextcord.Interaction, guild: str or GuildsManager
            ):
        chat_id: int = guild.get_data().chat_id if isinstance(guild,
                                                              GuildsManager) \
            else GuildsManager(
            guild.lower()).get_data().chat_id

        chat: nextcord.TextChannel = inter.guild.get_channel(chat_id)

        old_topic = chat.topic
        topic: str = await self.get_text(
            inter=inter,
            min_length=0,
            max_length=1024,
            label="Новая тема канала",
            placeholder='Введите новую тему канала. чтобы убрать тему канала '
                        '- напишите "1".'
        )

        ft = FormatSpeech(
            str(topic), {}, self.bot
        )

        await ft.format()

        new_topic: str = str(ft.speech)

        await chat.edit(
            topic=str(new_topic)
        )

        embed = \
            CustomEmbed(
                embed=nextcord.Embed(
                    title="Всё супер!",
                    description="Тема канал успешно изменена!"
                )
            ).normal

        embed.add_field(name="Старая тема канала",
                        value=f"{str(old_topic) if old_topic else '#'}",
                        inline=True)
        embed.add_field(name="Новая тема канала",
                        value=f"{str(new_topic) if new_topic else '#'}",
                        inline=True)

        await inter.send(
            ephemeral=True,
            embed=embed
        )

    @staticmethod
    def divide_list(lst: list, n: int):
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    @slash_command(
        name='members'
    )
    async def get_users(
            self, inter: nextcord.Interaction, guild_role: nextcord.Role
            ):

        divided_members: List[List[nextcord.Member]] = [
            d for d in self.divide_list(
                guild_role.members, 12
            )
        ]

        if len(divided_members) > 25:
            return await inter.send(
                embed=CustomEmbed.has_error(
                    exc="Слишком много пользователей имеют эту роль."),
                ephemeral=True,
            )

        embeds = []
        i = 1
        page = 1
        for l in divided_members:
            embed = CustomEmbed(
                embed=nextcord.Embed(
                    title=f"Пользователи - {page}",
                    description=f"Список из **{len(guild_role.members)}** "
                                f"пользователей с ролью {guild_role.mention},"
                                f" страница **{page}**.\nВзаимодействие "
                                f"возможно до "
                                f"{self.get_timestamp(minutes=5, discord=True, style='T')}"
                )
            ).normal

            for member in l:
                embed.add_field(
                    name=f"#{i}",
                    value=f"{member.mention} - {member.id}"
                )
                i += 1

            page += 1
            embeds.append(embed)

        if len(embeds) > 1:
            try:
                view = ListEmbedsView(
                    embeds=embeds,
                    user=inter.user,
                    button=True,
                    base_embed=embeds[0],

                )
            except ValueError as exc:
                return await self.bad_callback(
                    inter,
                    f"{exc}"
                )

            msg = await inter.send(
                embed=embeds[0],
                view=view,
                ephemeral=True
            )
            view.edit = msg.edit
            view.message = msg



        else:
            await inter.send(embed=embeds[0])

    @logger.catch()
    async def callback(self, do: str, inter: Interaction, guild: str):
        if do.lower() == 'речь':
            await self.change_speech(inter, guild)  # type: ignore

        elif do.lower() == 'тема':
            await self.change_topic(inter, guild)  # type: ignore

    @slash_command(
        name="gm",
        description="Профиль для гильд-мастера\nВарианты для использования: "
                    "/gm речь, /gm тема"

    )
    async def call(self, inter: Interaction, do: str):

        scripts = ('тема', 'речь')

        guild = await self.define_guild(inter)
        error_message = """Невозможно определить мастера, если это ошибка 
        обратитесь к <@!686207718822117463>."""

        if guild is None:
            return await self.bad_callback(
                interaction=inter,
                message=error_message
            )
        elif do.lower() in scripts:
            return await self.callback(do, inter, guild)
        else:
            await inter.send(
                str(await inter.guild.fetch_emoji(
                    868084062668095549)) + f"{scripts}"

            )

    @call.on_autocomplete("do")
    async def do_autocomplete(self, _inter: Interaction, value: str):
        sc = ('тема', 'речь')
        return sc if value not in sc else (value,)

    @slash_command(
        name='leave'
    )
    async def leave_from_guild(
            self,
            inter: Interaction,
    ):
        await inter.response.defer()

        check = CheckUser(
            self.bot,
            inter.guild,
            inter.user,
        )

        is_in_guild = await check.is_in_guild_get_guilds()

        if is_in_guild is False:
            return await self.bad_callback(
                interaction=inter,
                message="Вы не состоите в гильдии."
            )

        await inter.user.remove_roles(*is_in_guild)
        formatted_roles = ', '.join([f"{r.mention}" for r in is_in_guild])

        embed = ResponseEmbed(
            embed=nextcord.Embed(
                title="Вы покинули гильдию.",
                description=f"Вы покинули гильдию, у вас были сняты роли:"
                            f" {formatted_roles}"
            ),
            user=inter.user,
        ).normal

        await inter.send(
            embed=embed
        )

    @slash_command(
        name="g"
    )
    async def user_manage(
            self,
            inter: Interaction,
            member: nextcord.Member,
    ):
        await inter.response.defer()


        if member.bot:
            return await self.bad_callback(
                interaction=inter,
                message="Вы не можете управлять ботами."
            )

        elif member == inter.user:
            return await self.bad_callback(
                interaction=inter,
                message="Вы не можете управлять собой."
            )




        check = CheckUser(
            self.bot,
            inter.guild,
            member,
        )



        author_check = CheckUser(
            self.bot,
            inter.guild,
            inter.user,
        )

        is_master = await author_check.is_master_get_role()

        if is_master is False:
            return await self.bad_callback(
                interaction=inter,
                message="Вы не являетесь мастером."
            )

        _g = await self.define_guild(inter)
        manager = GuildsManager(_g)
        data = manager.get_data()
        role = inter.guild.get_role(data.role_id)

        is_in_guild = await check.is_in_guild_get_role()

        if not is_in_guild:
            await member.add_roles(role)
            return await inter.send(
                embed=ResponseEmbed(
                    embed=nextcord.Embed(
                        title="Добавлены в гильдию.",
                        description=f"{member.mention} добавлен в гильдию"
                                    f" {role.mention}"
                    ),
                    user=member,
                ).great
            )
        else:
            if has_role(role, member):
                creating_invite = await check.in_invite
                has_invite = await check.has_invite
                if creating_invite:
                    return await self.bad_callback(
                        interaction=inter,
                        message="Этот пользователь создает заявку."
                    )
                elif has_invite:
                    return await self.bad_callback(
                        interaction=inter,
                        message="У пользователя уже есть заявка."
                    )

                await member.remove_roles(role)
                return await inter.send(
                    embed=ResponseEmbed(
                        embed=nextcord.Embed(
                            title="Покинули гильдию.",
                            description=f"{member.mention } покинул гильдию"
                                        f" {role.mention}"
                        ),
                        user=member,
                    ).great
                )
            else:
                return await self.bad_callback(
                    interaction=inter,
                    message="Пользователь состоит в иной гильдии, вьі не "
                            "можете его исключить."
                )



















def setup(bot: Bot):
    bot.add_cog(MasterCommands(bot))
