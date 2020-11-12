import logging

import requests

from odoo import models, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

HRDLOG_API_UPLOAD_QSO = "http://robot.hrdlog.net/NewEntry.aspx"
HRDLOG_API_APP_NAME = "ham.thehellnet.org 14.0"

_logger = logging.getLogger(__name__)


class HRDLogUtility(models.AbstractModel):
    _name = "ham.utility.websites.hrdlog"
    _description = "Integration with HRDLog API"

    @api.model
    def upload_qso(self, callsign: str = "", code: str = "", adif_data: str = ""):
        if not callsign or not code or not adif_data:
            _logger.error("Invalid login data. Username: %s - Code: %s - ADIF data: %s" % (
                callsign, code, adif_data
            ))
            raise ValidationError(_("Invalid data"))

        url = HRDLOG_API_UPLOAD_QSO

        data = {
            "Callsign": callsign,
            "Code": code,
            "App": HRDLOG_API_APP_NAME,
            "ADIFData": adif_data
        }

        response = requests.post(url=url, data=data)

        if response.status_code != 200:
            _logger.error("Unable to upload QSO to HRDLog. Status code %d: %s" % (
                response.status_code, response.content
            ))
            _logger.error("Data: %s" % data)
            raise ValidationError(_("Unable to upload QSO to HRDLog"))

        if b"error" in response.content.lower():
            _logger.error("Error publishing QSO: %s" % response.content)
            _logger.error("Data: %s" % data)
            raise ValidationError(_("Error publishing QSO"))
