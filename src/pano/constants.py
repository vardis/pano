
class PanoConstants:
    """
    Every constant related to our framework will be stored in this class.
    """
    
    # names of the configuration variables
    CVAR_WIN_TITLE = 'game_title'
    CVAR_WIN_WIDTH = 'display_width'
    CVAR_WIN_HEIGHT = 'display_height'
    CVAR_WIN_VSYNC = 'display_vsync'
    CVAR_WIN_FULLSCREEN = 'display_fullscreen'
    CVAR_CAM_HSPEED = 'camera_hspeed'
    CVAR_CAM_VSPEED = 'camera_vspeed'
    CVAR_DEBUG_HOTSPOTS = 'debug_show_hotspots'
    CVAR_DEBUG_FPS = 'debug_show_fps'
    
    CVAR_RESOURCES_NODES = 'resources_nodes'
    CVAR_RESOURCES_TEXTURES = 'resources_textures'
    CVAR_RESOURCES_FONTS = 'resources_fonts'
    CVAR_RESOURCES_POINTERS = 'resources_pointers'
    CVAR_RESOURCES_LANGS = 'resources_langs'
    CVAR_RESOURCES_MODELS = 'resources_models'
    
    # names of the cvars which are related to the talk box
    CVAR_TALKBOX_X         = 'talkbox_x'
    CVAR_TALKBOX_Y         = 'talkbox_y'
    CVAR_TALKBOX_FONT      = 'talkbox_font'
    CVAR_TALKBOX_BGCOLOR   = 'talkbox_bg_color'
    CVAR_TALKBOX_IMAGE   = 'talkbox_image'
    CVAR_TALKBOX_TEXTCOLOR = 'talkbox_text_color'
    CVAR_TALKBOX_TEXTSCALE = 'talkbox_text_scale'
    
    # same for i18n
    CVAR_I18N_LANG = "i18n_language"
    
    
    # keys' names used to lookup window properties in a dictionary
    WIN_ORIGIN = 'win_origin'
    WIN_SIZE = 'win_size'
    WIN_ICON = 'win_icon'
    WIN_MOUSE_POINTER = 'mouse_pointer'
    WIN_FULLSCREEN = 'fullscreen'
    WIN_TITLE = 'win_title'
    
    #Constants for the faces of the cubemap
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
    RES_TYPE_SOUNDS = 4
    RES_TYPE_POINTERS = 5
    RES_TYPE_MODELS = 6
    RES_TYPE_LANGS = 7
    RES_TYPE_ALL = 100
    
    #Constants for the predefined mouse pointers
    SELECT_POINTER = "select"
    TALK_POINTER = "talk"
    EXAMINE_POINTER = "examine"
    EXIT_POINTER = "exit"
    LOOK_UP_POINTER = 5
    LOOK_DOWN_POINTER = 6
    LOOK_LEFT_POINTER = 7
    LOOK_RIGHT_POINTER = 8
    
    #Mouse modes
    MOUSE_PANORAMA_MODE = 1
    MOUSE_UI_MODE = 1        
    
     
    #Constants for the mouse regions used to rotate the camera
    CAM_CONTROL_TOP_REGION = 1
    CAM_CONTROL_BOTTOM_REGION = 2
    CAM_CONTROL_LEFT_REGION = 3
    CAM_CONTROL_RIGHT_REGION = 4
    
    # default path to configuration file
    CONFIG_FILE = "Config.prc"
    
    # name of the configuration variable that denotes the nodes path
    VAR_NODES_PATH = "var_nodes_path"
    
