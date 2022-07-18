from typing import NamedTuple, Literal

from .API import MessagesCounter
from .CheckDevice import CheckDevice
from .GuildsManager import GuildsManager, DB
from .InviteModal import InviteModal, do_get_genders_list, do_get_activities_list, do_create_years_list
from .InviteSend import InviteSend, InviteAnswer
from .InvitesManager import InvitesManager
from .base import User, Guild
from .embeds import CustomEmbed, ResponseEmbed
from .errors import *
from .getters import TextGetter
from .tools import get_year_end, has_role, __create_guild, get_or_create_guild, FormatData, FormatSpeech, CheckUser, UIResponse, VotingMenu
from .utils import GuildDefense, DataMixin, CommandsMixin
from .views import GuildView, WithoutView, InviteView, YesCloseVIew, GetMessageView, ListEmbedsView


class VersionInfo(NamedTuple):
	major: int
	minor: int
	micro: int
	releaselevel: Literal["alpha", "beta", "candidate", "final"]
	serial: int

	def __str__(self):
		return "{0.major}-{0.minor}-{0.micro}\nrelease level - {0.releaselevel}\nserial - {0.serial}".format(self)

	def get(self):
		return f'{self.major}-{self.minor}-{self.micro} -- {self.releaselevel}'

version_info: VersionInfo = VersionInfo(major=2, minor=0, micro=0, releaselevel="alpha", serial=0)

__version__ = version_info
__author__ = "Philip sagan <philipchef13@gmail.com>"
