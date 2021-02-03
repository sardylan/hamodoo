import datetime

from odoo import models, api


class DtUtility(models.AbstractModel):
    _name = "ham.utility.dt"
    _description = "Datetime utilities"

    @api.model
    def compute_start_end(self, mode: str = "") -> tuple:
        if not mode:
            raise ValueError("No mode")

        now = datetime.datetime.utcnow()

        dt_start: datetime.datetime
        dt_end: datetime.datetime

        if mode == "day":
            dt_start = (now - datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            dt_end = dt_start.replace(hour=23, minute=59, second=59, microsecond=0)
        elif mode == "week":
            dt_start = (now - datetime.timedelta(weeks=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            dt_end = dt_start.replace(hour=23, minute=59, second=59, microsecond=0)
        elif mode == "month":
            dt_start = (now - datetime.timedelta(days=30)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            dt_end = (dt_start + datetime.timedelta(mon)).replace(hour=23, minute=59, second=59, microsecond=0)
        elif mode == "year":
            dt_start = (now - datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            dt_end = dt_start.replace(hour=23, minute=59, second=59, microsecond=0)
        else:
            raise NotImplementedError

        return dt_start, dt_end
