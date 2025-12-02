# Hệ thống Quản lý Salon - Odoo 19.0

Hệ thống quản lý Salon được phát triển trên nền tảng Odoo 19.0, bao gồm các module quản lý khách hàng, nhân viên, dịch vụ, lịch hẹn, hóa đơn và thanh toán.

## 👤 Tác giả

*Lê Nguyễn Ngọc Tú Hương,...*


## 📁 Cấu trúc Thư mục Dự án

```
addons/
├── salon_management/              # Module gốc - Menu chính
│   ├── __init__.py
│   ├── __manifest__.py
│   ├── models/
│   │   └── __init__.py
│   └── views/
│       └── menu_root.xml
│
├── salon_tc_invoice_extend/       # Module hóa đơn và thanh toán
│   ├── __init__.py
│   ├── __manifest__.py
│   ├── data/
│   │   └── invoice_sequence.xml
│   ├── models/
│   │   ├── __init__.py
│   │   ├── account_move_inherit.py
│   │   └── sale_invoice.py
│   ├── reports/
│   │   ├── __init__.py
│   │   └── invoice_report.xml
│   ├── security/
│   │   └── ir.model.access.csv
│   ├── views/
│   │   ├── payment_confirm_wizard_view.xml
│   │   └── sale_invoice_views.xml
│   └── wizards/
│       ├── __init__.py
│       └── payment_confirm_wizard.py
│
├── salon_customer/                # Module quản lý khách hàng
│   ├── __init__.py
│   ├── __manifest__.py
│   ├── data/
│   │   └── customer_sequence.xml
│   ├── models/
│   │   ├── __init__.py
│   │   └── customer.py
│   ├── security/
│   │   ├── customer_rules.xml
│   │   └── ir.model.access.csv
│   ├── static/
│   │   └── src/
│   │       └── scss/
│   │           └── customer_theme.scss
│   └── views/
│       ├── customer_form_view.xml
│       ├── customer_kanban_view.xml
│       ├── customer_menu.xml
│       ├── customer_search_view.xml
│       └── customer_tree_view.xml
│
├── salon_employee/                # Module quản lý nhân viên
│   ├── __init__.py
│   ├── __manifest__.py
│   ├── data/
│   │   ├── employee_demo.xml
│   │   └── employee_sequence.xml
│   ├── models/
│   │   ├── __init__.py
│   │   ├── employee.py
│   │   └── shift.py
│   ├── security/
│   │   └── ir.model.access.csv
│   ├── static/
│   │   └── src/
│   │       └── js/
│   │           └── salon_shift_calendar.js
│   └── views/
│       ├── assets.xml
│       ├── employee_kanban_view.xml
│       ├── employee_views.xml
│       └── shift_views.xml
│
├── salon_service/                 # Module quản lý dịch vụ
│   ├── __init__.py
│   ├── __manifest__.py
│   ├── data/
│   │   └── service_sequence.xml
│   ├── models/
│   │   ├── __init__.py
│   │   └── salon_service.py
│   ├── security/
│   │   └── ir.model.access.csv
│   └── views/
│       └── salon_service_view.xml
│
├── salon_appointment/             # Module quản lý lịch hẹn
│   ├── __init__.py
│   ├── __manifest__.py
│   ├── data/
│   │   └── appointment_sequence.xml
│   ├── models/
│   │   ├── __init__.py
│   │   ├── appointment_cancel_wizard.py
│   │   ├── appointment_service.py
│   │   └── salon_appointment.py
│   ├── security/
│   │   └── ir.model.access.csv
│   └── views/
│       ├── appointment_cancel_wizard_view.xml
│       └── salon_appointment_view.xml
│
├── salon_membership_rank/         # Module quản lý hạng thành viên
│   ├── __init__.py
│   ├── __manifest__.py
│   ├── data/
│   │   └── membership_rank_sequence.xml
│   ├── models/
│   │   ├── __init__.py
│   │   └── membership_rank.py
│   ├── security/
│   │   └── ir.model.access.csv
│   └── views/
│       └── membership_rank_views.xml
│
├── salon_promotion/               # Module quản lý khuyến mãi
│   ├── __init__.py
│   ├── __manifest__.py
│   ├── data/
│   │   └── promotion_sequence.xml
│   ├── models/
│   │   ├── __init__.py
│   │   └── promotion.py
│   ├── security/
│   │   └── ir.model.access.csv
│   └── views/
│       ├── promotion_kanban_view.xml
│       └── promotion_views.xml
│
└── salon_service_history/         # Module lịch sử dịch vụ
    ├── __init__.py
    ├── __manifest__.py
    ├── models/
    │   ├── __init__.py
    │   └── service_history.py
    ├── security/
    │   └── ir.model.access.csv
    └── views/
        ├── service_history_menu.xml
        └── service_history_views.xml
```

## 🚀 Cài đặt & Chạy

### Yêu cầu Hệ thống

- **Python**: 3.10 hoặc cao hơn
- **PostgreSQL**: 12 hoặc cao hơn
- **Git**: Để clone repository
- **pip**: Để cài đặt dependencies

### Bước 1: Clone Odoo 19.0

Clone Odoo 19.0 chính thức từ GitHub:

```bash
git clone https://github.com/odoo/odoo.git --branch 19.0 --depth 1 odoo-19.0
cd odoo-19.0
```

### Bước 2: Clone Salon Modules

Clone repository salon modules và di chuyển vào thư mục `addons/`:

**Trên Linux/Mac:**
```bash
cd addons
git clone https://github.com/tuhuong7/Quan_ly_Salon_TH_ERP.git temp_salon
mv temp_salon/addons/salon_* .
rm -rf temp_salon
cd ..
```

**Trên Windows (PowerShell):**
```powershell
cd addons
git clone https://github.com/tuhuong7/Quan_ly_Salon_TH_ERP.git temp_salon
Move-Item temp_salon\addons\salon_* .
Remove-Item -Recurse -Force temp_salon
cd ..
```

### Bước 3: Cài đặt Dependencies

Cài đặt các thư viện Python cần thiết từ Odoo chính thức:

```bash
pip install -r requirements.txt
```

**Lưu ý**: File `requirements.txt` nằm trong thư mục Odoo chính thức (đã clone ở Bước 1), không có trong repository salon modules.

### Bước 4: Cấu hình Odoo

Tạo file `odoo.conf` trong thư mục gốc của Odoo (xem hướng dẫn trên YouTube)

### Bước 5: Khởi động Odoo Server

Chạy lệnh sau để khởi động Odoo:

```bash
python odoo-bin -c odoo.conf
```

**Lưu ý**: Giữ terminal/command prompt này mở để Odoo tiếp tục chạy.

### Bước 6: Tạo Database PostgreSQL

Sau khi Odoo đã khởi động, tạo database qua giao diện web:

1. Mở trình duyệt và truy cập: `http://localhost:8069`
2. Odoo sẽ hiển thị màn hình tạo database
3. Điền thông tin:
   - **Database Name**: `tạo tên database của bạn`
   - **Email**: Email của bạn
   - **Password**: Mật khẩu admin (dùng để đăng nhập Odoo)
   - **Language**: Tiếng Việt (hoặc ngôn ngữ bạn muốn)
   - **Country**: Việt Nam
4. Click **Create database**
5. Odoo sẽ tự động:
   - Tạo database PostgreSQL
   - Cài đặt module `base`
   - Thiết lập cấu hình cơ bản
   - Chuyển đến trang đăng nhập

### Bước 7: Cài đặt Modules Salon

Sau khi đã tạo database và đăng nhập vào Odoo:

1. Vào **Apps** (Ứng dụng)
2. Bỏ chọn **Apps** filter (nếu có) để hiển thị tất cả modules
3. Tìm và cài đặt các module salon theo thứ tự:
   - `salon_management` (cài đầu tiên - module gốc)
   - `salon_membership_rank`
   - `salon_service_history`
   - `salon_promotion`
   - `salon_service`
   - `salon_customer`
   - `salon_employee`
   - `salon_appointment`
   - `salon_tc_invoice_extend`

### Bước 8: Upgrade Modules (Nếu cần)

Nếu có thay đổi code, upgrade modules:

```bash
python odoo-bin -c odoo.conf -d db-t7-salon -u salon_management,salon_membership_rank,salon_service_history,salon_promotion,salon_service,salon_customer,salon_employee,salon_appointment,salon_tc_invoice_extend --stop-after-init
```

## 📦 Thứ tự Cài đặt Module

Các module phải được cài đặt theo thứ tự sau để đảm bảo dependencies được đáp ứng:

1. **salon_management** - Module gốc, cài đầu tiên
2. **salon_membership_rank** - Module hạng thành viên
3. **salon_service_history** - Module lịch sử (phụ thuộc: customer, employee)
4. **salon_promotion** - Module khuyến mãi
5. **salon_service** - Module dịch vụ
6. **salon_customer** - Module khách hàng (phụ thuộc: membership_rank)
7. **salon_employee** - Module nhân viên
8. **salon_appointment** - Module lịch hẹn (phụ thuộc: customer, employee, service)
9. **salon_tc_invoice_extend** - Module hóa đơn (phụ thuộc: customer, employee, service)

## 🔧 Cấu hình

### Database

File `odoo.conf` sử dụng đường dẫn tương đối:
- `data_dir = ./filestore` - Thư mục lưu trữ file
- `screenshots = ./screenshots` - Thư mục lưu screenshots

### Dependencies

Các module salon phụ thuộc vào:
- `base` - Module cơ bản của Odoo (bắt buộc)
- `mail` - Module mail của Odoo (bắt buộc)

## 📝 Lưu ý

- ✅ Đảm bảo PostgreSQL đang chạy trước khi khởi động Odoo
- ✅ Các module salon phải được cài đặt theo đúng thứ tự
- ✅ Sau khi cài đặt, cần upgrade database để áp dụng các thay đổi mới nhất
- ✅ Kiểm tra `addons_path` trong `odoo.conf` đúng với thư mục chứa modules

## 🐛 Xử lý Lỗi

### Lỗi "Module not found"
- Kiểm tra `addons_path` trong `odoo.conf`
- Đảm bảo các module salon nằm trong thư mục `addons/`
- Kiểm tra tên module trong `__manifest__.py`

### Lỗi "Dependencies not met"
- Cài đặt các module phụ thuộc trước
- Kiểm tra `depends` trong `__manifest__.py` của từng module
- Đảm bảo các module Odoo core (`base`, `mail`) đã được cài đặt

### Lỗi kết nối Database
- Kiểm tra PostgreSQL đang chạy
- Kiểm tra thông tin database trong `odoo.conf`
- Kiểm tra quyền truy cập của user database


## 📄 License

LGPL-3.0 (theo license của Odoo)
