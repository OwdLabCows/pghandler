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



@pytest.mark.parametrize(('name'), ['foo', 'bar'])
def test_insert_second_time(docker_postgres, name):
    # insert comment to each tables
    comment = f"I am {name} from test_basic_sql_query()."
    docker_postgres.set_query(f"insert into test_basic_sql_query_{name} (comment) values ('{comment}');")
    docker_postgres.execute_query(commit=True)

    # select comment from the table
    res = docker_postgres.execute_query(query=f"select comment from test_basic_sql_query_{name};", fetch_all=True)[0][0]
    assert comment == res

    docker_postgres.close()



def test_empty(docker_postgres):

    docker_postgres.set_query("select comment from table4test_empty;")
    docker_postgres.execute_query(commit=True)

    # check 'response_is_empty'
    assert docker_postgres.response_is_empty()



def test_unfetched_n(docker_postgres):

    comment = "fooooooooooooooooo"
    comments = ','.join([f'(\'{comment}\')' for _ in range(120)])
    docker_postgres.set_query(f"insert into test_basic_sql_query_foo (comment) values {comments};")
    docker_postgres.execute_query(commit=True)
    docker_postgres.execute_query(query=f"select comment from test_basic_sql_query_foo;")

    assert len(docker_postgres.fetch(rows=32)) == 32

    assert docker_postgres.get_unfetched_num() == (120 - 32)



def test_values_boost_error(docker_postgres):

    comment = "baaaaaaaaaaaaaaaar"
    comments_list = [[comment] for _ in range(120)]
    docker_postgres.set_query(f"insert into test_basic_sql_query_bar (comment) values %s;")
    docker_postgres.execute_query(commit=True, return_type=ReturnType.DICT, boost_type=BoostType.VALUES, param_list=comments_list)
    docker_postgres.execute_query(query=f"select comment from test_basic_sql_query_bar;")

    assert len(docker_postgres.fetch(rows=32)) == 32

    assert docker_postgres.get_unfetched_num() == (120 - 32)



def test_return_type_dict(docker_postgres):
    comment = "where is my mind"
    comments_list = [[comment]]
    docker_postgres.set_query(f"insert into test_returntype_dict (comment) values %s;")
    docker_postgres.execute_query(commit=True, boost_type=BoostType.VALUES, param_list=comments_list)
    res = docker_postgres.execute_query(query=f"select comment from test_returntype_dict;", fetch_all=True, return_type=ReturnType.DICT)[0]["comment"]
    assert res == comment
