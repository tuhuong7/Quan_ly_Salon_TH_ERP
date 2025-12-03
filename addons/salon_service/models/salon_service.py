from odoo import models, fields, api

class SalonService(models.Model):
    _name = 'salon.service'
    _description = 'Service Information'

    code = fields.Char(string='Mã dịch vụ', readonly=True, copy=False, default='New')
    name = fields.Char(string='Tên dịch vụ', required=True)
    service_type = fields.Selection([
        ('hair', 'Làm tóc'),
        ('nail', 'Làm móng'),
        ('spa', 'Spa'),
        ('other', 'Khác')
    ], string='Loại dịch vụ', required=True)
    duration = fields.Integer(string='Thời gian (phút)', required=True)
    price = fields.Float(string='Giá (VNĐ)', required=True)
    status = fields.Selection([
        ('active', 'Đang hoạt động'),
        ('inactive', 'Ngưng hoạt động')
    ], string='Trạng thái', default='active')
    description = fields.Text(string='Mô tả')

    @api.model_create_multi
    def create(self, vals_list):
        """Tự động tạo mã dịch vụ"""
        for vals in vals_list:
            if not vals.get('code') or vals.get('code', '').strip() == '' or vals.get('code') == 'New':
                sequence = self.env['ir.sequence'].next_by_code('salon.service.sequence') or 'New'
                vals['code'] = sequence
        return super().create(vals_list)
