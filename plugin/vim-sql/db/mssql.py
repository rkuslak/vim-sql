#!/usr/bin/python3
'''
    TDS Talker
    Copyright 2018 Ron Kuslak, All Rights Reserved.

    A Python program to talk to a described Microsoft SQL Server, at least 2008
    or higher.

    TODO: Parameterize the call to set the database?
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

    def connect(self, connection_database = None):
        ''' Connects to the server set via class variables '''
        db = connection_database or self.database or "master"
        sql = pytds.connect(database=db, server=self.server,
                            user=self.username, password=self.password,
                            as_dict=True)

        return sql

    def execute(self, query, params=None, database=None):
        ''' Executes passsed query after spliting into batches and returns
            list of dictonaries  of results.
        '''
        results = []

        with self.connect() as sql:
            try:
                cursor = sql.cursor()
            except:
                sql.close()
                raise models.SqlExeception

            try:
                # Set database at start of query to passed database
                db = database or self.database or "master"
                cursor.execute("USE [" + db + "]")

                # XXX: Break passed query into batches, and store results
                #      in return valaue
                if (params):
                    cursor.execute(query, params=params)
                else:
                    cursor.execute(query)

                # TODO: Result type indicators should really be some sort
                #   of descriptive object from db.models or something.
                while results == [] or cursor.nextset():
                    if cursor.rowcount == -1:
                        # SELECT query, append results:
                        results += [cursor.fetchall()]
                    else:
                        results += [cursor.rowcount]
            # except Exception as ex:
            except pytds.tds_base.ProgrammingError as ex:
                raise models.QueryException("Query failed: {}".format(ex))
            finally:
                cursor.close()

        return results

    def getdatabases(self, include_system=False):
        ''' Returns a array of database names from currently described server.
        '''
        results = []
        databases = []

        queryresults = self.execute("SELECT name FROM sys.databases")
        for row in queryresults[0]:
            if include_system or row['name'] not in _SYSTEM_TABLES:
                databases += [row["name"]]

        for database in databases:
            tables = self.gettables(database)
            views = self.getviews(database)
            results += [models.database(database, tables, views)]

        return results

    def gettables(self, database):
        ''' Returns the tables with columns for database passed '''
        tables = []

        query = ("SELECT TABLE_SCHEMA, TABLE_NAME " +
                 "FROM INFORMATION_SCHEMA.TABLES " +
                 "WHERE TABLE_TYPE = 'BASE TABLE'")

        queryresults = self.execute(query=query, database=database)
        print(queryresults)
        for table in queryresults[0]:
            tablename = table["TABLE_NAME"]
            schema = table["TABLE_SCHEMA"]
            columns = self.getcolumns(database, tablename, schema)
            tables += [models.table(tablename, schema, columns)]

        return tables

    def getviews(self, database):
        ''' Returns the views with columns for database passed '''
        views = []

        query = ("SELECT TABLE_SCHEMA, TABLE_NAME " +
                 "FROM INFORMATION_SCHEMA.VIEWS ")

        queryresults = self.execute(query=query, database=database)
        print(queryresults)
        for view in queryresults[0]:
            viewname = view["TABLE_NAME"]
            schema = view["TABLE_SCHEMA"]
            columns = self.getcolumns(database, viewname, schema)
            views += [models.view(viewname, schema, columns)]

        return views

    def getcolumns(self, database, table, schema):
        ''' Returns the columns for table within database passed '''
        columns = []

        query = ("SELECT COLUMN_NAME AS [Column],"
                 "  IS_NULLABLE AS [Nullable],"
                 "  DATA_TYPE AS Datatype "
                 "FROM INFORMATION_SCHEMA.COLUMNS "
                 "WHERE TABLE_NAME LIKE @table AND "
                 "    TABLE_SCHEMA LIKE @schema")
        params = {"table": table, "schema": schema}
        results = self.execute(query=query, params=params,
                               database=database)
        for row in results[0]:
            columnname = row["Column"]
            nullable = row["Nullable"] == 'YES'
            sqltype = row["Datatype"]

            columns += [models.column(columnname, nullable, sqltype)]

        return columns
