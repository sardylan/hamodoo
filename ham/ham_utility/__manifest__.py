{
    "name": "HAM Utility",
    "version": "14.0.1.1.0",
    "category": "HAM Utility",
    "sequence": 0,
    "summary": "HAM utilities and models",
    "depends": [
        "base",
        "mail",
        "widget_datetime_tz"
    ],
    "data": [
        "security/categories.xml",
        "security/profiles.xml",

        "security/models/modulation.xml",
        "security/models/country.xml",
        "security/models/band.xml",

        "security/wizard/import_prefix.xml",

        "views/modulation.xml",
        "views/country.xml",
        "views/band.xml",

        "wizard/import_prefix.xml",

        "menu/action.xml",
        "menu/items.xml",

        "data/zone_cq.xml",
        "data/zone_itu.xml",
        "data/modulation.xml",
        "data/band.xml"
    ],
    "application": True
}
