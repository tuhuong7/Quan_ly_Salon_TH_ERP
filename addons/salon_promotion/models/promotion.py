from odoo import models, fields, api
from datetime import date


class Promotion(models.Model):
    _name = "salon.promotion"
    _description = "Khuyến mãi"
    _order = "date_start desc, id desc"

    name = fields.Char(string="Tên khuyến mãi", required=True)
    code = fields.Char(string="Mã khuyến mãi", readonly=True, copy=False, default='New')
    description = fields.Text(string="Mô tả")
    
    date_start = fields.Date(string="Ngày bắt đầu", required=True, default=fields.Date.today)
    date_end = fields.Date(string="Ngày kết thúc", required=True)
    
    min_amount = fields.Monetary(
        string="Giá trị đơn hàng tối thiểu",
        currency_field="currency_id",
        default=0.0,
    )
    currency_id = fields.Many2one(
        "res.currency",
        default=lambda s: s.env.company.currency_id,
    )
    
    discount_type = fields.Selection([
        ("percentage", "Phần trăm (%)"),
        ("fixed", "Số tiền cố định"),
    ], string="Loại giảm giá", required=True, default="percentage")
    discount_value = fields.Float(string="Giá trị giảm", required=True, default=0.0)
    
    state = fields.Selection([
        ("draft", "Nháp"),
        ("active", "Đang áp dụng"),
        ("expired", "Hết hạn"),
        ("cancelled", "Đã hủy"),
    ], string="Trạng thái", default="draft", compute="_compute_state", store=True)
    
    active = fields.Boolean(string="Hoạt động", default=True)
    
    @api.depends("date_start", "date_end", "active")
    def _compute_state(self):
        today = date.today()
        for rec in self:
            if not rec.active:
                rec.state = "cancelled"
            elif rec.date_end < today:
                rec.state = "expired"
            elif rec.date_start <= today <= rec.date_end:
                rec.state = "active"
            else:
                rec.state = "draft"
    
    @api.model_create_multi
    def create(self, vals_list):
        """Tự động tạo mã khuyến mãi"""
        for vals in vals_list:
            if not vals.get('code') or vals.get('code', '').strip() == '' or vals.get('code') == 'New':
                sequence = self.env['ir.sequence'].next_by_code('salon.promotion.sequence') or 'New'
                vals['code'] = sequence
        return super().create(vals_list)
    
    def action_activate(self):
        """Kích hoạt khuyến mãi"""
        self.write({"active": True})
    
    def action_cancel(self):
        """Hủy khuyến mãi"""
        self.write({"active": False})

