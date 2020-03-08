import logging

from odoo import http
from odoo.http import route, request

_logger = logging.getLogger(__name__)


class AwardController(http.Controller):

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
    def single(self, awardid=0, **data):
        operator_obj = request.env["ham_award.operator"]
        award_obj = request.env["ham_award.award"]
        upload_obj = request.env["ham_award.upload"]

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

        values = {
            "error": {},
            "error_message": [],
            "page_name": "award_single",
            "award_id": award_id,
            "upload_ids": upload_ids
        }

        return request.render("ham_award.template_award_single", values)
