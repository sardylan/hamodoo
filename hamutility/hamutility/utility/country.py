from odoo import models, api


class CallsignUtility(models.AbstractModel):
    _name = "hamutility.utility_callsign"
    _description = "Utility for searching related country related to callsign"

    @api.model
    def get_country(self, callsign=""):
        if not callsign:
            return False

        countryprefix_obj = self.env["hamutility.countryprefix"]

        countryprefix_id = countryprefix_obj.search([("prefix", "=", callsign[:4])]) \
                           or countryprefix_obj.search([("prefix", "=", callsign[:3])]) \
                           or countryprefix_obj.search([("prefix", "=", callsign[:2])]) \
                           or countryprefix_obj.search([("prefix", "=", callsign[:1])])

        if not countryprefix_id:
            return False

        return countryprefix_id.country_id
