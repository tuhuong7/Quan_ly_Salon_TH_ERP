from odoo import models, fields, api


class SalonAppointmentService(models.Model):
    _name = 'salon.appointment.service'
    _description = 'Dịch vụ trong lịch hẹn'
    _order = 'sequence, id'

    appointment_id = fields.Many2one('salon.appointment', string='Lịch hẹn', required=True, ondelete='cascade')
    service_id = fields.Many2one('salon.service', string='Dịch vụ', required=True)
    quantity = fields.Integer(string='Số lượng', default=1, required=True)
    sequence = fields.Integer(string='Thứ tự', default=10)

    def name_get(self):
        """Hiển thị tên dịch vụ kèm số lượng nếu > 1"""
        result = []
        for record in self:
            if record.service_id:
                name = record.service_id.name
                if record.quantity and record.quantity > 1:
                    name = f"{name} (x{record.quantity})"
                result.append((record.id, name))
            else:
                result.append((record.id, ""))
        return result

