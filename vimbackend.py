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


class vimbackend(object):
    ''' Logic for Vim-SQL to deal with Vim buffers '''

    VIM_SQL_CONNECTIONS = {}
    VIM_SQL_LIST_BUFFERS = {}
    VIM_SQL_RESULTS_BUFFERS = {}


    @staticmethod
    def getconfigvar(var):
        ''' Searches the Vim variables for first the buffer, then global, for
            passed variable name. Returns None if not found.
        '''
        return vim.current.buffer.vars.get(var) or vim.vars.get(var) or None


    @staticmethod
    def get_dblist_buffer(bufn):
        ''' Returns the database list for a buffer passed, if a editor window, or
            for the connection if passed a list or results buffer
        '''
        if bufn in VIM_SQL_CONNECTIONS.keys():
            return VIM_SQL_CONNECTIONS[bufn]

        if bufn in VIM_SQL_LIST_BUFFERS.values():
            return bufn

        if bufn in VIM_SQL_RESULTS_BUFFERS.values():
            # It is a results buffer, find the parent buffer and return list buffer
            # if it exists:
            for key in VIM_SQL_RESULTS_BUFFERS.keys():
                if VIM_SQL_RESULTS_BUFFERS[key] == bufn:
                    return getlistbufferforbuffer(key)

        return None

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
    def updated_database_list(databases):
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
            return "* "

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
    def get_current_buffer_connection():
        ''' Returns a db.sqlRunner object for the current buffer '''
        buffer = vim.current.buffer

        # Attempt to find a conncetion for this buffer in the global cache:
        if buffer.number not in VIM_SQL_CONNECTIONS.keys():
            connection = db.mssql.sqlrunner(server, database, username,
                                            password)
            VIM_SQL_CONNECTIONS[buffer.number] = connection

        connection = VIM_SQL_CONNECTIONS[buffer.number]
        connection.server = getconfigvar("vim_sql_server")
        connection.database = getconfigvar("vim_sql_database")
        connection.username = getconfigvar("vim_sql_username")
        connection.password = getconfigvar("vim_sql_password")
        return connection

    @staticmethod
    def show_database_list():
        ''' Sets (or creates if non-existant) the contents of the database list
            buffer for the currently selected buffer to the values held in a
            query against the database.
        '''
        connection = vimbackend.get_current_buffer_connection()

        databases = connection.getdatabases()
        print(vimbackend.formatdatabaselist(databases))


