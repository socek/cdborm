class Relation(object):

    def __init__(self, class_name, index_name):
        self.parent = None
        self.value = None
        self.class_name = class_name
        self.index_name = index_name

    @property
    def related_class(self):
        return self.parent.get_class_by_name(self.class_name)

    def _on_save(self, database):
        pass

class LocalRelation(Relation):
    foreign = False

class ForeignRelation(Relation):
    foreign = True
