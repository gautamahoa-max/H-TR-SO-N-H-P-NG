"""
Module tạo ảnh mẫu CCCD gắn chip kèm mã QR chuẩn Bộ Công an để người dùng thử nghiệm nhanh.
"""
import io
import qrcode
from PIL import Image, ImageDraw, ImageFont

def generate_sample_cccd_image(
    so_cccd: str = "001200001234",
    ho_ten: str = "NGUYỄN VĂN AN",
    ngay_sinh: str = "15081995",
    gioi_tinh: str = "Nam",
    dia_chi: str = "Số 123 Phố Huế, Phường Hàng Bài, Quận Hoàn Kiếm, Hà Nội",
    ngay_cap: str = "25042021"
) -> io.BytesIO:
    """Tạo ảnh CCCD mẫu kích thước chuẩn thẻ ATM/CCCD với mã QR thực tế"""
    # 1. Tạo chuỗi QR chuẩn
    payload = f"{so_cccd}||{ho_ten}|{ngay_sinh}|{gioi_tinh}|{dia_chi}|{ngay_cap}"
    
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=4,
        border=2
    )
    qr.add_data(payload)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")

    # 2. Tạo phôi thẻ CCCD (tỷ lệ 85.6 x 53.98 mm, kích thước 800 x 504 px)
    width = 800
    height = 504
    card = Image.new("RGB", (width, height), color=(235, 245, 252))
    draw = ImageDraw.Draw(card)

    # Khung viền và dải màu thẻ
    draw.rectangle([8, 8, width - 8, height - 8], outline=(180, 205, 230), width=3)
    draw.rectangle([12, 12, width - 12, 70], fill=(215, 235, 250))

    # Quốc hiệu và Tiêu ngữ thẻ
    draw.text((250, 18), "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM", fill=(180, 0, 0))
    draw.text((310, 36), "Độc lập - Tự do - Hạnh phúc", fill=(20, 20, 20))
    draw.text((280, 80), "CĂN CƯỚC CÔNG DÂN", fill=(150, 20, 20))

    # Vẽ chip mô phỏng
    draw.rectangle([40, 160, 120, 230], fill=(220, 190, 100), outline=(170, 140, 60), width=2)
    draw.line([40, 195, 120, 195], fill=(170, 140, 60), width=1)
    draw.line([80, 160, 80, 230], fill=(170, 140, 60), width=1)

    # Vẽ khung ảnh chân dung
    draw.rectangle([35, 260, 165, 440], fill=(210, 225, 240), outline=(160, 180, 200), width=2)
    draw.text((55, 340), "[Ảnh 3x4]", fill=(120, 140, 160))

    # Thông tin công dân trên thẻ
    draw.text((200, 130), f"Số / No.: {so_cccd}", fill=(180, 0, 0))
    draw.text((200, 175), f"Họ và tên / Full name: {ho_ten}", fill=(20, 20, 20))
    draw.text((200, 215), f"Ngày sinh / Date of birth: {ngay_sinh[0:2]}/{ngay_sinh[2:4]}/{ngay_sinh[4:8]}", fill=(20, 20, 20))
    draw.text((200, 255), f"Giới tính / Sex: {gioi_tinh}    Quốc tịch / Nationality: Việt Nam", fill=(20, 20, 20))
    draw.text((200, 295), f"Nơi thường trú / Place of residence:", fill=(20, 20, 20))
    draw.text((200, 320), dia_chi[:45], fill=(20, 20, 20))
    if len(dia_chi) > 45:
        draw.text((200, 345), dia_chi[45:], fill=(20, 20, 20))
    draw.text((200, 400), f"Có giá trị đến / Date of expiry: 15/08/2035", fill=(60, 60, 60))

    # Dán mã QR vào góc trên bên phải
    qr_resized = qr_img.resize((150, 150))
    card.paste(qr_resized, (width - 175, 80))
    draw.text((width - 175, 235), "Mã QR CCCD", fill=(100, 100, 100))

    buffer = io.BytesIO()
    card.save(buffer, format="JPEG", quality=95)
    buffer.seek(0)
    return buffer
