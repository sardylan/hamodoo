import logging

from odoo import http
from odoo.http import route, request

_logger = logging.getLogger(__name__)


class AwardController(http.Controller):

    @route(
        route="/ham_award/award",
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
        route="/ham_award/award/<int:awardid>",
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

    # def list_get(self, **data):
    #     operator_obj = request.env["ham_award.operator"]
    #     award_obj = request.env["ham_award.award"]
    #     upload_obj = request.env["ham_award.upload"]
    #
    #     partner_id = request.env.user.partner_id
    #
    #     operator_id = operator_obj.search([
    #         ("partner_id.id", "=", partner_id.id)
    #     ])
    #
    #     award_ids = award_obj.search([
    #         ("operator_ids", "in", [operator_id.id])
    #     ])
    #
    #     upload_ids = upload_obj.search([
    #         ("award_id.id", "in", award_ids.ids),
    #         ("operator_id.id", "=", operator_id.id)
    #     ])
    #
    #     values = {
    #         "error": {},
    #         "error_message": [],
    #         "page_name": "uploads_list",
    #         "upload_ids": upload_ids,
    #         "award_ids": award_ids
    #     }
    #
    #     return request.render("ham_award.template_uploads_list", values)
    #
    # def list_post(self, **data):
    #     award_obj = request.env["ham_award.award"]
    #     operator_obj = request.env["ham_award.operator"]
    #     upload_obj = request.env["ham_award.upload"]
    #
    #     for item in ["adif_file", "award"]:
    #         if item not in data or not data[item]:
    #             return request.redirect("/ham_award/upload")
    #
    #     adif_file = data["adif_file"]
    #     adif_file_filename = adif_file.filename
    #     adif_file_raw = adif_file.stream.read()
    #
    #     awardid = data["award"]
    #     award_id = award_obj.search([
    #         ("id", "=", awardid)
    #     ])
    #     if not award_id:
    #         _logger.error("Award not found")
    #         return request.redirect("/ham_award/upload")
    #
    #     operator_id = operator_obj.search([
    #         ("partner_id.id", "=", request.env.user.partner_id.id)
    #     ])
    #     if not operator_id:
    #         _logger.error("Operator not found")
    #         return request.redirect("/ham_award/upload")
    #
    #     values = {
    #         "ts": fields.Datetime.now(),
    #         "file_name": adif_file_filename,
    #         "file_content": base64.b64encode(adif_file_raw),
    #         "operator_id": operator_id.id,
    #         "award_id": award_id.id,
    #     }
    #
    #     upload_id = upload_obj.create(values)
    #     if not upload_id:
    #         _logger.error("Upload not created")
    #
    #     return request.redirect("/ham_award/upload")
