"""
Шард бота номер 6, краткое ТЗ:

На сервере глинчиков созданы два канала, в одном есть сообщения от ГМ-ов и в конце сообщение с кнопками.

В каждом сообщении должно-быть указано кто является ГМ-ом той или иной гильдии,
а также агитация созданная всеми участниками каждой гильдии.

В последнем сообщении будет 8 кнопок, первые 7 отвечают за заявку на вступление в одну из 7-и гильдии.

Восьмая кнопка отвечает за заявку во все гильдии.


Требования:
-Автоматическое обновление сообщений в первом канале.
-Кнопки которые отвечают за набор в гильдии.
-Роль-менеджмент - автоматическое регулирование ролей.
-команда со статистикой каждой гильдии
-команды для ГМ-ов для управления собственной гильдией(смена названия канала, выгон участников и т.д)


Краткие тех. характеристики:

ЯП - Python,
Предназначение - Дискорд-сервер Глинчики
БД - MongoDB
Библиотека работы с дискордом - nextcord

файлы:

manager.py
Объединение 2 файлов

models.py
Управление базой данных

_config.py
Разные настройки

schedule.py
Задачи выполняющиеся раз в какое-то время

main.py
Основной код

"""
import requests

settings = {
    'pre': "!",
    "token": "ODYxNjI2NDA1MzEzNzA4MDYy.YOMiHw.2xTxozTjeP6xan0sByy_8XaBRLc",
    "bot": "SlaveBot#5164",
    "user_id": "861626405313708062",
    "ag_ci": 929059781245808700,
    "bi_ci": 929059926641356850,
}


def ret(user_id, guild_id):
    try:
        headers = {
            "authorization": "mfa.mZ7PZ22s2eWBnQpCZlRY8-iQYk6LAd-eJfAgpDljm5k9gf0RngsZgKEDbRQTNhPh84JYC-mqEnPuz_FPb1vg"
        }
        r = requests.get(f"https://discordapp.com/api/v9/guilds/{guild_id}/messages/search?author_id={user_id}&include_nsfw=true", headers=headers)
        r = r.json()
        total_results = r["total_results"]
        return total_results
    except Exception as e:
        print(f'----------------------------\nException in parser!\n\n {e}\n\n----------------------------\n')


def messages_in_guild(user_id, guild_id, channel_id):
    headers = {
        "authorization": "mfa.mZ7PZ22s2eWBnQpCZlRY8-iQYk6LAd-eJfAgpDljm5k9gf0RngsZgKEDbRQTNhPh84JYC-mqEnPuz_FPb1vg"
    }

    r = requests.get(f"https://discord.com/api/v9/guilds/{guild_id}/messages/search?author_id={user_id}&channel_id={channel_id}&include_nsfw=true", headers=headers)
    r = r.json()
    print(r)
    total_results = r['total_results']
    return total_results

