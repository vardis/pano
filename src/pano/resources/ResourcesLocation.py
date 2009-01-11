from constants import PanoConstants

class AbstractResourceLocation:
	"""
	A location from where resources will be found and loaded.
	This class serves as a base for classes that will implement
	specific types of resource locations like filesystem folders,
	multifiles, archives, databases, network streams, etc.
	"""
	def __init__(self, name = '', descrption = '', resTypes = PanoConstants.RES_TYPE_ALL, hotswap = True, checkPeriod = 10):
		self.name = name
		self.desc = descrption

		# specifies which resources types will be looked up in this location
		self.resTypes = [ resTypes ]

		# if True then the location will be checked for any modified resources
		self.hotswap = hotswap

		# the period at which the location will be checked for any modifications.
		# it is defined in seconds
		self.checkPeriod = checkPeriod

	def getName(self):
		return self.name

	def getDescription(self):
		return self.descrption

	def setDescription(self, descrption):
		self.descrption = descrption

	def getResourcesTypes(self):
		return self.resTypes 

	def indexResources(self):
		"""
		Creates an index on the resources' names for fast lookups.
		This is exposed as a public function in order to be possible
		to force a rebuild of the index when we know that something
		has changed.
		"""
		pass

	def containsResource(self, filename):
		"""
		Returns True if this resource location contains the specified filename.
		"""
		return False

	def getResourceFullPath(self, name):
		"""
		Temporary until streams are incorporated.
		"""
		return None
	
	def listResources(self, resType, fullPaths=True):
		"""
		List all filenames of type that matches resType. 
		"""
		return []

	def openResource(self, name):
		"""
		Opens a data stream for the resource identified by the given name.
		Derived class should implement this function.
		"""
		return None

	def hasChanged(self):
		"""
		Returns True if any resources have been modified.
		Derived classes should implement this function in order for hotswapping
		to work.
		"""
		return False

	def dispose(self):
		"""
		Since ResourcesLocations objects might consume plenty of resources
		for storing their index or utilising system resources (file handles,
		network sockets, threads) for accesing their data sources, this method
		provides a means for releasing these resources when they are no longer
		needed.
		Derived class should implement this function.
		"""
		pass

