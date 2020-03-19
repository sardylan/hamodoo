import datetime
import logging
import re

from odoo import http, fields
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.http import route, request

_logger = logging.getLogger(__name__)

QSO_PAGE_SIZE = 10


class AwardController(http.Controller):

    @route(
        route="/ham_award/public/award",
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False,
        website=True
    )
    def public_award(self):
        award_obj = request.env["ham_award.award"].sudo()

        award_ids = award_obj.search([
            ("public", "=", True)
        ])

        values = {
            "award_ids": award_ids
        }

        return request.render("ham_award.template_award_public_awards", values)

    @route(
        route=[
            "/ham_award/public/award/<int:awardid>",
            "/ham_award/public/award/<int:awardid>/page/<int:page>"
        ],
        type="http",
        auth="public",
        methods=["GET", "POST"],
        csrf=False,
        website=True
    )
    def public_award_qso(self, awardid, page=1, **get):
        award_obj = request.env["ham_award.award"].sudo()
        qso_obj = request.env["ham_award.qso"].sudo()

        award_id = award_obj.search([
            ("id", "=", awardid),
            ("public", "=", True),
        ], limit=1)

        qso_count = qso_obj.search_count([
            ("award_id", "=", award_id.id)
        ])

        country_count = len(qso_obj.read_group(
            domain=[("award_id", "=", award_id.id)],
            fields=["country_id"],
            groupby=["country_id"]
        ))

        qso_domain = [
            ("award_id", "=", award_id.id)
        ]

        search_callsign = ""

        if "search_callsign" in get and get["search_callsign"]:
            search_callsign = get["search_callsign"].strip().upper()
            search_callsign = re.sub(r"[^0-9A-Z/]+", "", search_callsign)

            qso_domain.extend([
                ("callsign", "ilike", search_callsign)
            ])

        search_qso_count = qso_obj.search_count(qso_domain)

        qso_ids = qso_obj.search(
            args=qso_domain,
            offset=((page - 1) * QSO_PAGE_SIZE),
            limit=QSO_PAGE_SIZE
        )

        pager = portal_pager(
            url="/ham_award/public/award/%d" % award_id.id,
            total=search_qso_count,
            page=page,
            step=QSO_PAGE_SIZE,
            url_args={
                "search_callsign": search_callsign
            }
        )

        values = {
            "award_id": award_id,
            "qso_count": qso_count,
            "country_count": country_count,
            "qso_ids": qso_ids,
            "pager": pager,
            "search_callsign": search_callsign
        }

        return request.render("ham_award.template_award_public_award_qsos", values)

    @route(
        route="/ham_award/private/award",
        type="http",
        auth="user",
        methods=["GET"],
        csrf=True,
        website=True
    )
    def list(self, **data):
        operator_obj = request.env["ham_award.operator"]
        award_obj = request.env["ham_award.award"]

        partner_id = request.env.user.partner_id

        operator_id = operator_obj.search([
            ("partner_id.id", "=", partner_id.id)
        ])

        award_ids = award_obj.search([
            ("operator_ids", "in", [operator_id.id])
        ])

        values = {
            "error": {},
            "error_message": [],
            "page_name": "award_list",
            "award_ids": award_ids
        }

        return request.render("ham_award.template_award_list", values)

    @route(
        route="/ham_award/private/award/<int:awardid>",
        type="http",
        auth="user",
        methods=["GET"],
        csrf=True,
        website=True
    )
    def single(self, awardid=0):
        operator_obj = request.env["ham_award.operator"]
        award_obj = request.env["ham_award.award"]
        qso_obj = request.env["ham_award.qso"]
        upload_obj = request.env["ham_award.upload"]
        specialcall_obj = request.env["ham_award.specialcall"]

        country_prefix_obj = request.env["ham_utility.country_prefix"]
        modulation_obj = request.env["ham_utility.modulation"]

        partner_id = request.env.user.partner_id

        operator_id = operator_obj.search([
            ("partner_id.id", "=", partner_id.id)
        ])

        award_id = award_obj.search([
            ("id", "=", awardid),
            ("operator_ids", "in", [operator_id.id]),
        ])

        upload_ids = upload_obj.search([
            ("award_id.id", "in", award_id.ids),
            ("operator_id.id", "=", operator_id.id)
        ])

        modulationids_cw = modulation_obj.search([("name", "in", ["CW"])]).ids
        modulationids_digi = modulation_obj.search([("name", "in", ["FT8", "RTTY", "BPSK31"])]).ids
        modulationids_phone = modulation_obj.search([("name", "in", ["SSB", "LSB", "USB"])]).ids

        domain_total_qso = [
            ("award_id", "=", award_id.id)
        ]

        domain_total_qso_cw = domain_total_qso.copy()
        domain_total_qso_cw.append(("modulation_id", "in", modulationids_cw))

        domain_total_qso_digi = domain_total_qso.copy()
        domain_total_qso_digi.append(("modulation_id", "in", modulationids_digi))

        domain_total_qso_phone = domain_total_qso.copy()
        domain_total_qso_phone.append(("modulation_id", "in", modulationids_phone))

        your_total_qso = [
            ("award_id", "=", award_id.id),
            ("operator_id.partner_id", "=", request.env.user.partner_id.id)
        ]

        your_total_qso_cw = your_total_qso.copy()
        your_total_qso_cw.append(("modulation_id", "in", modulationids_cw))

        your_total_qso_digi = your_total_qso.copy()
        your_total_qso_digi.append(("modulation_id", "in", modulationids_digi))

        your_total_qso_phone = your_total_qso.copy()
        your_total_qso_phone.append(("modulation_id", "in", modulationids_phone))

        total_qso_count = qso_obj.search_count(domain_total_qso)
        your_qso_count = qso_obj.search_count(your_total_qso)
        your_qso_percent = 100 * (float(your_qso_count) / total_qso_count)

        infos = {
            "total_qso": {
                "TOTAL": total_qso_count,
                "CW": qso_obj.search_count(domain_total_qso_cw),
                "DIGI": qso_obj.search_count(domain_total_qso_digi),
                "PHONE": qso_obj.search_count(domain_total_qso_phone),
            },
            "your_qso": {
                "TOTAL": your_qso_count,
                "PERCENT": your_qso_percent,
                "CW": qso_obj.search_count(your_total_qso_cw),
                "DIGI": qso_obj.search_count(your_total_qso_digi),
                "PHONE": qso_obj.search_count(your_total_qso_phone),
            }
        }

        countries = qso_obj.read_group(
            domain=domain_total_qso,
            fields=["country_id"],
            groupby=["country_id"]
        )

        country_list = []

        for country in countries:
            name = country["country_id"] and country["country_id"][1] or ""
            count = country["country_id_count"]

            countryid = country["country_id"] and country["country_id"][0] or False

            country_prefix_ids = country_prefix_obj.search([
                ("country_id", "=", countryid)
            ])

            prefixes = []

            for country_prefix_id in country_prefix_ids:
                prefixes.append(country_prefix_id.prefix)

            country_list.append({
                "name": name,
                "count": count,
                "prefixes": " ".join(prefixes)
            })

        countries = sorted(country_list, key=lambda x: x["count"], reverse=True)

        infos["countries"] = countries

        specialcall_ids = specialcall_obj.search([
            ("award_id", "=", award_id.id),
            ("callsign", "!=", award_id.common_callsign)
        ])

        days = (award_id.ts_end - award_id.ts_start).days + 1

        specialcalls = []

        specialcalls_header = ["Day"]

        for i in range(0, days):
            ts_start = (award_id.ts_start + datetime.timedelta(days=i))
            specialcalls_header.append(ts_start.strftime("%d"))

        specialcalls.append(specialcalls_header)

        for specialcall_id in specialcall_ids:
            specialcall_data = [specialcall_id.callsign]

            for i in range(0, days):
                ts_start = (award_id.ts_start + datetime.timedelta(days=i)).replace(
                    hour=0, minute=0, second=0, microsecond=0
                )

                ts_end = ts_start.replace(hour=23, minute=59, second=59, microsecond=999999)

                domain = [
                    ("award_id", "=", award_id.id),
                    ("callsign", "ilike", specialcall_id.callsign),
                    ("ts_start", ">=", ts_start.strftime(fields.DATETIME_FORMAT)),
                    ("ts_start", "<=", ts_end.strftime(fields.DATETIME_FORMAT))
                ]

                domain_cw = domain.copy()
                domain_cw.append(("modulation_id", "in", modulationids_cw))

                domain_digi = domain.copy()
                domain_digi.append(("modulation_id", "in", modulationids_digi))

                domain_phone = domain.copy()
                domain_phone.append(("modulation_id", "in", modulationids_phone))

                qso_count_cw = qso_obj.search_count(domain_cw)
                qso_count_digi = qso_obj.search_count(domain_digi)
                qso_count_phone = qso_obj.search_count(domain_phone)

                qso_count = "%s%s%s" % (
                    qso_count_cw > 0 and "C" or "",
                    qso_count_digi > 0 and "D" or "",
                    qso_count_phone > 0 and "P" or ""
                )

                specialcall_data.append(qso_count)

            specialcalls.append(specialcall_data)

        infos["specialcalls"] = specialcalls

        values = {
            "error": {},
            "error_message": [],
            "page_name": "award_single",
            "award_id": award_id,
            "infos": infos,
            "upload_ids": upload_ids
        }

        return request.render("ham_award.template_award_single", values)
