from pano.constants import PanoConstants

class ResourcesTypes:
	"""
	A registry of all supported resource types.
	"""
	resTypesExtensions = { 
			PanoConstants.RES_TYPE_NODES : ('.xml'),
			PanoConstants.RES_TYPE_MODELS : ('.egg', '.egg.pz' ),
			PanoConstants.RES_TYPE_TEXTURES : ('.jpg', '.bmp', '.tga', '.tif', '.png', '.dds'),
			PanoConstants.RES_TYPE_FONTS : ('.font'),
			PanoConstants.RES_TYPE_SOUNDS : ('.wav', '.ogg', '.midi', '.mp3'),
			PanoConstants.RES_TYPE_POINTERS : ('.pointer')
	}

	def getExtensions(resType):
		"""
		Returns a list of file extensions that are supported for the specified
		resource type. e.g. if resType specifies textures then the returned list
		could be ('.jpg', '.bmp', 'tga')
		"""
		if ResourcesTypes.resTypesExtensions.has_key(resType):
			return list(ResourcesTypes.resTypesExtensions[resType])
		elif resType == PanoConstants.RES_TYPE_ALL:
			all = []
			for val in resTypesExtensions.values():
				all.append(list(val))
			return all
		else:
			return None
		
	# makes getExtensions a static method
	getExtensions = staticmethod(getExtensions)
		
