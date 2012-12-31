from cdborm.errors import BadType
from cdborm.relation.relation import LocalRelation, ForeignRelation

class ManyToMany(LocalRelation):
    def __init__(self, *args, **kwargs):
        super(ManyToMany, self).__init__(*args, **kwargs)
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

    def _get_all_db_elements(self, db):
        return [ element for element in db.get_many(self.index_name, self.parent.id, with_doc=True) ]

    def __call__(self, database=None):
        db = self.parent._get_database(database)
        elements = self._get_all_db_elements(db)
        data = []
        for element in elements:
            data.append(
                self.related_class.get(element['doc'][self.class_name])
            )

        return data

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
                    data = {
                        self.parent._get_full_class_name() : self.parent.id,
                        self.related_class._get_full_class_name() : obj.id,
                        '_type' : 'relation link',
                    }
                    data =  database.insert(data)
            self._to_assign = []
        def remove_released_links(database, elements):
            for obj in self._to_release:
                database.delete(doc_of_obj_already_assigned(obj, elements))
        #-----------------------------------------------------------------------
        elements = self._get_all_db_elements(database)
        save_assigned_links(database, elements)
        remove_released_links(database, elements)
