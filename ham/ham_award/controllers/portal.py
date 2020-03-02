from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import request


class HamAwardCustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super()._prepare_portal_layout_values()

        upload_obj = request.env["ham_award.upload"].sudo()

        values["ham_award_upload_count"] = upload_obj.search_count([
            ("operator_id.partner_id.id", "=", request.env.user.partner_id.id)
        ])

        return values
