from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AppointmentCancelWizard(models.TransientModel):
    _name = 'salon.appointment.cancel.wizard'
    _description = 'Wizard hủy lịch hẹn'

    appointment_id = fields.Many2one('salon.appointment', string='Lịch hẹn', required=True)
    cancel_reason = fields.Text(string='Lý do hủy', required=True, help='Vui lòng nhập lý do hủy lịch hẹn')

    def action_confirm_cancel(self):
        """Xác nhận hủy lịch hẹn"""
        self.ensure_one()
        if not self.cancel_reason:
            raise ValidationError("Vui lòng nhập lý do hủy!")
        
        self.appointment_id.write({
            'state': 'cancel',
            'cancel_reason': self.cancel_reason,
        })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': 'Đã hủy lịch hẹn thành công.',
                'type': 'success',
                'sticky': False,
            }
        }

