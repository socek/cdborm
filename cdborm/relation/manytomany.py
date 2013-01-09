from cdborm.errors import BadType
from cdborm.relation.relation import LocalRelation, ForeignRelation


class ManyToMany(LocalRelation):

    def _get_all_db_elements(self, db):
        return [element for element in db.get_many(self.index_name, self.parent.id, with_doc=True)]

    def __call__(self, database=None):
        db = self.parent._get_database(database)
        return self._get_linked_object_from_database()

    def _get_linked_object_from_database(self, database):
        elements = self._get_all_db_elements(database)
        data = []
        for element in elements:
            data.append(
                self.related_class.get(element['doc'][self.class_name])
            )
        return data

    def _link_data(self, obj):
        return {
            self.parent._get_full_class_name(): self.parent.id,
            self.related_class._get_full_class_name(): obj.id,
            '_type': 'relation link',
        }

    def _on_save(self, database):
        def doc_of_obj_already_assigned(obj, elements):
            try:
                for element in elements:
                    if element['doc'][self.related_class._get_full_class_name()] == obj.id:
                        return element['doc']
            except KeyError:
                pass
            return False

        def save_assigned_links(database, elements):
            for obj in self._to_assign:
                if doc_of_obj_already_assigned(obj, elements):
                    return
                else:
                    data = self._link_data()
                    data = database.insert(data)
            self._to_assign = []

        def remove_released_links(database, elements):
            for obj in self._to_release:
                database.delete(doc_of_obj_already_assigned(obj, elements))
        #-----------------------------------------------------------------------
        elements = self._get_all_db_elements(database)
        save_assigned_links(database, elements)
        remove_released_links(database, elements)
