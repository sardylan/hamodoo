from odoo import models, api


class ModulationUtility(models.AbstractModel):
    _name = "hamutility.utility_modulation"
    _description = "Utility methods for Modulation entities"

    @api.model
    def compute_bandwidth_tag(self, bandwidth=0):
        letter = "H"
        multiplier = 1

        if 1000 <= bandwidth < 1000000:
            letter = "K"
            multiplier = 1000
        elif 1000000 <= bandwidth < 1000000000:
            letter = "M"
            multiplier = 1000000
        elif 1000000000 <= bandwidth < 1000000000000:
            letter = "G"
            multiplier = 1000000000
        elif 1000000000000 <= bandwidth < 1000000000000000:
            letter = "T"
            multiplier = 1000000000000

        value = bandwidth / multiplier
        integer = int(value)
        decimal = value - integer

        text = "%d%s" % (integer, letter)

        if len(text) == 4:
            return text
        elif len(text) == 3:
            return ("%s%.01f" % (text, decimal)).replace("0.", "")
        elif len(text) == 2:
            return ("%s%.02f" % (text, decimal)).replace("0.", "")
        else:
            return ("%s%.03f" % (text, decimal)).replace("0.", "")
