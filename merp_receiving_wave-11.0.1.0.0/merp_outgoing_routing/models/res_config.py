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

from openerp import api, models, fields


class StockConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    outgoing_routing_strategy = fields.Selection(
        [
            ('name', 'Sort by source locations in alphabetical order'),
            ('removal_prio', 'Sort by location removal strategy priority field'),
        ],
        string='Routing Strategy', default='name')

    outgoing_routing_order = fields.Selection(
        [
            (0, 'Ascending (A-Z)'),
            (1, 'Descending (Z-A)'),
        ],
        string='Routing Order', default=0)

    @api.model
    def get_default_company_outgoing_strategy_values(self, fields):
        company = self.env.user.company_id
        return {
            'outgoing_routing_strategy': company.outgoing_routing_strategy,
            'outgoing_routing_order': company.outgoing_routing_order,
        }

    @api.multi
    def set_company_outgoing_strategy_values(self):
        company = self.env.user.company_id
        company.outgoing_routing_strategy = self.outgoing_routing_strategy
        company.outgoing_routing_order = self.outgoing_routing_order
