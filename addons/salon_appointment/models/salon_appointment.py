from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import timedelta


class SalonAppointment(models.Model):
    _name = "salon.appointment"
    _description = "Salon Appointment Management"
    _order = "id desc"

    code = fields.Char(
        string="Mã Lịch Hẹn",
        readonly=True,  
        copy=False,
        default=lambda self: 'New'
    )
    customer_id = fields.Many2one('salon.customer', string="Khách Hàng", required=True)
    phone = fields.Char(string="Số Điện Thoại", related="customer_id.phone", store=True, readonly=True)
    employee_id = fields.Many2one('salon.employee', string="Stylist", required=True)
    service_ids = fields.One2many('salon.appointment.service', 'appointment_id', string="Dịch Vụ", required=True)
    service_names = fields.Char(
        string="Tên dịch vụ",
        compute="_compute_service_names",
        store=False,
        help="Danh sách tên dịch vụ (dùng để hiển thị)"
    )
    service_list = fields.Char(
        string="Danh sách dịch vụ (separated)",
        compute="_compute_service_list",
        store=False,
        help="Danh sách dịch vụ phân cách bằng || để hiển thị trong kanban"
    )
    duration = fields.Float(string="Thời Lượng (Giờ)", default=1.0, required=True)
    date_appointment = fields.Datetime(string="Ngày Giờ Hẹn", required=True)
    arrival_time = fields.Datetime(string="Giờ Khách Đến")
    note = fields.Text(string="Ghi Chú")

    state = fields.Selection([
        ('pending', 'Đang chờ'),
        ('confirmed', 'Đã xác nhận'),
        ('processing', 'Đang thực hiện'),
        ('done', 'Đã hoàn thành'),
        ('cancel', 'Đã hủy')
    ], string="Trạng Thái", default='pending')
    cancel_reason = fields.Text(string="Lý do hủy", help="Ghi chú lý do hủy lịch hẹn")

    @api.constrains('employee_id', 'date_appointment', 'duration', 'state')
    def _check_duplicate_appointment(self):
        for rec in self:
            rec._check_conflict()

    def _check_conflict(self):
        """Kiểm tra trùng lịch riêng (để gọi lại trong reschedule)"""
        if self.state in ('pending', 'confirmed', 'processing'):
            start = self.date_appointment
            end = start + timedelta(hours=self.duration)
            conflicts = self.search([
                ('id', '!=', self.id),
                ('employee_id', '=', self.employee_id.id),
                ('state', 'in', ['pending', 'confirmed', 'processing']),
            ])
            for conflict in conflicts:
                c_start = conflict.date_appointment
                c_end = c_start + timedelta(hours=conflict.duration)
                if start < c_end and c_start < end:
                    raise ValidationError("Stylist đã có lịch hẹn trùng tại thời điểm này!")

    @api.model_create_multi
    def create(self, vals_list):
        """Tự động tạo mã lịch hẹn và dịch vụ"""
        for vals in vals_list:
            code = vals.get('code', 'New')
            if not code or code.strip() == '' or code == 'New':
                sequence = self.env['ir.sequence'].next_by_code('salon.appointment.sequence') or 'New'
                vals['code'] = sequence
            
            service_ids = vals.get('service_ids', [])
            if not service_ids or (isinstance(service_ids, list) and len(service_ids) == 0):
                raise ValidationError("Vui lòng nhập ít nhất một dịch vụ!")
        
        records = super().create(vals_list)
        
        return records
    
    @api.model
    def _update_old_appointment_codes(self):
        """Tự động cập nhật mã cho các records cũ có code='New'"""
        appointments = self.env['salon.appointment'].search([('code', '=', 'New')])
        for appointment in appointments:
            sequence = self.env['ir.sequence'].next_by_code('salon.appointment.sequence') or 'New'
            appointment.write({'code': sequence})
        return len(appointments)
    
    def action_update_codes(self):
        """Cập nhật mã cho các records có code='New'"""
        appointments = self.env['salon.appointment'].search([('code', '=', 'New')])
        if appointments:
            for appointment in appointments:
                sequence = self.env['ir.sequence'].next_by_code('salon.appointment.sequence') or 'New'
                appointment.write({'code': sequence})
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Thành công',
                    'message': f'Đã cập nhật mã cho {len(appointments)} lịch hẹn.',
                    'type': 'success',
                    'sticky': False,
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Thông báo',
                    'message': 'Không có lịch hẹn nào cần cập nhật mã.',
                    'type': 'info',
                    'sticky': False,
                }
            }
    
    def action_update_code(self):
        """Cập nhật mã cho record hiện tại nếu code='New'"""
        for record in self:
            if record.code == 'New':
                sequence = self.env['ir.sequence'].next_by_code('salon.appointment.sequence') or 'New'
                record.write({'code': sequence})
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Thành công',
                        'message': f'Đã cập nhật mã lịch hẹn thành: {sequence}',
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Thông báo',
                        'message': f'Mã lịch hẹn đã có: {record.code}',
                        'type': 'info',
                        'sticky': False,
                    }
                }
    
    
    def action_confirm(self):
        """Xác nhận lịch hẹn"""
        for rec in self:
            if rec.state != 'pending':
                raise ValidationError("Chỉ lịch đang chờ mới có thể xác nhận.")
            rec.state = 'confirmed'

    def action_start(self):
        """Bắt đầu thực hiện dịch vụ"""
        for rec in self:
            if rec.state not in ('pending', 'confirmed'):
                raise ValidationError("Chỉ lịch đang chờ hoặc đã xác nhận mới có thể bắt đầu.")
            rec.state = 'processing'
            rec.arrival_time = fields.Datetime.now()

    def action_done(self):
        for rec in self:
            if rec.state != 'processing':
                raise ValidationError("Chỉ lịch đang làm mới có thể hoàn tất.")
            rec.state = 'done'
    
    def action_create_invoice(self):
        """Tạo hóa đơn từ appointment"""
        self.ensure_one()
        if self.state != 'done':
            raise ValidationError("Chỉ có thể tạo hóa đơn cho lịch hẹn đã hoàn thành!")
        
        existing_invoice = self.env['salon.invoice'].search([
            ('appointment_id', '=', self.id),
            ('state', '!=', 'cancel')
        ], limit=1)
        
        if existing_invoice:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Hóa đơn',
                'res_model': 'salon.invoice',
                'res_id': existing_invoice.id,
                'view_mode': 'form',
                'target': 'current',
            }
        
        invoice = self.env['salon.invoice'].create({
            'customer_id': self.customer_id.id,
            'appointment_id': self.id,
            'date_invoice': fields.Datetime.now(),
        })
        
        for service_line in self.service_ids:
            if not hasattr(service_line, 'service_id'):
                continue
            if not service_line.service_id: 
                continue
            service_record = service_line.service_id 
            if not hasattr(service_record, 'id'):
                continue
            quantity = getattr(service_line, 'quantity', 1) or 1  
            self.env['salon.invoice.line'].create({
                'invoice_id': invoice.id,
                'service_id': service_record.id,
                'quantity': quantity,
            })
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Hóa đơn',
            'res_model': 'salon.invoice',
            'res_id': invoice.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_cancel(self):
        """Hủy lịch hẹn - mở wizard để nhập lý do"""
        self.ensure_one()
        if self.state in ('done', 'cancel'):
            raise ValidationError("Không thể hủy lịch đã hoàn thành hoặc đã hủy.")
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Hủy lịch hẹn',
            'res_model': 'salon.appointment.cancel.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_appointment_id': self.id,
            },
        }

    def action_reschedule(self, new_date=None, new_stylist=None):
        for rec in self:
            if rec.state in ('done', 'cancel'):
                raise ValidationError("Không thể dời lịch đã hoàn thành hoặc đã huỷ.")
            if new_date:
                rec.date_appointment = new_date
            if new_stylist:
                rec.employee_id = new_stylist
            rec._check_conflict()  

    def action_create_customer(self):
        """Mở form tạo khách hàng mới, sau đó tự động điền vào appointment"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Tạo khách hàng mới',
            'res_model': 'salon.customer',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_membership_rank_id': self.env['salon.membership.rank'].get_default_rank().id if self.env['salon.membership.rank'].get_default_rank() else False,
                'form_view_initial_mode': 'edit',
                'return_model': 'salon.appointment',
                'return_id': self.id,
            },
        }

    @api.onchange('customer_id')
    def _onchange_customer_id(self):
        """Tự động cập nhật phone khi chọn customer"""
        if self.customer_id:
            self.phone = self.customer_id.phone

    @api.depends('service_ids', 'service_ids.service_id', 'service_ids.service_id.name', 'service_ids.quantity')
    def _compute_service_names(self):
        """Tính toán danh sách tên dịch vụ để hiển thị"""
        for rec in self:
            if rec.service_ids:
                names = []
                for line in rec.service_ids:
                    if line.service_id:
                        service_name = line.service_id.name or ''
                        if line.quantity and line.quantity > 1:
                            names.append(f"{service_name} (x{line.quantity})")
                        else:
                            names.append(service_name)
                rec.service_names = ", ".join(names) if names else ""
            else:
                rec.service_names = ""

    @api.depends('service_ids', 'service_ids.service_id', 'service_ids.service_id.name', 'service_ids.quantity')
    def _compute_service_list(self):
        """Tính toán danh sách dịch vụ phân cách bằng || để hiển thị trong kanban"""
        for rec in self:
            if rec.service_ids:
                services = []
                for line in rec.service_ids:
                    if hasattr(line, 'service_id') and line.service_id and hasattr(line.service_id, 'name'):
                        service_name = line.service_id.name
                        if line.quantity and line.quantity > 1:
                            display_name = f"{service_name} (x{line.quantity})"
                        else:
                            display_name = service_name
                        services.append(display_name)
                rec.service_list = "||".join(services) if services else ""
            else:
                rec.service_list = ""

    @api.onchange('date_appointment', 'duration')
    def _onchange_date_appointment(self):
        """Filter employee theo ca làm việc khi chọn ngày giờ"""
        if not self.date_appointment or not self.duration:
            return {'domain': {'employee_id': []}}
        
        start_time = self.date_appointment
        end_time = start_time + timedelta(hours=self.duration)
        appointment_date = start_time.date()
        
        shifts = self.env['salon.shift'].search([
            ('ngay_lam_viec', '=', appointment_date),
        ])
        
        valid_employee_ids = []
        for shift in shifts:
            if shift.ngay_gio_bat_dau and shift.ngay_gio_ket_thuc:
                if shift.ngay_gio_bat_dau <= start_time and shift.ngay_gio_ket_thuc >= end_time:
                    if shift.ma_nv.id not in valid_employee_ids:
                        valid_employee_ids.append(shift.ma_nv.id)
        
        if valid_employee_ids:
            return {
                'domain': {'employee_id': [('id', 'in', valid_employee_ids)]},
                'warning': {
                    'title': 'Lưu ý',
                    'message': f'Đã lọc {len(valid_employee_ids)} nhân viên có ca làm việc trong khung giờ này.'
                }
            }
        else:
            return {
                'domain': {'employee_id': []},
                'warning': {
                    'title': 'Cảnh báo',
                    'message': 'Không có nhân viên nào có ca làm việc trong khung giờ này! Vui lòng chọn lại thời gian hoặc tạo ca làm việc cho nhân viên.'
                }
            }
