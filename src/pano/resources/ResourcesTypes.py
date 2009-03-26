'''
    Copyright (c) 2008 Georgios Giannoudovardis, <vardis.g@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

'''

from constants import PanoConstants

class ResourcesTypes:
	"""
	A registry of all supported resource types.
	"""
	resTypesExtensions = { 
			PanoConstants.RES_TYPE_NODES : ('.node'),
			PanoConstants.RES_TYPE_MODELS : ('.egg', '.egg.pz' ),
			PanoConstants.RES_TYPE_TEXTURES : ('.jpg', '.bmp', '.tga', '.tif', '.png', '.dds'),
			PanoConstants.RES_TYPE_FONTS : ('.font'),
			PanoConstants.RES_TYPE_SOUNDS : ('.wav', '.ogg', '.midi', '.mp3', '.avi', '.mpg', '.mpeg', '.sound'),
			PanoConstants.RES_TYPE_POINTERS : ('.pointer'),
			PanoConstants.RES_TYPE_LANGS : ('.lang'),
			PanoConstants.RES_TYPE_SPRITES : ('.spr'),
			PanoConstants.RES_TYPE_PLAYLISTS : ('.mpl'),
			PanoConstants.RES_TYPE_VIDEOS : ('.wmv', '.flv', '.asf', '.avi', '.mpg', '.ogg', '.ogm', '.mov'),
			PanoConstants.RES_TYPE_MAPPINGS : ('.mappings'),
			PanoConstants.RES_TYPE_ITEMS : ('.item'),
			PanoConstants.RES_TYPE_SCRIPTS : ('.py')
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
		
	def isExtensionOfType(extension, resType):
		if ResourcesTypes.resTypesExtensions.has_key(resType):
			exts = ResourcesTypes.resTypesExtensions[resType]
			return extension in exts
		else:
			return False
			
	getExtensions = staticmethod(getExtensions)
	isExtensionOfType = staticmethod(isExtensionOfType)
		
