from app.config import DB_USERNAME, DB_PASSWORD, DB_ALIAS, ORACLE_HOME
import oracledb

class DatabaseManager:

    def __init__(self, db_username, db_password, db_alias):

        oracledb.init_oracle_client(lib_dir=ORACLE_HOME)

        self.db_username = db_username
        self.db_password = db_password
        self.db_alias    = db_alias
        # commented out temporarily because we don't necessarily need to connect to a DB
        # self.connection  = oracledb.connect(user=self.db_username, password=self.db_password, dsn=self.db_alias)
        self.connection  = None

    def close(self):
        if self.connection:
            self.connection.close()
        self.connection = None

    def get_connection(self):
        # make sure the connection is open
        # if not self.connection:
        #     self.connection = oracledb.connect(user=self.db_username, password=self.db_password, dsn=self.db_alias)
        # return self.connection

        return None


database_manager = DatabaseManager(DB_USERNAME, DB_PASSWORD, DB_ALIAS)

async def get_db():
    return database_manager.get_connection()