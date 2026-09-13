# HỆ THỐNG HỖ TRỢ SOẠN THẢO HỢP ĐỒNG TỰ ĐỘNG
### Chuẩn Nghị định 30/2020/NĐ-CP & Giao diện Apple Design System

Hệ thống tự động hóa trích xuất thông tin Căn cước công dân (CCCD) gắn chip và xuất hợp đồng pháp lý chuẩn xác, phục vụ chuyên nghiệp cho các doanh nghiệp, luật sư, chuyên viên pháp lý và kinh doanh.

---

## 🌟 ĐẶC ĐIỂM NỔI BẬT

1. **Giao diện chuẩn Apple Design System (`apple.com/vn`):**
   - Thiết kế tối giản, hiện đại, phông chữ SF Pro / Inter.
   - Thẻ Squircle bo góc mềm mại, hiệu ứng kính mờ *Frosted Glass*.
   - Thanh **Apple Floating Dock** cố định 3 nút bấm tác vụ nhanh ở cạnh dưới màn hình.

2. **Khu vực thao tác chuẩn 3 Nút Bấm:**
   - **`[ 👁️ Xem trước ]`**: Xem trực tiếp file hợp đồng PDF A4 trên trình duyệt qua modal kính mờ.
   - **`[ 📄 Xuất PDF ]`**: Tải file PDF chuẩn A4, bảo toàn nguyên vẹn thể thức in ấn.
   - **`[ 📝 Xuất docx ]`**: Tải file Microsoft Word `.docx` để tiếp tục tinh chỉnh nội bộ.

3. **Văn bản chuẩn 100% Thể thức Nghị định 30/2020/NĐ-CP:**
   - Căn lề A4: **Trái 30mm**, **Phải 15mm**, **Trên 20mm**, **Dưới 20mm**.
   - Phông chữ **Times New Roman**, dãn dòng 1.15, thụt đầu dòng 1.27 cm.
   - Bảng 2 cột cân đối Quốc hiệu - Tiêu ngữ và Khung ký tên.
   - Đánh số trang từ trang 2 ở chính giữa lề trên.
   - Để khoảng trống ký tên thoáng sạch, không in sẵn họ tên để các bên tự ký và tự viết họ tên theo đúng quy chuẩn thực tế.

4. **Đa dạng phương thức nhập liệu Bên B & Đồng ký kết:**
   - **Quét mã QR CCCD gắn chip (< 0.1s):** Hỗ trợ kéo thả ảnh (JPG, PNG, WEBP) hoặc **file PDF scan**.
   - **Chụp ảnh trực tiếp từ Camera:** Hỗ trợ camera laptop/điện thoại khi gặp gỡ khách hàng trực tiếp.
   - **Nhập tay trực tiếp:** Tự do gõ thông tin không bắt buộc phải có ảnh.
   - **Tự động hóa thông tin Vợ/Chồng:** Hỗ trợ nạp 2 CCCD cùng lúc, tự phân loại và đồng bộ vào hợp đồng.

5. **Bộ chuyển đổi số tiền thành chữ tiếng Việt:**
   - Tự động phiên dịch chính xác các mệnh giá từ số sang chữ (ví dụ: `150.000.000` $\rightarrow$ *"Một trăm năm mươi triệu đồng chẵn"*).

6. **Kho 41 mẫu hợp đồng Thương mại & Dịch vụ chuẩn mực:**
   - Tích hợp sẵn 41 mẫu hợp đồng chuyên nghiệp (Dịch vụ, đại lý, mua bán, bảo vệ, gia công, môi giới...).

7. **Bảo mật dữ liệu tuyệt đối (Nghị định 13/2023/NĐ-CP):**
   - 100% vận hành cục bộ (Local / Offline) trên máy tính của bạn, không gửi dữ liệu ra máy chủ bên ngoài.

---

## 📁 CẤU TRÚC DỰ ÁN

```
├── Chay_Ung_Dung.command          # Phím tắt nhấp đúp chạy trên macOS
├── start.sh                       # Script khởi động tự động từ Terminal
├── requirements.txt               # Các thư viện phụ thuộc Python
├── test_system.py                 # Bộ kiểm thử tự động toàn diện
├── templates/
│   └── 1.1_Thuong_mai_va_Dich_vu/ # Kho 41 mẫu hợp đồng nguồn Word
├── app/
│   ├── main.py                    # Máy chủ FastAPI & APIs xuất bản
│   ├── cccd_parser.py             # Bộ bóc tách QR Code CCCD & PDF
│   ├── vn_num2words.py            # Chuyển đổi số tiền thành chữ tiếng Việt
│   ├── document_generator.py      # Bộ sinh PDF & DOCX chuẩn Nghị định 30
│   ├── sample_generator.py        # Bộ tạo dữ liệu CCCD mẫu
│   └── templates/
│       └── company_profile.json   # Hồ sơ Bên A lưu sẵn
└── static/
    ├── index.html                 # Giao diện Apple Design System
    ├── css/apple.css              # Apple styling & floating dock
    └── js/app.js                  # Logic bóc tách, camera & 3 nút bấm
```

---

## 🚀 HƯỚNG DẪN CÀI ĐẶT & SỬ DỤNG

### 1. Yêu cầu hệ thống
- Python 3.10 trở lên.
- Hệ điều hành: macOS, Linux, Windows.

### 2. Khởi chạy nhanh trên macOS
- Nhấp đúp chuột vào file **`Chay_Ung_Dung.command`**.
- Trình duyệt sẽ tự động mở tại địa chỉ: `http://localhost:8000`.

### 3. Khởi chạy bằng dòng lệnh
```bash
# Cài đặt môi trường ảo và dependencies (nếu chạy lần đầu)
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Khởi chạy hệ thống
./start.sh
```

---

## ⚖️ GIẤY PHÉP & BẢN QUYỀN
Phát triển bởi đội ngũ chuyên gia công nghệ & pháp lý. Tuân thủ đầy đủ quy định pháp luật Việt Nam về thương mại điện tử và bảo vệ dữ liệu cá nhân.
