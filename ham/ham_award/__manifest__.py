{
    "name": "HAM Awards",
    "version": "15.0.2.12.0",
    "category": "HAM Radio",
    "summary": "HAM award management",
    "sequence": 0,
    "author": "Luca Cireddu",
    "license": "GPL-3",
    "depends": [
        "website",
        "portal",
        "contacts",
        "ham_utility",
    ],
    "data": [
        "cron/award_qso.xml",

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

        "templates/portal/my_home.xml",
        "templates/portal/breadcrumbs.xml",

        "templates/private/award/list.xml",
        "templates/private/award/single.xml",
        "templates/private/award/single_upload.xml",

        "templates/public/award/list.xml",
        "templates/public/award/single.xml",

        "actions/qso.xml",

        "menu/action.xml",
        "menu/items.xml"
    ],
    "assets": {
        "web.assets_frontend": [
            "ham_award/static/src/css/public/award.css"
        ],
    },
    "application": True
}
