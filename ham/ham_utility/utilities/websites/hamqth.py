import datetime
import logging

import requests

from odoo import models, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

HAMQTH_API_UPLOAD_QSO = "https://www.hamqth.com/qso_realtime.php"
HAMQTH_API_UPLOAD_ADIF = "https://www.hamqth.com/prg_log_upload.php"
HAMQTH_API_APP_NAME = "ham.thehellnet.org"

_logger = logging.getLogger(__name__)


class HamQTHUtility(models.AbstractModel):
    _name = "ham.utility.websites.hamqth"
    _description = "Integration with HamQTH API"

    @api.model
    def upload_qso(self, username: str = "", password: str = "", callsign: str = "", adif_data: str = ""):
        if not username or not password or not callsign or not adif_data:
            _logger.error("Invalid login data. Username: %s - Password: %s - Callsign: %s" % (
                username, password, callsign
            ))
            raise ValidationError(_("Invalid login data"))

        if not adif_data:
            _logger.error("Invalid ADIF data")
            raise ValidationError(_("Invalid ADIF data"))

        url = HAMQTH_API_UPLOAD_QSO

        data = {
            "u": username,
            "p": password,
            "c": callsign,
            "adif": adif_data,
            "prg": HAMQTH_API_APP_NAME,
            "cmd": "insert"
        }

        response = requests.post(url=url, data=data)

        if response.status_code != 200:
            message = "%s. Status code %d: %s" % (
                _("Unable to upload QSO to HamQTH"),
                response.status_code,
                response.content
            )
            _logger.error(message)
            raise ValidationError(message)

    @api.model
    def upload_adif(self, username: str = "", password: str = "", callsign: str = "", adif_data: str = ""):
        if not username or not password or not callsign:
            _logger.error("Invalid login data. Username: %s - Password: %s - Callsign: %s" % (
                username, password, callsign
            ))
            raise ValidationError(_("Invalid login data"))

        if not adif_data:
            _logger.error("Invalid ADIF data")
            raise ValidationError(_("Invalid ADIF data"))

        url = HAMQTH_API_UPLOAD_ADIF

        data = {
            "u": username,
            "p": password,
            "c": callsign,
        }

        adif_name = "%s.adi" % datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")

        files = {
            "f": (adif_name, adif_data)
        }

        response = requests.post(url=url, data=data, files=files)

        if response.status_code != 200:
            message = "%s. Status code %d: %s" % (
                _("Unable to upload ADIF to HamQTH"),
                response.status_code,
                response.content
            )
            _logger.error(message)
            raise ValidationError(message)
