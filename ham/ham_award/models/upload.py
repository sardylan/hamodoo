import base64
import datetime
import json
import logging

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

SELECTION_STATE = [
    ("draft", "To parse"),
    ("parsed", "Parsed"),
    ("error", "Error")
]

_logger = logging.getLogger(__name__)


class Upload(models.Model):
    _name = "ham.award.upload"
    _inherit = "mail.thread"
    _description = "ADIF Upload by Operator"
    _order = "ts DESC"

    ts = fields.Datetime(
        string="Date & Time of upload",
        required=True,
        default=lambda self: self._default_ts(),
        tracking=True
    )

    file_name = fields.Char(
        string="File name",
        tracking=True
    )

    file_content = fields.Binary(
        string="File",
        help="Uploaded file",
        required=True,
        attachment=True,
        tracking=True
    )

    operator_id = fields.Many2one(
        string="Operator",
        help="Operator",
        comodel_name="ham.award.operator",
        required=True,
        tracking=True
    )

    award_id = fields.Many2one(
        string="Award",
        help="Related award",
        comodel_name="ham.award",
        required=True,
        tracking=True
    )

    state = fields.Selection(
        string="Status",
        help="Upload status",
        selection=SELECTION_STATE,
        required=True,
        default="draft",
        tracking=True
    )

    headers = fields.Char(
        string="Headers",
        help="ADIF headers",
        readonly=True,
        tracking=True
    )

    errors = fields.Char(
        string="Errors",
        help="Error during ADIF parsing",
        readonly=True,
        tracking=True
    )

    qso_ids = fields.One2many(
        string="QSOs",
        help="Related QSOs",
        comodel_name="ham.award.qso",
        inverse_name="upload_id",
        readonly=True,
        tracking=True
    )

    name = fields.Char(
        string="Name",
        help="Name",
        compute="_compute_name",
        readonly=True
    )

    @api.depends("ts", "operator_id")
    def _compute_name(self):
        for rec in self:
            rec.name = "%s - %s" % (
                rec.operator_id.name,
                rec.ts.strftime("%Y-%m-%d %H:%M:%S")
            )

    def _default_ts(self):
        return fields.Datetime.now()

    def action_parse(self):
        for rec in self:
            ret = self.parse_adif(rec)

            if ret:
                return ret

        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }

    @api.model
    def parse_adif(self, upload):
        qso_obj = self.env["ham.award.qso"]

        modulation_obj = self.env["ham.utility.modulation"]
        adif_utility = self.env["ham.utility.adif"]
        qso_utility = self.env["ham.utility.qso"]

        if not upload:
            raise ValidationError(_("Invalid Upload"))

        file_raw = base64.b64decode(upload.with_context(bin_size=False).file_content)

        try:
            adif = adif_utility.parse_file_adif(file_raw)
        except Exception as e:
            _logger.error(e)
            error_message = str(e)

            upload.status = "error"
            upload.errors = error_message

            return {
                "warning": {
                    "title": _("Error parsing upload %d: %s" % (upload.id, upload.name)),
                    "message": error_message
                }
            }

        upload.headers = json.dumps(adif["headers"])

        for qso in adif["qso"]:
            ts_time = qso["TIME_ON"]
            ts_date = qso["QSO_DATE"]

            modulation = qso["MODE"]

            modulation_id = modulation_obj.search([("name", "=", modulation)])
            if not modulation_id:
                modulation_id = modulation_obj.search([("name", "ilike", modulation)])

            if not modulation_id:
                _logger.error("Modulation not found for value: %s", modulation)
                upload.status = "error"
                return

            ts_start = datetime.datetime.combine(ts_date, ts_time)
            local_callsign = upload.award_id.common_callsign
            callsign = qso["CALL"]
            frequency = qso["FREQ"]

            footprint = qso_obj.footprint_value(ts_start, local_callsign, callsign, modulation_id, frequency)

            values = qso_utility.values_from_adif_record(qso)
            values.update({
                "local_callsign": local_callsign,
                "award_id": upload.award_id.id,
                "operator_id": upload.operator_id.id,
                "upload_id": upload.id
            })

            qso_id = qso_obj.search([("footprint", "=", footprint)])
            if not qso_id:
                _logger.info("Creating new QSO: %s" % footprint)
                qso_id = qso_id.create(values)
            else:
                _logger.info("Updating QSO: %s" % footprint)
                qso_id.write(values)

            if not qso_id:
                raise ValidationError("Unable to create QSO with values: %s" % json.dumps(values))

        upload.status = "parsed"
