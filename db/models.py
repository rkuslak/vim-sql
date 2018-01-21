class database(object):
    ''' Container object for Database information: '''
    def __init__(self, database, tables=None):
        self.name = database
        self.tables = tables
        self.active = True


class table(object):
    ''' Container object for Table information: '''
    def __init__(self, name, columns=None):
        self.name = name
        self.columns = columns
        self.active = True


class column(object):
    ''' Container object for Column information: '''
    def __init__(self, name, nullable, sqltype):
        self.name = name
        self.nullable = nullable
        self.sqltype = sqltype
        self.active = True
