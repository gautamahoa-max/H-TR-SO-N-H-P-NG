#!/usr/bin/env bash
# Script khởi động Hệ thống Tự động hóa Hợp đồng chuẩn Nghị định 30 & Apple Design

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "================================================================="
echo "   HỆ THỐNG TẠO HỢP ĐỒNG TỰ ĐỘNG - CHUẨN NGHỊ ĐỊNH 30/2020/NĐ-CP"
echo "   THIẾT KẾ: APPLE DESIGN SYSTEM (APPLE.COM/VN)"
echo "================================================================="

if [ ! -d ".venv" ]; then
    echo "Đang khởi tạo môi trường Python..."
    python3 -m venv .venv
    .venv/bin/pip install -r requirements.txt
fi

echo "Đang khởi chạy máy chủ cục bộ..."
echo "Ứng dụng sẽ tự động mở tại: http://localhost:8000"
echo "Nhấn Ctrl+C để dừng."

# Mở trình duyệt sau 1.5 giây
if command -v open >/dev/null 2>&1; then
    (sleep 1.5 && open "http://localhost:8000") &
elif command -v xdg-open >/dev/null 2>&1; then
    (sleep 1.5 && xdg-open "http://localhost:8000") &
fi

# Chạy server FastAPI uvicorn
.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
