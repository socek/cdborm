from cdborm.errors import BadType


class Relation(object):

    def __init__(self, class_name, index_name):
        self.parent = None
        self.value = None
        self.class_name = class_name
        self.index_name = index_name
        self._to_assign = []
        self._to_release = []

    def assign(self, obj):
        cls = self.related_class
        if type(obj) == cls:
            self._to_assign.append(obj)
        else:
            raise BadType()

    def release(self, obj):
        self._to_release.append(obj)

    @property
    def related_class(self):
        return self.parent.get_class_by_name(self.class_name)

    def _get_all_db_elements(self, db):
        for element in db.get_many(self.index_name, self.parent.id, with_doc=True):
            print element
        return [element for element in db.get_many(self.index_name, self.parent.id, with_doc=True)]

    def _get_linked_object_from_database(self, database):
        elements = self._get_all_db_elements(database)
        data = []
        for element in elements:
            data.append(
                self.related_class.get(element['doc'][self.class_name])
            )
        return data

    def __call__(self, database=None):
        db = self.parent._get_database(database)
        return self._get_linked_object_from_database(db)

    def _link_data(self, obj):
        return {
            self.parent._get_full_class_name(): self.parent.id,
            self.related_class._get_full_class_name(): obj.id,
            '_type': 'relation link',
        }

    def _remove_released_links(self, database, elements):
        if self._to_release == True:
            for element in elements:
                database.delete(element['doc'])
        else:
            for obj in self._to_release:
                doc = self.doc_of_obj_already_assigned(obj, elements)
                if doc:
                    database.delete(doc)

    def doc_of_obj_already_assigned(self, obj, elements):
        try:
            for element in elements:
                if element['doc'][self.related_class._get_full_class_name()] == obj.id:
                    return element['doc']
        except KeyError:
            pass
        return False

    def _on_save(self, database):
        def save_assigned_links(database, elements):
            for obj in self._to_assign:
                if self.doc_of_obj_already_assigned(obj, elements):
                    return
                else:
                    data = self._link_data(obj)
                    data = database.insert(data)
            self._to_assign = []

        #-----------------------------------------------------------------------
        elements = self._get_all_db_elements(database)
        save_assigned_links(database, elements)
        self._remove_released_links(database, elements)
