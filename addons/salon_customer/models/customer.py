from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Customer(models.Model):
    _name = "salon.customer"
    _description = "Khách hàng"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "create_date desc"
    code = fields.Char(string="Mã KH", readonly=True, copy=False, default='New')

    membership_rank_id = fields.Many2one(
        "salon.membership.rank",
        string="Hạng thành viên",
        required=True,
        ondelete="restrict",
        default=lambda self: self.env["salon.membership.rank"].get_default_rank(),
    )

    name = fields.Char(string="Họ và tên", required=True, index=True)

    gender = fields.Selection(
        selection=[
            ("m", "Nam"),
            ("f", "Nữ"),
            ("o", "Khác"),
        ],
        string="Giới tính",
        required=True,
        default="o",
    )

    phone = fields.Char(string="Số điện thoại", required=True, index=True)
    email = fields.Char(string="Email", index=True)
    birthday = fields.Date(string="Ngày sinh")
    address = fields.Char(string="Địa chỉ")

    total_spent = fields.Monetary(
        string="Tổng chi tiêu",
        currency_field="currency_id",
        default=0.0,
    )
    currency_id = fields.Many2one(
        "res.currency",
        default=lambda s: s.env.company.currency_id,
    )
    visit_count = fields.Integer(string="Số lần ghé", default=0)

    service_history_count = fields.Integer(
        string="Số lịch sử dịch vụ",
        compute="_compute_service_history_count",
        store=False,
    )

    def _compute_service_history_count(self):
        """Tính số lượng lịch sử dịch vụ của khách hàng"""
        for customer in self:
            try:
                if 'salon.service.history' in self.env.registry:
                    service_histories = self.env['salon.service.history'].search_count([
                        ('customer_id', '=', customer.id)
                    ])
                    customer.service_history_count = service_histories
                else:
                    customer.service_history_count = 0
            except (KeyError, AttributeError):
                customer.service_history_count = 0

    def _assign_membership_rank(self):
        for customer in self:
            rank = self.env["salon.membership.rank"].get_rank_for(
                total_spent=customer.total_spent or 0.0,
                visit_count=customer.visit_count or 0,
            )
            if rank and customer.membership_rank_id != rank:
                customer.membership_rank_id = rank.id

    def recompute_membership_rank(self):
        """API công khai để cập nhật lại hạng thành viên"""
        self._assign_membership_rank()

    def action_open_service_history(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Lịch sử dịch vụ",
            "res_model": "salon.service.history",
            "view_mode": "list,form",  
            "target": "current",
            "domain": [("customer_id", "=", self.id)],
            "context": {"default_customer_id": self.id},
        }

    def action_open_form_view(self):
        """Mở form ở chế độ xem (popup)."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Khách hàng",
            "res_model": "salon.customer",
            "res_id": self.id,
            "view_mode": "list,form",
            "target": "new",
            "context": {"form_view_initial_mode": "view"},
        }

    def action_open_form_edit(self):
        """Mở form ở chế độ sửa (popup)."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Chỉnh sửa khách hàng",
            "res_model": "salon.customer",
            "res_id": self.id,
            "view_mode": "form",
            "target": "current",
            "context": {"form_view_initial_mode": "edit"},
        }

    def action_delete_record(self):
        for rec in self:
            rec.unlink()

    @api.model
    def action_create_customer(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Tạo khách hàng",
            "res_model": "salon.customer",
            "view_mode": "form",
            "target": "current",
            "context": {"default_membership_rank_id": self.env["salon.membership.rank"].get_default_rank().id if self.env["salon.membership.rank"].get_default_rank() else False},
        }

    @api.model
    def action_edit_customer(self):
        active_id = self.env.context.get("active_id")
        if not active_id:
            return {"type": "ir.actions.client", "tag": "display_notification", "params": {"message": "Không có bản ghi nào được chọn.", "type": "warning"}}
        return {
            "type": "ir.actions.act_window",
            "name": "Sửa khách hàng",
            "res_model": "salon.customer",
            "res_id": active_id,
            "view_mode": "form",
            "target": "current",
            "context": {"form_view_initial_mode": "edit"},
        }

    @api.model
    def action_delete_customers(self):
        active_ids = self.env.context.get("active_ids", [])
        if active_ids:
            self.env["salon.customer"].browse(active_ids).unlink()
            return {"type": "ir.actions.client", "tag": "display_notification", "params": {"message": "Đã xóa khách hàng đã chọn.", "type": "success"}}
        return {"type": "ir.actions.client", "tag": "display_notification", "params": {"message": "Không có bản ghi nào được chọn.", "type": "warning"}}

    _sql_constraints = [
        ("uniq_phone", "unique(phone)", "Số điện thoại đã tồn tại! Mỗi số điện thoại chỉ được dùng cho 1 khách hàng."),
        ("check_total_spent", "CHECK(total_spent >= 0)", "Tổng chi tiêu phải ≥ 0!"),
        ("check_visit_count", "CHECK(visit_count >= 0)", "Số lần ghé phải ≥ 0!"),
    ]
    
    @api.constrains('email')
    def _check_unique_email(self):
        """Kiểm tra email unique (chỉ khi email không trống)"""
        for rec in self:
            if rec.email:
                existing = self.search([
                    ('email', '=', rec.email),
                    ('id', '!=', rec.id)
                ], limit=1)
                if existing:
                    raise ValidationError("Email này đã tồn tại cho khách hàng khác!")

    @api.model_create_multi
    def create(self, vals_list):
        """Tự động tạo mã khách hàng"""
        for vals in vals_list:
            if not vals.get('code') or vals.get('code', '').strip() == '' or vals.get('code') == 'New':
                sequence = self.env['ir.sequence'].next_by_code('salon.customer.sequence') or 'New'
                vals['code'] = sequence
        records = super().create(vals_list)
        
        ctx = self.env.context
        if ctx.get('return_model') == 'salon.appointment' and ctx.get('return_id'):
            appointment = self.env['salon.appointment'].browse(ctx.get('return_id'))
            if appointment and records:
                appointment.customer_id = records[0].id
        
        return records

    def write(self, vals):
        res = super().write(vals)
        tracked_fields = {'total_spent', 'visit_count'}
        if tracked_fields.intersection(vals.keys()):
            self._assign_membership_rank()
        return res

    @api.onchange('total_spent', 'visit_count')
    def _onchange_rank_from_stats(self):
        self._assign_membership_rank()

