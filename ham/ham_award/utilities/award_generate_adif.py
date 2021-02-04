import base64
import datetime
import logging

from odoo import models, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)

DT_FORMAT = "%Y%m%d %H%M%S"


class AwardPublish(models.AbstractModel):
    _name = "ham.utility.award.generate.adif"
    _description = "Utility for publishing Award QSOs to websites"

    @api.model
    def generate(
            self,
            award,
            callsign,
            filename: str = "",
            dt_start: datetime.datetime = None,
            dt_end: datetime.datetime = None,
            dt: datetime.datetime = datetime.datetime.utcnow()
    ):
        qso_obj = self.env["ham.award.qso"]
        ir_attachment_obj = self.env["ir.attachment"]

        adif_utility = self.env["ham.utility.adif"]

        _logger.info("Generating ADIF for %s with callsign %s" % (award, callsign))

        qso_domain = [
            ("award_id", "=", award.id),
            ("local_callsign", "=", callsign.callsign)
        ]

        if dt_start:
            qso_domain.append(("ts_start", ">=", dt_start))

        if dt_end:
            qso_domain.append(("ts_end", "<=", dt_end))

        qsos = qso_obj.search(qso_domain)

        adif_content = adif_utility.generate_adif(qsos, dt=dt)

        if not filename:
            filename = self.generate_name(award, callsign, dt)

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

    @api.model
    def generate_name(self, award, callsign, dt: datetime.datetime, suffix: str = "") -> str:
        filename = f"{dt.strftime(DT_FORMAT)} - {callsign.callsign} - {award.name}"

        if suffix.strip():
            filename = f"{filename} - {suffix.strip()}"

        return f"{filename}.adi"
