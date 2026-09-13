"""
FastAPI Server phục vụ Hệ thống Tự động hóa Trích xuất CCCD & Xuất Hợp đồng chuẩn Nghị định 30
Thiết kế theo chuẩn Apple Design System, phục vụ trực tiếp 3 nút bấm:
[Xem trước] - [Xuất PDF] - [Xuất docx]
"""
import os
import json
import urllib.parse
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, File, UploadFile, Body, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse, Response, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.cccd_parser import extract_from_image
from app.document_generator import generate_contract_pdf, generate_contract_docx, prepare_contract_data
from app.vn_num2words import doc_so_thanh_chu
from app.sample_generator import generate_sample_cccd_image

app = FastAPI(title="Apple-Styled Contract Automation System", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
PROFILE_PATH = os.path.join(BASE_DIR, "app", "templates", "company_profile.json")

# Mount thư mục static
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def get_company_profile() -> Dict[str, Any]:
    if os.path.exists(PROFILE_PATH):
        try:
            with open(PROFILE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


@app.get("/", response_class=HTMLResponse)
async def serve_home():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>Đang khởi động giao diện...</h1>")


@app.get("/api/company-profile")
async def read_profile():
    return get_company_profile()


@app.get("/api/templates")
async def list_templates():
    """Liệt kê danh sách các mẫu hợp đồng nguồn trong folder templates/1.1_Thuong_mai_va_Dich_vu"""
    tpl_dir = os.path.join(BASE_DIR, "templates", "1.1_Thuong_mai_va_Dich_vu")
    if not os.path.exists(tpl_dir):
        return []
    
    files = sorted(os.listdir(tpl_dir))
    results = []
    for f in files:
        if f.endswith(".docx") or f.endswith(".doc"):
            clean_name = f
            for ext in [".docx", ".doc"]:
                if clean_name.endswith(ext):
                    clean_name = clean_name[:-len(ext)]
            results.append({
                "filename": f,
                "title": clean_name
            })
    return results


@app.post("/api/company-profile")
async def save_profile(profile: Dict[str, Any] = Body(...)):
    try:
        os.makedirs(os.path.dirname(PROFILE_PATH), exist_ok=True)
        with open(PROFILE_PATH, "w", encoding="utf-8") as f:
            json.dump(profile, f, ensure_ascii=False, indent=2)
        return {"success": True, "message": "Đã lưu hồ sơ Bên A thành công."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/extract-cccd")
async def api_extract_cccd(file: UploadFile = File(...)):
    """Trích xuất dữ liệu từ ảnh CCCD tải lên (mã QR + thông tin)"""
    try:
        content = await file.read()
        res = extract_from_image(content)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi phân tích ảnh: {str(e)}")


@app.get("/api/sample-cccd-image")
async def api_sample_image():
    """Trả về ảnh CCCD mẫu có mã QR thật để kiểm thử"""
    buf = generate_sample_cccd_image()
    return Response(content=buf.getvalue(), media_type="image/jpeg")


@app.get("/api/sample-cccd-data")
async def api_sample_data():
    """Trả về dữ liệu mẫu để thử nghiệm 1-click"""
    return {
        "success": True,
        "method": "sample",
        "so_cccd": "001200001234",
        "so_cmnd_cu": "",
        "ho_ten": "NGUYỄN VĂN AN",
        "ngay_sinh": "15/08/1995",
        "gioi_tinh": "Nam",
        "dia_chi": "Số 123 Phố Huế, Phường Hàng Bài, Quận Hoàn Kiếm, Hà Nội",
        "ngay_cap": "25/04/2021",
        "noi_cap": "Cục Cảnh sát quản lý hành chính về trật tự xã hội"
    }


@app.post("/api/num-to-words")
async def api_num_to_words(payload: Dict[str, Any] = Body(...)):
    so_tien = payload.get("so_tien", "")
    chu = doc_so_thanh_chu(so_tien)
    return {"so_tien": so_tien, "chu": chu}


@app.post("/api/preview-pdf")
async def preview_pdf(payload: Dict[str, Any] = Body(...)):
    """NÚT 1: [Xem trước] - Trả về luồng PDF hiển thị trực tiếp trên trình duyệt"""
    try:
        pdf_buf = generate_contract_pdf(payload)
        return Response(
            content=pdf_buf.getvalue(),
            media_type="application/pdf",
            headers={"Content-Disposition": "inline; filename=preview.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi tạo bản xem trước PDF: {str(e)}")


@app.post("/api/export-pdf")
async def export_pdf(payload: Dict[str, Any] = Body(...)):
    """NÚT 2: [Xuất PDF] - Tải về file PDF chuẩn Nghị định 30/2020/NĐ-CP"""
    try:
        pdf_buf = generate_contract_pdf(payload)
        ten_kh = payload.get("ben_b_ten", "KHACH_HANG").strip().replace(" ", "_")
        now_str = datetime.now().strftime("%Y%m%d_%H%M")
        raw_filename = f"HD_{ten_kh}_{now_str}.pdf"
        ascii_filename = f"HD_{now_str}.pdf"
        encoded_filename = urllib.parse.quote(raw_filename)
        
        return Response(
            content=pdf_buf.getvalue(),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=\"{ascii_filename}\"; filename*=UTF-8''{encoded_filename}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xuất file PDF: {str(e)}")


@app.post("/api/export-docx")
async def export_docx(payload: Dict[str, Any] = Body(...)):
    """NÚT 3: [Xuất docx] - Tải về file Word .docx chuẩn Nghị định 30/2020/NĐ-CP"""
    try:
        docx_buf = generate_contract_docx(payload)
        ten_kh = payload.get("ben_b_ten", "KHACH_HANG").strip().replace(" ", "_")
        now_str = datetime.now().strftime("%Y%m%d_%H%M")
        raw_filename = f"HD_{ten_kh}_{now_str}.docx"
        ascii_filename = f"HD_{now_str}.docx"
        encoded_filename = urllib.parse.quote(raw_filename)
        
        return Response(
            content=docx_buf.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f"attachment; filename=\"{ascii_filename}\"; filename*=UTF-8''{encoded_filename}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xuất file Word: {str(e)}")
