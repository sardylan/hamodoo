from odoo.addons.portal.controllers.portal import CustomerPortal

from odoo.http import request


class HamAwardCustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super()._prepare_portal_layout_values()

        operator_obj = request.env["ham_award.operator"]
        award_obj = request.env["ham_award.award"]

        partner_id = request.env.user.partner_id

        operator_id = operator_obj.search([
            ("partner_id.id", "=", partner_id.id)
        ])

        award_count = award_obj.search_count([
            ("operator_ids", "in", [operator_id.id])
        ])

        values["ham_award_award_count"] = award_count

        return values
