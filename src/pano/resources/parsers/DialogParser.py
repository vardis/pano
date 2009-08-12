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

import logging
import json

from pano.constants import PanoConstants
from pano.errors.ParseException import ParseException
from pano.model.Dialog import Dialog

class DialogParser(object):
    '''
    Parses dialog resources.
    '''

    def __init__(self):
        self.log = logging.getLogger('pano.dialogParser')
        
    def parse(self, dlg, fileContents):
        try:
            # encoding is assumed to be utf-8
            d = json.loads(fileContents, object_hook=dialog_hook)
            dlg.options = d.options
            dlg.initialOption = d.initialOption
            dlg.color = d.color
            
        except (ValueError, TypeError), e:
            raise ParseException(error='error.parse.json', resFile=dlg.name + '.dlg', args=(str(e)))
        
        else:
            return dlg
        
        
class DialogEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Dialog):
            return {
                '__Dialog__' : True,
                'name' : obj.name,
                'options' : obj.options,
                'initialOption' : obj.initialOption,
                'color' : obj.color
                }
        elif isinstance(obj, DialogOption):
            print 'message: ', obj.message
            return {
                '__DialogOption__' : True,
                'name' : obj.name,
                'parent' : obj.parent,
                'enabled' : obj.enabled,
                'message' : obj.message,
                'sound' : obj.sound,
                'events' : obj.events,
                'options' : obj.options,                
                'color' : obj.color
                }
        else:
            return json.JSONEncoder.default(self, obj)
        
def dialog_hook(dct):
    if '__Dialog__' in dct:
        print 'decoding dialog'        
        d = Dialog(dct['name'])
        d.options = dct['options']
        d.initialOption = dct['initialOption']
        d.color = dct['color']
        return d
        
    elif '__DialogOption__' in dct:
        print 'decoding dialog option'
        opt = DialogOption(dct['name'], dct['parent'])
        opt.message = dct['message']
        opt.options = dct['options']
        opt.events = dct['events']
        opt.enabled = dct['enabled']
        opt.color = dct['color']
        opt.sound = dct['sound']
        return opt
    else:
        return dct
