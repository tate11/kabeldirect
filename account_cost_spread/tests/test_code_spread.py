# -*- coding: utf-8 -*-
# Copyright 2017 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.account.tests.account_test_classes import AccountingTestCase
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from datetime import datetime
from odoo.exceptions import Warning
from odoo import fields


class TestAccountCostSpread(AccountingTestCase):

    def setUp(self):
        super(TestAccountCostSpread, self).setUp()
        receivable = self.env.ref('account.data_account_type_receivable')
        expenses = self.env.ref('account.data_account_type_expenses')

        def get_account(obj):
            res = self.env['account.account'].search([
                ('user_type_id', '=', obj.id)
            ], limit=1)
            return res

        self.invoice_account = get_account(receivable)
        self.invoice_line_account = get_account(expenses)

        self.spread_account = self.env['account.account'].search([
            ('user_type_id', '=', expenses.id),
            ('id', '!=', self.invoice_line_account.id)
        ], limit=1).id

        self.partner = self.env['res.partner'].create({
            'name': 'Partner Name',
            'supplier': True,
        })
        self.invoice = self.env['account.invoice'].with_context(
            default_type='in_invoice'
        ).create({
            'partner_id': self.partner.id,
            'account_id': self.invoice_account.id,
            'type': 'in_invoice',
        })
        self.invoice_line = self.env['account.invoice.line'].create({
            'quantity': 1.0,
            'price_unit': 1000.0,
            'invoice_id': self.invoice.id,
            'name': 'product that cost 1000',
            'account_id': self.invoice_line_account.id,
            'spread_account_id': self.spread_account,
            'period_number': 12,
            'period_type': 'month',
            'spread_date': '2017-02-01'
        })

        self.invoice_2 = self.env['account.invoice'].with_context(
            default_type='in_invoice'
        ).create({
            'partner_id': self.partner.id,
            'account_id': self.invoice_account.id,
            'type': 'in_invoice',
        })
        self.invoice_line_2 = self.env['account.invoice.line'].create({
            'quantity': 1.0,
            'price_unit': 1000.0,
            'invoice_id': self.invoice_2.id,
            'name': 'product that cost 1000',
            'account_id': self.invoice_line_account.id,
            'spread_account_id': self.spread_account,
            'period_number': 12,
            'period_type': 'month',
            'spread_date': '2017-02-01'
        })

    def test_01_supplier_invoice(self):
        # spread date set
        self.invoice_line.write({
            'period_number': 12,
            'period_type': 'month',
            'spread_date': '2017-02-01'
        })

        # change the state of invoice to open by clicking Validate button
        self.invoice.action_invoice_open()
        self.assertEqual(len(self.invoice_line.spread_line_ids), 12)
        self.assertEqual(81.77, self.invoice_line.spread_line_ids[0].amount)
        self.assertEqual(83.33, self.invoice_line.spread_line_ids[1].amount)
        self.assertEqual(83.33, self.invoice_line.spread_line_ids[2].amount)
        self.assertEqual(83.33, self.invoice_line.spread_line_ids[3].amount)
        self.assertEqual(83.33, self.invoice_line.spread_line_ids[4].amount)
        self.assertEqual(83.33, self.invoice_line.spread_line_ids[5].amount)
        self.assertEqual(83.33, self.invoice_line.spread_line_ids[6].amount)
        self.assertEqual(83.33, self.invoice_line.spread_line_ids[7].amount)
        self.assertEqual(83.33, self.invoice_line.spread_line_ids[8].amount)
        self.assertEqual(83.33, self.invoice_line.spread_line_ids[9].amount)
        self.assertEqual(83.33, self.invoice_line.spread_line_ids[10].amount)
        self.assertEqual(84.93, self.invoice_line.spread_line_ids[11].amount)

        # Cancel the account move which is in posted state
        # and verifies that it gives warning message
        with self.assertRaises(Warning):
            self.invoice.move_id.button_cancel()

    def test_02_supplier_invoice(self):
        # date invoice set
        self.invoice.date_invoice = '2017-03-01'
        self.invoice_line.write({
            'price_unit': 2000.0,
            'name': 'product that cost 2000',
            'period_number': 7,
            'period_type': 'quarter',
            'spread_date': None
        })

        # change the state of invoice to open by clicking Validate button
        self.invoice.action_invoice_open()

        self.assertEqual(len(self.invoice_line.spread_line_ids), 8)
        self.assertEqual(100.96, self.invoice_line.spread_line_ids[0].amount)
        self.assertEqual(285.72, self.invoice_line.spread_line_ids[1].amount)
        self.assertEqual(285.72, self.invoice_line.spread_line_ids[2].amount)
        self.assertEqual(285.72, self.invoice_line.spread_line_ids[3].amount)
        self.assertEqual(285.72, self.invoice_line.spread_line_ids[4].amount)
        self.assertEqual(285.72, self.invoice_line.spread_line_ids[5].amount)
        self.assertEqual(285.72, self.invoice_line.spread_line_ids[6].amount)
        self.assertEqual(184.72, self.invoice_line.spread_line_ids[7].amount)
        total_line_amount = 0.0
        for line in self.invoice_line.spread_line_ids:
            total_line_amount += line.amount
        self.assertLessEqual(abs(total_line_amount - 2000.0), 0.0001)

        # simulate the click on the arrow that displays the spread details
        details = self.invoice_line.spread_details()
        self.assertEqual(details['res_id'], self.invoice_line.id)

    def test_03_supplier_invoice(self):
        # no date set
        self.invoice_line.write({
            'quantity': 1.0,
            'price_unit': 1000.0,
            'invoice_id': self.invoice.id,
            'name': 'product that cost 1000',
            'account_id': self.invoice_line_account.id,
            'spread_account_id': self.spread_account,
            'period_number': 3,
            'period_type': 'year',
            'spread_date': None
        })
        self.invoice.write({'date_invoice': None})
        self.invoice_line._compute_spread_start_date()

        # change the state of invoice to open by clicking Validate button
        self.invoice.action_invoice_open()

        self.assertEqual(len(self.invoice_line.spread_line_ids), 4)
        self.assertEqual(333.33, self.invoice_line.spread_line_ids[1].amount)
        self.assertEqual(333.33, self.invoice_line.spread_line_ids[2].amount)
        first_amount = self.invoice_line.spread_line_ids[0].amount
        last_amount = self.invoice_line.spread_line_ids[3].amount
        remaining_amount = first_amount + last_amount
        self.assertLessEqual(abs(remaining_amount - 333.34), 0.0001)
        total_line_amount = 0.0
        for line in self.invoice_line.spread_line_ids:
            total_line_amount += line.amount
        self.assertLessEqual(abs(total_line_amount - 1000.0), 0.0001)

    def test_04_supplier_invoice(self):
        # spread date set
        self.invoice_line.write({
            'period_number': 12,
            'period_type': 'month',
            'spread_date': '2017-02-01'
        })

        # change the state of invoice to open by clicking Validate button
        self.invoice.action_invoice_open()

        # create moves for all the spread lines and open them
        self.invoice_line.spread_line_ids.create_moves()
        for spread_line in self.invoice_line.spread_line_ids:
            attrs = spread_line.open_move()
            self.assertEqual(isinstance(attrs, dict), True)

        # post and then unlink all created moves
        self.invoice.journal_id.write({'update_posted': True})
        for line in self.invoice_line.spread_line_ids:
            line.move_id.post()
        self.invoice_line.spread_line_ids.unlink_move()
        for spread_line in self.invoice_line.spread_line_ids:
            self.assertEqual(len(spread_line.move_id), 0)

    def test_05_supplier_invoice(self):
        # spread date set
        self.invoice_line.write({
            'period_number': 8,
            'period_type': 'month'
        })

        # change the state of invoice to open by clicking Validate button
        self.invoice.action_invoice_open()

        # create moves for all the spread lines and open them
        self.invoice_line.spread_line_ids.create_moves()

        # check move lines
        for spread_line in self.invoice_line.spread_line_ids:
            for move_line in spread_line.move_id.line_ids:
                spread_account = self.invoice_line.spread_account_id
                if move_line.account_id == spread_account:
                    self.assertEqual(move_line.credit, spread_line.amount)

    def test_06_supplier_invoice(self):
        # spread date set
        self.invoice_line.write({
            'price_unit': 345.96,
            'period_number': 3,
            'period_type': 'month',
            'spread_date': '2017-01-01'
        })
        self.invoice.write({
            'date_invoice': '2016-12-31'
        })
        # change the state of invoice to open by clicking Validate button
        self.invoice.action_invoice_open()
        self.assertEqual(len(self.invoice_line.spread_line_ids), 3)
        self.assertEqual(115.32,
                         self.invoice_line.spread_line_ids[0].amount)
        self.assertEqual('2017-01-31',
                         self.invoice_line.spread_line_ids[0].line_date)
        self.assertEqual(115.32,
                         self.invoice_line.spread_line_ids[1].amount)
        self.assertEqual('2017-02-28',
                         self.invoice_line.spread_line_ids[1].line_date)
        self.assertEqual(115.32,
                         self.invoice_line.spread_line_ids[2].amount)
        self.assertEqual('2017-03-31',
                         self.invoice_line.spread_line_ids[2].line_date)

    def test_07_supplier_invoice(self):
        # spread date set
        self.invoice_line.write({
            'period_number': 12,
            'period_type': 'month',
            'spread_date': '2017-02-01'
        })

        # change the state of invoice to open by clicking Validate button
        self.invoice.action_invoice_open()
        self.invoice.journal_id.write({'update_posted': True})
        self.invoice.action_invoice_cancel()
        self.assertEqual(len(self.invoice_line.spread_line_ids), 0)

    def test_08_supplier_invoice(self):
        # spread date set
        self.invoice_line.write({
            'period_number': 12,
            'period_type': 'month',
            'spread_date': '2017-02-01'
        })

        # change the state of invoice to open by clicking Validate button
        self.invoice.action_invoice_open()
        self.invoice.journal_id.write({'update_posted': True})
        self.invoice.action_invoice_cancel()
        self.assertEqual(len(self.invoice_line.spread_line_ids), 0)

    def test_09_get_fy_duration_days(self):
        # spread date set
        fy_dates = {
            'date_from': fields.Date.from_string('2017-01-01'),
            'date_to': fields.Date.from_string('2017-12-31'),
        }

        date_invoice_formatted = datetime.strptime('2017-01-01', DF).date()
        days = self.invoice_line._get_fy_duration('2017-01-01', option='days')

        self.assertEqual(
            days, (fy_dates['date_to'] - date_invoice_formatted).days + 1)

    def test_10_get_fy_duration_months(self):
        # spread date set
        fy_dates = {
            'date_from': fields.Date.from_string('2017-01-01'),
            'date_to': fields.Date.from_string('2017-12-31'),
        }

        months = self.invoice_line._get_fy_duration(
            '2017-01-01', option='months')

        self.assertEqual(
            months,
            (int(fy_dates['date_to'].strftime('%Y-%m-%d')[:4]) -
             int(fy_dates['date_from'].strftime('%Y-%m-%d')[:4])) * 12 +
            (int(fy_dates['date_to'].strftime('%Y-%m-%d')[5:7]) -
             int(fy_dates['date_from'].strftime('%Y-%m-%d')[5:7])) + 1
        )

    def test_11_get_fy_duration_years(self):
        # spread date set

        self.invoice.write({
            'date_invoice': '2015-01-01',
        })

        fy_dates = {
            'date_from': fields.Date.from_string('2015-01-01'),
            'date_to': fields.Date.from_string('2017-12-31'),
        }

        years = self.invoice_line._get_years(fy_dates)

        self.assertEqual(years, 3)

    def test_12_compute_spread_table(self):

        self.invoice_line.write({
            'spread_account_id': None,
        })

        table = self.invoice_line._compute_spread_table()
        self.assertEqual([], table)

    def test_13_internal_compute_spread_board_lines(self):
        table = [{'lines': [
            {
                'date': datetime.strptime('2017-01-01', '%Y-%m-%d').date(),
                'amount': 100.0,
            },
            {
                'date': datetime.strptime('2017-03-01', '%Y-%m-%d').date(),
                'amount': 200.0,
            },
            {
                'date': datetime.strptime('2017-01-01', '%Y-%m-%d').date(),
                'amount': 500.0,
            }
        ]}]

        self.invoice_line.write({
            'spread_start_date': '2017-02-01',
        })

        spread_start_date = datetime.strptime(
            self.invoice_line.spread_start_date, '%Y-%m-%d').date()

        tst_lines = [
            {
                'amount': 600.0,
                'date': datetime.strptime('2017-01-01', '%Y-%m-%d').date(),
                'spreaded_value': 0.0
            },
            {
                'amount': 200.0,
                'date': datetime.strptime('2017-03-01', '%Y-%m-%d').date(),
            }
        ]
        lines = self.invoice_line._internal_compute_spread_board_lines(
            spread_start_date, table)
        self.assertEqual(tst_lines, lines)

    def test_14_compute_spread_board(self):
        self.invoice_line.account_id.write({
            'deprecated': True,
        })

        with self.assertRaises(Warning):
            self.invoice_line.compute_spread_board()

    def test_15_create_entries(self):
        self.env['account.invoice.spread.line']._create_entries()

    def test_16_create_move_in_invoice(self):
        self.invoice_2.action_invoice_open()
        self.invoice_line_2.spread_line_ids.create_moves()
