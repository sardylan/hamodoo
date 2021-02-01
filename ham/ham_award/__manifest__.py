{
    "name": "HAM Awards",
    "version": "14.0.2.8.3",
    "category": "HAM Radio",
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
        "security/profiles.xml",

        "security/access/qso.xml",
        "security/access/operator.xml",
        "security/access/award.xml",
        "security/access/upload.xml",

        "security/wizard/award_publish.xml",
        "security/wizard/award_generate_adif.xml",
        "security/wizard/upload_reject.xml",

        "security/utilities/award_publish.xml",

        "views/qso.xml",
        "views/operator.xml",
        "views/award.xml",
        "views/upload.xml",

        "wizard/award_publish.xml",
        "wizard/award_generate_adif.xml",
        "wizard/upload_reject.xml",

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
