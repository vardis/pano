###########################################################
###                                                     ###
### Panda3D Configuration File -  User-Editable Portion ###
###                                                     ###
###########################################################

# Uncomment one of the following lines to choose whether you should
# run using OpenGL or DirectX rendering.

load-display pandagl

# These control the placement and size of the default rendering window.

win-origin 50 50
win-size 800 600

# Uncomment this line if you want to run Panda fullscreen instead of
# in a window.

fullscreen #f

# The framebuffer-hardware flag forces it to use an accelerated driver.
# The framebuffer-software flag forces it to use a software renderer.
# If you don't set either, it will use whatever's available.

framebuffer-hardware #t
framebuffer-software #f

# These set the minimum requirements for the framebuffer.

depth-bits 16
color-bits 16
alpha-bits 0
stencil-bits 0
multisamples 0

# These control the amount of output Panda gives for some various
# categories.  The severity levels, in order, are "spam", "debug",
# "info", "warning", and "fatal"; the default is "info".  Uncomment
# one (or define a new one for the particular category you wish to
# change) to control this output.

notify-level spam
default-directnotify-level spam

# These specify where model files may be loaded from.  You probably
# want to set this to a sensible path for yourself.  $THIS_PRC_DIR is
# a special variable that indicates the same directory as this
# particular Config.prc file.

model-path    $MAIN_DIR
model-path    $THIS_PRC_DIR/..
model-path    $THIS_PRC_DIR/../models
sound-path    $MAIN_DIR
sound-path    $THIS_PRC_DIR/..
sound-path    $THIS_PRC_DIR/../models
texture-path  $MAIN_DIR
texture-path  $THIS_PRC_DIR/..
texture-path  $THIS_PRC_DIR/../models

# This enable the automatic creation of a TK window when running
# Direct.

want-directtools  #f
want-tk           #f

# Enable/disable performance profiling tool and frame-rate meter

want-pstats            #f
show-frame-rate-meter  #t

# Enable audio using the OpenAL audio library by default:

audio-library-name p3openal_audio

# Enable the use of the new movietexture class.

use-movietexture #t

# The new version of panda supports hardware vertex animation, but it's not quite ready

hardware-animated-vertices 0

# Enable the model-cache, but only for models, not textures.

model-cache-dir $THIS_PRC_DIR/../modelcache
model-cache-textures #f

# Limit the use of advanced shader profiles.
# Currently, advanced profiles are not reliable under Cg.

basic-shaders-only #t

# path to nodes resources
nodes-path data/nodes

