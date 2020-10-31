from odoo import models, fields, api


class Country(models.Model):
    _name = "ham.country"
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

    image_url = fields.Char(
        related="res_country_id.image_url",
        readonly=True
    )

    prefix_ids = fields.One2many(
        string="Prefixes",
        comodel_name="ham.country.prefix",
        inverse_name="country_id",
        tracking=True
    )

    cq_zone_ids = fields.Many2many(
        string="CQ Zones",
        comodel_name="ham.zone.cq",
        required=True,
        tracking=True
    )

    itu_zone_ids = fields.Many2many(
        string="ITU Zones",
        comodel_name="ham.zone.itu",
        required=True,
        tracking=True
    )


class CountryPrefix(models.Model):
    _name = "ham.country.prefix"
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
        comodel_name="ham.country",
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
    _name = "ham.zone.cq"
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
    _name = "ham.zone.itu"
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
