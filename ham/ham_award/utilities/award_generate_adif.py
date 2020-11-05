import base64
import datetime
import logging

from odoo import models, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


class AwardPublish(models.AbstractModel):
    _name = "ham.utility.award.generate.adif"
    _description = "Utility for publishing Award QSOs to websites"

    @api.model
    def generate(self, award, callsign):
        qso_obj = self.env["ham.award.qso"]
        ir_attachment_obj = self.env["ir.attachment"]

        adif_utility = self.env["ham.utility.adif"]

        _logger.info("Generating ADIF for %s with callsign %s" % (award, callsign))

        qsos = qso_obj.search([
            ("award_id", "=", award.id),
            ("local_callsign", "=", callsign.callsign)
        ])

        adif_content = adif_utility.generate_adif(qsos)

        ts_string = datetime.datetime.utcnow().strftime("%Y%m%d %H%M%S")
        filename = "%s - %s - %s.adi" % (ts_string, callsign.callsign, award.name)

        values = {
            "name": filename,
            "type": "binary",
            "datas": base64.b64encode(adif_content.encode()),
            "res_model": award._name,
            "res_id": award.id,
            "store_fname": filename,
            "mimetype": "text/plain",
        }

        ir_attachments = ir_attachment_obj.create([values])
        if len(ir_attachments) != 1:
            raise ValidationError(_("Unable to create attachment"))

        ir_attachment = ir_attachments[0]
        return ir_attachment
