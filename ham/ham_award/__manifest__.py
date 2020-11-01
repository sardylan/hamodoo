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

        "views/qso.xml",
        "views/operator.xml",

        "menu/action.xml",
        "menu/items.xml",
    ],
    "application": True
}
