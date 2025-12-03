from odoo import models, fields, api

class SalonEmployee(models.Model):
    _name = 'salon.employee'
    _description = 'Nhân viên Salon'
    _rec_name = 'ten_nv'

    ma_nv = fields.Char(string="Mã nhân viên", readonly=True, copy=False, default='New')
    ten_nv = fields.Char(string="Tên nhân viên", required=True)
    gioi_tinh = fields.Selection([
        ('nam', 'Nam'),
        ('nu', 'Nữ'),
        ('khac', 'Khác'),
    ], string="Giới tính")
    chuc_vu = fields.Char(string="Chức vụ", required=True)
    sdt = fields.Char(string="Số điện thoại", required=True)
    ngay_sinh = fields.Date(string="Ngày sinh")

    @api.model_create_multi
    def create(self, vals_list):
        """Tự động tạo mã nhân viên"""
        if isinstance(vals_list, dict):
            vals_list = [vals_list]
        for vals in vals_list:
            if not vals.get('ma_nv') or vals.get('ma_nv', '').strip() == '' or vals.get('ma_nv') == 'New':
                sequence = self.env['ir.sequence'].next_by_code('salon.employee.sequence') or 'New'
                vals['ma_nv'] = sequence
        return super(SalonEmployee, self).create(vals_list)

    def action_open_form_view(self):
        """Mở form xem chi tiết nhân viên"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Chi tiết nhân viên',
            'res_model': 'salon.employee',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
        }

    def action_open_edit(self):
        """Mở form chỉnh sửa nhân viên"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Chỉnh sửa nhân viên',
            'res_model': 'salon.employee',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
            'context': {'form_view_initial_mode': 'edit'},
        }

    def action_delete_record(self):
        """Xóa nhân viên"""
        for rec in self:
            rec.unlink()

