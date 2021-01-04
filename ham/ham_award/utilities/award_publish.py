import logging

from odoo import models, api
from odoo.exceptions import ValidationError, UserError
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


class AwardPublish(models.AbstractModel):
    _name = "ham.utility.award.publish"
    _description = "Utility for publishing Award QSOs to websites"

    @api.model
    def publish_not_published_qsos(self, award, callsign, website):
        qso_obj = self.env["ham.award.qso"]
        qso_publish_obj = self.env["ham.award.qso.publish"]

        adif_utility = self.env["ham.utility.adif"]

        eqsl_utility = self.env["ham.utility.websites.eqsl"]
        hrdlog_utility = self.env["ham.utility.websites.hrdlog"]

        cr = self._cr

        _logger.info("Publishing QSOs. Award: %d - Callsign: %s - Website: %s" % (
            award.id,
            callsign.callsign,
            website.name
        ))

        sql_query = """SELECT haq.id
                        FROM ham_award_qso haq
                                 LEFT JOIN ham_award_qso_publish haqp ON haq.id = haqp.qso_id
                        WHERE haq.award_id = %(award_id)s
                          AND haq.local_callsign = %(callsign)s
                          AND (haqp.website_id != %(website_id)s OR haqp.website_id IS NULL)"""

        sql_params = {
            "award_id": award.id,
            "callsign": callsign.callsign,
            "website_id": website.id
        }

        cr.execute(query=sql_query, params=sql_params)
        qso_ids = [x[0] for x in cr.fetchall()]

        _logger.info("Publishing QSOs. Found %s QSOs with %s not uploaded to %s" % (
            len(qso_ids),
            callsign.callsign,
            website.name
        ))

        for qso_id in qso_ids:
            qso = qso_obj.browse(qso_id)

            if website.tag == self.env.ref("ham_utility.data_ham_website_eqsl").tag:
                if not callsign.eqsl_enabled:
                    raise UserError(_("eQSL not enabled"))

                qso_adif_data = adif_utility.generate_adif_qso(qso)

                eqsl_utility.upload_qso(
                    username=callsign.eqsl_username,
                    password=callsign.eqsl_password,
                    adif_data=qso_adif_data
                )

                qso_publish_obj.create([{
                    "qso_id": qso.id,
                    "website_id": website.id
                }])

                cr.commit()

            elif website.tag == self.env.ref("ham_utility.data_ham_website_hrdlog").tag:
                if not callsign.hrdlog_enabled:
                    raise UserError(_("HRDLog not enabled"))

                qso_adif_data = adif_utility.generate_adif_qso(qso)

                hrdlog_utility.upload_qso(
                    callsign=callsign.hrdlog_callsign,
                    code=callsign.hrdlog_code,
                    adif_data=qso_adif_data
                )

                qso_publish_obj.create([{
                    "qso_id": qso.id,
                    "website_id": website.id
                }])

                cr.commit()

            else:
                raise ValidationError(_("Upload website not supported"))
