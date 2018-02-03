#!/usr/bin/python3
'''
    TDS Talker
    Copyright 2018 Ron Kuslak, All Rights Reserved.

    A Python program to talk to a described Microsoft SQL Server, at least 2008
    or higher.

    TODO: All the exception handling!
    TODO: Print statements in query currently unhandled.
    TODO: Dropping tables/databases does not work as expected, or at all.
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

    def connect(self, database=None):
        ''' Connects to the server set via class variables '''
        db = database or self.database or "master"
        sql = pytds.connect(database=db, server=self.server,
                            user=self.username, password=self.password,
                            as_dict=True)

        return sql

    def execute(self, query, params=None, database=None,
                persistdatabase=False):
        ''' Executes passsed query after spliting into batches and returns
            list of dictonaries  of results.

            @query: String of the query to run
            @params: Query variables to replace in query in the form of a
                dict formated "@var_name": "value"
            @database: database, other than class global, to connect to
            @persistdatabase: wether to persist current database after query
                as class global database after query execution.
        '''
        results = []

        with self.connect(database=database) as sql:
            try:
                cursor = sql.cursor()
            except Exception as ex:
                sql.close()
                raise models.SqlExeception

            try:
                # XXX: Break passed query into batches, and store results
                #      in return valaue
                if params:
                    cursor.execute(query, params=params)
                else:
                    cursor.execute(query)

                # TODO: Result type indicators should really be some sort
                #   of descriptive object from db.models or something.
                while results == [] or cursor.nextset():

                    if cursor.rowcount == -1:
                        # results += [cursor.fetchall()]
                        table = []
                        result = cursor.fetchone()
                        while result:
                            table += [result]
                            result = cursor.fetchone()
                        if table:
                            results += [[models.ResultType.TABLE, table]]
                    else:
                        # results += [cursor.rowcount]
                        results += [[models.ResultType.ROWS_AFFECTED,
                                     cursor.rowcount]]


                sql.commit()

                if persistdatabase:
                    # TODO: This would be nice to have. Please add.
                    currentdatabase = cursor.execute("SELECT DB_NAME()")

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

        queryresults = self.execute("SELECT name FROM sys.databases",
                                    database='master')
        for result in queryresults:
            if result[0] == models.ResultType.TABLE:
                for row in result[1]:
            # if queryresults[0][0] == models.ResultType.TABLE:
            #     for row in queryresults[0]:
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
        for result in queryresults:
            if result[0] == models.ResultType.TABLE:
                for table in result[1]:
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
        # for view in queryresults:
        #     if isinstance(view, dict):
        for result in queryresults:
            if result[0] == models.ResultType.TABLE:
                for view in result[1]:
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
        queryresults = self.execute(query=query, params=params,
                                    database=database)
        for result in queryresults:
            if result[0] == models.ResultType.TABLE:
                # for row in results[0]:
                for row in result[1]:
                    columnname = row["Column"]
                    nullable = row["Nullable"] == 'YES'
                    sqltype = row["Datatype"]
                    columns += [models.column(columnname, nullable, sqltype)]


        return columns
