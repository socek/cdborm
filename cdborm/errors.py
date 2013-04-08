class BadType(Exception): pass
class FieldCanNotBeNull(Exception): pass

class FieldValidationError(Exception):
    def __init__(self, model_name, field_name, error_message):
        self.model_name = model_name
        self.field_name = field_name
        self.error_message = error_message

    def __repr__(self):
        return u'Model: "%s" Field: "%s": %s' %(self.model_name,
                                                self.field_name,
                                                self.error_message)

class CanNotOverwriteRelationVariable(Exception): pass
class AlreadyAssigned(Exception): pass
class BadValueType(Exception): pass
class NoDbSelected(Exception): pass

from CodernityDB.database import RecordNotFound, RecordDeleted
