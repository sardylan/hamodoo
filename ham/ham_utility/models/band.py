from odoo import models, fields, api

SELECTION_RANGE_ITU = [
    ("ELF", "ELF (3-30 Hz | 100000-10000 km)"),
    ("SLF", "SLF (30-300 Hz | 10000-1000 km)"),
    ("ULF", "ULF (300-3000 Hz | 1000-100 km)"),
    ("VLF", "VLF (3-30 kHz | 100-10 km)"),
    ("LF", "LF (30-300 kHz | 10-1 km)"),
    ("MF", "MF (300-3000 kHz | 1000-100 m)"),
    ("HF", "HF (3-30 MHz | 100-10 m)"),
    ("VHF", "VHF (30-300 MHz | 10-1 m)"),
    ("UHF", "UHF (300-3000 MHz | 100-10 cm)"),
    ("SHF", "SHF (3-30 GHz | 10-1 cm)"),
    ("EHF", "EHF (30-300 GHz | 10-1 mm)"),
    ("THF", "THF (300-3000 GHz | 1-0.1 mm)")
]


class Band(models.Model):
    _name = "ham_utility.band"
    _inherit = "mail.thread"
    _description = "Frequency band"
    _order = "start ASC, end ASC"

    name = fields.Char(
        string="Name",
        required=True,
        tracking=True
    )

    start = fields.Float(
        string="Start",
        help="Start frequency",
        digits=(12, 0),
        group_operator=False,
        required=True,
        tracking=True
    )

    end = fields.Float(
        string="End",
        help="End frequency",
        digits=(12, 0),
        group_operator=False,
        required=True,
        tracking=True
    )

    range_itu = fields.Selection(
        string="Range ITU",
        help="Frequency range accordingly to ITU standards",
        selection=SELECTION_RANGE_ITU,
        required=True,
        tracking=True
    )

    note = fields.Html(
        string="Note",
        help="Note",
        tracking=True
    )

    @api.model
    def get_band(self, frequency):
        if not frequency:
            return False

        band_obj = self

        band_id = band_obj.search([
            ("start", "<=", frequency),
            ("end", ">=", frequency)
        ])

        if not band_id:
            return False

        return band_id
