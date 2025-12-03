from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SalonShift(models.Model):
    _name = 'salon.shift'
    _description = 'Ca làm việc Salon'
    _order = 'ngay_gio_bat_dau desc'
    _rec_name = 'ma_ca'

    ma_ca = fields.Char(string="Mã ca", readonly=True, copy=False, default='New')
    ma_nv = fields.Many2one('salon.employee', string="Nhân viên", required=True, ondelete='cascade')
    ghi_chu = fields.Text(string="Ghi chú")

    ngay_gio_bat_dau = fields.Datetime(string="Ngày & Giờ bắt đầu", required=True)
    ngay_gio_ket_thuc = fields.Datetime(string="Ngày & Giờ kết thúc", required=True)

    color = fields.Integer(string='Màu hiển thị', compute='_compute_color', store=True)

    @api.model
    def default_get(self, fields_list):
        """Khi kéo thả trên Calendar, tự động lấy giờ và ngày"""
        defaults = super().default_get(fields_list)
        ctx = self.env.context

        start = (
            ctx.get('default_start')
            or ctx.get('default_date_start')
            or ctx.get('default_ngay_gio_bat_dau')
        )
        stop = (
            ctx.get('default_stop')
            or ctx.get('default_date_stop')
            or ctx.get('default_ngay_gio_ket_thuc')
        )

        if start:
            start_dt = fields.Datetime.from_string(start) if isinstance(start, str) else start
            defaults['ngay_gio_bat_dau'] = start_dt

        if stop:
            stop_dt = fields.Datetime.from_string(stop) if isinstance(stop, str) else stop
            defaults['ngay_gio_ket_thuc'] = stop_dt

        return defaults


    @api.model_create_multi
    def create(self, vals_list):
        """Tự động tạo mã ca"""
        for vals in vals_list:
            if not vals.get('ma_ca') or vals.get('ma_ca', '').strip() == '' or vals.get('ma_ca') == 'New':
                seq = self.env['ir.sequence'].next_by_code('salon.shift.sequence')
                vals['ma_ca'] = seq or 'New'
        return super(SalonShift, self).create(vals_list)

    @api.constrains('ngay_gio_bat_dau', 'ngay_gio_ket_thuc')
    def _check_time(self):
        for rec in self:
            if rec.ngay_gio_bat_dau and rec.ngay_gio_ket_thuc:
                if rec.ngay_gio_bat_dau >= rec.ngay_gio_ket_thuc:
                    raise ValidationError("Giờ bắt đầu phải nhỏ hơn giờ kết thúc.")

    @api.depends('ma_nv')
    def _compute_color(self):
        for rec in self:
            rec.color = (rec.ma_nv.id * 23) % 12 if rec.ma_nv else 1

    def name_get(self):
        result = []
        for rec in self:
            if rec.ma_nv:
                if rec.ngay_gio_bat_dau and rec.ngay_gio_ket_thuc:
                    start_dt = fields.Datetime.context_timestamp(self, rec.ngay_gio_bat_dau)
                    end_dt = fields.Datetime.context_timestamp(self, rec.ngay_gio_ket_thuc)
                    start_str = start_dt.strftime('%H:%M')
                    end_str = end_dt.strftime('%H:%M')
                    name = f"{rec.ma_nv.ten_nv or ''} ({start_str}-{end_str})"
                else:
                    name = rec.ma_nv.ten_nv or ''
            else:
                name = rec.ma_ca or 'New'
            result.append((rec.id, name))
        return result
