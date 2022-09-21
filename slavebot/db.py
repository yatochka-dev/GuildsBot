from nextcord import Interaction
from tortoise import Tortoise, run_async


async def initdb():
	# Here we create a SQLite DB using file "db.sqlite3"
	#  also specify the app name of "models"
	#  which contain models from "app.models"
	await Tortoise.init(
		db_url='sqlite://database.db',
		modules={'models': ['models']}
	)
	# Generate the schema
	await Tortoise.generate_schemas()


run_async(initdb())

