'''
    Vim Backend
    Copyright 2018 Ron Kuslak, All Rights Reserved.

    Provide backend helper functions for creating and displaying buffers of
    information on SQL connections.

    Intended to be used with models returned from the vim_sql.models class.

    TODO: Convert to a class to keep things out of the global namespace.
'''
import db.mssql
import vim


class vimsql(object):

    # XXX: No longer globals. Reformat you fool!
    CONNECTIONS = {}
    LIST_BUFFERS = {}
    RESULTS_BUFFERS = {}

    @staticmethod
    def createscratchbuffer(parentname):
        ''' Create a Vim 'results' scratch buffer for the buffer named in
            parentname.

            if creating, use:
                :new
                :setlocal buftype=nofile
                :setlocal bufhidden=hide
                :setlocal noswapfile
                :autocmd BufEnter results_buffer_name stopinsert
        '''
        pass

    @staticmethod
    def get_formated_database_list(databases):
        ''' Takes passed list of db.models objects and creates a plesant
            textual view of them.
        '''
        results = ""

        def isactive(state):
            ''' Returns formatted string based on if passed state is active or
                not
            '''
            if state:
                return "- "
            return "  "

        for database in databases:
            results += isactive(database.active) + database.name + "\n"
            if database.active:
                # Display table records:
                for table in database.tables:
                    results += "  {}{}\n".format(isactive(table.active),
                                                 table.name)
                    if table.active:
                        for column in table.columns:
                            results += "      {} [{}]\n".format(column.name,
                                                                column.sqltype)

        return results

    @staticmethod
    def get_connection():
        ''' Returns db.sqlRunner object for current buffer. '''
        connection = None
        buffer = vim.current.buffer

        # Attempt to find a conncetion for this buffer in the global cache:
        if buffer.number not in vimsql.CONNECTIONS.keys():
            connection = db.mssql.sqlrunner()
            vimsql.CONNECTIONS[buffer.number] = connection

        connection = vimsql.CONNECTIONS[buffer.number]
        connection.server = vimsql.getconfigvar("vim_sql_server")
        connection.database = vimsql.getconfigvar("vim_sql_database")
        connection.username = vimsql.getconfigvar("vim_sql_username")
        connection.password = vimsql.getconfigvar("vim_sql_password")

        return connection

    @staticmethod
    def show_database_list():
        ''' Sets (or creates if non-existant) the contents of the database list
            buffer for the currently selected buffer to the values held in a
            query against the database.
        '''
        connection = vimsql.get_connection()
        databases = connection.getdatabases()
        print(vimsql.get_formated_database_list(databases))

    @staticmethod
    def get_dblist_buffer(parentbuff):
        ''' Returns the database list for a buffer passed, if a editor window, or
            for the connection if passed a list or results buffer
        '''
        if parentbuff in vimsql.CONNECTIONS.keys():
            return vimsql.CONNECTIONS[parentbuff]

        if parentbuff in vimsql.LIST_BUFFERS.values():
            return parentbuff

        if parentbuff in vimsql.RESULTS_BUFFERS.values():
            # It is a results buffer, find the parent buffer and return list
            # buffer if it exists:
            for key in vimsql.RESULTS_BUFFERS.keys():
                if vimsql.RESULTS_BUFFERS[key] == parentbuff:
                    return vimsql.get_dblist_buffer(key)

        return None
