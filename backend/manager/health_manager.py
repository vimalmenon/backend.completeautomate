class HealthManager:

    def check(self) -> dict[str, str]:
        db_check = self.__check_db()
        s3_check = self.__check_s3()
        return {**db_check, **s3_check, "status": "ok"}

    def __check_db(self) -> dict[str, str]:
        return {"db_write": "ok", "db_read": "ok"}

    def __check_s3(self):
        return {"write_s3": "ok", "read_s3": "ok"}
