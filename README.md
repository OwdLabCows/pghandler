# PGHandler

Simplify PostgreSQL operations and makes it easy to handle SQL operations.



## What PGHandler does


The SQL operations that can be performed with PGHandler are as follows.

- connect to PostgreSQL easily
- set SQL query and show current SQL query
- execute SQL query in one line
- get all columns in a table easily
- and more!

## Prerequisites

- Python 3.6.1 or above
- psycopg2 2.9.3 or above



## Installation

### Installing psycopg2

- Windows
- Linux (Debian or Ubuntu based distributions)
- Docker

#### Windows

```powershell
pip3 install psycopg2
```

or

```powershell
pip3 install -r requirements.txt
```

#### Linux (Debian or Ubuntu based distributions)

```sh
apt-get install libpq-dev
pip3 install psycopg2
```

or

```sh
apt-get install libpq-dev
pip3 install -r requirements.txt
```

#### Docker

```
git clone https://github.com/OwdLabCows/pghandler.git
docker build -t pghandler .
docker run -it --rm pghandler
```

## Usage

- clone pghandler into of your project folder or add pghandler as a git submodule

clone
```sh
git clone https://github.com/OwdLabCows/pghandler.git
```

git submodule
```sh
git submodule add https://github.com/OwdLabCows/pghandler.git
```

- To connect to PostgreSQL database

example
```python
my_postgres = PGHandler(
    host="192.168.1.10", # server ip
    port=5432,
    user="admin",
    dbname="admin",
    password="admin"
)
```

- To execute SQL operations

example
```python
my_postgres.execute_query(query="insert into table_foo (comment) values ('foo') ;", commit=True)

my_postgres.execute_query(
    query="insert into table_bar (col1, col2, col3) valuues %s", 
    commit=True, 
    boost_type=BoostType.VALUES,
    param_list=[
        ["value1 for col1", "value1 for col2", "value1 for col3"],
        ["value2 for col1", "value2 for col2", "value2 for col3"],
        ["value3 for col1", "value3 for col2", "value3 for col3"]
    ]
)
```
