# Hệ thống Quản lý Salon - Odoo 19.0

Hệ thống quản lý Salon được phát triển trên nền tảng Odoo 19.0, bao gồm các module quản lý khách hàng, nhân viên, dịch vụ, lịch hẹn, hóa đơn và thanh toán.

## 📋 Danh sách Module

- **salon_management**: Module quản lý Salon - Menu gốc
- **salon_tc_invoice_extend**: Module quản lý hóa đơn và thanh toán
- **salon_customer**: Module quản lý khách hàng
- **salon_employee**: Module quản lý nhân viên
- **salon_service**: Module quản lý dịch vụ
- **salon_appointment**: Module quản lý lịch hẹn
- **salon_membership_rank**: Module quản lý hạng thành viên
- **salon_promotion**: Module quản lý khuyến mãi
- **salon_service_history**: Module lịch sử dịch vụ

## 🚀 Hướng dẫn Cài đặt

### Yêu cầu hệ thống

- Python 3.10 hoặc cao hơn
- PostgreSQL 12 hoặc cao hơn
- Git

### Bước 1: Clone Odoo 19.0 chính thức

```bash
git clone https://github.com/odoo/odoo.git --branch 19.0 --depth 1 odoo-19.0
cd odoo-19.0
```

### Bước 2: Clone Salon Modules

```bash
# Clone repository salon modules vào thư mục addons
cd addons
git clone https://github.com/tuhuong7/Quan_ly_Salon_TH_ERP.git temp_salon
# Di chuyển các module salon vào thư mục addons
mv temp_salon/addons/salon_* .
# Xóa thư mục temp
rm -rf temp_salon
cd ..
```

**Hoặc trên Windows (PowerShell):**
```powershell
cd addons
git clone https://github.com/tuhuong7/Quan_ly_Salon_TH_ERP.git temp_salon
Move-Item temp_salon\addons\salon_* .
Remove-Item -Recurse -Force temp_salon
cd ..
```

### Bước 3: Cài đặt Dependencies

```bash
pip install -r requirements.txt
```

### Bước 4: Tạo Database

Tạo database PostgreSQL:
```sql
CREATE DATABASE salon_db;
CREATE USER salon_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE salon_db TO salon_user;
```

### Bước 5: Cấu hình Odoo

Tạo file `odoo.conf`:
```ini
[options]
addons_path = addons
db_host = localhost
db_port = 5432
db_user = salon_user
db_password = your_password
db_name = salon_db
http_port = 8069
```

### Bước 6: Khởi động Odoo

```bash
python odoo-bin -c odoo.conf
```

### Bước 7: Cài đặt Modules

1. Truy cập: `http://localhost:8069`
2. Tạo database mới hoặc chọn database đã tạo
3. Vào **Apps** → Tìm và cài đặt các module salon:
   - `salon_management` (cài đầu tiên)
   - `salon_tc_invoice_extend`
   - `salon_customer`
   - `salon_employee`
   - `salon_service`
   - `salon_appointment`
   - `salon_membership_rank`
   - `salon_promotion`
   - `salon_service_history`

## 📦 Thứ tự Cài đặt Module

1. **salon_management** (Module gốc, cài đầu tiên)
2. **salon_tc_invoice_extend**
3. **salon_customer**
4. **salon_employee**
5. **salon_service**
6. **salon_membership_rank**
7. **salon_appointment** (phụ thuộc vào customer, employee, service)
8. **salon_promotion**
9. **salon_service_history** (phụ thuộc vào customer, employee)

## 🔧 Cấu hình

### Database

File `odoo.conf` đã được cấu hình với đường dẫn tương đối:
- `data_dir = ./filestore`
- `screenshots = ./screenshots`

### Dependencies

Các module salon phụ thuộc vào:
- `base` (Odoo core)
- `mail` (Odoo core)

## 📝 Lưu ý

- Đảm bảo PostgreSQL đang chạy trước khi khởi động Odoo
- Các module salon phải được cài đặt theo đúng thứ tự
- Sau khi cài đặt, cần upgrade database để áp dụng các thay đổi mới nhất

## 🐛 Xử lý Lỗi

### Lỗi "Module not found"
- Kiểm tra `addons_path` trong `odoo.conf`
- Đảm bảo các module salon nằm trong thư mục `addons/`

### Lỗi "Dependencies not met"
- Cài đặt các module phụ thuộc trước
- Kiểm tra `depends` trong `__manifest__.py` của từng module

## 📞 Liên hệ

- Repository: https://github.com/tuhuong7/Quan_ly_Salon_TH_ERP
- Tác giả: Tú Hương

## 📄 License

LGPL-3.0 (theo license của Odoo)

