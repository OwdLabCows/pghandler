class Query():

    def __init__(
        self,
        sql: str
    ) -> None:
        self.sql = sql
        self.is_excuted = False



    def excuted(
        self
    ) -> None:
        self.is_excuted = True