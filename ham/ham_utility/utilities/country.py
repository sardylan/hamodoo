from odoo import models, api


class CallsignUtility(models.AbstractModel):
    _name = "ham.utility.country"
    _description = "Utility for searching related country related to callsign"

    @api.model
    def get_country(self, callsign: str = ""):
        if not callsign:
            return False

        country_prefix_obj = self.env["ham.country.prefix"]

        country_prefix_id = country_prefix_obj.search([("prefix", "=", callsign[:4])]) \
                            or country_prefix_obj.search([("prefix", "=", callsign[:3])]) \
                            or country_prefix_obj.search([("prefix", "=", callsign[:2])]) \
                            or country_prefix_obj.search([("prefix", "=", callsign[:1])])

        if not country_prefix_id:
            return False

        return country_prefix_id.country_id
