from odoo import http
from odoo.http import route, request


class UploadsController(http.Controller):

    @route(
        route="/ham_award/uploads",
        type="http",
        auth="user",
        methods=["GET", "POST"],
        csrf=True,
        website=True
    )
    def list(self, **data):
        if request.httprequest.method == "GET":
            return self.list_get(**data)

        if request.httprequest.method == "POST":
            return self.list_post(**data)

    def list_get(self, **data):
        upload_obj = request.env["ham_award.upload"]

        upload_ids = upload_obj.search([
            ("operator_id.partner_id.id", "=", request.env.user.partner_id.id)
        ])

        values = {
            "error": {},
            "error_message": [],
            "page_name": "uploads_list",
            "upload_ids": upload_ids
        }

        return request.render("ham_award.template_uploads_list", values)

    def list_post(self, **data):
        print(data)

        return self.list_get(**data)
