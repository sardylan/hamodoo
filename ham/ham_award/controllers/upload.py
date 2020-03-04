import base64
import logging

from odoo import http, fields
from odoo.http import route, request, content_disposition

_logger = logging.getLogger(__name__)


class UploadController(http.Controller):
    @route(
        route="/ham_award/upload/file_content/<int:uploadid>",
        type="http",
        auth="user",
        methods=["GET"],
        csrf=True,
        website=True
    )
    def file_content(self, uploadid=0):
        operator_obj = request.env["ham_award.operator"]
        award_obj = request.env["ham_award.award"]
        upload_obj = request.env["ham_award.upload"]

        partner_id = request.env.user.partner_id

        operator_id = operator_obj.search([
            ("partner_id.id", "=", partner_id.id)
        ])

        award_ids = award_obj.search([
            ("operator_ids", "in", [operator_id.id]),
        ])

        upload_id = upload_obj.search([
            ("id", "=", uploadid),
            ("award_id.id", "in", award_ids.ids),
            ("operator_id.id", "=", operator_id.id)
        ])

        raw_content = base64.b64decode(upload_id.with_context(bin_size=False).file_content)

        return request.make_response(raw_content, [
            ("Content-Type", "application/octet-stream"),
            ("Content-Length", len(raw_content)),
            ("Content-Disposition", content_disposition(upload_id.file_name))
        ])

    @route(
        route="/ham_award/upload/add",
        type="http",
        auth="user",
        methods=["POST"],
        csrf=True,
        website=True
    )
    def add(self, **data):
        operator_obj = request.env["ham_award.operator"]
        award_obj = request.env["ham_award.award"]
        upload_obj = request.env["ham_award.upload"]

        for item in ["award", "adif_file"]:
            if item not in data or not data[item]:
                return "error"

        award = data["award"]
        adif_file = data["adif_file"]

        adif_file_filename = adif_file.filename
        adif_file_raw = adif_file.stream.read()

        partner_id = request.env.user.partner_id

        operator_id = operator_obj.search([
            ("partner_id.id", "=", partner_id.id)
        ])
        if not operator_id:
            _logger.error("Operator not found")
            return "error"

        award_id = award_obj.search([
            ("id", "=", award),
            ("operator_ids", "in", [operator_id.id]),
        ])
        if not award_id:
            _logger.error("Award not found")
            return "error"

        values = {
            "ts": fields.Datetime.now(),
            "file_name": adif_file_filename,
            "file_content": base64.b64encode(adif_file_raw),
            "operator_id": operator_id.id,
            "award_id": award_id.id,
        }

        upload_id = upload_obj.create(values)
        if not upload_id:
            _logger.error("Upload not created")

        return request.redirect("/ham_award/award/%d" % award_id.id)
