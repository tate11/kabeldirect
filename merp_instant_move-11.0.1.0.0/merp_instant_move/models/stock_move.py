from odoo import models


class StockMove(models.Model):
    _inherit = 'stock.move'

    def action_done(self):
        return self._action_done()
