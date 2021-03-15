{
    "name": "HAM Utility",
    "version": "14.0.2.11.0",
    "category": "HAM Radio",
    "summary": "HAM utilities and models",
    "sequence": 0,
    "author": "Luca Cireddu",
    "depends": [
        "base",
        "mail",
        "widget_datetime_tz"
    ],
    "data": [
        "data/ir_module_category.xml",
        "data/zone_cq.xml",
        "data/zone_itu.xml",
        "data/modulation.xml",
        "data/band.xml",
        "data/website.xml",

        "security/profiles.xml",

        "security/utilities/adif.xml",
        "security/utilities/cabrillo.xml",
        "security/utilities/callsign.xml",
        "security/utilities/country.xml",
        "security/utilities/locator.xml",
        "security/utilities/modulation.xml",
        "security/utilities/qso.xml",

        "security/utilities/websites/hamqth.xml",
        "security/utilities/websites/hrdlog.xml",

        "security/models/modulation.xml",
        "security/models/country.xml",
        "security/models/band.xml",
        "security/models/website.xml",

        "security/wizard/import_prefix.xml",

        "views/modulation.xml",
        "views/country.xml",
        "views/band.xml",
        "views/website.xml",

        "views/inherit_res_users.xml",

        "wizard/import_prefix.xml",

        "menu/action.xml",
        "menu/items.xml",
    ],
    "application": True
}
