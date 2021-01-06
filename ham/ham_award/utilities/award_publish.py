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
        hamqth_utility = self.env["ham.utility.websites.hamqth"]

        cr = self._cr

        _logger.info("Publishing QSOs. Award: %d - Callsign: %s - Website: %s" % (
            award.id,
            callsign.callsign,
            website.name
        ))

        sql_query = """SELECT DISTINCT haq.id
                        FROM ham_award_qso haq
                                 LEFT JOIN ham_award_qso_publish haqp ON haq.id = haqp.qso_id
                        WHERE haq.award_id = %(award_id)s
                          AND haq.local_callsign = %(callsign)s
                          AND (haqp.website_id IS NULL OR haq.id NOT IN (SELECT DISTINCT haq.id
                                                                         FROM ham_award_qso haq
                                                                                  LEFT JOIN ham_award_qso_publish haqp ON haq.id = haqp.qso_id
                                                                         WHERE haq.award_id = %(award_id)s
                                                                           AND haq.local_callsign = %(callsign)s
                                                                           AND (haqp.website_id = %(website_id)s)))"""
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

        if not qso_ids:
            return

        if website.id == self.env.ref("ham_utility.data_ham_website_eqsl").id:
            if not callsign.eqsl_enabled:
                raise UserError(_("eQSL not enabled"))

            for qso_id in qso_ids:
                qso = qso_obj.browse(qso_id)
                eqsl_utility.upload_qso(
                    qso=qso,
                    username=callsign.eqsl_username,
                    password=callsign.eqsl_password,
                    qth_nickname=callsign.eqsl_qth_nickname
                )
                qso_publish_obj.create([{
                    "qso_id": qso.id,
                    "website_id": website.id
                }])
                cr.commit()

        elif website.id == self.env.ref("ham_utility.data_ham_website_hrdlog").id:
            if not callsign.hrdlog_enabled:
                raise UserError(_("HRDLog not enabled"))

            for qso_id in qso_ids:
                qso = qso_obj.browse(qso_id)
                hrdlog_utility.upload_qso(
                    qso=qso,
                    callsign=callsign.hrdlog_callsign,
                    code=callsign.hrdlog_code
                )
                qso_publish_obj.create([{
                    "qso_id": qso.id,
                    "website_id": website.id
                }])
                cr.commit()

        elif website.id == self.env.ref("ham_utility.data_ham_website_hamqth").id:
            if not callsign.hamqth_enabled:
                raise UserError(_("HamQTH not enabled"))

            qsos = qso_obj.browse(qso_ids)
            adif_data = adif_utility.generate_adif(qsos)

            hamqth_utility.upload_adif(
                username=callsign.hamqth_username,
                password=callsign.hamqth_password,
                callsign=callsign.hamqth_callsign,
                adif_data=adif_data
            )

            for qso_id in qso_ids:
                qso = qso_obj.browse(qso_id)
                qso_publish_obj.create([{
                    "qso_id": qso.id,
                    "website_id": website.id
                }])

        else:
            raise ValidationError(_("Website not implemented"))
