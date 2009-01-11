import fnmatch, dircache, os
import logging

from ResourcesLocation import AbstractResourceLocation
from ResourcesTypes import ResourcesTypes

class DirectoryResourcesLocation(AbstractResourceLocation):
	def __init__(self, directory, name, description, resTypes, hotswap=True, checkPeriod=10):
		AbstractResourceLocation.__init__(self, name, description, resTypes, hotswap, checkPeriod)
		
		self.log = logging.getLogger('pano.directoryResource')
		
		# the directory to look into for supported resource types
		self.directory = directory

		# a sorted list of all filenames of supported types that were found in self.directory
		self.resourcesNames = []
		
	def indexResources(self):
		AbstractResourceLocation(self)
		
		# get a listing of the directory and match filenames against
		# all supported resource types
		try:
			filenames = dircache.listdir(self.directory)
		except Exception, e:
			# dircache.listdir can throw 
			self.log.exception('error while calling dircache.listdir')
			return 
		
		suffixes = []
		for resType in self.resTypes:			 		
			suffixes.extend(ResourcesTypes.getExtensions(resType))

		suffixes = tuple(suffixes)
		self.resourcesNames = [item for item in filenames if item.endswith(suffixes)]
		self.resourcesNames.sort()
		
		print 'resource names ' , self.resourcesNames

	def containsResource(self, filename):
		return self.resourcesNames.count(filename) > 0

	def getResourceFullPath(self, name):
		if self.resourcesNames.count(name) > 0:
#			return os.path.abspath(os.path.join(self.directory, name))
			return os.path.join(self.directory, name)
		else:
			return None
		
	def listResources(self, resType, fullPaths=True):
		if resType in self.getResourcesTypes():
			prefix = ''
			if fullPaths:
				prefix = self.directory
			return [os.path.join(prefix, resName) for resName in self.resourcesNames if ResourcesTypes.isExtensionOfType(resName[-4:], resType)]
		else:
			return []

				
					

