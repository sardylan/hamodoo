import base64
import logging

from odoo import http
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
    def single(self, uploadid=0):
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
