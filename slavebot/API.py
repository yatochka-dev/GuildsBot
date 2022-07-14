import json
import re
import time
from typing import Tuple

import nextcord
from nextcord.ext import commands

from .tools import has_role
from _config import Config

config = Config()

logger = config.get_logger


class BaseAPIGetter:
	DISCORD_API = "https://discord.com/api/v9/"

	def __init__(self):
		self.data = None

	async def get(self, *args, **kwargs):
		pass

	async def format(self, *args, **kwargs):
		pass


# self.formatted_data = None


class MessagesCounter(BaseAPIGetter):
	def __init__(self, role: int):
		super(MessagesCounter, self).__init__()
		self.role = role

	async def get(self, channel: nextcord.TextChannel) -> Tuple[dict, str]:

		res = {}

		start = time.time()

		async for _ in channel.history(limit=100_000):
			f = "<@!" + str(_.author.id) + ">"
			if f.lower() in list(res.keys()):
				res[f] += 1
			else:
				res[f] = 1

			with open("./res.json", 'w') as file:
				json.dump(res, file, indent=4)

		now = time.time()

		return res, f"{now - start} seconds"

	async def format(self, bot: commands.Bot):

		server = bot.get_guild(config.base_server)
		role = server.get_role(self.role)
		with open("./res.json", 'r') as file:
			j: dict = json.load(file)

		prs = {}

		for _ in list(j.keys()):
			logger.info(int(re.findall(r'\d+', _)[0]))
			member = server.get_member(int(re.findall(r'\d+', _)[0]))

			if member:
				if has_role(role, member):
					prs[_] = j[_]
			else:
				logger.info(f"Non in guild member {_}")

		return prs

	@staticmethod
	async def sort(prs: dict):

		return {i[0]: i[1] for i in sorted(prs.items(), key=lambda para: (para[1]))}
