import sqlite3

from _config import Config
from .base import User

config = Config()

logger = config.get_logger
con = sqlite3.connect(config.DB_PATH)
cur = con.cursor()


class InvitesManager:

	def __init__(self, user_id: int):
		self.user: User = self.get_user(user_id)

	@classmethod
	def get_user(cls, user_id: int) -> User:
		try:
			try:
				return User.get(_id=user_id)
			except:
				return cls.__create_user(user_id)
		except Exception as exc:
			logger.error(f"Ошибка получения пользователя {exc}")
			raise LookupError(f"Ошибка получения пользователя {exc}") from exc

	@classmethod
	def __create_user(cls, _id: int):
		try:
			user = User.create(_id=int(_id))
			user.save()
			return user
		except Exception as exc:
			logger.error(f"Ошибка создание пользователя {exc}")
			raise LookupError(f"Ошибка создание пользователя {exc}") from exc

	def has_invite(self, _is: bool or None = None) -> bool:
		try:
			if _is is not None:
				self.user.has_invite = _is
				self.user.save()

			return self.user.has_invite
		except Exception as exc:
			logger.error(f"Ошибка получения данных has_invite {exc}")
			raise LookupError(f"Ошибка получения данных has_invite {exc}") from exc

	def creating_invite(self, _is: bool or None = None) -> bool:
		try:
			if _is is not None:
				self.user.is_in_creating_invite = _is
				self.user.save()

			return self.user.is_in_creating_invite
		except Exception as exc:
			logger.error(f"Ошибка получения данных creating_invite {exc}")
			raise LookupError(f"Ошибка получения данных creating_invite {exc}") from exc

	@classmethod
	def clear_invites(cls):
		query = """
		UPDATE user
			SET has_invite = 0
		WHERE _id >= 0
			"""

		query_ = """
		UPDATE user
			SET is_in_creating_invite = 0
		WHERE _id >= 0
			"""

		cur.execute(query)
		cur.execute(query_)

		con.commit()
