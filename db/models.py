'''
    db.models
    Ron Kuslak 2018

    Defines basic model objects for interaction in a general manner
    across DB engines.
'''

class dbmodel(object):
    def escapedname(self):
        ''' Returns a escaped-version of the object name. '''
        return "[" + self.name + "]"

class database(dbmodel):
    ''' Container object for Database information: '''
    def __init__(self, database, tables=None):
        self.name = database
        self.tables = tables
        self.active = True


class table(dbmodel):
    ''' Container object for Table information: '''
    def __init__(self, name, schema="dbo", columns=None):
        self.name = name
        self.schema = schema
        self.columns = columns
        self.active = True

    def escapedname(self):
        ''' Returns a escaped-version of the object name. '''
        return "[" + self.schema + "].[" + self.name + "]"


class column(dbmodel):
    ''' Container object for Column information: '''
    def __init__(self, name, nullable, sqltype):
        self.name = name
        self.nullable = nullable
        self.sqltype = sqltype
        self.active = True


if __name__ == "__main__":
    test = database("Test")
    print(test.escapedname())
