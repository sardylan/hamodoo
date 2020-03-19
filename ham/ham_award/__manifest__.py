{
    "name": "HAM Awards",
    "version": "13.0.1.0.0",
    "category": "Extra Tools",
    "summary": "HAM award management",
    "depends": [
        "website",
        "portal",
        "ham_utility",
        "web_responsive"
    ],
    "data": [
        "actions/upload.xml",

        "security/groups/award.xml",
        "security/groups/operator.xml",
        "security/groups/qso.xml",
        "security/groups/station.xml",
        "security/groups/upload.xml",
        "security/groups/specialcall.xml",

        "security/categories.xml",
        "security/profiles.xml",

        "security/access/award.xml",
        "security/access/operator.xml",
        "security/access/qso.xml",
        "security/access/station.xml",
        "security/access/upload.xml",
        "security/access/specialcall.xml",

        "views/award.xml",
        "views/operator.xml",
        "views/qso.xml",
        "views/station.xml",
        "views/upload.xml",
        "views/specialcall.xml",

        "menu/action.xml",
        "menu/items.xml",

        "templates/assets/frontend.xml",

        "templates/portal/my_home.xml",
        "templates/portal/breadcrumbs.xml",
        "templates/award/list.xml",
        "templates/award/single.xml",
        "templates/award/public.xml",
        "templates/upload/list.xml"
    ],
    "application": True
}
