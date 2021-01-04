import datetime
import logging

from odoo import http, fields
from odoo.http import route, request

_logger = logging.getLogger(__name__)

QSO_PAGE_SIZE = 10


class AwardController(http.Controller):

    @route(
        route="/ham_award/private/award",
        type="http",
        auth="user",
        methods=["GET"],
        csrf=True,
        website=True
    )
    def list(self):
        operator_obj = request.env["ham.award.operator"]
        award_obj = request.env["ham.award"]

        partner = request.env.user.partner_id

        operator = operator_obj.search([
            ("partner_id", "=", partner.id)
        ])

        now = fields.Datetime.now()
        awards = award_obj.search([
            ("operator_ids", "in", [operator.id]),
            ("ts_start", "<=", now + datetime.timedelta(days=7)),
            ("ts_end", ">=", now - datetime.timedelta(days=90)),
            "|",
            ("ts_upload_start", "=", False),
            ("ts_upload_start", "<=", now)
        ], order="ts_start DESC")

        values = {
            "error": {},
            "error_message": [],
            "page_name": "award_list",
            "awards": awards
        }

        return request.render("ham_award.template_private_award_list", values)

    @route(
        route="/ham_award/private/award/<int:award_id>",
        type="http",
        auth="user",
        methods=["GET"],
        csrf=True,
        website=True
    )
    def single(self, award_id: int = 0):
        award_obj = request.env["ham.award"]
        operator_obj = request.env["ham.award.operator"]
        upload_obj = request.env["ham.award.upload"]

        partner = request.env.user.partner_id

        operator = operator_obj.search([
            ("partner_id", "=", partner.id)
        ])

        award = award_obj.search([
            ("id", "=", award_id),
            ("operator_ids", "in", [operator.id]),
        ])

        uploads = upload_obj.search([
            ("award_id", "in", award.ids),
            ("operator_id", "=", operator.id)
        ])

        values = {
            "error": {},
            "error_message": [],
            "page_name": "award_single",
            "award": award,
            "uploads": uploads
        }

        return request.render("ham_award.template_private_award_single", values)

    @route(
        route="/ham_award/private/award/<int:award_id>/upload/<int:upload_id>",
        type="http",
        auth="user",
        methods=["GET"],
        csrf=True,
        website=True
    )
    def single_upload(self, award_id: int = 0, upload_id: int = 0):
        award_obj = request.env["ham.award"]
        operator_obj = request.env["ham.award.operator"]
        upload_obj = request.env["ham.award.upload"]

        partner = request.env.user.partner_id

        operator = operator_obj.search([
            ("partner_id", "=", partner.id)
        ])

        award = award_obj.search([
            ("id", "=", award_id),
            ("operator_ids", "in", [operator.id]),
        ])

        upload = upload_obj.search([
            ("award_id", "in", award.ids),
            ("operator_id", "=", operator.id),
            ("id", "=", upload_id)
        ])

        values = {
            "error": {},
            "error_message": [],
            "page_name": "award_single_upload",
            "award": award,
            "upload": upload
        }

        return request.render("ham_award.template_private_award_single_upload", values)
