from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class SalonShift(models.Model):
    _name = 'salon.shift'
    _description = 'Ca làm việc Salon'
    _order = 'ngay_lam_viec desc, gio_bat_dau asc'
    _rec_name = 'ma_ca'

    ma_ca = fields.Char(string="Mã ca", readonly=True, copy=False, default='New')
    ma_nv = fields.Many2one('salon.employee', string="Nhân viên", required=True, ondelete='cascade')
    ngay_lam_viec = fields.Date(string="Ngày làm việc", required=True, default=fields.Date.context_today)
    ghi_chu = fields.Text(string="Ghi chú")

    gio_bat_dau = fields.Float(string="Giờ bắt đầu", required=True, help="VD: 8.0 = 08:00, 14.5 = 14:30")
    gio_ket_thuc = fields.Float(string="Giờ kết thúc", required=True, help="VD: 12.5 = 12:30, 18.0 = 18:00")

    gio_bat_dau_str = fields.Char(string="Giờ bắt đầu (hh:mm)", compute="_compute_time_display", store=True)
    gio_ket_thuc_str = fields.Char(string="Giờ kết thúc (hh:mm)", compute="_compute_time_display", store=True)

    ngay_gio_bat_dau = fields.Datetime(string="Ngày & Giờ bắt đầu", compute="_compute_datetime_range", store=True)
    ngay_gio_ket_thuc = fields.Datetime(string="Ngày & Giờ kết thúc", compute="_compute_datetime_range", store=True)

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
            start_dt = fields.Datetime.from_string(start)
            defaults['ngay_lam_viec'] = start_dt.date()
            defaults['gio_bat_dau'] = start_dt.hour + start_dt.minute / 60
            defaults['ngay_gio_bat_dau'] = start_dt

        if stop:
            stop_dt = fields.Datetime.from_string(stop)
            defaults['gio_ket_thuc'] = stop_dt.hour + stop_dt.minute / 60
            defaults['ngay_gio_ket_thuc'] = stop_dt

        return defaults

    @api.depends('gio_bat_dau', 'gio_ket_thuc')
    def _compute_time_display(self):
        for rec in self:
            def float_to_time_str(f):
                if f is False:
                    return ""
                hour = int(f)
                minute = int(round((f - hour) * 60))
                return f"{hour:02d}:{minute:02d}"

            rec.gio_bat_dau_str = float_to_time_str(rec.gio_bat_dau)
            rec.gio_ket_thuc_str = float_to_time_str(rec.gio_ket_thuc)

    @api.depends('ngay_lam_viec', 'gio_bat_dau', 'gio_ket_thuc')
    def _compute_datetime_range(self):
        for rec in self:
            if rec.ngay_lam_viec:
                base_date = datetime.combine(rec.ngay_lam_viec, datetime.min.time())
                rec.ngay_gio_bat_dau = base_date + timedelta(hours=rec.gio_bat_dau or 0)
                rec.ngay_gio_ket_thuc = base_date + timedelta(hours=rec.gio_ket_thuc or 0)
            else:
                rec.ngay_gio_bat_dau = rec.ngay_gio_ket_thuc = False

    @api.model_create_multi
    def create(self, vals_list):
        """Tự động tạo mã ca và xử lý datetime"""
        for vals in vals_list:
            if not vals.get('ma_ca') or vals.get('ma_ca', '').strip() == '' or vals.get('ma_ca') == 'New':
                seq = self.env['ir.sequence'].next_by_code('salon.shift.sequence')
                vals['ma_ca'] = seq or 'New'

            if vals.get('ngay_gio_bat_dau') and not vals.get('gio_bat_dau'):
                start_dt = fields.Datetime.from_string(vals['ngay_gio_bat_dau'])
                vals['ngay_lam_viec'] = start_dt.date()
                vals['gio_bat_dau'] = start_dt.hour + start_dt.minute / 60

            if vals.get('ngay_gio_ket_thuc') and not vals.get('gio_ket_thuc'):
                end_dt = fields.Datetime.from_string(vals['ngay_gio_ket_thuc'])
                vals['gio_ket_thuc'] = end_dt.hour + end_dt.minute / 60

        return super(SalonShift, self).create(vals_list)

    def write(self, vals):
        for rec in self:
            if vals.get('ngay_gio_bat_dau'):
                start_dt = fields.Datetime.from_string(vals['ngay_gio_bat_dau'])
                vals['ngay_lam_viec'] = start_dt.date()
                vals['gio_bat_dau'] = start_dt.hour + start_dt.minute / 60

            if vals.get('ngay_gio_ket_thuc'):
                end_dt = fields.Datetime.from_string(vals['ngay_gio_ket_thuc'])
                vals['gio_ket_thuc'] = end_dt.hour + end_dt.minute / 60

        return super(SalonShift, self).write(vals)

    @api.constrains('gio_bat_dau', 'gio_ket_thuc')
    def _check_time(self):
        for rec in self:
            if rec.gio_bat_dau >= rec.gio_ket_thuc:
                raise ValidationError("Giờ bắt đầu phải nhỏ hơn giờ kết thúc.")
            if not (0 <= rec.gio_bat_dau <= 24 and 0 <= rec.gio_ket_thuc <= 24):
                raise ValidationError("Giờ làm việc phải nằm trong khoảng 0–24.")

    @api.depends('ma_nv')
    def _compute_color(self):
        for rec in self:
            rec.color = (rec.ma_nv.id * 23) % 12 if rec.ma_nv else 1

    def name_get(self):
        result = []
        for rec in self:
            name = f"{rec.ma_ca} ({rec.ma_nv.ten_nv or ''}): {rec.gio_bat_dau_str}-{rec.gio_ket_thuc_str}"
            result.append((rec.id, name))
        return result
