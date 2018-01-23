#!/usr/bin/python3
'''
    TDS Talker
    Copyright 2018 Ron Kuslak, All Rights Reserved.

    A Python program to talk to a described Microsoft SQL Server, at least 2008
    or higher.

    TODO: Parameterize the calls in the database/table/column functions to
        avoid injection. Ex:

        SET @TableID INT = OBJECT_ID(Table)
        SET @Query VARCHAR(MAX) =  'SELECT FOO FROM ' + OBJECT_NAME(@TableID)
    TODO: All the exception handling!
'''
import pytds
from . import models

# List of "system" tables that may not be useful to include:
_SYSTEM_TABLES = ["master", "tempdb", "model", "msdb"]


class sqlrunner(object):
    def __init__(self, server=None, database=None, username=None,
                 password=None):
        ''' Initializes class

            @server = URL for server to connect to
            @database = Database on server to default to for queries
            @username = username to use during connection
            @password = password for username
# TODO:
            @intergrated_sec = Use integrated security (on supported platforms)
        '''
        self.buffer = None

        self.server = server
        self.database = database
        self.username = username
        self.password = password

    def connect(self):
        ''' Connects to the server set via class variables '''
        sql = pytds.connect(database=self.database or "master",
                            server=self.server, user=self.username,
                            password=self.password, as_dict=True)

        return sql

    def execute(self, query):
        ''' Executes passsed query after spliting into batches and returns
            list of dictonaries  of results.
        '''
        results = None

        with self.connect() as sql:
            with sql.cursor() as cursor:
                # XXX: Break passed query into batches, and store results
                #      in return valaue
                cursor.execute(query)

                results = cursor.fetchall()

        return results

    def getdatabases(self, include_system=False):
        ''' Returns a array of database names from currently described server.
        '''
        results = []
        databases = []

        with self.connect() as sql:
            with sql.cursor() as cursor:
                cursor.execute("SELECT name FROM sys.databases")
                for row in cursor.fetchall():
                    # TODO: There has to be a better, "cleaner" way to do this.
                    # Maybe use sys.objects? It's deprecated but still...
                    if include_system or row['name'] not in _SYSTEM_TABLES:
                        databases += [row["name"]]

                for database in databases:
                    results += [models.database(database,
                                                self.gettables(database))]

        return results

    def gettables(self, database):
        ''' Returns the tables with columns for database passed '''
        tables = []

        with self.connect() as sql:
            with sql.cursor() as cursor:
                cursor.execute("SELECT DB_NAME(3) AS dbname")

                cursor.execute("USE [" + database + "]")
                cursor.execute("SELECT TABLE_SCHEMA, TABLE_NAME FROM " +
                               "INFORMATION_SCHEMA.TABLES WHERE " +
                               "TABLE_TYPE = 'BASE TABLE'",
                               {"database": database})

                for table in cursor.fetchall():
                    tablename = table["TABLE_NAME"]
                    schema = table["TABLE_SCHEMA"]
                    columns = self.getcolumns(database, tablename, schema)
                    tables += [models.table(tablename, schema, columns)]

        return tables

    def getcolumns(self, database, table, schema):
        ''' Returns the columns for table within database passed '''
        columns = []

        with self.connect() as sql:
            with sql.cursor() as cursor:
                cursor.execute("USE [" + database + "]")
                cursor.execute("SELECT COLUMN_NAME AS [Column], "
                               "IS_NULLABLE AS [Nullable], "
                               "DATA_TYPE AS Datatype "
                               "FROM INFORMATION_SCHEMA.COLUMNS "
                               "WHERE TABLE_NAME LIKE @table AND "
                               "    TABLE_SCHEMA LIKE @schema",
                               {"table": table, "schema": schema})
                for row in cursor.fetchall():
                    columnname = row["Column"]
                    nullable = row["Nullable"] == 'YES'
                    sqltype = row["Datatype"]

                    columns += [models.column(columnname, nullable, sqltype)]

        return columns
