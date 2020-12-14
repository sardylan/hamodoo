from odoo import models


class AdifUtility(models.AbstractModel):
    _inherit = "ham.utility.adif"

    def generate_adif_qso_extra_fields(self, qso) -> str:
        qso_string: str = super().generate_adif_qso_extra_fields(qso)

        qso_publish_obj = self.env["ham.award.qso.publish"]

        if qso.operator_id:
            qso_string += self._tag_serialize("OPERATOR", qso.operator_id.callsign)

        website_hrdlog = self.env.ref("ham_utility.data_ham_website_hrdlog")

        qso_publish_hrdlog = qso_publish_obj.search([
            ("qso_id", "=", qso.id),
            ("website_id", "=", website_hrdlog.id),
        ], limit=1, order="create_date DESC")

        if qso_publish_hrdlog:
            qso_string += self._tag_serialize("HRDLOG_QSO_UPLOAD_DATE", qso_publish_hrdlog.ts.strftime("%Y%m%d"))
            qso_string += self._tag_serialize("HRDLOG_QSO_UPLOAD_STATUS", "Y")

        return qso_string
