{
    "name": "HAM Awards",
    "version": "14.0.1.0.0",
    "category": "Extra Tools",
    "summary": "HAM award management",
    "sequence": 0,
    "author": "Luca Cireddu",
    "depends": [
        "website",
        "portal",
        "contacts",
        "ham_utility",
    ],
    "data": [
        "security/categories.xml",
        "security/profiles.xml",

        "security/access/qso.xml",
        "security/access/operator.xml",
        "security/access/award.xml",
        "security/access/upload.xml",

        "views/qso.xml",
        "views/operator.xml",
        "views/award.xml",
        "views/upload.xml",

        "menu/action.xml",
        "menu/items.xml",

        "templates/portal/my_home.xml",
        "templates/portal/breadcrumbs.xml",

        "templates/private/award/list.xml",
        "templates/private/award/single.xml",
        "templates/private/award/single_upload.xml"
    ],
    "application": True
}
