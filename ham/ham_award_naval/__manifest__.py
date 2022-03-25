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
        "security/access/station.xml",

        "views/club.xml",
        "views/station.xml",
        "views/inherit_award_qso.xml",

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
