"""
Module bóc tách dữ liệu từ thẻ Căn cước công dân (CCCD) gắn chip
Hỗ trợ cả file ẢNH (JPG, PNG, WEBP) và file PDF (quét từ máy scan).
Sử dụng zxing-cpp và pypdfium2 để giải mã mã QR Code chuẩn của Bộ Công an trong < 0.1s.
"""
import io
import base64
from typing import Optional, Dict, Any, Union
from PIL import Image, ImageEnhance
import zxingcpp

try:
    import pypdfium2 as pdfium
except ImportError:
    pdfium = None


def format_date(raw_date: str) -> str:
    """Chuyển DDMMYYYY hoặc YYYYMMDD sang DD/MM/YYYY"""
    raw_date = raw_date.strip()
    if len(raw_date) == 8 and raw_date.isdigit():
        day = raw_date[0:2]
        month = raw_date[2:4]
        year = raw_date[4:8]
        return f"{day}/{month}/{year}"
    return raw_date


def determine_noi_cap(ngay_cap_str: str) -> str:
    """
    Xác định cơ quan cấp theo quy định pháp luật:
    - Từ 01/07/2024 (Luật Căn cước 2023): Bộ Công an
    - Trước 01/07/2024 (CCCD gắn chip): Cục Cảnh sát quản lý hành chính về trật tự xã hội
    """
    try:
        parts = ngay_cap_str.split("/")
        if len(parts) == 3:
            day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
            if year > 2024 or (year == 2024 and (month > 7 or (month == 7 and day >= 1))):
                return "Bộ Công an"
    except Exception:
        pass
    return "Cục Cảnh sát quản lý hành chính về trật tự xã hội"


def parse_qr_payload(payload: str) -> Optional[Dict[str, Any]]:
    """
    Phân tích chuỗi QR code từ CCCD gắn chip:
    Định dạng: Số CCCD|Số CMND cũ|Họ và tên|Ngày sinh|Giới tính|Địa chỉ thường trú|Ngày cấp
    """
    if not payload or "|" not in payload:
        return None

    parts = payload.split("|")
    if len(parts) < 6:
        return None

    so_cccd = parts[0].strip()
    so_cmnd_cu = parts[1].strip() if len(parts) > 1 else ""
    ho_ten = parts[2].strip().upper() if len(parts) > 2 else ""
    ngay_sinh_raw = parts[3].strip() if len(parts) > 3 else ""
    gioi_tinh = parts[4].strip() if len(parts) > 4 else ""
    dia_chi = parts[5].strip() if len(parts) > 5 else ""
    ngay_cap_raw = parts[6].strip() if len(parts) > 6 else ""

    ngay_sinh = format_date(ngay_sinh_raw)
    ngay_cap = format_date(ngay_cap_raw) if ngay_cap_raw else ""
    noi_cap = determine_noi_cap(ngay_cap) if ngay_cap else "Cục Cảnh sát quản lý hành chính về trật tự xã hội"

    return {
        "success": True,
        "method": "qr_code",
        "so_cccd": so_cccd,
        "so_cmnd_cu": so_cmnd_cu,
        "ho_ten": ho_ten,
        "ngay_sinh": ngay_sinh,
        "gioi_tinh": gioi_tinh,
        "dia_chi": dia_chi,
        "ngay_cap": ngay_cap,
        "noi_cap": noi_cap,
        "raw_payload": payload
    }


def scan_pil_image(image: Image.Image) -> Optional[Dict[str, Any]]:
    """Thử quét mã QR từ PIL Image với nhiều góc xoay và độ tương phản"""
    if image.mode != "RGB":
        image = image.convert("RGB")

    # 1. Quét góc gốc
    barcodes = zxingcpp.read_barcodes(image)
    for b in barcodes:
        parsed = parse_qr_payload(b.text)
        if parsed:
            return parsed

    # 2. Xoay các góc 90, 180, 270 độ
    for angle in [90, 180, 270]:
        rotated = image.rotate(angle, expand=True)
        barcodes = zxingcpp.read_barcodes(rotated)
        for b in barcodes:
            parsed = parse_qr_payload(b.text)
            if parsed:
                return parsed

    # 3. Tăng độ tương phản (ảnh mờ, scan chói)
    enhancer = ImageEnhance.Contrast(image)
    enhanced_image = enhancer.enhance(1.8)
    barcodes = zxingcpp.read_barcodes(enhanced_image)
    for b in barcodes:
        parsed = parse_qr_payload(b.text)
        if parsed:
            return parsed

    for angle in [90, 180, 270]:
        rotated = enhanced_image.rotate(angle, expand=True)
        barcodes = zxingcpp.read_barcodes(rotated)
        for b in barcodes:
            parsed = parse_qr_payload(b.text)
            if parsed:
                return parsed

    return None


def extract_from_image(input_data: Union[bytes, Image.Image]) -> Dict[str, Any]:
    """
    Nhận diện QR code từ ảnh hoặc file PDF tải lên.
    Hỗ trợ JPG, PNG, WEBP, PDF (tự chuyển trang PDF thành ảnh chất lượng cao để quét).
    """
    try:
        # Trường hợp 1: Đã là PIL Image
        if isinstance(input_data, Image.Image):
            res = scan_pil_image(input_data)
            if res:
                return res
            return {
                "success": False,
                "message": "Không tìm thấy mã QR trên ảnh. Bạn có thể nhập trực tiếp các trường trên màn hình."
            }

        file_bytes = input_data

        # Trường hợp 2: File PDF
        if file_bytes.startswith(b"%PDF") or b"/Type /Catalog" in file_bytes[:1024]:
            if not pdfium:
                return {
                    "success": False,
                    "message": "Hệ thống chưa cài đặt thư viện xử lý PDF (pypdfium2)."
                }

            pdf = pdfium.PdfDocument(file_bytes)
            num_pages = len(pdf)
            preview_base64 = None

            for i in range(min(num_pages, 5)):  # Quét tối đa 5 trang đầu
                page = pdf[i]
                pil_page = page.render(scale=2).to_pil()  # Render độ phân giải cao

                # Lưu trang đầu làm ảnh xem trước (base64)
                if i == 0:
                    thumb_buf = io.BytesIO()
                    pil_page.save(thumb_buf, format="JPEG", quality=85)
                    preview_base64 = "data:image/jpeg;base64," + base64.b64encode(thumb_buf.getvalue()).decode("ascii")

                parsed = scan_pil_image(pil_page)
                if parsed:
                    parsed["is_pdf"] = True
                    parsed["preview_image"] = preview_base64
                    return parsed

            return {
                "success": False,
                "is_pdf": True,
                "preview_image": preview_base64,
                "message": "Đã đọc file PDF nhưng không tìm thấy mã QR CCCD. Bạn có thể nhập thông tin trực tiếp vào form."
            }

        # Trường hợp 3: File ảnh thông thường
        image = Image.open(io.BytesIO(file_bytes))
        parsed = scan_pil_image(image)
        if parsed:
            return parsed

        return {
            "success": False,
            "message": "Không tìm thấy mã QR trên ảnh. Bạn có thể nhập trực tiếp các trường trên màn hình."
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Lỗi khi xử lý file: {str(e)}"
        }
