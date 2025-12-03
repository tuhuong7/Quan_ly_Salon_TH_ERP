from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SalonInvoice(models.Model):
    _name = 'salon.invoice'
    _description = 'Hoá đơn thanh toán'
    _order = 'date_invoice desc, id desc'

    name = fields.Char(
        string='Mã hoá đơn',
        required=True,
        copy=False,
        readonly=True,
        default='New'
    )
    customer_id = fields.Many2one('salon.customer', string='Khách hàng', required=True)
    customer_membership_rank_id = fields.Many2one(
        'salon.membership.rank',
        string='Hạng thành viên',
        related='customer_id.membership_rank_id',
        store=False,
        readonly=True
    )
    appointment_id = fields.Many2one('salon.appointment', string='Lịch hẹn')
    employee_id = fields.Many2one(
        'salon.employee',
        string='Nhân viên',
        help="Nhân viên thực hiện dịch vụ (tự động lấy từ appointment nếu có)"
    )
    date_invoice = fields.Datetime(string='Ngày lập', default=fields.Datetime.now, required=True)
    total_amount = fields.Monetary(
        string='Tổng hoá đơn',
        currency_field='currency_id',
        compute='_compute_total',
        store=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda s: s.env.company.currency_id
    )
    payment_method = fields.Selection([
        ('cash', 'Tiền mặt'),
        ('bank', 'Chuyển khoản'),
        ('mixed', 'Kết hợp')
    ], string='Phương thức thanh toán', required=True, default='cash')
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('paid', 'Đã thanh toán'),
        ('cancel', 'Huỷ')
    ], default='draft', string='Trạng thái')
    promotion_id = fields.Many2one(
        'salon.promotion',
        string='Khuyến mãi',
        domain="[('state', '=', 'active')]",
        help="Chọn khuyến mãi để áp dụng cho hóa đơn này"
    )
    discount = fields.Float(string='Chiết khấu từ hạng (%)', compute='_compute_discount', store=True)
    promotion_discount_amount = fields.Monetary(
        string='Giảm giá từ khuyến mãi',
        currency_field='currency_id',
        compute='_compute_promotion_discount',
        store=True
    )
    line_ids = fields.One2many('salon.invoice.line', 'invoice_id', string='Chi tiết hoá đơn')

    @api.depends('line_ids.subtotal', 'discount', 'promotion_discount_amount')
    def _compute_total(self):
        for rec in self:
            subtotal_after_line_promotions = sum(line.subtotal for line in rec.line_ids)
            amount_after_membership_discount = subtotal_after_line_promotions * (1 - rec.discount / 100.0)
            rec.total_amount = max(0.0, amount_after_membership_discount - rec.promotion_discount_amount)

    @api.depends('customer_id.membership_rank_id', 'customer_id.membership_rank_id.discount_percentage')
    def _compute_discount(self):
        for rec in self:
            if rec.customer_id.membership_rank_id:
                rec.discount = rec.customer_id.membership_rank_id.discount_percentage or 0.0
            else:
                rec.discount = 0.0

    @api.depends('promotion_id', 'line_ids.subtotal', 'discount')
    def _compute_promotion_discount(self):
        for rec in self:
            if not rec.promotion_id or rec.promotion_id.state != 'active':
                rec.promotion_discount_amount = 0.0
                continue
            
            subtotal = sum(line.subtotal for line in rec.line_ids)
            amount_after_membership_discount = subtotal * (1 - rec.discount / 100.0)
            
            if amount_after_membership_discount < rec.promotion_id.min_amount:
                rec.promotion_discount_amount = 0.0
                continue
            
            if rec.promotion_id.discount_type == 'percentage':
                rec.promotion_discount_amount = amount_after_membership_discount * (rec.promotion_id.discount_value / 100.0)
            elif rec.promotion_id.discount_type == 'fixed':
                rec.promotion_discount_amount = min(rec.promotion_id.discount_value, amount_after_membership_discount)
            else:
                rec.promotion_discount_amount = 0.0

    def action_open_payment_confirm_wizard(self):
        """Mở wizard xác nhận thanh toán"""
        self.ensure_one()
        if self.state != 'draft':
            raise ValidationError("Chỉ có thể thanh toán hóa đơn ở trạng thái nháp!")
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Xác nhận thanh toán',
            'res_model': 'salon.payment.confirm.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'active_id': self.id,
                'default_invoice_id': self.id,
            }
        }

    def action_print_invoice(self):
        """Mở màn hình in hóa đơn"""
        self.ensure_one()
        return {
            'type': 'ir.actions.report',
            'report_name': 'salon_tc_invoice_extend.report_salon_invoice',
            'report_type': 'qweb-pdf',
            'res_model': 'salon.invoice',
            'res_id': self.id,
            'context': self.env.context,
        }


    @api.onchange('promotion_id')
    def _onchange_promotion_id(self):
        """Validate promotion khi chọn"""
        if self.promotion_id:
            if self.promotion_id.state != 'active':
                return {
                    'warning': {
                        'title': 'Cảnh báo',
                        'message': f"Khuyến mãi '{self.promotion_id.name}' không còn hoạt động!"
                    }
                }
            from datetime import date
            today = date.today()
            if not (self.promotion_id.date_start <= today <= self.promotion_id.date_end):
                return {
                    'warning': {
                        'title': 'Cảnh báo',
                        'message': f"Khuyến mãi '{self.promotion_id.name}' không còn trong thời gian áp dụng!"
                    }
                }

    @api.model_create_multi
    def create(self, vals_list):
        """Tự động tạo mã hóa đơn"""
        for vals in vals_list:
            if not vals.get('name') or vals.get('name', '').strip() == '' or vals.get('name') == 'New':
                sequence = self.env['ir.sequence'].next_by_code('salon.invoice') or 'New'
                vals['name'] = sequence
        return super().create(vals_list)

    def write(self, vals):
        """Override write để xử lý khi state thay đổi qua kéo thả trong kanban"""
        old_states = {rec.id: rec.state for rec in self}
        
        if 'state' in vals and vals['state'] == 'paid':
            for rec in self:
                if old_states.get(rec.id) == 'draft':
                    customer = rec.customer_id
                    customer.total_spent += rec.total_amount
                    customer.visit_count += 1
                    customer._assign_membership_rank()
                    rec._create_service_history()
        elif 'state' in vals and vals['state'] == 'cancel':
            for rec in self:
                if old_states.get(rec.id) == 'paid':
                    service_histories = self.env['salon.service.history'].search([('invoice_name', '=', rec.name)])
                    service_histories.unlink()
                    customer = rec.customer_id
                    customer.total_spent -= rec.total_amount
                    customer.visit_count = max(0, customer.visit_count - 1)
                    customer._assign_membership_rank()
        return super().write(vals)

    @api.constrains('promotion_id')
    def _check_promotion_validity(self):
        """Kiểm tra khuyến mãi có hợp lệ không"""
        for rec in self:
            if rec.promotion_id:
                if rec.promotion_id.state != 'active':
                    raise ValidationError(f"Khuyến mãi '{rec.promotion_id.name}' không còn hoạt động!")
                from datetime import date
                today = date.today()
                if not (rec.promotion_id.date_start <= today <= rec.promotion_id.date_end):
                    raise ValidationError(f"Khuyến mãi '{rec.promotion_id.name}' không còn trong thời gian áp dụng!")

    def _create_service_history(self):
        """Tạo Service History từ invoice lines"""
        for rec in self:
            if not rec.line_ids:
                continue
            
            employee_id = False
            if rec.employee_id:
                employee_id = rec.employee_id.id
            elif rec.appointment_id and rec.appointment_id.employee_id:
                employee_id = rec.appointment_id.employee_id.id
                rec.employee_id = employee_id
            
            if not employee_id:
                raise ValidationError("Vui lòng chọn nhân viên thực hiện dịch vụ!")
            
            for line in rec.line_ids:
                self.env['salon.service.history'].create({
                    'customer_id': rec.customer_id.id,
                    'date': rec.date_invoice,
                    'service_id': line.service_id.id,
                    'staff_id': employee_id,
                    'amount': line.subtotal,
                    'currency_id': rec.currency_id.id,
                    'notes': f"Hóa đơn: {rec.name}",
                    'invoice_name': rec.name,
                })

    def action_cancel(self):
        """Hủy hóa đơn"""
        for rec in self:
            if rec.state == 'paid':
                service_histories = self.env['salon.service.history'].search([('invoice_name', '=', rec.name)])
                service_histories.unlink()
                customer = rec.customer_id
                customer.total_spent -= rec.total_amount
                customer.visit_count = max(0, customer.visit_count - 1)
                customer._assign_membership_rank()
            rec.state = 'cancel'

class SalonInvoiceLine(models.Model):
    _name = 'salon.invoice.line'
    _description = 'Chi tiết hoá đơn'

    invoice_id = fields.Many2one('salon.invoice', string='Hoá đơn', required=True, ondelete='cascade')
    service_id = fields.Many2one('salon.service', string='Dịch vụ', required=True)
    quantity = fields.Integer(string='Số lượng', default=1, required=True)
    price_unit = fields.Monetary(
        string='Đơn giá',
        currency_field='currency_id',
        compute='_compute_price_unit',
        store=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='invoice_id.currency_id',
        store=True
    )
    promotion_id = fields.Many2one(
        'salon.promotion',
        string='Khuyến mãi',
        domain="[('state', '=', 'active')]",
        help="Khuyến mãi áp dụng cho dịch vụ này"
    )
    line_promotion_discount_amount = fields.Monetary(
        string='Giảm giá từ khuyến mãi',
        currency_field='currency_id',
        compute='_compute_line_promotion_discount',
        store=True
    )
    subtotal_before_discount = fields.Monetary(
        string='Thành tiền (trước giảm giá)',
        currency_field='currency_id',
        compute='_compute_subtotal_before_discount',
        store=True
    )
    subtotal = fields.Monetary(
        string='Thành tiền',
        currency_field='currency_id',
        compute='_compute_subtotal',
        store=True
    )

    @api.depends('service_id')
    def _compute_price_unit(self):
        """Tính đơn giá từ service"""
        for rec in self:
            if rec.service_id and rec.service_id.price:
                rec.price_unit = rec.service_id.price
            else:
                rec.price_unit = 0.0

    @api.depends('quantity', 'price_unit')
    def _compute_subtotal_before_discount(self):
        """Tính thành tiền trước khi giảm giá"""
        for rec in self:
            rec.subtotal_before_discount = rec.quantity * rec.price_unit

    @api.depends('promotion_id', 'subtotal_before_discount')
    def _compute_line_promotion_discount(self):
        """Tính giảm giá từ khuyến mãi của dòng"""
        for rec in self:
            if not rec.promotion_id or rec.promotion_id.state != 'active':
                rec.line_promotion_discount_amount = 0.0
            else:
                promotion = rec.promotion_id
                if promotion.discount_type == 'percentage':
                    rec.line_promotion_discount_amount = rec.subtotal_before_discount * (promotion.discount_value / 100.0)
                elif promotion.discount_type == 'fixed':
                    rec.line_promotion_discount_amount = min(promotion.discount_value, rec.subtotal_before_discount)
                else:
                    rec.line_promotion_discount_amount = 0.0

    @api.depends('subtotal_before_discount', 'line_promotion_discount_amount')
    def _compute_subtotal(self):
        """Tính thành tiền sau khi giảm giá từ khuyến mãi dòng"""
        for rec in self:
            rec.subtotal = max(0.0, rec.subtotal_before_discount - rec.line_promotion_discount_amount)
