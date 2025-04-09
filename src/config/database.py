__all__ = ["Database", "COLLECTIONS"]

from motor.motor_asyncio import AsyncIOMotorClient

from .__base_config import MONGODB_URI

MONGO_DB_NAME = "invest"
COLLECTIONS = ["iol_mi_cuenta_estado", "users"]

# # Inicializar la conexión con MongoDB
# client = AsyncIOMotorClient(MONGODB_URI)
# db = client[MONGO_DB_NAME]

# # Send a ping to confirm a successful connection
# try:
#     client.admin.command("ping")
#     logger.info("Pinged your deployment. You successfully connected to MongoDB!")
# except Exception as e:
#     print(e)


# # Función para obtener la base de datos en servicios/repositorios
# def get_database():
#     return db


class Database:
    client = None
    db = None

    @classmethod
    def initialize(cls):
        cls.client = AsyncIOMotorClient(MONGODB_URI)
        cls.db = cls.client[MONGO_DB_NAME]


# Inicializar la base de datos antes de usarla
# try:
#     Database.initialize()
#     Database.client.admin.command("ping")
#     logger.info("Pinged your deployment. You successfully connected to MongoDB!")
# except Exception as e:
#     print(e)

# Database.initialize()
# collection = Database.db["users"]
