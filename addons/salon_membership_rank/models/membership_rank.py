from odoo import models, fields, api
from odoo.exceptions import ValidationError


class MembershipRank(models.Model):
    _name = "salon.membership.rank"
    _description = "Hạng thành viên"
    _order = "min_total_spent desc, min_visit_count desc"
    
    code = fields.Char(string="Mã hạng", readonly=True, copy=False, default='New')
    name = fields.Char(string="Tên hạng", required=True)
    min_total_spent = fields.Monetary(
        string="Tổng chi tiêu tối thiểu",
        currency_field="currency_id",
        default=0.0,
        required=True,
    )
    min_visit_count = fields.Integer(
        string="Số lần ghé tối thiểu",
        default=0,
        required=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        default=lambda s: s.env.company.currency_id,
    )
    discount_percentage = fields.Float(
        string="Chiết khấu (%)",
        default=0.0,
        help="Phần trăm chiết khấu áp dụng cho khách hàng có hạng này"
    )

    @api.constrains('discount_percentage')
    def _check_discount_percentage(self):
        for rec in self:
            if rec.discount_percentage < 0.0:
                raise ValidationError("Chiết khấu không được âm!")
            if rec.discount_percentage > 100.0:
                raise ValidationError("Chiết khấu không được vượt quá 100%!")
    description = fields.Text(string="Mô tả")
    active = fields.Boolean(string="Hoạt động", default=True)

    @api.model_create_multi
    def create(self, vals_list):
        """Tự động tạo mã hạng thành viên"""
        for vals in vals_list:
            if not vals.get('code') or vals.get('code', '').strip() == '' or vals.get('code') == 'New':
                sequence = self.env['ir.sequence'].next_by_code('salon.membership.rank.sequence') or 'New'
                vals['code'] = sequence
        return super().create(vals_list)

    @api.model
    def get_default_rank(self):
        """Lấy hạng mặc định (hạng thấp nhất)"""
        return self.search([("active", "=", True)], order="min_total_spent asc, min_visit_count asc", limit=1)

    @api.model
    def get_rank_for(self, total_spent=0.0, visit_count=0):
        """Lấy hạng phù hợp dựa trên tổng chi tiêu và số lần ghé"""
        ranks = self.search([("active", "=", True)], order="min_total_spent desc, min_visit_count desc")
        for rank in ranks:
            if total_spent >= rank.min_total_spent and visit_count >= rank.min_visit_count:
                return rank
        return self.get_default_rank()

