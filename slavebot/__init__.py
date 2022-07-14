from typing import NamedTuple, Literal


class VersionInfo(NamedTuple):
	major: int
	minor: int
	micro: int
	releaselevel: Literal["alpha", "beta", "candidate", "final"]
	serial: int

	def __str__(self):
		return "{0.major}-{0.minor}-{0.micro}\nrelease level - {0.releaselevel}\nserial - {0.serial}".format(self)


version_info: VersionInfo = VersionInfo(major=2, minor=0, micro=0, releaselevel="final", serial=0)

__version__ = version_info
__author__ = "Ята#7777"

from .API import MessagesCounter  # type: ignore
from .CheckDevice import CheckDevice  # type: ignore
from .GuildsManager import GuildsManager, DB  # type: ignore
from .InviteModal import InviteModal, do_get_genders_list, do_get_activities_list, do_create_years_list  # type: ignore
from .InviteSend import InviteSend, InviteAnswer  # type: ignore
from .InvitesManager import InvitesManager  # type: ignore
from .base import User, Guild  # type: ignore
from .embeds import CustomEmbed  # type: ignore
from .errors import *  # type: ignore
from .tools import get_year_end, has_role, __create_guild, get_or_create_guild, FormatData, FormatSpeech, CheckUser, UIResponse, VotingMenu  # type: ignore
from .utils import GuildDefense, DataMixin, CommandsMixin  # type: ignore
from .views import GuildView, WithoutView, InviteView, YesCloseVIew, GetMessageView, VotingView  # type: ignore
from .getters import TextGetter