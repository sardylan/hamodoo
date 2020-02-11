import base64
import io
import logging
import string

import magic
from openpyxl import load_workbook

from odoo import models, fields
from odoo.exceptions import ValidationError

LETTERS = string.digits + string.ascii_uppercase

_logger = logging.getLogger(__name__)


class ImportPrefix(models.TransientModel):
    _name = "ham_utility.wizard_import_prefix"
    _description = "Wizard user for import of official ITU XLSX countries file"

    xlsx_file = fields.Binary(
        string="XLSX File from ITU offical site"
    )

    xlsx_file_name = fields.Char(
        string="XLSX File name"
    )

    def action_delete_all(self):
        self.ensure_one()

        _logger.info("Deleting all country prefixes")
        country_prefix_ids = self.env["ham_utility.country_prefix"].search([])
        country_prefix_ids.unlink()

        _logger.info("Deleting all countries")
        country_ids = self.env["ham_utility.country"].search([])
        country_ids.unlink()

    def action_open_web_site(self):
        self.ensure_one()

        url = "https://www.itu.int/en/ITU-R/terrestrial/fmd/Pages/call_sign_series.aspx"

        return {
            "type": "ir.actions.act_url",
            "target": "new",
            "url": url
        }

    def action_import_xlsx(self):
        self.ensure_one()

        country_obj = self.env["ham_utility.country"]
        country_prefix_obj = self.env["ham_utility.country_prefix"]
        res_country_obj = self.env["res.country"]

        rawfile = base64.b64decode(self.xlsx_file)

        valid_mimes = [
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ]

        mime = magic.Magic(mime=True)
        file_mime = mime.from_buffer(rawfile)

        if file_mime not in valid_mimes:
            raise ValidationError("Inserted file is not a valid XLSX")

        fd = io.BytesIO(rawfile)
        wb = load_workbook(fd)
        sheet = wb.active
        limits = sheet.dimensions.split(":")

        if limits[0] != "A1" or not limits[1].startswith("B"):
            raise ValidationError("Malformed table")

        if sheet["A1"].value != "Series" or sheet["B1"].value != "Allocated to":
            raise ValidationError("Malformed table")

        first_row = 2
        last_row = int(limits[1][1:])

        country_prefixes = {}
        for r in range(first_row, last_row + 1):
            raw_prefix = sheet["A%d" % r].value.strip()
            raw_country = sheet["B%d" % r].value.strip()

            _logger.info("Parsing row %d: Prefix: %s - Country: %s" % (r, raw_prefix, raw_country))

            if raw_country not in country_prefixes:
                country_prefixes[raw_country] = []

            country_prefixes[raw_country].append(raw_prefix)

        for country in country_prefixes:
            country_id = country_obj.search([
                ("name", "=", country)
            ], limit=1)

            if not country_id:
                _logger.info("Creating country %s" % country)

                country_id = country_obj.create({
                    "name": country
                })

            country_name = country_id.name.split(" ")[0].strip()

            res_country_id = res_country_obj.search([("name", "ilike", country_name)])
            if len(res_country_id) == 1:
                _logger.info("Association with res.country %d: %s" % (res_country_id.id, res_country_id.name))
                country_id.res_country_id = res_country_id.id

            prefixes = self._reduce_prefixes(country_prefixes[country])

            for prefix in prefixes:
                country_prefix_id = country_prefix_obj.search([
                    ("country_id", "=", country_id.id),
                    ("prefix", "=", prefix)
                ])

                if not country_prefix_id:
                    _logger.info("Adding country prefix %s to %s" % (prefix, country_id.name))

                    country_prefix_obj.create({
                        "prefix": prefix,
                        "country_id": country_id.id,
                    })

        return {
            "type": "ir.actions.client",
            "tag": "reload"
        }

    @staticmethod
    def _reduce_prefixes(raw_input=None):
        if raw_input is None or len(raw_input) == 0:
            return []

        prefixes = raw_input.copy()

        for idx, val in enumerate(prefixes):
            interval_items = [x.strip() for x in val.split("-")]
            if len(interval_items) == 1:
                continue

            interval_start = interval_items[0].upper()
            interval_end = interval_items[1].upper()

            letter_start = interval_start[-1]
            letter_end = interval_end[-1]

            if letter_start == "A" and letter_end == "Z":
                prefixes[idx] = interval_start[:-1]

        prefixes_old = []

        while prefixes != prefixes_old:
            prefixes_old = prefixes.copy()

            series = {}
            for prefix in prefixes:
                val = prefix[:-1]
                if val not in series:
                    series[val] = 0

                series[val] += 1

            for s in series:
                if series[s] == 26:
                    for prefix in prefixes.copy():
                        if prefix.startswith(s):
                            prefixes.remove(prefix)

                    prefixes.append(s)

        return sorted(prefixes)
