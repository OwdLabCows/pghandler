import sys
from typing import Dict, List, Union, Any
import psycopg2
from psycopg2 import extras
import getpass
import time
from traceback import print_exc, format_exc
from ._exceptions import *
from .query import Query
import enum




class ReturnType(enum.Enum):
    LIST = enum.auto()
    DICT = enum.auto()





class BoostType(enum.Enum):
    NORMAL = enum.auto()
    BATCH = enum.auto()
    VALUES = enum.auto()






class PGHandler():

    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        user: str = "admin",
        password: str = None,
        dbname: str = "admin",
        loop_mode: bool = False,
        connect_timeout: int = 15,
        print_debug: bool = True,
    ) -> None:
        """
        This class simplifies PostgreSQL operations and makes it easy to handle
        SQL operations.
        This designed for PostgreSQL mainly.
        The SQL operations that can be performed with this class are as
        follows.
        - connect to PostgreSQL easily
        - set SQL query and show current SQL query
        - execute SQL query in one line
        - get all columns in a table easily

        Parameters
        ----------
        host: str, optional
            database host address
            Default is 'localhost'.
        port: int, optional
            connection port number
            Default is 5432.
        user: str, optional
            user name used to authenticate
            Default is 'admin'.
        password: str, optional
            password used to authenticate
            If this is not provided, you type password in stdin.
            Default is `None`.
        dbname: str, optional
            the database name
            Default is 'admin'.
        loop_mode: bool, optional
            whether to keep trying to reconnect
            If `True` is set, reconnection is repeated.
            Default is `False`.
        connection_timeout: int, optional
            connection timeout seconds
            Default is 15.
        print_debug: int, optional
            whether to print out information in stdout
            If `True` is set, print out it.
            Default is `True`.
        """


        self.print_debug = print_debug

        # set password in STDIN if 'password' is not provided
        if password is None:
            password = getpass.getpass(prompt=f"{user}'s password is:")

        self.host = host
        self.port = port
        self.user = user

        # internal variables
        self.__query: Query = Query("")

        # connection attempt process
        # Recconect if necessary
        while True:

            try:
                self.__print("Connecting to SQL server...")
                try:
                    self.conn = psycopg2.connect(
                        database=dbname,
                        user=user,
                        password=password,
                        host=host,
                        port=str(port),
                        gssencmode="disable",
                        connect_timeout=connect_timeout
                    )

                # for versions where 'gssencmode' cannot be used
                except psycopg2.ProgrammingError:
                    self.conn = psycopg2.connect(
                        database=dbname,
                        user=user,
                        password=password,
                        host=host,
                        port=str(port),
                        connect_timeout=connect_timeout
                    )

                # unexpected error
                except Exception:
                    raise

                # set postgreSQL cursor
                self.cur = self.conn.cursor(cursor_factory=extras.DictCursor)
                self.__print("Connected.")
                break

            # connection failure
            except psycopg2.OperationalError:
                print_exc()
                self.__print("An error occurred while connecting to the SQL server.")
                # reconnect if necessary
                if loop_mode:
                    self.__print("Reconnect after five seconds.")
                    time.sleep(5)
                    continue
                retry_cmd = ""
                while True:
                    retry_cmd = input("Do you want to reconnect to the server? [y/N]")
                    if retry_cmd not in ['y', 'Y', 'n', 'N', '']:
                        print("Type 'y', 'Y', 'n' or 'N'.")
                    else:
                        break
                if retry_cmd in ['', 'n', 'N']:
                    break

            # unexpected error
            except Exception:
                raise



    def __enter__(
        self
    ):

        return self



    def __exit__(
        self
    ) -> None:

        try:
            self.close()
        except Exception as e:
            ExitFailedError(f"{e}\n{format_exc()}")



    # internal print function
    def __print(
        self,
        *object,
        sep: str = ' ',
        file = sys.stdout,
        flush = False
    ) -> None:

        if self.print_debug:
            print(
                object,
                sep=sep,
                file=file,
                flush=flush
            )



    # close PostgreSQL database connection
    def close(
        self
    ) -> None:
        """
        Close the connection.
        This doesn't handle errors that occur when close the connection.

        Parameter
        ---------
        None
        """

        self.cur.close()
        self.conn.close()


    # get all columns in a table
    def get_columns(
        self,
        table_name: str
    ) -> List[str]:
        """
        Get all columns in a table in order by ordinal_position.
        This doesn't handle errors that occur when acquiring the columns.

        Parameter
        ---------
        table_name: str
            table name
        """

        columns = []

        self.__print("Getting columns...")
        # query to get all columns
        query = f"select column_name from information_schema.columns where table_name='{table_name}' order by ordinal_position;"

        self.set_query(query)
        self.execute_query()

        for row in self.cur:
            for c in row:
                columns.append(c)

        return columns



    def set_query(
        self,
        query: str
    ) -> None:
        """
        Set a SQL query

        Parameter
        ---------
        query: str
        SQL query
        """

        self.__query = Query(query)



    def get_current_query(
        self
    ) -> str:
        """
        Get the current SQL query
        """

        return self.__query.sql



    def execute_query(
        self,
        query: Union[str, None] = None,
        fetch_all: bool = False,
        commit: bool = False,
        return_type: ReturnType = ReturnType.LIST,
        boost_type: BoostType = BoostType.NORMAL,
        param_list: Union[None, List[str]] = None
    ) -> Union[None, List[Union[Dict[Any, Any], List[Any]]]]:
        """
        Execute a SQL query

        Parameter
        ---------
        query: str or None, optional
        the query you want to execute
        If you have set current query by 'set_query()',
        this overwrites the query and executes it.
        Default is None
        fetch_all: bool, optinal
        whether fetch all response or not
        If True is set, list object of List[obj] is returned
        Default is False
        commit: bool, optional
        whether the current query needs to be committed
        Default is False
        return_type: ReturnType, optional
        which type of list object to return
        If ReturnType.DICT is set, return list object of dict
        which has columns as key and data as value.
        If ReturnType.LIST is set, return list object of list.
        Default is ReturnType.LIST.
        boost_type: BoostType, optional
        type of performance of execution
        - BoostType.NORMAL: normal performance
        - BoostType.BATCH: speed up the repeated execution of a
        statement against a set of parameters.
        - BoostTYpe.VALUES: speed up the execution by statement
        using VLUES with a sequence of parameters.
        If you use BoostType.BATCH or BoostType.VALUES, you have
        to set valid parameter on param_list and query must
        contain `%s` placeholder that will be replaced by
        param_list.
        Default is BoostType.NORMAL.
        param_list: list, optional
        paramters will repace placeholder that query contain if
        BoostType.VALUES or BoostType.BATCH is set on boost_type
        Default is None.

        Returns
        -------
        reponse: None or list
        fetched data or None
        If True is set on fetch_all and the response unfetched is
        empty, empty list is returned, and if False is set on
        fetch_all, None is returned.
        If ReturnType.DICT is set on return_type,
        return list object of dict which has columns
        as key and data as value.
        If ReturnType.LIST is set, return list
        object of list.
        """

        if query is not None:
            self.set_query(query)

        self.__print(f"execute `{self.__query.sql}`")
        if self.__query.sql == "":
            raise InvalidSQLQueryError("Current SQL query is empty.")
        if boost_type == BoostType.BATCH or boost_type == BoostType.VALUES:
            try:
                extras.execute_values(self.cur, self.__query.sql, param_list)
            except ValueError:
                raise BoostModeError(boost_type.name)
        elif boost_type == BoostType.NORMAL:
            self.cur.execute(self.__query.sql)
        else:
            if type(boost_type) == BoostType:
                raise RuntimeError(f"Unspported Boost Type. {boost_type.name}")
            else:
                raise ValueError("boost_type is not BoostType")
        self.__query.excuted()
        if commit:
            self.conn.commit()
        self.__print(f"status: `{self.get_status()}`")

        if fetch_all:
            return self.fetch(return_type=return_type)
        else:
            return None



    def fetch(
        self,
        rows: Union[None, int] = None,
        return_type: ReturnType = ReturnType.LIST
    ) -> List[Union[Dict[Any, Any], List[Any]]]:
        """
        Get the response
        If the response is empty, None is returned.

        Parameters
        ----------
        rows: None or int, optional
        the number of rows you want to fetch
        If None is set, this fetch all rows as
        possible.
        Default is None
        return_type: ReturnType, optional
        which type of list object to return
        If ReturnType.DICT is set, return list
        object of dict which has columns as
        key and data as value.
        If ReturnType.LIST is set, return list
        object of list.
        Default is ReturnType.LIST.

        Returns
        -------
        response: None or list
        if the response unfetched is empty, empty
        list is returned
        If ReturnType.DICT is set on return_type,
        return list object of dict which has columns
        as key and data as value.
        If ReturnType.LIST is set, return list
        object of list.
        """

        response: List[Any] = []

        if rows is None:
            for r in self.cur:
                if return_type == ReturnType.LIST:
                    response.append(list(r))
                elif return_type == ReturnType.DICT:
                    response.append(dict(r))
                else:
                    if type(return_type) == ReturnType:
                        raise RuntimeError(f"Unspported Return Type {return_type.name}")
                    else:
                        raise ValueError(f"return_type is not ReturnType.")
        else:
            for cnt, r in enumerate(self.cur, start=1):
                if cnt > rows:
                    break
                if return_type == ReturnType.LIST:
                    response.append(list(r))
                elif return_type == ReturnType.DICT:
                    response.append(dict(r))

        return response






    def get_last_query_exuted(
        self,
    ) -> str:
        """
        Get the last query excuted.

        Returns
        -------
        last_query
        the last query excuted
        """
        last_query = self.cur.query
        return last_query



    def get_status(
        self,
    ) -> str:
        """
        Get the message returned by the last query excuted.

        Returns
        -------
        status: str
        the status message returned by the last query excuted
        """
        status: str = self.cur.statusmessage
        return status



    def current_query_is_excuted(
        self
    ) -> bool:
        """
        get bool whether the current query has be excuted or
        not.
        If it has be excuted, True is returned

        Returns
        -------
        is_excuted: bool
        bool whether the current query has be excuted
        If it has be excuted, True is returned
        """

        is_excuted = self.__query.is_excuted
        return is_excuted



    def response_is_empty(
        self,
    ) -> bool:
        """
        Get bool whether the current cursor response is empty
        or not.
        If it is empty, True is returned

        Returns
        -------
        is_empty: bool
        If the current cursor response is empty, True is returned
        """
        is_empty: bool = False
        if self.cur.rownumber == 0:
            is_empty = True

        return is_empty



    def all_are_fetched(
        self,
    ) -> bool:
        """
        Get bool whether the current cursor responses are fetched
        or not.
        If these are fetched, True is returned

        Returns
        -------
        are_fetched: bool
        If the current cursor responses are fetched, True is returned
        """

        are_fetched = False
        if self.cur.rownumber == self.cur.rowcount:
            are_fetched = True

        return are_fetched



    def get_unfetched_num(
        self,
    ) -> int:
        """
        Get the number of rows are unfetched

        Returns
        -------
        rows: int
        the number of rows are unfetched
        """

        rows = self.cur.rowcount - self.cur.rownumber
        return rows