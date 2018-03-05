# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2017 Xpansa Group (<http://xpansa.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    operations_to_pick = fields.Many2many(
        'stock.move.line', relation='picking_operations_to_pick',
        string='Operations to Pick',
        compute='_compute_operations_to_pick', store=False)

    strategy_order_r = fields.Char(string='Strategy Order',
        compute='_compute_operations_to_pick', store=False)

    @api.one
    @api.depends('move_line_ids',
                 'move_line_ids.location_id',
                 'move_line_ids.qty_done')
    def _compute_operations_to_pick(self):
        strategy = self.env.user.company_id.outgoing_routing_strategy
        strategy_order = self.env.user.company_id.outgoing_routing_order
        res = self.env['stock.move.line']
        for operation in self.move_line_ids:
            if operation._compute_operation_valid():
                res += operation
        self.operations_to_pick = res.sorted(
            key=lambda r: getattr(r.location_id, strategy, 'None'),
            reverse=strategy_order
        )

        settings = self.env['res.company'].fields_get(
            ['outgoing_routing_strategy', 'outgoing_routing_order'])
        strategies = settings['outgoing_routing_strategy']['selection']
        orders = settings['outgoing_routing_order']['selection']
        self.strategy_order_r = _('Strategy Order: ') + ', '.join([
            dict(strategies)[strategy].lower(),
            dict(orders)[strategy_order].lower()
        ])
