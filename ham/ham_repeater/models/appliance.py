from odoo import models, fields, api
from odoo.tools.translate import _

SELECTION_ITEM_TYPE = [
    ("simplex", "Simplex"),
    ("duplex", "Duplex")
]

SELECTION_SQUELCH_TYPE = [
    ("none", "None"),
    ("ctcss", "CTCSS (Continuous Tone-Coded Squelch System)"),
    ("cds", "CDS (Digital-Coded Squelch)"),
    ("dgid", "System Fusion DG-ID")
]


class Appliance(models.Model):
    _name = "ham.repeater.appliance"
    _description = "Represent a single appliance installed in a station"

    _inherit = [
        "mail.thread",
    ]

    station_id = fields.Many2one(
        string="Station",
        help="Related Station",
        comodel_name="ham.repeater.station",
        required=True,
        tracking=True
    )

    station_callsign = fields.Char(related="station_id.callsign")

    item_ids = fields.One2many(
        string="Items",
        help="Appliance items",
        comodel_name="ham.repeater.appliance.item",
        inverse_name="appliance_id",
        tracking=True
    )

    main_item_id = fields.Many2one(
        string="Main Item",
        help="Main Item",
        comodel_name="ham.repeater.appliance.item",
        compute="_compute_main_item_id",
        readonly=True
    )

    item_type = fields.Selection(related="main_item_id.item_type")
    freq_out = fields.Float(related="main_item_id.freq_out")
    freq_in = fields.Float(related="main_item_id.freq_in")
    modulation_id = fields.Selection(related="main_item_id.modulation_id")
    squelch_type = fields.Selection(related="main_item_id.squelch_type")
    squelch_value = fields.Selection(related="main_item_id.squelch_value")
    power = fields.Integer(related="main_item_id.power")
    antenna_out = fields.Char(related="main_item_id.antenna_out")
    antenna_in = fields.Char(related="main_item_id.antenna_in")

    note = fields.Html(
        string="Note",
        help="Note"
    )

    @api.depends("item_ids")
    def _compute_main_item_id(self):
        for rec in self:
            if not rec.item_ids:
                rec.main_item_id = False
                continue

            rec.main_item_id = rec.item_ids[0]


class ApplianceItem(models.Model):
    _name = "ham.repeater.appliance.item"
    _description = "Represent a single item in a appliance",
    _order = "appliance_id, order_num"

    _sql_constraints = [
        ("appliance_sequence_uniq", "UNIQUE(appliance_id, order_num)", _("Order num must be unique"))
    ]

    appliance_id = fields.Many2one(
        string="Appliance",
        help="Related Appliance",
        required=True
    )

    order_num = fields.Integer(
        string="Order",
        help="Item order",
        required=True,
        default="_default_order_num",
        readonly=True
    )

    item_type = fields.Selection(
        string="Type",
        help="Item type",
        selection=SELECTION_ITEM_TYPE,
        required=True
    )

    freq_out = fields.Float(
        string="Output Frequency",
        help="Output Frequency",
        digits=(9, 3),
        required=True
    )

    freq_in = fields.Float(
        string="Output Frequency",
        help="Output Frequency",
        digits=(9, 3),
        required=True
    )

    modulation_id = fields.Many2one(
        string="Modulation",
        help="Modulation",
        comodel_name="ham.modulation",
        required=True
    )

    squelch_type = fields.Selection(
        string="Squelch type",
        help="Squelch type",
        selection=SELECTION_SQUELCH_TYPE,
        required=True,
        default="none"
    )

    squelch_value = fields.Char(
        string="Squelch value",
        help="Squelch value"
    )

    power = fields.Integer(
        string="Output power",
        help="Output Power (W)"
    )

    antenna_out = fields.Char(
        string="Output Antenna",
        help="Output Antenna"
    )

    antenna_in = fields.Char(
        string="Input Antenna",
        help="Input Antenna"
    )

    @api.onchange("item_type", "freq_out")
    def _onchange_type(self):
        for rec in self:
            if rec.item_type == "simplex":
                rec.freq_in = rec.freq_out

    def _default_order_num(self):
        for rec in self:
            order_nums = [x.order_num for x in self.search([("appliance_id", "=", rec.appliance_id)])]
            order_nums.append(1)

            rec.order_num = max(order_nums) + 1
