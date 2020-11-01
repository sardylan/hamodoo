import base64
import logging

from odoo import http, fields
from odoo.http import route, request, content_disposition

_logger = logging.getLogger(__name__)


class UploadController(http.Controller):
    @route(
        route="/ham_award/private/upload/file_content/<int:uploadid>",
        type="http",
        auth="user",
        methods=["GET"],
        csrf=True,
        website=True
    )
    def file_content(self, upload_id: int = 0):
        operator_obj = request.env["ham.award.operator"]
        award_obj = request.env["ham.award"]
        upload_obj = request.env["ham.award.upload"]

        partner = request.env.user.partner_id

        operator = operator_obj.search([
            ("partner_id", "=", partner.id)
        ])

        awards = award_obj.search([
            ("operator_ids", "in", [operator.id]),
        ])

        upload = upload_obj.search([
            ("id", "=", upload_id),
            ("award_id", "in", awards.ids),
            ("operator_id", "=", operator.id)
        ])

        raw_content = base64.b64decode(upload.with_context(bin_size=False).file_content)

        return request.make_response(raw_content, [
            ("Content-Type", "application/octet-stream"),
            ("Content-Length", len(raw_content)),
            ("Content-Disposition", content_disposition(upload.file_name))
        ])

    @route(
        route="/ham_award/private/upload/add",
        type="http",
        auth="user",
        methods=["POST"],
        csrf=True,
        website=True
    )
    def add(self, **data):
        operator_obj = request.env["ham.award.operator"]
        award_obj = request.env["ham.award"]
        upload_obj = request.env["ham.award.upload"]

        for item in ["award", "adif_file"]:
            if item not in data or not data[item]:
                return "error"

        award = data["award"]
        adif_file = data["adif_file"]

        adif_file_filename = adif_file.filename
        adif_file_raw = adif_file.stream.read()

        partner = request.env.user.partner_id

        operator = operator_obj.search([
            ("partner_id", "=", partner.id)
        ])
        if not operator:
            _logger.error("Operator not found")
            return "error"

        award = award_obj.search([
            ("id", "=", award),
            ("operator_ids", "in", [operator.id]),
        ])
        if not award:
            _logger.error("Award not found")
            return "error"

        values = {
            "ts": fields.Datetime.now(),
            "file_name": adif_file_filename,
            "file_content": base64.b64encode(adif_file_raw),
            "operator_id": operator.id,
            "award_id": award.id,
        }

        upload = upload_obj.create(values)
        if not upload:
            _logger.error("Upload not created")

        return request.redirect("/ham_award/private/award/%d" % award.id)
