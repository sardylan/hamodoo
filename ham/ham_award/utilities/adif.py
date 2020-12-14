from odoo import models


class AdifUtility(models.AbstractModel):
    _inherit = "ham.utility.adif"

    def generate_adif_qso_extra_fields(self, qso):
        qso_string = super().generate_adif_qso_extra_fields(qso)

        if qso.operator_id:
            qso_string += self._tag_serialize("OPERATOR", qso.operator_id.callsign)

        return qso_string
