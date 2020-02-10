import base64
import io
import string

import magic
from openpyxl import load_workbook

from odoo import models, fields
from odoo.exceptions import ValidationError


class ImportPrefix(models.TransientModel):
    _name = "hamutility.wizard_import_prefix"
    _description = "Wizard user for import of official ITU XLSX countries file"

    LETTERS = string.digits + string.ascii_uppercase

    xlsx_file = fields.Binary(
        string="XLSX File from ITU offical site"
    )

    def action_delete_all(self):
        countryprefix_ids = self.env["hamutility.countryprefix"].search([])
        countryprefix_ids.unlink()

        country_ids = self.env["hamutility.country"].search([])
        country_ids.unlink()

    def action_import_xlsx(self):
        self.ensure_one()

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
        sheet = wb.get_active_sheet()
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

            if raw_country not in country_prefixes:
                country_prefixes[raw_country] = []

            country_prefixes[raw_country].append(raw_prefix)

        for country in country_prefixes:
            country_id = self.env["hamutility.country"].search([
                ("name", "=", country)
            ], limit=1)

            if len(country_id) == 0:
                country_id = self.env["hamutility.country"].create({
                    "name": country
                })

            prefixes = self._reduce_prefixes(country_prefixes[country])

            for prefix in prefixes:
                self.env["hamutility.countryprefix"].create({
                    "prefix": prefix,
                    "country_id": country_id.id,
                })

        return {
            "type": "ir.actions.client",
            "tag": "reload",
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
