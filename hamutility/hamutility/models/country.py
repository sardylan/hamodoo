from odoo import models, fields, api


class Country(models.Model):
    _name = "hamutility.country"
    _inherit = "mail.thread"
    _description = "Country"
    _order = "name ASC"

    name = fields.Char(
        string="Name",
        required=True,
        tracking=True
    )

    res_country_id = fields.Many2one(
        string="System Country",
        comodel_name="res.country",
        tracking=True
    )

    flag = fields.Binary(
        string="Flag",
        help="Country flag",
        related="res_country_id.image",
        readonly=True
    )

    prefix_ids = fields.One2many(
        string="Prefixes",
        comodel_name="hamutility.countryprefix",
        inverse_name="country_id",
        tracking=True
    )

    cq_zone_ids = fields.Many2many(
        string="CQ Zones",
        comodel_name="hamutility.cq_zone",
        required=True,
        tracking=True
    )

    itu_zone_ids = fields.Many2many(
        string="ITU Zones",
        comodel_name="hamutility.itu_zone",
        required=True,
        tracking=True
    )


class CountryPrefix(models.Model):
    _name = "hamutility.countryprefix"
    _description = "Country Prefix"
    _order = "prefix ASC"
    _rec_name = "prefix"

    prefix = fields.Char(
        string="Prefix",
        required=True,
        translate=False
    )

    country_id = fields.Many2one(
        string="Country",
        comodel_name="hamutility.country",
        required=True
    )

    note = fields.Text(
        string="Note"
    )

    @api.onchange("prefix")
    def _check_uppercase_prefix(self):
        if self.prefix:
            self.prefix = self.prefix.upper()


class CQZone(models.Model):
    _name = "hamutility.cq_zone"
    _description = "CQ Zone"
    _order = "number ASC"
    _rec_name = "number"

    number = fields.Integer(
        string="Number",
        required=True
    )

    note = fields.Text(
        string="Note"
    )


class ITUZone(models.Model):
    _name = "hamutility.itu_zone"
    _description = "ITU Zone"
    _order = "number ASC"
    _rec_name = "number"

    number = fields.Integer(
        string="Number",
        required=True
    )

    note = fields.Text(
        string="Note"
    )
