{
    "name": "ARMI Naval Clubs utility",
    "version": "15.0.0.0.0",
    "category": "HAM Radio",
    "summary": "Adds models for Naval clubs",
    "sequence": 0,
    "author": "Luca Cireddu",
    "license": "GPL-3",
    "depends": [
        "ham_award"
    ],
    "data": [
        "security/access/club.xml",

        "views/club.xml",

        "menu/actions.xml",
        "menu/items.xml",

        "data/club.xml"
    ],
    "assets": {
        "web.assets_frontend": [
        ],
    },
    "application": True
}
