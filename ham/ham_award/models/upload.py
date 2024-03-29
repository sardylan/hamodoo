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
        default=lambda self: fields.Datetime.now(),
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

    award_callsign_id = fields.Many2one(
        string="Callsign",
        help="Force Callsign for parsing",
        comodel_name="ham.award.callsign"
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

    errors = fields.Html(
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

    note = fields.Html(
        string="Note",
        help="Note"
    )

    @api.onchange("award_id")
    def onchange_award_id(self):
        self.ensure_one()

        return {
            "domain": {
                "operator_id": [("award_ids", "in", self.award_id.id)],
                "award_callsign_id": [("award_id", "=", self.award_id.id)],
            }
        }

    @api.depends("ts", "operator_id")
    def _compute_name(self):
        for rec in self:
            rec.name = "%s - %s" % (
                rec.operator_id.name,
                rec.ts.strftime("%Y-%m-%d %H:%M:%S")
            )

    def action_parse(self):
        for rec in self:
            ret = self.parse_adif(rec)

            if ret:
                return ret

        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }

    def action_reject(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": _("Upload Reject"),
            "res_model": "ham.wizard.upload.reject",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_upload_id": self.id
            }
        }

    @api.model
    def parse_adif(self, upload):
        qso_obj = self.env["ham.award.qso"]
        modulation_obj = self.env["ham.modulation"]
        award_callsign_obj = self.env["ham.award.callsign"]
        band_obj = self.env["ham.band"]

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

            upload.state = "error"
            upload.errors = error_message

            return {
                "warning": {
                    "title": _("Error parsing upload %d: %s" % (upload.id, upload.name)),
                    "message": error_message
                }
            }

        upload.headers = json.dumps(adif["headers"])

        enabled_callsigns = [x.callsign for x in self.award_id.callsigns]

        for qso in adif["qso"]:
            ts_time = qso["TIME_ON"]
            ts_date = qso["QSO_DATE"]

            modulation_name = qso["MODE"]

            modulation = modulation_obj.search([("name", "=", modulation_name)])
            if not modulation:
                modulation = modulation_obj.search([("name", "ilike", modulation_name)])

            if not modulation:
                raise ValidationError(_("Modulation not found for value: %s") % modulation_name)

            ts_start = datetime.datetime.combine(ts_date, ts_time)

            if upload.award_callsign_id:
                local_callsign = upload.award_callsign_id.callsign
            else:
                local_callsigns = [qso[x] for x in ["STATION_CALLSIGN", "OPERATOR"] if x in qso]

                if not local_callsigns:
                    raise ValidationError(_("Both STATION_CALLSIGN and OPERATOR empty or not present in ADIF row"))

                local_callsign = False
                for item in local_callsigns:
                    if item in enabled_callsigns:
                        local_callsign = item
                        break

                if not local_callsign:
                    raise ValidationError(_("Callsign not enabled in award"))

            award_callsign = award_callsign_obj.search([("callsign", "=", local_callsign)])

            callsign = qso["CALL"]

            if "FREQ" not in qso and "BAND" not in qso:
                raise ValidationError(_("QSO has no BAND and NO FREQ!"))

            if "FREQ" not in qso:
                band = band_obj.search([("name", "=", qso["BAND"])])
                qso["FREQ"] = band.start

            frequency = qso["FREQ"]

            footprint = qso_obj.footprint_value(ts_start, local_callsign, callsign, modulation, frequency)

            values = qso_utility.values_from_adif_record(qso)
            values.update({
                "local_callsign": award_callsign.callsign,
                "local_latitude": award_callsign.latitude,
                "local_longitude": award_callsign.longitude,
                "award_id": upload.award_id.id,
                "operator_id": upload.operator_id.id,
                "upload_id": upload.id
            })

            qso = qso_obj.search([("footprint", "=", footprint)])
            if not qso:
                _logger.info("Creating new QSO: %s" % footprint)
                qso = qso.create(values)
            else:
                _logger.info("Updating QSO: %s" % footprint)
                qso.write(values)

            if not qso:
                raise ValidationError("Unable to create QSO with values: %s" % json.dumps(values))

        upload.state = "parsed"
