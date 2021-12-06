{
    "name": "HAM Repeaters",
    "version": "15.0.0.0.0",
    "category": "HAM Radio",
    "summary": "HAM utilities and models",
    "sequence": 0,
    "author": "Luca Cireddu",
    "depends": [
        "base",
        "mail",
        "ham_utility"
    ],
    "data": [
        "security/profiles.xml",

        "security/models/location.xml",
        "security/models/station.xml",
        "security/models/appliance.xml",

        "views/location.xml",
        "views/station.xml",
        "views/appliance.xml",

        "menu/action.xml",
        "menu/items.xml"
    ],
    "application": True
}
