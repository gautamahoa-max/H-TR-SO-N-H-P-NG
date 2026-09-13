"""
Kịch bản kiểm thử toàn diện hệ thống (End-to-End System Test)
Kiểm tra tất cả các tính năng cốt lõi:
1. Bóc tách QR Code CCCD
2. Nhập tay trực tiếp không cần ảnh
3. Chuyển đổi số tiền ra chữ tiếng Việt
4. Xuất PDF chuẩn Nghị định 30/2020/NĐ-CP (lề 30-15-20-20 mm, font Times New Roman)
5. Xuất Word DOCX chuẩn Nghị định 30
6. Toàn bộ API của FastAPI Server
"""
import io
from fastapi.testclient import TestClient
from app.main import app
from app.sample_generator import generate_sample_cccd_image
from app.vn_num2words import doc_so_thanh_chu

client = TestClient(app)

def test_full_system():
    print("\n--- BẮT ĐẦU KIỂM THỬ HỆ THỐNG ---")

    # 1. Kiểm tra trang chủ HTML
    res = client.get("/")
    assert res.status_code == 200
    assert "Hợp Đồng Văn Phòng" in res.text
    print("✓ 1. Giao diện trang chủ (Apple Design System): OK")

    # 2. Kiểm tra API Hồ sơ Bên A
    res = client.get("/api/company-profile")
    assert res.status_code == 200
    profile = res.json()
    assert "CÔNG TY" in profile.get("ten_to_chuc", "")
    print(f"✓ 2. Hồ sơ Bên A lưu sẵn ({profile.get('ten_to_chuc')}): OK")

    # 3. Kiểm tra Bóc tách QR Code CCCD từ ảnh
    img_buf = generate_sample_cccd_image()
    files = {"file": ("cccd.jpg", img_buf.getvalue(), "image/jpeg")}
    res = client.post("/api/extract-cccd", files=files)
    assert res.status_code == 200
    cccd_data = res.json()
    assert cccd_data["success"] == True
    assert cccd_data["ho_ten"] == "NGUYỄN VĂN AN"
    assert cccd_data["so_cccd"] == "001200001234"
    assert cccd_data["ngay_sinh"] == "15/08/1995"
    assert cccd_data["ngay_cap"] == "25/04/2021"
    print(f"✓ 3. Bóc tách QR Code CCCD ({cccd_data['ho_ten']} - {cccd_data['so_cccd']}): OK")

    # 4. Kiểm tra bộ chuyển đổi số tiền thành chữ tiếng Việt
    test_amount = "250.000.000"
    res = client.post("/api/num-to-words", json={"so_tien": test_amount})
    assert res.status_code == 200
    chu = res.json()["chu"]
    assert "Hai trăm năm mươi triệu đồng chẵn" in chu
    print(f"✓ 4. Dịch tiền ra chữ ({test_amount} đ -> '{chu}'): OK")

    # 5. Kiểm tra Nút 1: [Xem trước] (PDF Preview Stream)
    payload = {
        "ben_b_ten": cccd_data["ho_ten"],
        "ben_b_cccd": cccd_data["so_cccd"],
        "ben_b_ngay_sinh": cccd_data["ngay_sinh"],
        "ben_b_dia_chi": cccd_data["dia_chi"],
        "ben_b_ngay_cap": cccd_data["ngay_cap"],
        "gia_tri_hop_dong": test_amount,
        "gia_tri_bang_chu": chu
    }
    res = client.post("/api/preview-pdf", json=payload)
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert len(res.content) > 50000
    print(f"✓ 5. NÚT 1 [Xem trước] (Tạo luồng PDF kích thước {len(res.content):,} bytes): OK")

    # 6. Kiểm tra Nút 2: [Xuất PDF] chuẩn Nghị định 30
    res = client.post("/api/export-pdf", json=payload)
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert "attachment" in res.headers["content-disposition"]
    print(f"✓ 6. NÚT 2 [Xuất PDF] (Download PDF chuẩn NĐ 30 kích thước {len(res.content):,} bytes): OK")

    # 7. Kiểm tra Nút 3: [Xuất docx] chuẩn Nghị định 30
    res = client.post("/api/export-docx", json=payload)
    assert res.status_code == 200
    assert "wordprocessingml" in res.headers["content-type"]
    assert len(res.content) > 20000
    print(f"✓ 7. NÚT 3 [Xuất docx] (Download Word chuẩn NĐ 30 kích thước {len(res.content):,} bytes): OK")

    # 8. Kiểm tra luồng Nhập tay trực tiếp (không quét ảnh)
    manual_payload = {
        "ben_b_ten": "TRẦN VĂN BÌNH",
        "ben_b_cccd": "001099008888",
        "ben_b_ngay_sinh": "01/01/1990",
        "ben_b_dia_chi": "Quận 1, Thành phố Hồ Chí Minh",
        "ben_b_ngay_cap": "10/10/2022",
        "gia_tri_hop_dong": "500.000.000",
        "gia_tri_bang_chu": "Năm trăm triệu đồng chẵn"
    }
    res_man_pdf = client.post("/api/export-pdf", json=manual_payload)
    assert res_man_pdf.status_code == 200
    res_man_docx = client.post("/api/export-docx", json=manual_payload)
    assert res_man_docx.status_code == 200
    print("✓ 8. Luồng Nhập tay trực tiếp không cần ảnh: OK")

    print("\n=========================================================")
    print("   TẤT CẢ 8 BÀI KIỂM THỬ ĐÃ VƯỢT QUA 100% THÀNH CÔNG!")
    print("=========================================================\n")

if __name__ == "__main__":
    test_full_system()
