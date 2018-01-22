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

    ResultsBuff = None
    DBListBuff = None

    @staticmethod
    def get_vim_variable(var):
        ''' Returns the value of the passed name Vim variable from buffer
            scope, global scope, or None if it can not be found in either.

        '''
        result = vim.current.buffer.vars.get(var) or vim.vars.get(var) or None
        return result

    @staticmethod
    def show_dblist_window():
        ''' Create a Vim 'results' scratch buffer for the buffer named in
            parentname.

            if creating, use:
                :new
                :setlocal buftype=nofile
                :setlocal bufhidden=hide
                :setlocal noswapfile
                :autocmd BufEnter results_buffer_name stopinsert
        '''
        # TODO: Make this configurable?
        width = 30

        if not vimsql.DBListBuff:
            vim.command("topleft vertical " + str(width) + " new")
            vim.command("edit VimSqlServerList")
            vim.command("setlocal buftype=nofile")
            vim.command("setlocal bufhidden=hide")
            vim.command("setlocal noswapfile shiftwidth=2")
            vimsql.DBListBuff = vim.current.buffer.number
        else:
            if not vimsql.get_buffer(vimsql.DBListBuff):
                # We set the buffer, but it is no longer in existance.
                # Recreate the buffer and return.
                vimsql.DBListBuff = None
                vimsql.show_dblist_window()
                return
            if vim.eval("bufwinnr(" + str(vimsql.DBListBuff) + ")") == "-1":
                # Buffer exists, but is not shown on this tab. Fix that...
                vim.command("topleft vertical " + str(width) + " vsplit")
                vim.command("b " + str(vimsql.DBListBuff))

            print(vim.eval("bufwinnr(" + str(vimsql.DBListBuff) + ")"))

    def show_results_window():
        height = 10

        if not vimsql.ResultsBuff:
            parentbuff = vim.current.buffer.number
            vim.exec("belowright " + height + " new")
            vim.exec("edit VimSqlResults" + parentbuff)
            vimsql.ResultsBuff = vim.current.buffer.number
        else:
            vim.exec("belowright " + height + " split")
            vim.exec("b " + vimsql.ResultsBuff)

    @staticmethod
    def get_formated_database_list(databases):
        ''' Takes passed list of db.models objects and creates a plesant
            textual view of them.
        '''
        results = ""

        for database in databases:
            results += "* {}\n".format(database.name)
            if database.active:
                # Display table records:
                for table in database.tables:
                    results += "  - {}\n".format(table.name)
                    if table.active:
                        for column in table.columns:
                            results += "    {} [{}]\n".format(column.name,
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
        connection.server = vimsql.get_vim_variable("vim_sql_server")
        connection.database = vimsql.get_vim_variable("vim_sql_database")
        connection.username = vimsql.get_vim_variable("vim_sql_username")
        connection.password = vimsql.get_vim_variable("vim_sql_password")

        return connection

    @staticmethod
    def get_buffer(buffnbr):
        for buffer in vim.buffers:
            if buffer.number == buffnbr:
                return buffer
        return None

    @staticmethod
    def show_database_list():
        ''' Sets (or creates if non-existant) the contents of the database list
            buffer for the currently selected buffer to the values held in a
            query against the database.
        '''
        # TODO: Need to see if already shown and reuse tab.
        vimsql.show_dblist_window()
        connection = vimsql.get_connection()
        databases = connection.getdatabases()

        listbuff = vimsql.get_buffer(vimsql.DBListBuff)
        listbuff[:] = vimsql.get_formated_database_list(databases).split("\n")

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
