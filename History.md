0.2.0 / 2013-04-08
==================

  * Added multidatabase support
  * Fixed element name bug
  * Fixed problem with infinite loop made by relations.
  * Init now expects objects for relation, not id's.
  * Fixed choosing wrong database in Model.all
  * get, all and save no raises NoDatabaseSelected when database == None.
  * default now can be used with 2 arguments or no arguments
  * fixed removing elements from databas (remove now delete element from cache)
  * Added RecordNotFound and RecordDeleted to cdborm.errors

0.1.0 / 2012-12-15
==================

  * First version with relation.
