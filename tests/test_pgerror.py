import pytest
from pghandler import *
import os



@pytest.fixture
def docker_postgres():
    # prepare PGHandler of docker postgresql
    docker_pg = PGHandler(
        host=os.environ["DOCKER_HOSTIP"],
        port=5432,
        dbname="admin",
        password="admin"
    )

    return docker_pg



def test_values_boost_error(docker_postgres):

    comment = "baaaaaaaaaaaaaaaar"
    comments = ','.join([f'(\'{comment}\')' for _ in range(120)])
    docker_postgres.set_query(f"insert into test_basic_sql_query_bar (comment) values {comments};")
    docker_postgres.execute_query(commit=True)
    with pytest.raises(BoostModeError):
        docker_postgres.execute_query(query=f"select comment from test_basic_sql_query_bar;", return_type=ReturnType.DICT, boost_type=BoostType.VALUES)



def test_boost_type_value_error(docker_postgres):

    with pytest.raises(ValueError):
        docker_postgres.execute_query(query=f"select comment from test_basic_sql_query_bar;", boost_type=1)



def test_return_type_value_error(docker_postgres):

    with pytest.raises(ValueError):
        docker_postgres.execute_query(query=f"select comment from test_basic_sql_query_bar;", fetch_all=True, return_type=1, boost_type=BoostType.NORMAL)
