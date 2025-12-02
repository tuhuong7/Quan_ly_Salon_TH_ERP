from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    payment_state_custom = fields.Selection([
        ('not_paid', 'Chưa thanh toán'),
        ('partial', 'Thanh toán một phần'),
        ('paid', 'Đã thanh toán'),
    ], string='Trạng thái thanh toán', compute='_compute_payment_state_custom', store=True)

    transfer_receipt = fields.Binary(string='Biên lai chuyển khoản')
    transfer_receipt_name = fields.Char(string='Tên file biên lai')

    @api.depends('payment_state')
    def _compute_payment_state_custom(self):
        for record in self:
            if record.payment_state == 'not_paid':
                record.payment_state_custom = 'not_paid'
            elif record.payment_state == 'partial':
                record.payment_state_custom = 'partial'
            elif record.payment_state == 'paid':
                record.payment_state_custom = 'paid'
            else:
                record.payment_state_custom = 'not_paid'

