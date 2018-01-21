'''
    Vim Backend
    Copyright 2018 Ron Kuslak, All Rights Reserved.

    Provide backend helper functions for creating and displaying buffers of
    information on SQL connections.

    Intended to be used with models returned from the vim_sql.models class.
'''
# import vim


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


def getscratchbuffer(parentname):
    ''' Returns the buffer object for the buffer named "parentname" or None if
        no such buffer exists.
    '''
    for buffer in vim.buffers:
        if buffer.name == "results_" + parentname:
            return buffer

    return None


def isactive(state):
    ''' Returns formatted string based on if passed state is active or not '''
    if state:
        return "↘ "
    return "  "


def formatdatabaselist(databases):
    ''' Takes passed list of db.models objects and creates a plesant textual
        view of them.
    '''
    results = ""
    # Indent 0
    for database in databases:
        # results += database["database"] + '\n'
        results += isactive(database.active) + database.name + "\n"
        if database.active:
            # Display table records:
            for table in database.tables:
                results += "  " + isactive(table.active) + table.name + "\n"
                if table.active:
                    for column in table.columns:
                        results += "      {} [{}]\n".format(column.name,
                                                            column.sqltype)

    return results
