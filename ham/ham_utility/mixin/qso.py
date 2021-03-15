import datetime
import logging

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


class QSO(models.AbstractModel):
    _name = "ham.mixin.qso"
    _inherit = "mail.thread"
    _description = "Abstract QSO"
    _order = "ts_start DESC"
    _rec_name = "footprint"

    _sql_constraints = [
        ("footprint_uniq", "UNIQUE(footprint)", _("QSO Already present"))
    ]

    ts_start = fields.Datetime(
        string="Date & Time Start",
        help="Date and Time of start",
        required=True,
        tracking=True
    )

    ts_end = fields.Datetime(
        string="Date & Time End",
        help="Date and Time of end",
        required=True,
        tracking=True
    )

    local_callsign = fields.Char(
        string="Local Callsign",
        help="Callsign used for QSO",
        required=True,
        tracking=True
    )

    local_locator = fields.Char(
        string="Local Locator",
        help="Local Maidenhead Locator",
        tracking=True
    )

    local_latitude = fields.Float(
        string="Local Latitude",
        help="Local Station Latitude",
        digits=(8, 6),
        tracking=True
    )

    local_longitude = fields.Float(
        string="Local Longitude",
        help="Local Station Longitude",
        digits=(9, 6),
        tracking=True
    )

    callsign = fields.Char(
        string="Callsign",
        help="Callsign of remote station",
        required=True,
        tracking=True
    )

    op_name = fields.Char(
        string="Operator name",
        help="Name of remote operator",
        tracking=True
    )

    frequency = fields.Float(
        string="Frequency",
        help="Frequency of TX",
        digits=(12, 0),
        group_operator=False,
        required=True,
        tracking=True
    )

    rx_frequency = fields.Float(
        string="RX Frequency",
        help="Frequency of RX",
        digits=(12, 0),
        group_operator=False,
        required=True,
        tracking=True
    )

    modulation_id = fields.Many2one(
        string="Modulation",
        help="Modulation",
        comodel_name="ham.modulation",
        required=True,
        tracking=True
    )

    tx_rst = fields.Char(
        string="RST TX",
        help="RST sent",
        required=True,
        tracking=True
    )

    rx_rst = fields.Char(
        string="RST RX",
        help="RST received",
        required=True,
        tracking=True
    )

    qth = fields.Char(
        string="QTH",
        help="QTH of remote station",
        tracking=True
    )

    locator = fields.Char(
        string="Locator",
        help="Maidenhead Locator",
        tracking=True
    )

    latitude = fields.Float(
        string="Latitude",
        help="Station Latitude",
        digits=(8, 6),
        tracking=True
    )

    longitude = fields.Float(
        string="Longitude",
        help="Station Longitude",
        digits=(9, 6),
        tracking=True
    )

    footprint = fields.Char(
        string="Footprint",
        help="QSO Footprint",
        readonly=True,
        compute="compute_footprint",
        store=True
    )

    country_id = fields.Many2one(
        string="Country",
        help="HAM Country",
        comodel_name="ham.country",
        readonly=True,
        compute="_compute_country_id",
        store=True
    )

    band_id = fields.Many2one(
        string="Band",
        help="HAM Band",
        comodel_name="ham.band",
        readonly=True,
        compute="_compute_band_id",
        store=True
    )

    distance = fields.Float(
        string="Distance",
        help="Distance",
        readonly=True,
        compute="_compute_distance",
        store=True
    )

    note = fields.Html(
        string="Note",
        help="Note",
        tracking=True
    )

    @api.model_create_multi
    def create(self, vals):
        if isinstance(vals, dict):
            self.sanitize_vals(vals)
        else:
            for item in vals:
                self.sanitize_vals(item)

        return super().create(vals)

    def write(self, vals):
        self.sanitize_vals(vals, in_write=True)
        return super().write(vals)

    @api.onchange("callsign", "local_callsign")
    def uppercase_onchange(self):
        callsign_utility = self.env["ham.utility.callsign"]

        for rec in self:
            rec.callsign = callsign_utility.uppercase(rec.callsign)
            rec.local_callsign = callsign_utility.uppercase(rec.local_callsign)

    @api.depends("ts_start", "local_callsign", "callsign", "modulation_id", "frequency")
    def compute_footprint(self):
        for rec in self:
            footprint = self.footprint_value(
                rec.ts_start,
                rec.local_callsign,
                rec.callsign,
                rec.modulation_id,
                rec.frequency
            )

            rec.footprint = footprint.strip().upper()

    @api.depends("callsign")
    def _compute_country_id(self):
        country_utility = self.env["ham.utility.country"]

        for rec in self:
            country_id = country_utility.get_country(rec.callsign)
            rec.country_id = country_id and country_id.id or False

    @api.depends("frequency")
    def _compute_band_id(self):
        band_obj = self.env["ham.band"]

        for rec in self:
            band_id = band_obj.get_band(rec.frequency)
            rec.band_id = band_id and band_id.id or False

    @api.depends("local_locator", "local_latitude", "local_longitude", "locator", "latitude", "longitude")
    def _compute_distance(self):
        locator_utility = self.env["ham.utility.locator"]

        for rec in self:
            if rec.local_locator is False \
                    or rec.local_latitude is False \
                    or rec.local_longitude is False \
                    or rec.locator is False \
                    or rec.latitude is False \
                    or rec.longitude is False:
                rec.distance = False
                continue

            rec.distance = locator_utility.distance_latlng(
                src_latitude=rec.local_latitude,
                src_longitude=rec.local_longitude,
                dst_latitude=rec.latitude,
                dst_longitude=rec.longitude,
            )

    def action_export_adif(self):
        ir_attachment_obj = self.env["ir.attachment"]

        adif_utility = self.env["ham.utility.adif"]

        qsos = self

        dt = datetime.datetime.utcnow()

        adif_content: str = adif_utility.generate_adif(qsos=qsos, dt=dt)

        file_name: str = self.compute_adif_filename(dt, qsos)

        ir_attachments = ir_attachment_obj.create([{
            "name": file_name,
            "type": "binary",
            "raw": adif_content.encode(),
            "store_fname": file_name,
        }])
        if not ir_attachments:
            raise ValidationError(_("Unable to create ADIF attachment"))

        ir_attachment = ir_attachments[0]

        return {
            "type": "ir.actions.act_url",
            "target": "new",
            "url": f"/web/content/{ir_attachment.id}/{file_name}"
        }

    @api.model
    def compute_adif_filename(self, dt: datetime.datetime, qsos) -> str:
        return f"{dt.strftime('%Y%m%d-%H%m%s')}.adi"

    @api.model
    def footprint_value(self, ts_start, local_callsign, callsign, modulation_id, frequency):
        if not ts_start or not local_callsign or not callsign or not modulation_id or not frequency:
            return ""

        footprint = "%s-%s-%s-%s-%d" % (
            ts_start.strftime("%Y%m%d%H%M%S"),
            local_callsign.strip().upper(),
            callsign.strip().upper(),
            modulation_id.name.strip().upper(),
            frequency
        )

        return footprint

    @api.model
    def sanitize_vals(self, vals: dict, in_write: bool = False):
        modulation_obj = self.env["ham.modulation"]

        callsign_utility = self.env["ham.utility.callsign"]

        if "rx_frequency" not in vals or not vals["rx_frequency"]:
            if "frequency" in vals:
                vals["rx_frequency"] = vals["frequency"]

        if not in_write:
            if "modulation_id" not in vals:
                raise ValidationError(_("No Modulation in QSO"))

            modulation = modulation_obj.browse(vals["modulation_id"])
            if not modulation:
                raise ValidationError(_("Modulation not found when creating QSO"))

            if "tx_rst" not in vals or not vals["tx_rst"].strip():
                vals["tx_rst"] = modulation.default_rst
            if "rx_rst" not in vals or not vals["rx_rst"].strip():
                vals["rx_rst"] = modulation.default_rst

        for field in ["callsign", "local_callsign"]:
            if field in vals:
                vals[field] = callsign_utility.uppercase(vals[field])
