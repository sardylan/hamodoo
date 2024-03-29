from odoo import models, api


class AwardQSOCron(models.AbstractModel):
    _name = "ham.cron.award.qso"
    _description = "Updates Award QSO locator from QRZ.com"

    @api.model
    def update_locator_from_qrzcom(self):
        qso_obj = self.env["ham.award.qso"]

        sql_query = "SELECT haq.id " \
                    "FROM ham_award_qso haq " \
                    "WHERE haq.qrzcom_updated = FALSE " \
                    "ORDER BY haq.id " \
                    "LIMIT %(limit)s"

        sql_params = {
            "limit": 50
        }

        self.env.cr.execute(sql_query, sql_params)
        qso_ids = [x[0] for x in self.env.cr.fetchall()]

        qsos = qso_obj.browse(qso_ids)

        qsos.action_update_from_qrzcom()

        qsos.qrzcom_updated = True
