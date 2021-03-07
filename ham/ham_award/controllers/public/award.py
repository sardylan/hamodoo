import logging

from odoo import http
from odoo.http import route, request

_logger = logging.getLogger(__name__)

QSO_PAGE_SIZE = 10

MOST_CONTACTED_COUNTRIES = 10


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
        csrf=True,
        website=True
    )
    def single(self, award_id: int = 0):
        award_obj = request.env["ham.award"].sudo()
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

        sql_query = "SELECT haq.country_id, " \
                    "   count(haq.id) " \
                    "FROM ham_award_qso haq " \
                    "WHERE haq.award_id = %(award_id)s " \
                    "GROUP BY haq.country_id"
        request.env.cr.execute(sql_query, sql_params)
        sql_result = request.env.cr.fetchall()
        country_count_full = dict(sorted({
                                             x[0]: x[1]
                                             for x in sql_result
                                         }.items(),
                                         key=lambda x: x[1],
                                         reverse=True
                                         ))
        country_ids = list(country_count_full.keys())

        most_contacted_countries = []

        for i in range(0, MOST_CONTACTED_COUNTRIES):
            country_id = country_ids[i]
            country = country_obj.browse(country_id)
            qso_count = country_count_full[country.id]

            most_contacted_countries.append({
                "country_name": country.name,
                "qso_count": qso_count
            })

        values = {
            "error": {},
            "error_message": [],
            "award": award,
            "award_qso_count": award_qso_count,
            "award_country_count": len(country_ids),
            "modulations": modulations,
            "most_contacted_countries_count": MOST_CONTACTED_COUNTRIES,
            "most_contacted_countries": most_contacted_countries
        }

        return request.render("ham_award.template_public_award_single", values)
