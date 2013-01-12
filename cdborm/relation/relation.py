from cdborm.errors import BadType
from cdborm.index import LinkLeftIndex, LinkRightIndex


class Relation(object):

    def __init__(self, class_name, subname=''):
        self.parent = None
        self.value = None
        self.class_name = class_name
        self.relation_name = subname
        self._to_assign = []
        self._to_release = []

    def _init_with_parent(self, parent):
        self.parent = parent
        self.relation_name = self._get_relation_name(self.class_name)
        if self.class_name == self._get_class_names(self.class_name)[0]:
            self.foreign_class_nickname = 'left'
        else:
            self.foreign_class_nickname = 'right'

    def _get_class_names(self, class_name):
        class_name = self.parent.__class__.__name__
        return sorted([class_name, self.class_name])

    def _get_relation_name(self, class_name):
        return self.relation_name + '_'.join(self._get_class_names(class_name))

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

    def _get_all_db_elements(self, db, _id=None):
        def append_element_from_my_relation(element, elements):
            if element['doc']['relation name'] == self.relation_name:
                elements.append(element)
        #-----------------------------------------------------------------------
        if not _id:
            _id = self.parent.id
        elements = []
        for element in db.get_many(LinkLeftIndex._name, _id, with_doc=True):
            append_element_from_my_relation(element, elements)
        for element in db.get_many(LinkRightIndex._name, _id, with_doc=True):
            append_element_from_my_relation(element, elements)
        return elements

    def _get_linked_object_from_database(self, database):
        elements = self._get_all_db_elements(database)
        data = []
        for element in elements:
            data.append(
                self.related_class.get(element['doc'][self.foreign_class_nickname])
            )
        return data

    def __call__(self, database=None):
        db = self.parent._get_database(database)
        return self._get_linked_object_from_database(db)

    def _link_data(self, obj):
        hierarchy = self._get_class_names(obj.__class__.__name__)
        if hierarchy[0] == obj.__class__.__name__:
            return {
                'left': obj.id,
                'right': self.parent.id,
                'relation name': self.relation_name,
                '_type': 'relation link',
            }
        else:
            return {
                'left': self.parent.id,
                'right': obj.id,
                'relation name': self.relation_name,
                '_type': 'relation link',
            }

    def _remove_released_links(self, database, elements):
        if self._to_release == True:
            for element in elements:
                database.delete(element['doc'])
            if len(self._to_assign) > 0:
                for element in self._get_all_db_elements(database, self._to_assign[0].id):
                    database.delete(element['doc'])
        else:
            for obj in self._to_release:
                doc = self.doc_of_obj_already_assigned(obj, elements)
                if doc:
                    database.delete(doc)

    def doc_of_obj_already_assigned(self, obj, elements):
        for element in elements:
            if element['doc'][self.foreign_class_nickname] == obj.id:
                return element['doc']
        return False

    def _save_assigned_links(self, database, elements):
        for obj in self._to_assign:
            if self.doc_of_obj_already_assigned(obj, elements):
                return
            else:
                data = self._link_data(obj)
                data = database.insert(data)
        self._to_assign = []

    def _on_save(self, database):
        elements = self._get_all_db_elements(database)
        self._remove_released_links(database, elements)
        self._save_assigned_links(database, elements)
