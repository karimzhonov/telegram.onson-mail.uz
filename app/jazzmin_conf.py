JAZZMIN_SETTINGS = {
    # title of the window (Will default to current_admin_site.site_title if absent or None)
    "site_title": "Onson-mail",

    # Title on the login screen (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_header": "Onson-mail",

    # Title on the brand (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_brand": "Onson-mail",

    # Logo to use for your site, must be present in static files, used for brand on top left
    # "site_logo": "books/img/logo.png",

    # Logo to use for your site, must be present in static files, used for login form logo (defaults to site_logo)
    "login_logo": None,

    # Logo to use for login form in dark themes (defaults to login_logo)
    "login_logo_dark": None,

    # CSS classes that are applied to the logo above
    "site_logo_classes": "img-circle",

    # Relative path to a favicon for your site, will default to site_logo if absent (ideally 32x32 px)
    "site_icon": None,

    # Welcome text on the login screen
    "welcome_sign": "Welcome",

    # List of model admins to search from the search bar, search bar omitted if excluded
    # If you want to use a single search field you dont need to use a list, you can use a simple string
    # "search_model": ["oauth.User"],

    # Field name on user model that contains avatar ImageField/URLField/Charfield or a callable that receives the user
    "user_avatar": None,

    ############
    # Top Menu #
    ############

    # Links to put along the top menu
    # "topmenu_links": [
    #
    #     # Url that gets reversed (Permissions can be added)
    #     {"name": "Home",  "url": "admin:index", "permissions": ["auth.view_user"]},
    #
    # ],

    #############
    # User Menu #
    #############

    # Additional links to include in the user menu on the top right ("app" url type is not allowed)
    # "usermenu_links": [
    #     {"name": "Support", "url": "https://github.com/farridav/django-jazzmin/issues", "new_window": True},
    #     # {"model": "auth.user"}
    # ],

    #############
    # Side Menu #
    #############

    # Whether to display the side menu
    "show_sidebar": True,

    # Whether to aut expand the menu
    "navigation_expanded": True,

    # Hide these apps when generating side menu e.g (auth)
    "hide_apps": [],

    # Hide these models when generating side menu (e.g auth.user)
    "hide_models": [],

    # List of apps (and/or models) to base side menu ordering off of (does not need to contain all apps/models)
    "order_with_respect_to": [
        "auth.Group", "auth.User",
        "ichd.Uploads",
        "ichd.Sector", 'ichd.Region', "ichd.Area", "ichd.Criteria",
        "ichd.SectorTable", "ichd.RegionTable", "ichd.RegionSectorTable", 
        "ichd.AreaTable", "ichd.DataTable", "ichd.RegionDataTable",
        "ichd.CriteriaDataTable",
        "passport_indicators.Uploads", "passport_indicators.Region",
        "passport_indicators.Criteria", "passport_indicators.DataTable",
    ],

    # Custom links to append to app groups, keyed on app name
    # "custom_links": {
    #     "books": [{
    #         "name": "Make Messages",
    #         "url": "make_messages",
    #         "icon": "fas fa-comments",
    #         "permissions": ["books.view_book"]
    #     }]
    # },

    # for the full list of 5.13.0 free icon classes
    "icons": {
        "auth.User": "fas fa-user",
        "auth.Group": "fas fa-users",
    },
    # Icons that are used when one is not manually specified
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",

    #################
    # Related Modal #
    #################
    # Use modals instead of popups
    "related_modal_active": False,

    #############
    # UI Tweaks #
    #############
    # Relative paths to custom CSS/JS scripts (must be present in static files)
    "custom_css": None,
    "custom_js": None,
    # Whether to link font from fonts.googleapis.com (use custom_css to supply font otherwise)
    "use_google_fonts_cdn": True,
    # Whether to show the UI customizer on the sidebar
    "show_ui_builder": True,

    ###############
    # Change view #
    ###############
    # Render out the change view as a single form, or in tabs, current options are
    # - single
    # - horizontal_tabs (default)
    # - vertical_tabs
    # - collapsible
    # - carousel
    "changeform_format": "single",
    # override change forms on a per modeladmin basis
    # "changeform_format_overrides": {"auth.user": "collapsible", "auth.group": "vertical_tabs"},
    # Add a language dropdown into the admin
    "language_chooser": True,
}

JAZZMIN_UI_TWEAKS = {
    # Small text on the top navbar
    "navbar_small_text": False,
    # Small text on the footer
    "footer_small_text": True,
    # Small text everywhere
    "body_small_text": False,
    # Small text on the brand/logo
    "brand_small_text": False,
    # brand/logo background colour
    "brand_colour": False,
    # Link colour
    "accent": "accent-primary",
    # topmenu colour
    "navbar": "navbar-gray-dark navbar-dark",
    # topmenu border
    "no_navbar_border": False,
    # Make the top navbar sticky, keeping it in view as you scroll
    "navbar_fixed": True,
    # Whether to constrain the page to a box (leaving big margins at the side)
    "layout_boxed": False,
    # Make the footer sticky, keeping it in view all the time
    "footer_fixed": True,
    # Make the sidebar sticky, keeping it in view as you scroll
    "sidebar_fixed": True,
    # sidemenu colour
    "sidebar": "sidebar-dark-primary",
    # sidemenu small text
    "sidebar_nav_small_text": False,
    # Disable expanding on hover of collapsed sidebar
    "sidebar_disable_expand": False,
    # Indent child menu items on sidebar
    "sidebar_nav_child_indent": False,
    # Use a compact sidebar
    "sidebar_nav_compact_style": False,
    # Use the AdminLTE2 style sidebar
    "sidebar_nav_legacy_style": False,
    # Use a flat style sidebar
    "sidebar_nav_flat_style": True,
    # Bootstrap theme to use (default, or from bootswatch, see THEMES below)
    "theme": "default",
    # Theme to use instead if the user has opted for dark mode (e.g darkly/cyborg/slate/solar/superhero)
    "dark_mode_theme": None,
    # The classes/styles to use with buttons
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },
}
