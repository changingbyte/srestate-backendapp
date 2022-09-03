class chatRouter(object):

	def db_for_read(self,model,**hints):

		if model._meta.app_label == 'chat':
			return 'messagedb'
		return None

	def db_for_write(self,model,**hints):

		if model._meta.app_label == 'chat':
			return 'messagedb'

		return None

	def db_relation(self,obj1,obj2, **hints):

		## this is returned true if the both objects are of same database. 
		if obj1._meta.app_label == 'chat' and obj2._meta.app_label == 'chat':
			return True
		return None

	def allow_migrate(self,db,app_label,model_name=None, **hints):

		## migration only is only for chat in database messagedb
		if app_label == 'chat':
			return db=='messagedb'

		## migration for other apps is not accepted in messagedb 
		elif db == 'messagedb':
			return True

		return None