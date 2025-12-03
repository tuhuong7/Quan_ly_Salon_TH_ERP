from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PaymentConfirmWizard(models.TransientModel):
    _name = 'salon.payment.confirm.wizard'
    _description = 'Wizard xác nhận thanh toán hóa đơn'

    invoice_id = fields.Many2one('salon.invoice', string='Hóa đơn', required=True, readonly=True)
    customer_id = fields.Many2one('salon.customer', related='invoice_id.customer_id', string='Khách hàng', readonly=True)
    total_amount = fields.Monetary(
        related='invoice_id.total_amount',
        string='Tổng tiền',
        currency_field='currency_id',
        readonly=True
    )
    currency_id = fields.Many2one('res.currency', related='invoice_id.currency_id', readonly=True)
    payment_method = fields.Selection(related='invoice_id.payment_method', string='Phương thức thanh toán', readonly=True)
    config_bank_account_name = fields.Char(string='Tên chủ TK (Salon)', readonly=True)
    config_bank_account_number = fields.Char(string='Số tài khoản (Salon)', readonly=True)
    config_bank_name = fields.Char(string='Ngân hàng (Salon)', readonly=True)
    
    line_ids = fields.One2many(
        'salon.payment.confirm.wizard.line',
        'wizard_id',
        string='Chi tiết dịch vụ',
        readonly=True
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        invoice_id = self.env.context.get('active_id')
        if invoice_id:
            invoice = self.env['salon.invoice'].browse(invoice_id)
            res['invoice_id'] = invoice_id
            
            res['config_bank_account_name'] = ''
            res['config_bank_account_number'] = ''
            res['config_bank_name'] = ''
            
            lines = []
            for line in invoice.line_ids:
                lines.append((0, 0, {
                    'service_id': line.service_id.id,
                    'quantity': line.quantity,
                    'price_unit': line.price_unit,
                    'promotion_id': line.promotion_id.id if line.promotion_id else False,
                    'line_promotion_discount_amount': line.line_promotion_discount_amount,
                    'subtotal': line.subtotal,
                }))
            res['line_ids'] = lines
        return res

    def action_confirm_payment(self):
        """Xác nhận thanh toán và hoàn tất"""
        self.ensure_one()
        invoice = self.invoice_id
        
        if invoice.state != 'draft':
            raise ValidationError("Chỉ có thể thanh toán hóa đơn ở trạng thái nháp!")
        
        invoice.state = 'paid'
        customer = invoice.customer_id
        customer.total_spent += invoice.total_amount
        customer.visit_count += 1
        customer._assign_membership_rank()
        
        invoice._create_service_history()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Thành công',
                'message': f'Đã xác nhận thanh toán hóa đơn {invoice.name} thành công!',
                'type': 'success',
                'sticky': False,
            }
        }


class PaymentConfirmWizardLine(models.TransientModel):
    _name = 'salon.payment.confirm.wizard.line'
    _description = 'Chi tiết dịch vụ trong wizard xác nhận thanh toán'

    wizard_id = fields.Many2one('salon.payment.confirm.wizard', string='Wizard', required=True, ondelete='cascade')
    service_id = fields.Many2one('salon.service', string='Dịch vụ', readonly=True)
    quantity = fields.Integer(string='Số lượng', readonly=True)
    price_unit = fields.Monetary(
        string='Đơn giá',
        currency_field='currency_id',
        readonly=True
    )
    promotion_id = fields.Many2one('salon.promotion', string='Khuyến mãi', readonly=True)
    line_promotion_discount_amount = fields.Monetary(
        string='Giảm giá từ KM',
        currency_field='currency_id',
        readonly=True
    )
    currency_id = fields.Many2one('res.currency', related='wizard_id.currency_id', readonly=True)
    subtotal = fields.Monetary(
        string='Thành tiền',
        currency_field='currency_id',
        readonly=True
    )

