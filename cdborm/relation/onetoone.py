from cdborm.errors import BadType
from cdborm.relation.relation import Relation


class OneToOne(Relation):

    def assign(self, obj):
        cls = self.related_class
        if type(obj) == cls:
            self._to_assign = [obj]
            self.release()
        else:
            raise BadType()

    def release(self):
        self._to_release = True

    def __call__(self, database=None):
        data = super(OneToOne, self).__call__(database)
        if len(data) == 0:
            return None
        else:
            return data[0]

    def _remove_released_links(self, database, elements):
        if self._to_release == True:
            for element in elements:
                database.delete(element['doc'])
            if len(self._to_assign) > 0:
                for element in self._get_all_db_elements(database, self._to_assign[0].id):
                    database.delete(element['doc'])
