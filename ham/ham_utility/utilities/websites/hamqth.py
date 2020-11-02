import logging

import requests

from odoo import models, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

HAMQTH_API_UPLOAD_ADIF = "https://www.hamqth.com/prg_log_upload.php"

_logger = logging.getLogger(__name__)


class HamQTHUtility(models.AbstractModel):
    _name = "ham.utility.websites.hamqth"
    _description = "Integration with HamQTH API"

    @api.model
    def upload(self,
               username: str = "",
               password: str = "",
               callsign: str = "",
               adif_name: str = "",
               adif_content: str = ""):
        if not username or not password or not callsign:
            _logger.error("Invalid login data. Username: %s - Password: %s - Callsign: %s" % (
                username, password, callsign
            ))
            raise ValidationError(_("Invalid login data"))

        url = HAMQTH_API_UPLOAD_ADIF

        data = {
            "u": username,
            "p": password,
            "c": callsign,
        }

        files = {
            "f": (adif_name, adif_content)
        }

        response = requests.post(url=url, data=data, files=files)

        if response.status_code != 200:
            _logger.error("Unable to upload ADIF to HamQTH. Status code %d: %s" % (
                response.status_code, response.content
            ))
            raise ValidationError(_("Unable to upload ADIF to HamQTH"))
