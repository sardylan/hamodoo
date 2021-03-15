import logging

from odoo import http
from odoo.http import route, request

_logger = logging.getLogger(__name__)

QSO_PAGE_SIZE = 10


class AwardPublicController(http.Controller):

    @route(
        route="/ham_award/public/award",
        type="http",
        auth="public",
        methods=["GET"],
        csrf=True,
        website=True
    )
    def list(self):
        award_obj = request.env["ham.award"].sudo()

        awards = award_obj.search([
            ("public", "=", True),
        ], order="ts_start DESC")

        values = {
            "awards": awards
        }

        return request.render("ham_award.template_public_award_list", values)

    @route(
        route="/ham_award/public/award/<int:award_id>",
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False,
        cors="*",
        website=True
    )
    def single(self, award_id: int = 0):
        award_obj = request.env["ham.award"].sudo()
        award_qso_obj = request.env["ham.award.qso"].sudo()
        country_obj = request.env["ham.country"].sudo()
        modulation_obj = request.env["ham.modulation"].sudo()

        award = award_obj.search([
            ("public", "=", True),
            ("id", "=", award_id),
        ])

        sql_params = {
            "award_id": award_id
        }

        sql_query = "SELECT count(haq.id) " \
                    "FROM ham_award_qso haq " \
                    "WHERE haq.award_id = %(award_id)s"
        request.env.cr.execute(sql_query, sql_params)
        sql_result = request.env.cr.fetchall()
        award_qso_count = sql_result[0][0]

        sql_query = "SELECT haq.modulation_id," \
                    "   count(haq.id) " \
                    "FROM ham_award_qso haq " \
                    "WHERE haq.award_id = %(award_id)s " \
                    "GROUP BY haq.modulation_id"
        request.env.cr.execute(sql_query, sql_params)
        sql_result = request.env.cr.fetchall()
        modulation_count_full = dict(sorted({
                                                x[0]: x[1]
                                                for x in sql_result
                                            }.items(),
                                            key=lambda x: x[1],
                                            reverse=True
                                            ))

        cw_modulation_ids = modulation_obj.search([("count_as", "=", "cw")]).ids
        phone_modulation_ids = modulation_obj.search([("count_as", "=", "phone")]).ids
        digi_modulation_ids = modulation_obj.search([("count_as", "=", "digi")]).ids

        modulations = {
            "CW": 0,
            "PHONE": 0,
            "DIGI": 0
        }

        for modulation_id, count in modulation_count_full.items():
            if modulation_id in cw_modulation_ids:
                modulations["CW"] += count
            elif modulation_id in phone_modulation_ids:
                modulations["PHONE"] += count
            elif modulation_id in digi_modulation_ids:
                modulations["DIGI"] += count

        longest_qso = award_qso_obj.search([
            ("award_id", "=", award_id),
            ("distance", "!=", 0)
        ], order="distance DESC", limit=1)

        longest_qso = {
            "distance": longest_qso.distance and int(longest_qso.distance) or 0,
            "country": longest_qso.country_id.name,
            "callsign": longest_qso.callsign,
            "mode": longest_qso.modulation_id.name,
            "band": longest_qso.band_id.name,
            "operator": longest_qso.operator_id and longest_qso.operator_id.name_get()[0][1] or "",
        }

        sql_query = "SELECT haq.country_id, " \
                    "   count(haq.id) " \
                    "FROM ham_award_qso haq " \
                    "WHERE haq.award_id = %(award_id)s " \
                    "GROUP BY haq.country_id"
        request.env.cr.execute(sql_query, sql_params)
        sql_result = request.env.cr.fetchall()

        country_count_full = dict(sorted({x[0]: x[1] for x in sql_result}.items(), key=lambda x: x[1], reverse=True))

        countries = []

        for country_id, qso_count in country_count_full.items():
            country = country_obj.browse(country_id)

            countries.append({
                "flag_url": country.flag_url,
                "country_name": country.name,
                "qso_count": qso_count
            })

        award_country_count = len(countries)

        values = {
            "error": {},
            "error_message": [],
            "award": award,
            "award_qso_count": award_qso_count,
            "award_country_count": award_country_count,
            "modulations": modulations,
            "longest_qso": longest_qso,
            "countries": countries
        }

        return request.render("ham_award.template_public_award_single", values)
