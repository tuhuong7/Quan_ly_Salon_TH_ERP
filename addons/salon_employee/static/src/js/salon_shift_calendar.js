/** @odoo-module **/

import { CalendarRenderer } from '@web/views/calendar/calendar_renderer';
import { patch } from '@web/core/utils/patch';

// Thay đổi cú pháp patch từ 3 đối số sang 2 đối số (Đã sửa lỗi cú pháp trước đó)
patch(CalendarRenderer.prototype, {
    // Thuộc tính mới bắt buộc trong cú pháp patch 2 đối số
    name: 'salon_shift_calendar_hover', 
    
    // ĐÃ SỬA: Xóa this._super() để tránh lỗi TypeError
    setup() {
        // KHÔNG GỌI this._super()
        console.log('Custom CalendarRenderer patch loaded');
        // Hàm setup() hiện tại chỉ thực hiện việc log, không gây lỗi.
    },

    // Sự kiện khi rê chuột vào một sự kiện (event)
    onMouseEnterEvent(ev, record) {
        if (record && record.data) {
            const popup = document.createElement('div');
            popup.classList.add('o_calendar_popup');
            Object.assign(popup.style, {
                position: 'absolute',
                left: ev.clientX + 'px',
                top: ev.clientY + 'px',
                background: '#fff',
                padding: '6px 10px',
                borderRadius: '6px',
                boxShadow: '0 2px 6px rgba(0,0,0,0.2)',
                zIndex: 9999,
                fontSize: '13px',
                whiteSpace: 'nowrap',
            });

            popup.innerHTML = `
                <b>${record.data.ma_nv?.display_name || 'Chưa có NV'}</b><br/>
                ${record.data.gio_bat_dau}h - ${record.data.gio_ket_thuc}h<br/>
                ${record.data.ghi_chu || ''}
            `;

            document.body.appendChild(popup);

            // Xóa popup khi chuột rời đi
            ev.target.addEventListener('mouseleave', () => popup.remove(), { once: true });
        }
    },
});