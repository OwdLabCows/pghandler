class PGHandlerException(Exception):
    """
    Handle errors that occurred in SQLHander
    """

    def __init__(self, *args: object) -> None:
        self.args = args



class InvalidSQLQueryError(PGHandlerException):

    def __str__(self):
        return (
            f"query is invalid: {self.args}"
        )



class ExitFailedError(PGHandlerException):

    def __str__(self):
        return (
            """Exit process failed. Details are as follows.
{}""".format(self.args)
        )



class BoostModeError(PGHandlerException):

    def __str__(self):
        return (
            f"BoostType {self.args} is set but the query doesn't contain any '%s' placeholder"
        )
