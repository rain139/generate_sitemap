import mysql.connector
from generator.Helpers import env,send_telegram


class Db:
    __instance = None

    def __init__(self):
        if not self.__instance:
            Db.__instance = Db.__Mysql().connect()

    def connect(self) -> mysql:
        return Db.__instance

    class __Mysql:
        def connect(self):
            try:
                return mysql.connector.connect(host=env('DB_HOST'), database=env('DB_DATABASE'), user=env('DB_USERNAME'),
                                           password=env('DB_PASSWORD'))
            except:
                send_telegram('Error connect')
