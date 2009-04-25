
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


class PanoConstants:
    """
    Every constant related to our framework will be stored in this class.
    """
    
    # names of events
    EVENT_GAME_UPDATE = "game.update"
    EVENT_GAME_EXIT = "game.exit"
    EVENT_GAME_PAUSED = "game.paused"
    EVENT_GAME_RESUMED = "game.resumed"
    EVENT_ITEMS_CLEARED = "inventory.items.cleared"
    EVENT_ITEM_ADDED = "inventory.item.added"
    EVENT_ITEM_REMOVED = "inventory.item.removed"
    EVENT_ITEM_COUNT_CHANGED = "inventory.count.changed"
    EVENT_ITEMS_RESTORED = "inventory.items.restored"
    EVENT_ITEMS_COMBINED = "inventory.items.combined"   # args[0]: first item, args[1]: second item
    EVENT_SAVELOAD_ERROR = "saveload.error"
    EVENT_SAVE_COMPLETED = "save.complete"
    EVENT_LOAD_COMPLETED = "load.complete"
    EVENT_CHANGE_NODE = "node.change"
    EVENT_RESTORE_NODE = "node.restore"
    EVENT_HOTSPOT_ACTION = "hotspot.action"
    EVENT_HOTSPOT_ITEM_INTERACTION = "hotspot.item.interact"
    EVENT_HOTSPOT_LOOKAT = "hotspot.lookat"
    
    
    # tasks' names
    TASK_GAME_LOOP = 'game_loop_task'
    TASK_MOUSE_POINTER = 'mouse_pointer_task'
    TASK_MUSIC = 'music_task'
    
    # config variables in boot configuration
    CVAR_GAME_DIR = 'game_dir'
    CVAR_SAVES_DIR = 'saves_dir'
    
    # names of the configuration variables that define locations for each resource type
    CVAR_WIN_TITLE = 'game_title'
    CVAR_WIN_WIDTH = 'display_width'
    CVAR_WIN_HEIGHT = 'display_height'
    CVAR_WIN_VSYNC = 'display_vsync'
    CVAR_WIN_FULLSCREEN = 'display_fullscreen'
    CVAR_CAM_HSPEED = 'camera_hspeed'
    CVAR_CAM_VSPEED = 'camera_vspeed'
    CVAR_DEBUG_HOTSPOTS = 'debug_show_hotspots'
    CVAR_DEBUG_FPS = 'debug_show_fps'
    CVAR_DEBUG_CONSOLE = 'debug_enable_console'
    
    CVAR_RESOURCES_NODES = 'resources_nodes'
    CVAR_RESOURCES_TEXTURES = 'resources_textures'
    CVAR_RESOURCES_FONTS = 'resources_fonts'
    CVAR_RESOURCES_POINTERS = 'resources_pointers'
    CVAR_RESOURCES_LANGS = 'resources_langs'
    CVAR_RESOURCES_MODELS = 'resources_models'
    CVAR_RESOURCES_SPRITES = 'resources_sprites'
    CVAR_RESOURCES_PLAYLISTS = 'resources_playlists'
    CVAR_RESOURCES_SFX = 'resources_sfx'
    CVAR_RESOURCES_MUSIC = 'resources_music'
    CVAR_RESOURCES_SOUNDS_DEFS = 'resources_sounds_defs'
    CVAR_RESOURCES_VIDEOS = 'resources_videos'
    CVAR_RESOURCES_MAPPINGS = 'resources_mappings'
    CVAR_RESOURCES_ITEMS = 'resources_items'
    CVAR_RESOURCES_SCRIPTS = 'resources_scripts'
    CVAR_RESOURCES_TEXTS = 'resources_texts'
    CVAR_RESOURCES_BINARIES = 'resources_binaries'
    
    # cvars related to preloading
    CVAR_PRELOAD_POINTERS = 'preloads_pointers'
    CVAR_PRELOAD_NODES = 'preloads_nodes'
    CVAR_PRELOAD_TEXTURES = 'preloads_textures'
    CVAR_PRELOAD_FONTS = 'preloads_fonts'
    CVAR_PRELOAD_POINTERS = 'preloads_pointers'
    CVAR_PRELOAD_LANGS = 'preloads_langs'
    CVAR_PRELOAD_MODELS = 'preloads_models'
    CVAR_PRELOAD_SPRITES = 'preloads_sprites'
    CVAR_PRELOAD_PLAYLISTS = 'preloads_playlists'
    CVAR_PRELOAD_SFX = 'preloads_sfx'
    CVAR_PRELOAD_MUSIC = 'preloads_music'
    CVAR_PRELOAD_SOUNDS_DEFS = 'preloads_sounds_defs'
    CVAR_PRELOAD_VIDEOS = 'preloads_videos'
    CVAR_PRELOAD_MAPPINGS = 'preloads_mappings'
    CVAR_PRELOAD_ITEMS = 'preloads_items'
    CVAR_PRELOAD_SCRIPTS = 'preloads_scripts'
    CVAR_PRELOAD_LOCATIONS = 'preloads_locations'
    CVAR_PRELOAD_TEXTS = 'preloads_texts'
    CVAR_PRELOAD_BINARIES = 'preloads_binaries'

    # names of vars related to the credits state
    CVAR_CREDITS_BACKGROUND   = 'credits_background'
    CVAR_CREDITS_FONT         = 'credits_font'
    CVAR_CREDITS_FONT_COLOR   = 'credits_font_color'
    CVAR_CREDITS_FONT_SCALE   = 'credits_font_scale'
    CVAR_CREDITS_SCROLL_SPEED = 'credits_scroll_speed'
    CVAR_CREDITS_TEXT_FILE    = 'credits_text_file'
    CVAR_CREDITS_MUSIC    = 'credits_music'
    
    # names of the cvars which are related to the talk box
    CVAR_TALKBOX_FONT      = 'talkbox_font'
    CVAR_TALKBOX_BGCOLOR   = 'talkbox_bg_color'
    CVAR_TALKBOX_IMAGE   = 'talkbox_image'
    CVAR_TALKBOX_TEXTCOLOR = 'talkbox_text_color'
    CVAR_TALKBOX_TEXTSCALE = 'talkbox_text_scale'
    
    # same for i18n
    CVAR_I18N_LANG = "i18n_language"
    
    # for paused state
    CVAR_PAUSED_STATE_FONT = 'paused_font_name'
    CVAR_PAUSED_STATE_FGCOLOR = 'paused_fg_color'
    CVAR_PAUSED_STATE_MESSAGE = 'paused_message'
    CVAR_PAUSED_STATE_SCALE = 'paused_font_scale'

    # for intro state
    CVAR_INTRO_STATE_VIDEOS = 'intro_videos'
    CVAR_INTRO_STATE_DELAY = 'intro_delay'
    
    # for inventory
    CVAR_INVENTORY_BACKDROP = 'inventory_backdrop'
    CVAR_INVENTORY_POINTER = 'inventory_mouse_pointer'
    CVAR_INVENTORY_FONT = 'inventory_font_name'
    CVAR_INVENTORY_FONT_COLOR = 'inventory_font_color'
    CVAR_INVENTORY_FONT_BG_COLOR = 'inventory_font_bg_color'
    CVAR_INVENTORY_POS = 'inventory_pos'
    CVAR_INVENTORY_REL_POS = 'inventory_rel_pos'
    CVAR_INVENTORY_SIZE = 'inventory_size'
    CVAR_INVENTORY_TEXT_POS = 'inventory_item_text_pos'
    CVAR_INVENTORY_TEXT_REL_POS = 'inventory_item_text_rel_pos'
    CVAR_INVENTORY_TEXT_SCALE = 'inventory_item_text_scale'
    CVAR_INVENTORY_OPACITY = 'inventory_opacity'
    CVAR_INVENTORY_SLOTS = 'inventory_slots_provider'
    
    # keys' names used to lookup window properties in a dictionary
    WIN_ORIGIN = 'win_origin'
    WIN_SIZE = 'win_size'
    WIN_ICON = 'win_icon'
    WIN_MOUSE_POINTER = 'mouse_pointer'
    WIN_FULLSCREEN = 'fullscreen'
    WIN_TITLE = 'win_title'
    
    CBM_FRONT_FACE = 1
    CBM_BACK_FACE = 2
    CBM_LEFT_FACE = 3
    CBM_RIGHT_FACE = 4
    CBM_TOP_FACE = 5
    CBM_BOTTOM_FACE = 6    
    
    #Constants for the resource types
    RES_TYPE_NODES = 1
    RES_TYPE_TEXTURES = 2
    RES_TYPE_FONTS = 3
    RES_TYPE_SFX = 4
    RES_TYPE_POINTERS = 5
    RES_TYPE_MODELS = 6
    RES_TYPE_LANGS = 7
    RES_TYPE_SPRITES = 8
    RES_TYPE_PLAYLISTS = 9
    RES_TYPE_VIDEOS = 10
    RES_TYPE_MAPPINGS = 11
    RES_TYPE_ITEMS = 12
    RES_TYPE_SCRIPTS = 13
    RES_TYPE_MUSIC = 14
    RES_TYPE_SOUNDS_DEFS = 15
    RES_TYPE_TEXTS = 16
    RES_TYPE_BINARIES = 17
    RES_TYPE_ALL = 100
    
    #Constants for the predefined mouse pointers
    SELECT_POINTER = "select"
    TALK_POINTER = "talk"
    EXAMINE_POINTER = "examine"
    EXIT_POINTER = "exit"
    
    #Mouse modes
    MOUSE_PANORAMA_MODE = 1
    MOUSE_UI_MODE = 1        
    
     
    #Constants for the mouse regions used to rotate the camera
    CAM_CONTROL_TOP_REGION = 1
    CAM_CONTROL_BOTTOM_REGION = 2
    CAM_CONTROL_LEFT_REGION = 3
    CAM_CONTROL_RIGHT_REGION = 4

    # constants for the states' names
    STATE_INIT      = 'initState'
    STATE_EXPLORE   = 'exploreState'
    STATE_PAUSED    = 'pausedState'
    STATE_INVENTORY = 'inventoryState'
    STATE_INTRO     = 'introState'
    STATE_CONSOLE   = 'consoleState'
    STATE_CREDITS   = 'creditsState'
    
    # default path to configuration file
    CONFIG_FILE = "Config.prc"
    
    # name of the configuration variable that denotes the nodes path
    VAR_NODES_PATH = "var_nodes_path"
    
    # scenegraph node that acts as the common ancestor of all nodes which are involved with the rendering
    # of the currently active game node
    NODE_ROOT_NODE = "root_node"
    
    # name of scenegraph node where the cubemap is stored
    NODE_CUBEMAP = 'cmap'
    
    # scenegraph node that acts as the common ancestor of all nodes that store debug geometries
    NODE_DEBUG_GEOMS_PARENT = 'debug_geoms'
    
    # scenegraph node that acts as the common ancestor of all nodes that store sprites 
    NODE_SPRITES_PARENT = 'sprites_tex_cards'
    
    # prefix to use when naming sprite nodes
    SPRITES_NAME_PREFIX = 'sprite_'
    
    # prefix to use when naming nodes for debug geometries
    DEBUG_GEOMS_NAME_PREFIX = 'debug_geom_'
    
    MOUSE_CULL_BIN_NAME = "mouse_pointer_bin"
    MOUSE_CULL_BIN_VAL = 60 
    
    CONSOLE_CULL_BIN_NAME = "console_pointer_bin"
    CONSOLE_CULL_BIN_VAL = 70
    
    BLEND_TYPE_EASEIN = "easeIn"
    BLEND_TYPE_EASEOUT = "easeOut"
    BLEND_TYPE_EASEINOUT = "easeInOut"
    BLEND_TYPE_ABRUPT = "noBlend"
    
    