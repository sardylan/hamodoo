import logging

from odoo import http
from odoo.http import route, request

_logger = logging.getLogger(__name__)

QSO_PAGE_SIZE = 10

AWARD_COUNTRY_COUNT = 10


class AwardPublicController(http.Controller):

    @route(
        route="/ham_award/public/award",
        type="http",
        auth="user",
        methods=["GET"],
        csrf=True,
        website=True
    )
    def list(self):
        award_obj = request.env["ham.award"]

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
        auth="user",
        methods=["GET"],
        csrf=True,
        website=True
    )
    def single(self, award_id: int = 0):
        award_obj = request.env["ham.award"]
        country_obj = request.env["ham.country"]

        award = award_obj.search([
            ("public", "=", True),
            ("id", "=", award_id),
        ])

        sql_query = "SELECT haq.country_id, " \
                    "   count(haq.id) " \
                    "FROM ham_award_qso haq " \
                    "WHERE award_id = %(award_id)s " \
                    "GROUP BY haq.country_id"

        sql_params = {
            "award_id": award_id
        }

        request.env.cr.execute(sql_query, sql_params)
        sql_result = request.env.cr.fetchall()
        country_count_full = dict(sorted({
            x[0]: x[1]
            for x in sql_result
        }.items(), key=lambda x: x[1], reverse=True))
        country_ids = list(country_count_full.keys())

        country_counts = []

        for i in range(0, AWARD_COUNTRY_COUNT):
            country_id = country_ids[i]
            country = country_obj.browse(country_id)
            qso_count = country_count_full[country.id]

            country_counts.append({
                "country_name": country.name,
                "qso_count": qso_count
            })

        values = {
            "error": {},
            "error_message": [],
            "award": award,
            "country_counts": country_counts
        }

        return request.render("ham_award.template_public_award_single", values)
