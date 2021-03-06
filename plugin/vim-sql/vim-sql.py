'''
    Vim Backend
    Copyright 2018 Ron Kuslak, All Rights Reserved.

    Provide backend helper functions for creating and displaying buffers of
    information on SQL connections.

    Intended to be used with models returned from the vim_sql.models class.

    TODO: Convert to a class to keep things out of the global namespace.
'''
# TODO: Everything in here is scoped to module, no need to namespace to
# class any more. Move out of class and into module namespace.
import db.models
import db.mssql
import vim


class vimsql(object):

    # XXX: No longer globals. Reformat you fool!
    # Should probably hook the calling buffers for close, so we can release
    # these once the buffers are gone.
    ServerResultCaches = {}
    LIST_BUFFERS = {}
    RESULTS_BUFFERS = {}

    ResultsBuff = None
    DBListBuff = None

    @staticmethod
    def style_current_buffer():
        style_cmds = [
            # Syntax Highlighting:
            r'syn clear',
            r'syntax match DBName /^\* \zs.*\ze$/',
            r'syntax match SchemaName /- \[\zs[^\.\]]*\ze]/',
            r'syntax match TableName /\.\[\zs[^\]]*\ze\]$/',
            r'syntax match SqlType /(\zs.*\ze)/',
            r'syntax match ColumnName /> \zs\w*\ze/',
            r'highlight def link DBName Statement',
            r'highlight def link SchemaName Constant',
            r'highlight def link TableName Constant',
            r'highlight def link ColumnName Type',
            r'highlight def link SqlType Comment'
            # Set state for UI on buffer:
        ]

        vim.command("setlocal buftype=nofile")
        vim.command("setlocal bufhidden=hide")
        vim.command("setlocal noswapfile")
        vim.command("setlocal shiftwidth=2")
        # vim.command("setlocal nonumbers")
        # vim.command("setlocal norelativenumbers")

        # Add syntax highlighting:
        if vim.current.buffer.number == vimsql.DBListBuff:
            for cmd in style_cmds:
                vim.command(cmd)

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
        '''
        # TODO: Make width configurable?
        width = 30

        if not vimsql.DBListBuff:
            vim.command("topleft vertical {} new".format(width))
            vim.command("edit VimSqlServerList")
            vimsql.DBListBuff = vim.current.buffer.number

            vimsql.style_current_buffer()
        else:
            if not vimsql.get_buffer(vimsql.DBListBuff):
                # We set the buffer, but it is no longer in existance.
                # Recreate the buffer and return.
                vimsql.DBListBuff = None
                vimsql.show_dblist_window()
                return
            windowid = vim.eval("bufwinnr(" + str(vimsql.DBListBuff) + ")")
            if windowid == "-1":
                # Buffer exists, but is not shown on this tab. Fix that...
                vim.command("topleft vertical " + str(width) + " vsplit")
                vim.command("b " + str(vimsql.DBListBuff))
            else:
                # Buffer is show, go to that window
                vim.command(windowid + "wincmd w")

    @staticmethod
    def show_results_window():
        ''' . '''
        # TODO: Make height configurable?
        height = 15

        if not vimsql.ResultsBuff:
            vim.command("botright {}new VimSqlResults".format(height))
            vimsql.ResultsBuff = vim.current.buffer.number

            vimsql.style_current_buffer()
        else:
            if not vimsql.get_buffer(vimsql.ResultsBuff):
                # We set the buffer, but it is no longer in existance.
                # Recreate the buffer and return.
                vimsql.ResultsBuff = None
                vimsql.show_results_window()
                return
            if vim.eval("bufwinnr(" + str(vimsql.ResultsBuff) + ")") == "-1":
                # Buffer exists, but is not shown on this tab. Fix that...
                vim.command("botright {}split ".format(height))
                vim.command("b " + str(vimsql.ResultsBuff))

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
                results += ' > Tables:\n'
                for table in database.tables:
                    results += "  - {}\n".format(table.escapedname())
                    if table.active and table.columns:
                        for col in table.columns:
                            results += "    > {0} ({1})\n".format(col.name,
                                                                  col.sqltype)
                # Display view records
                for view in database.views:
                    results += "  - {}\n".format(view.escapedname())
                    if view.active and view.columns:
                        for col in view.columns:
                            results += "    > {0} ({1})\n".format(col.name,
                                                                  col.sqltype)

        return results

    @staticmethod
    def get_connection():
        ''' Returns db.sqlRunner object for current buffer. '''
        connection = db.mssql.sqlrunner()
        connection.server = vimsql.get_vim_variable("vim_sql_server")
        connection.database = vimsql.get_vim_variable("vim_sql_database")
        connection.username = vimsql.get_vim_variable("vim_sql_username")
        connection.password = vimsql.get_vim_variable("vim_sql_password")

        return connection

    @staticmethod
    def get_buffer(buffnbr):
        ''' Returns a buffer object for the numbered buffer passed, or None if
            it does not exist.
        '''
        # Ensure we are searching for what we're getting:
        buffer_number = int(buffnbr)

        for buffer in vim.buffers:
            if buffer.number == buffer_number:
                return buffer
        return None

    @staticmethod
    def reload_database_cache():
        ''' Sets (or creates if non-existant) the contents of the database list
            buffer for the currently selected buffer to the values held in a
            query against the database.
        '''
        connection = vimsql.get_connection()
        databases = connection.getdatabases()

        # Cache the results so we can use it for completion:
        vimsql.ServerResultCaches[vim.current.buffer.number] = databases

    def show_database_list():
        current_buffer = vim.current.buffer.number
        vimsql.reload_database_cache()

        vimsql.show_dblist_window()
        databases = vimsql.ServerResultCaches[current_buffer]
        listbuff = vimsql.get_buffer(vimsql.DBListBuff)
        listbuff[:] = vimsql.get_formated_database_list(databases).split("\n")

    # TODO: This doesn't appear to do what the docstring says. Refactor?
    @staticmethod
    def get_dblist_buffer(parentbuff):
        ''' Returns the database list for a buffer passed, if a editor window,
            or for the connection if passed a list or results buffer
        '''
        if parentbuff in vimsql.LIST_BUFFERS.values():
            return parentbuff

        if parentbuff in vimsql.RESULTS_BUFFERS.values():
            # It is a results buffer, find the parent buffer and return list
            # buffer if it exists:
            for key in vimsql.RESULTS_BUFFERS.keys():
                if vimsql.RESULTS_BUFFERS[key] == parentbuff:
                    return vimsql.get_dblist_buffer(key)

        return None

    @staticmethod
    def execute_buffer():
        ''' Treat contents of current buffer as query, and print the results
            to the result buffer
        '''
        results = []

        query = '\n'.join(vim.current.buffer[:])
        connection = vimsql.get_connection()

        vimsql.show_results_window()
        buffer = vimsql.get_buffer(vimsql.ResultsBuff)
        # buffer[:] = ['']
        buffer.append('')

        try:
            results = connection.execute(query)
        except db.models.QueryException as ex:
            buffer.append(str(ex))
            return

        for resultset in results:
            # We have a list of dictonarys; iterate through and add to buffer:
            # if isinstance(resultset, int):
            if resultset[0] == db.models.ResultType.ROWS_AFFECTED:
                # Results is a array; it is the number of rows affected
                buffer.append('{} rows affected.'.format(resultset[1]))
            if resultset[0] == db.models.ResultType.TABLE:
            # else:
                # Results are a dictonary; this is a query result
                # Create a dictonary of row sizes:
                columnsizes = {}
                for row in resultset[1]:
                    for key in row.keys():
                        columnsizes[key] = len(str(key))
                    for key in row.keys():
                        columnsize = len(str(row[key]))
                        if columnsize > columnsizes[key]:
                            columnsizes[key] = columnsize

                # Make column header:
                headersize = sum(columnsizes.values())
                headersize += len(columnsizes.values()) * 3

                headerframe = ' +'
                columnnameline = ' | '
                # Add header sizes to columnsizes dictonary, and then
                # build our table:
                for key in columnsizes.keys():
                    if len(str(key)) > columnsizes[key]:
                        columnsizes[key] = len(str(key))
                    columnsize = columnsizes[key] + 2
                    headerframe += ('-' * columnsize) + '+'
                    columnnameline += str(key).center(columnsizes[key]) + ' | '
                buffer.append(headerframe)
                buffer.append(columnnameline)
                buffer.append(headerframe)

                # Show results:
                for row in resultset[1]:
                    bufferline = ' | '
                    for key in row.keys():
                        bufferline += str(row[key]).ljust(columnsizes[key])
                        bufferline += ' | '
                    buffer.append(bufferline)
                buffer.append([headerframe, ''])
