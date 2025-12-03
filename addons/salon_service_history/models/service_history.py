from odoo import models, fields


class ServiceHistory(models.Model):
    _name = "salon.service.history"
    _description = "Lịch sử dịch vụ"

    customer_id = fields.Many2one(
        "salon.customer", string="Khách hàng", required=True, ondelete="cascade"
    )
    date = fields.Datetime(
        string="Ngày thực hiện", required=True, default=fields.Datetime.now
    )
    service_id = fields.Many2one("salon.service", string="Dịch vụ", required=True)
    staff_id = fields.Many2one("salon.employee", string="Nhân viên", required=True)
    invoice_name = fields.Char(string="Mã hóa đơn", help="Mã hóa đơn liên quan", index=True)
    amount = fields.Monetary(
        string="Chi phí", currency_field="currency_id", default=0.0
    )
    currency_id = fields.Many2one(
        "res.currency", default=lambda s: s.env.company.currency_id
    )
    notes = fields.Text(string="Ghi chú")

    def action_open_invoice(self):
        """Mở hóa đơn từ invoice_name"""
        self.ensure_one()
        if not self.invoice_name:
            return False
        
        try:
            if 'salon.invoice' in self.env.registry:
                invoice = self.env['salon.invoice'].search([
                    ('name', '=', self.invoice_name)
                ], limit=1)
                if invoice:
                    return {
                        'type': 'ir.actions.act_window',
                        'name': 'Hóa đơn',
                        'res_model': 'salon.invoice',
                        'res_id': invoice.id,
                        'view_mode': 'form',
                        'target': 'current',
                    }
        except (KeyError, AttributeError):
            pass
        return False

