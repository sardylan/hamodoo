import logging

from odoo import models, api

_logger = logging.getLogger(__name__)


class AwardPublish(models.AbstractModel):
    _name = "ham.utility.award.publish"
    _description = "Utility for publishing Award QSOs to websites"

    @api.model
    def publish_not_published_qsos(self, award, callsign, website):
        qso_obj = self.env["ham.award.qso"]
        qso_publish_obj = self.env["ham.award.qso.publish"]

        hrdlog_utility = self.env["ham.utility.websites.hrdlog"]
        adif_utility = self.env["ham.utility.adif"]

        cr = self._cr

        _logger.info("Publishing QSOs. Award: %s - Callsign: %s - Website: %s" % (award, callsign, website))

        sql_query = """SELECT haq.id
                        FROM ham_award_qso haq
                                 LEFT JOIN ham_award_qso_publish haqp ON haq.id = haqp.qso_id
                        WHERE haq.award_id = %(award_id)s
                          AND haq.local_callsign = %(callsign)s
                          AND (haqp.website_tag != %(website_tag)s OR haqp.website_tag IS NULL)"""

        sql_params = {
            "award_id": award.id,
            "callsign": callsign.callsign,
            "website_tag": website
        }

        cr.execute(query=sql_query, params=sql_params)
        qso_ids = [x[0] for x in cr.fetchall()]

        _logger.info("Publishing QSOs. Found %s QSOs with %s not uploaded to %s" % (len(qso_ids), callsign, website))

        for qso_id in qso_ids:
            qso = qso_obj.browse(qso_id)

            if website == "hrdlog":
                qso_adif_data = adif_utility.generate_adif_qso(qso)

                try:
                    hrdlog_utility.upload_qso(
                        callsign=callsign.hrdlog_callsign,
                        code=callsign.hrdlog_code,
                        adif_data=qso_adif_data
                    )
                except Exception as e:
                    _logger.error(e)
                    continue

                qso_publish_obj.create([{
                    "qso_id": qso.id,
                    "website_tag": "hrdlog",
                    "website": "HRDLog",
                }])

                cr.commit()
