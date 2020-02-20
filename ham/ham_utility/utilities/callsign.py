from odoo import models, api


class CallsignUtility(models.AbstractModel):
    _name = "ham_utility.utility_callsign"
    _description = "Callsign utilities"

    @api.model
    def uppercase(self, value):
        return value and value.strip().upper() or False
