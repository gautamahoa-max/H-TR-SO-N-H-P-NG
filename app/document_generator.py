"""
Module kết xuất tài liệu Hợp đồng chuẩn Nghị định 30/2020/NĐ-CP
- Định dạng PDF: Sử dụng ReportLab với phông chữ Times New Roman nhúng, đo đạc chính xác lề 30-15-20-20 mm, đánh số trang từ trang 2 ở chính giữa lề trên.
- Định dạng Word: Sử dụng python-docx với chuẩn lề, font, dãn dòng 1.15, thụt đầu dòng 1.27 cm.
"""
import os
import io
from datetime import datetime
from typing import Dict, Any, Optional

# ReportLab imports
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT

# python-docx imports
import docx
from docx.shared import Inches, Pt, RGBColor, Mm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

from app.vn_num2words import doc_so_thanh_chu

# Đăng ký phông chữ Times New Roman (hỗ trợ macOS, Linux, Docker, GitHub Codespaces)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_FONTS_DIR = os.path.join(BASE_DIR, "app", "fonts")
MACOS_FONT_DIR = "/System/Library/Fonts/Supplemental"

FONT_DIR = PROJECT_FONTS_DIR if os.path.exists(os.path.join(PROJECT_FONTS_DIR, "Times New Roman.ttf")) else MACOS_FONT_DIR

TIMES_REGULAR = os.path.join(FONT_DIR, "Times New Roman.ttf")
TIMES_BOLD = os.path.join(FONT_DIR, "Times New Roman Bold.ttf")
TIMES_ITALIC = os.path.join(FONT_DIR, "Times New Roman Italic.ttf")
TIMES_BOLD_ITALIC = os.path.join(FONT_DIR, "Times New Roman Bold Italic.ttf")

try:
    pdfmetrics.registerFont(TTFont("TimesNewRoman", TIMES_REGULAR))
    pdfmetrics.registerFont(TTFont("TimesNewRoman-Bold", TIMES_BOLD))
    pdfmetrics.registerFont(TTFont("TimesNewRoman-Italic", TIMES_ITALIC))
    pdfmetrics.registerFont(TTFont("TimesNewRoman-BoldItalic", TIMES_BOLD_ITALIC))
except Exception as e:
    print(f"Cảnh báo đăng ký font: {e}")


class NumberedCanvasND30(canvas.Canvas):
    """
    Canvas tùy biến để đánh số trang theo chuẩn Nghị định 30/2020/NĐ-CP:
    - Đánh số từ trang 2
    - Đặt canh giữa lề trên (Header Center)
    - Cỡ chữ 13, đứng
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        # Không đánh số trang ở trang 1
        if self._pageNumber > 1:
            self.saveState()
            self.setFont("TimesNewRoman", 13)
            # Vị trí: Giữa chiều ngang khổ A4 (210mm / 2), cách mép trên 10mm (trong lề trên 20mm)
            x = 210 * mm / 2
            y = 297 * mm - 12 * mm
            self.drawCentredString(x, y, str(self._pageNumber))
            self.restoreState()


def prepare_contract_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Làm sạch và chuẩn hóa toàn bộ dữ liệu hợp đồng trước khi sinh file"""
    now = datetime.now()
    ngay_ky = data.get("ngay_ky", f"ngày {now.day:02d} tháng {now.month:02d} năm {now.year}")
    
    so_tien_raw = data.get("gia_tri_hop_dong", "")
    so_tien_chu = data.get("gia_tri_bang_chu", "")
    if not so_tien_chu and so_tien_raw:
        so_tien_chu = doc_so_thanh_chu(so_tien_raw)

    return {
        "so_hop_dong": data.get("so_hop_dong", f"{now.strftime('%m%d')}/2026/HĐDV"),
        "ngay_ky": ngay_ky,
        "dia_diem_ky": data.get("dia_diem_ky", "Hà Nội"),
        "ten_hop_dong": data.get("ten_hop_dong", "HỢP ĐỒNG DỊCH VỤ TƯ VẤN VÀ CUNG CẤP GIẢI PHÁP"),
        # Bên A
        "ben_a_ten": data.get("ben_a_ten", "CÔNG TY CỔ PHẦN CÔNG NGHỆ VÀ THƯƠNG MẠI VIỆT NAM"),
        "ben_a_mst": data.get("ben_a_mst", "0109888999"),
        "ben_a_dia_chi": data.get("ben_a_dia_chi", "Số 68 Phố Liễu Giai, Phường Cống Vị, Quận Ba Đình, Hà Nội"),
        "ben_a_dai_dien": data.get("ben_a_dai_dien", "VÕ VĂN HÒA"),
        "ben_a_chuc_vu": data.get("ben_a_chuc_vu", "Tổng Giám đốc"),
        "ben_a_cccd": data.get("ben_a_cccd", "001085006789"),
        "ben_a_ngay_cap": data.get("ben_a_ngay_cap", "15/05/2021"),
        "ben_a_noi_cap": data.get("ben_a_noi_cap", "Cục Cảnh sát quản lý hành chính về trật tự xã hội"),
        "ben_a_stk": data.get("ben_a_stk", "19036888999999 tại Techcombank - CN Ba Đình"),
        # Bên B
        "ben_b_ten": data.get("ben_b_ten", "").strip().upper(),
        "ben_b_cccd": data.get("ben_b_cccd", "").strip(),
        "ben_b_ngay_sinh": data.get("ben_b_ngay_sinh", "").strip(),
        "ben_b_gioi_tinh": data.get("ben_b_gioi_tinh", "Nam"),
        "ben_b_dia_chi": data.get("ben_b_dia_chi", "").strip(),
        "ben_b_ngay_cap": data.get("ben_b_ngay_cap", "").strip(),
        "ben_b_noi_cap": data.get("ben_b_noi_cap", "Cục Cảnh sát quản lý hành chính về trật tự xã hội"),
        "ben_b_dien_thoai": data.get("ben_b_dien_thoai", "").strip(),
        # Người đồng ký (nếu có)
        "has_co_signer": data.get("has_co_signer", False),
        "co_signer_ten": data.get("co_signer_ten", "").strip().upper(),
        "co_signer_cccd": data.get("co_signer_cccd", "").strip(),
        "co_signer_ngay_sinh": data.get("co_signer_ngay_sinh", "").strip(),
        "co_signer_dia_chi": data.get("co_signer_dia_chi", "").strip(),
        "co_signer_quan_he": data.get("co_signer_quan_he", "Vợ/Chồng"),
        # Chi tiết hợp đồng
        "noi_dung_cong_viec": data.get("noi_dung_cong_viec", "Cung cấp giải pháp phần mềm, chuyển giao công nghệ và hỗ trợ kỹ thuật vận hành theo yêu cầu của Bên B."),
        "gia_tri_hop_dong": so_tien_raw,
        "gia_tri_bang_chu": so_tien_chu,
        "thoi_han": data.get("thoi_han", "12 tháng kể từ ngày ký"),
        "phuong_thuc_thanh_toan": data.get("phuong_thuc_thanh_toan", "Chuyển khoản qua ngân hàng trong vòng 05 ngày làm việc sau khi ký hợp đồng.")
    }


def generate_contract_pdf(data: Dict[str, Any]) -> io.BytesIO:
    """
    Sinh file PDF A4 chuẩn 100% Nghị định 30/2020/NĐ-CP:
    - Lề: Trái 30mm, Phải 15mm, Trên 20mm, Dưới 20mm.
    - Font: Times New Roman, dãn dòng 1.15, thụt đầu dòng 1.27cm.
    """
    c_data = prepare_contract_data(data)
    buffer = io.BytesIO()

    # Khổ A4 đứng, lề NĐ 30: Trái 30mm, Phải 15mm, Trên 20mm, Dưới 20mm
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=30 * mm,
        rightMargin=15 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm
    )

    # Styles chuẩn
    style_normal = ParagraphStyle(
        "ND30_Normal",
        fontName="TimesNewRoman",
        fontSize=13,
        leading=16,
        alignment=TA_JUSTIFY,
        firstLineIndent=1.27 * 28.35,  # 1.27cm tính theo pt (1cm ~ 28.35pt)
        spaceAfter=4
    )

    style_normal_no_indent = ParagraphStyle(
        "ND30_NormalNoIndent",
        fontName="TimesNewRoman",
        fontSize=13,
        leading=16,
        alignment=TA_JUSTIFY,
        spaceAfter=3
    )

    style_bold_no_indent = ParagraphStyle(
        "ND30_BoldNoIndent",
        fontName="TimesNewRoman-Bold",
        fontSize=13,
        leading=16,
        spaceAfter=3
    )

    style_center = ParagraphStyle(
        "ND30_Center",
        fontName="TimesNewRoman",
        fontSize=13,
        leading=16,
        alignment=TA_CENTER
    )

    style_center_bold = ParagraphStyle(
        "ND30_CenterBold",
        fontName="TimesNewRoman-Bold",
        fontSize=13,
        leading=16,
        alignment=TA_CENTER
    )

    style_header_agency = ParagraphStyle(
        "ND30_HeaderAgency",
        fontName="TimesNewRoman-Bold",
        fontSize=12,
        leading=15,
        alignment=TA_CENTER
    )

    style_header_motto = ParagraphStyle(
        "ND30_HeaderMotto",
        fontName="TimesNewRoman-Bold",
        fontSize=13,
        leading=16,
        alignment=TA_CENTER
    )

    style_italic = ParagraphStyle(
        "ND30_Italic",
        fontName="TimesNewRoman-Italic",
        fontSize=13,
        leading=16,
        alignment=TA_CENTER
    )

    style_title = ParagraphStyle(
        "ND30_Title",
        fontName="TimesNewRoman-Bold",
        fontSize=15,
        leading=19,
        alignment=TA_CENTER,
        spaceBefore=12,
        spaceAfter=14
    )

    story = []

    # 1. TIÊU ĐỀ ĐẦU TRANG (BẢNG 2 CỘT CÂN ĐỐI NĐ 30)
    # Cột trái: Tên đơn vị + Số HĐ | Cột phải: Quốc hiệu + Tiêu ngữ + Ngày tháng
    cell_left = [
        Paragraph(c_data["ben_a_ten"], style_header_agency),
        Paragraph(f"Số: {c_data['so_hop_dong']}", style_center)
    ]
    
    cell_right = [
        Paragraph("CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM", style_header_agency),
        Paragraph("Độc lập - Tự do - Hạnh phúc", style_header_motto),
        Paragraph(f"<em>{c_data['dia_diem_ky']}, {c_data['ngay_ky']}</em>", style_italic)
    ]

    header_table = Table([[cell_left, cell_right]], colWidths=[75 * mm, 90 * mm])
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 10 * mm))

    # 2. TÊN HỢP ĐỒNG
    story.append(Paragraph(c_data["ten_hop_dong"], style_title))

    # 3. CĂN CỨ PHÁP LÝ
    can_cu_list = [
        "- Căn cứ Bộ luật Dân sự số 91/2015/QH13 ngày 25 tháng 11 năm 2015 của Quốc hội;",
        "- Căn cứ Luật Thương mại số 36/2005/QH11 ngày 14 tháng 06 năm 2005 của Quốc hội;",
        "- Căn cứ Nghị định số 13/2023/NĐ-CP ngày 17 tháng 04 năm 2023 của Chính phủ về bảo vệ dữ liệu cá nhân;",
        "- Căn cứ vào nhu cầu và khả năng thực tế của hai bên."
    ]
    for cc in can_cu_list:
        p_cc = Paragraph(f"<em>{cc}</em>", ParagraphStyle("CC", fontName="TimesNewRoman-Italic", fontSize=12, leading=15, firstLineIndent=1.27 * 28.35, spaceAfter=2))
        story.append(p_cc)

    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph("Hôm nay, hai bên chúng tôi gồm có:", style_normal_no_indent))
    story.append(Spacer(1, 2 * mm))

    # 4. THÔNG TIN BÊN A
    story.append(Paragraph("<b>BÊN A (BÊN CUNG CẤP DỊCH VỤ):</b>", style_bold_no_indent))
    story.append(Paragraph(f"Tên doanh nghiệp: <b>{c_data['ben_a_ten']}</b>", style_normal_no_indent))
    story.append(Paragraph(f"Mã số thuế: {c_data['ben_a_mst']}", style_normal_no_indent))
    story.append(Paragraph(f"Địa chỉ trụ sở: {c_data['ben_a_dia_chi']}", style_normal_no_indent))
    story.append(Paragraph(f"Người đại diện: <b>{c_data['ben_a_dai_dien']}</b> - Chức vụ: {c_data['ben_a_chuc_vu']}", style_normal_no_indent))
    story.append(Paragraph(f"Số CCCD: {c_data['ben_a_cccd']} cấp ngày {c_data['ben_a_ngay_cap']} tại {c_data['ben_a_noi_cap']}", style_normal_no_indent))
    story.append(Paragraph(f"Tài khoản thanh toán: {c_data['ben_a_stk']}", style_normal_no_indent))

    story.append(Spacer(1, 3 * mm))

    # 5. THÔNG TIN BÊN B (TRÍCH XUẤT TỪ CCCD HOẶC NHẬP TAY)
    story.append(Paragraph("<b>BÊN B (KHÁCH HÀNG):</b>", style_bold_no_indent))
    if c_data["has_co_signer"] and c_data["co_signer_ten"]:
        co_rel = c_data.get("co_signer_quan_he", "Vợ/Chồng")
        story.append(Paragraph(f"<b>1. Họ và tên: {c_data['ben_b_ten']}</b>", style_normal_no_indent))
        story.append(Paragraph(f"Ngày sinh: {c_data['ben_b_ngay_sinh']}  |  Giới tính: {c_data['ben_b_gioi_tinh']}", style_normal_no_indent))
        story.append(Paragraph(f"Số CCCD/Căn cước: <b>{c_data['ben_b_cccd']}</b>  |  Ngày cấp: {c_data['ben_b_ngay_cap']}  |  Nơi cấp: {c_data['ben_b_noi_cap']}", style_normal_no_indent))
        story.append(Paragraph(f"Nơi đăng ký thường trú: {c_data['ben_b_dia_chi']}", style_normal_no_indent))
        if c_data['ben_b_dien_thoai']:
            story.append(Paragraph(f"Điện thoại liên hệ: {c_data['ben_b_dien_thoai']}", style_normal_no_indent))

        story.append(Spacer(1, 2 * mm))
        story.append(Paragraph(f"<b>2. Cùng {co_rel.lower()} là: {c_data['co_signer_ten']}</b>", style_normal_no_indent))
        story.append(Paragraph(f"Ngày sinh: {c_data['co_signer_ngay_sinh']}  |  Số CCCD/Căn cước: <b>{c_data['co_signer_cccd']}</b>", style_normal_no_indent))
        story.append(Paragraph(f"Nơi đăng ký thường trú: {c_data['co_signer_dia_chi'] or c_data['ben_b_dia_chi']}", style_normal_no_indent))
    else:
        story.append(Paragraph(f"Họ và tên: <b>{c_data['ben_b_ten']}</b>", style_normal_no_indent))
        story.append(Paragraph(f"Ngày sinh: {c_data['ben_b_ngay_sinh']}  |  Giới tính: {c_data['ben_b_gioi_tinh']}", style_normal_no_indent))
        story.append(Paragraph(f"Số CCCD/Căn cước: <b>{c_data['ben_b_cccd']}</b>", style_normal_no_indent))
        story.append(Paragraph(f"Ngày cấp: {c_data['ben_b_ngay_cap']}  |  Nơi cấp: {c_data['ben_b_noi_cap']}", style_normal_no_indent))
        story.append(Paragraph(f"Nơi đăng ký thường trú: {c_data['ben_b_dia_chi']}", style_normal_no_indent))
        if c_data['ben_b_dien_thoai']:
            story.append(Paragraph(f"Điện thoại liên hệ: {c_data['ben_b_dien_thoai']}", style_normal_no_indent))

    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph("Sau khi bàn bạc thống nhất, hai bên thỏa thuận ký kết hợp đồng này với các điều khoản cụ thể sau:", style_normal_no_indent))
    story.append(Spacer(1, 3 * mm))

    # 6. CÁC ĐIỀU KHOẢN HỢP ĐỒNG CHUẨN MỰC
    # Điều 1
    story.append(Paragraph("<b>Điều 1. Nội dung dịch vụ và phạm vi công việc</b>", style_bold_no_indent))
    story.append(Paragraph(f"1.1. Bên A đồng ý cung cấp và Bên B đồng ý tiếp nhận dịch vụ với nội dung: {c_data['noi_dung_cong_viec']}", style_normal))
    story.append(Paragraph("1.2. Bên A cam kết thực hiện đúng tiêu chuẩn chất lượng, đúng tiến độ và hỗ trợ kỹ thuật xuyên suốt thời gian thực hiện hợp đồng.", style_normal))

    # Điều 2
    story.append(Paragraph("<b>Điều 2. Giá trị hợp đồng và phương thức thanh toán</b>", style_bold_no_indent))
    story.append(Paragraph(f"2.1. Tổng giá trị hợp đồng là: <b>{c_data['gia_tri_hop_dong']} VNĐ</b> (Bằng chữ: <em>{c_data['gia_tri_bang_chu']}</em>).", style_normal))
    story.append(Paragraph(f"2.2. Phương thức thanh toán: {c_data['phuong_thuc_thanh_toan']}", style_normal))
    story.append(Paragraph(f"2.3. Thời hạn thực hiện: {c_data['thoi_han']}.", style_normal))

    # Điều 3
    story.append(Paragraph("<b>Điều 3. Quyền và nghĩa vụ của các bên</b>", style_bold_no_indent))
    story.append(Paragraph("3.1. Bên A có nghĩa vụ bàn giao sản phẩm, giải pháp và dịch vụ đúng tiến độ cam kết; có quyền yêu cầu Bên B thanh toán đầy đủ theo đúng thỏa thuận tại Điều 2.", style_normal))
    story.append(Paragraph("3.2. Bên B có nghĩa vụ cung cấp đầy đủ thông tin, tài liệu cần thiết và thanh toán đúng hạn; có quyền yêu cầu Bên A hỗ trợ kỹ thuật và bảo hành theo cam kết.", style_normal))

    # Điều 4 - Tuân thủ bảo vệ dữ liệu cá nhân theo NĐ 13
    story.append(Paragraph("<b>Điều 4. Cam kết bảo vệ dữ liệu cá nhân (Nghị định 13/2023/NĐ-CP)</b>", style_bold_no_indent))
    story.append(Paragraph("4.1. Các bên cam kết bảo mật tuyệt đối mọi thông tin định danh cá nhân, số CCCD, hình ảnh và dữ liệu nhạy cảm được cung cấp trong quá trình giao kết hợp đồng.", style_normal))
    story.append(Paragraph("4.2. Dữ liệu chỉ được sử dụng đúng mục đích thực hiện hợp đồng này và không được cung cấp cho bất kỳ bên thứ ba nào khi chưa có sự đồng ý bằng văn bản của chủ thể dữ liệu.", style_normal))

    # Điều 5
    story.append(Paragraph("<b>Điều 5. Điều khoản chung và hiệu lực thi hành</b>", style_bold_no_indent))
    story.append(Paragraph("5.1. Hai bên cam kết thực hiện nghiêm túc các điều khoản đã thỏa thuận trong hợp đồng. Mọi sửa đổi, bổ sung phải được lập thành văn bản phụ lục hợp đồng.", style_normal))
    story.append(Paragraph("5.2. Trong quá trình thực hiện, nếu phát sinh tranh chấp, hai bên chủ động thương lượng trên tinh thần hợp tác. Trường hợp không giải quyết được sẽ đưa ra Tòa án có thẩm quyền để giải quyết.", style_normal))
    story.append(Paragraph("5.3. Hợp đồng này có hiệu lực kể từ ngày ký và được lập thành 02 (hai) bản có giá trị pháp lý như nhau, mỗi bên giữ 01 (một) bản.", style_normal))

    story.append(Spacer(1, 8 * mm))

    # 7. KHUNG KÝ TÊN 2 BÊN (CÂN ĐỐI NGHỊ ĐỊNH 30)
    # Theo chuẩn thực tế: Để khoảng trống ký tên, không in sẵn họ tên người ký để các bên tự ký và tự ghi rõ họ tên.
    # Khi có vợ chồng cùng ký thì tiêu đề vẫn là BÊN B như thông thường.
    sig_cell_left = [
        Paragraph("<b>ĐẠI DIỆN BÊN A</b>", style_center_bold),
        Paragraph("<em>(Ký, ghi rõ họ tên và đóng dấu)</em>", style_italic),
        Spacer(1, 35 * mm)
    ]

    sig_cell_right = [
        Paragraph("<b>BÊN B</b>", style_center_bold),
        Paragraph("<em>(Ký, ghi rõ họ tên)</em>", style_italic),
        Spacer(1, 35 * mm)
    ]

    sig_table = Table([[sig_cell_left, sig_cell_right]], colWidths=[82 * mm, 83 * mm])
    sig_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(KeepTogether(sig_table))

    # Xây dựng tài liệu với NumberedCanvasND30
    doc.build(story, canvasmaker=NumberedCanvasND30)
    buffer.seek(0)
    return buffer


def generate_contract_docx(data: Dict[str, Any]) -> io.BytesIO:
    """
    Sinh file Word .docx chuẩn 100% Nghị định 30/2020/NĐ-CP:
    - Margins: Trái 30mm, Phải 15mm, Trên 20mm, Dưới 20mm.
    - Phông chữ: Times New Roman, cỡ 13-14, dãn dòng 1.15, thụt đầu dòng 1.27cm.
    """
    c_data = prepare_contract_data(data)
    doc = docx.Document()

    # Thiết lập kích thước A4 và căn lề theo NĐ 30
    section = doc.sections[0]
    section.page_width = Mm(210)
    section.page_height = Mm(297)
    section.left_margin = Mm(30)
    section.right_margin = Mm(15)
    section.top_margin = Mm(20)
    section.bottom_margin = Mm(20)

    # Đặt phông chữ mặc định Times New Roman
    doc.styles['Normal'].font.name = 'Times New Roman'
    doc.styles['Normal'].font.size = Pt(13)
    doc.styles['Normal'].font.color.rgb = RGBColor(0, 0, 0)

    # 1. BẢNG TIÊU ĐỀ ĐẦU TRANG
    header_table = doc.add_table(rows=1, cols=2)
    header_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    header_table.autofit = False
    
    cell_l = header_table.cell(0, 0)
    cell_r = header_table.cell(0, 1)
    cell_l.width = Mm(75)
    cell_r.width = Mm(90)

    # Bên trái
    p_l1 = cell_l.paragraphs[0]
    p_l1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_l1 = p_l1.add_run(c_data['ben_a_ten'] + "\n")
    r_l1.bold = True
    r_l1.font.size = Pt(12)
    r_l2 = p_l1.add_run(f"Số: {c_data['so_hop_dong']}")
    r_l2.font.size = Pt(13)

    # Bên phải
    p_r1 = cell_r.paragraphs[0]
    p_r1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_r1 = p_r1.add_run("CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM\n")
    r_r1.bold = True
    r_r1.font.size = Pt(12)
    r_r2 = p_r1.add_run("Độc lập - Tự do - Hạnh phúc\n")
    r_r2.bold = True
    r_r2.font.size = Pt(13)
    r_r3 = p_r1.add_run(f"{c_data['dia_diem_ky']}, {c_data['ngay_ky']}")
    r_r3.italic = True
    r_r3.font.size = Pt(13)

    # Khoảng cách
    p_space = doc.add_paragraph()
    p_space.paragraph_format.space_before = Pt(12)
    p_space.paragraph_format.space_after = Pt(6)

    # 2. TÊN HỢP ĐỒNG
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run(c_data['ten_hop_dong'])
    r_title.bold = True
    r_title.font.size = Pt(15)
    p_title.paragraph_format.space_after = Pt(14)

    # 3. CĂN CỨ
    can_cu = [
        "- Căn cứ Bộ luật Dân sự số 91/2015/QH13 ngày 25 tháng 11 năm 2015 của Quốc hội;",
        "- Căn cứ Luật Thương mại số 36/2005/QH11 ngày 14 tháng 06 năm 2005 của Quốc hội;",
        "- Căn cứ Nghị định số 13/2023/NĐ-CP ngày 17 tháng 04 năm 2023 của Chính phủ về bảo vệ dữ liệu cá nhân;",
        "- Căn cứ vào nhu cầu và khả năng thực tế của hai bên."
    ]
    for cc in can_cu:
        p_c = doc.add_paragraph()
        r_c = p_c.add_run(cc)
        r_c.italic = True
        r_c.font.size = Pt(12)
        p_c.paragraph_format.first_line_indent = Mm(12.7)
        p_c.paragraph_format.space_after = Pt(2)

    p_intro = doc.add_paragraph("Hôm nay, hai bên chúng tôi gồm có:")
    p_intro.paragraph_format.space_before = Pt(6)
    p_intro.paragraph_format.space_after = Pt(4)

    # Helper paragraph
    def add_line(label: str, value: str, bold_val: bool = False):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.15
        r_lbl = p.add_run(label)
        r_val = p.add_run(value)
        if bold_val:
            r_val.bold = True
        return p

    # 4. BÊN A
    p_ba = doc.add_paragraph()
    p_ba.add_run("BÊN A (BÊN CUNG CẤP DỊCH VỤ):").bold = True
    p_ba.paragraph_format.space_before = Pt(6)
    p_ba.paragraph_format.space_after = Pt(2)
    
    add_line("Tên doanh nghiệp: ", c_data['ben_a_ten'], True)
    add_line("Mã số thuế: ", c_data['ben_a_mst'])
    add_line("Địa chỉ trụ sở: ", c_data['ben_a_dia_chi'])
    add_line("Người đại diện: ", f"{c_data['ben_a_dai_dien']} - Chức vụ: {c_data['ben_a_chuc_vu']}")
    add_line("Số CCCD: ", f"{c_data['ben_a_cccd']} cấp ngày {c_data['ben_a_ngay_cap']} tại {c_data['ben_a_noi_cap']}")
    add_line("Tài khoản ngân hàng: ", c_data['ben_a_stk'])

    # 5. BÊN B
    p_bb = doc.add_paragraph()
    p_bb.add_run("BÊN B (KHÁCH HÀNG):").bold = True
    p_bb.paragraph_format.space_before = Pt(6)
    p_bb.paragraph_format.space_after = Pt(2)

    if c_data["has_co_signer"] and c_data["co_signer_ten"]:
        co_rel = c_data.get("co_signer_quan_he", "Vợ/Chồng")
        add_line("1. Họ và tên: ", c_data['ben_b_ten'], True)
        add_line("Ngày sinh: ", f"{c_data['ben_b_ngay_sinh']}  |  Giới tính: {c_data['ben_b_gioi_tinh']}")
        add_line("Số CCCD/Căn cước: ", f"{c_data['ben_b_cccd']}  |  Ngày cấp: {c_data['ben_b_ngay_cap']}  |  Nơi cấp: {c_data['ben_b_noi_cap']}")
        add_line("Nơi thường trú: ", c_data['ben_b_dia_chi'])
        if c_data['ben_b_dien_thoai']:
            add_line("Điện thoại: ", c_data['ben_b_dien_thoai'])

        p_cs_gap = doc.add_paragraph()
        p_cs_gap.paragraph_format.space_before = Pt(3)
        add_line(f"2. Cùng {co_rel.lower()} là: ", c_data['co_signer_ten'], True)
        add_line("Số CCCD/Căn cước: ", f"{c_data['co_signer_cccd']}  |  Ngày sinh: {c_data['co_signer_ngay_sinh']}")
        add_line("Nơi thường trú: ", c_data['co_signer_dia_chi'] or c_data['ben_b_dia_chi'])
    else:
        add_line("Họ và tên: ", c_data['ben_b_ten'], True)
        add_line("Ngày sinh: ", f"{c_data['ben_b_ngay_sinh']}  |  Giới tính: {c_data['ben_b_gioi_tinh']}")
        add_line("Số CCCD/Căn cước: ", c_data['ben_b_cccd'], True)
        add_line("Ngày cấp: ", f"{c_data['ben_b_ngay_cap']}  |  Nơi cấp: {c_data['ben_b_noi_cap']}")
        add_line("Nơi thường trú: ", c_data['ben_b_dia_chi'])
        if c_data['ben_b_dien_thoai']:
            add_line("Điện thoại: ", c_data['ben_b_dien_thoai'])

    p_agree = doc.add_paragraph("Sau khi bàn bạc thống nhất, hai bên thỏa thuận ký kết hợp đồng này với các điều khoản cụ thể sau:")
    p_agree.paragraph_format.space_before = Pt(6)
    p_agree.paragraph_format.space_after = Pt(4)

    def add_clause(title: str, items: list):
        p_t = doc.add_paragraph()
        p_t.add_run(title).bold = True
        p_t.paragraph_format.space_before = Pt(6)
        p_t.paragraph_format.space_after = Pt(2)
        for it in items:
            p_i = doc.add_paragraph()
            p_i.paragraph_format.first_line_indent = Mm(12.7)
            p_i.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p_i.paragraph_format.line_spacing = 1.15
            p_i.paragraph_format.space_after = Pt(3)
            p_i.add_run(it)

    add_clause("Điều 1. Nội dung dịch vụ và phạm vi công việc", [
        f"1.1. Bên A đồng ý cung cấp và Bên B đồng ý tiếp nhận dịch vụ với nội dung: {c_data['noi_dung_cong_viec']}",
        "1.2. Bên A cam kết thực hiện đúng tiêu chuẩn chất lượng, đúng tiến độ và hỗ trợ kỹ thuật xuyên suốt thời gian thực hiện hợp đồng."
    ])

    add_clause("Điều 2. Giá trị hợp đồng và phương thức thanh toán", [
        f"2.1. Tổng giá trị hợp đồng là: {c_data['gia_tri_hop_dong']} VNĐ (Bằng chữ: {c_data['gia_tri_bang_chu']}).",
        f"2.2. Phương thức thanh toán: {c_data['phuong_thuc_thanh_toan']}",
        f"2.3. Thời hạn thực hiện: {c_data['thoi_han']}."
    ])

    add_clause("Điều 3. Quyền và nghĩa vụ của các bên", [
        "3.1. Bên A có nghĩa vụ bàn giao sản phẩm, giải pháp và dịch vụ đúng tiến độ cam kết; có quyền yêu cầu Bên B thanh toán đầy đủ theo đúng thỏa thuận tại Điều 2.",
        "3.2. Bên B có nghĩa vụ cung cấp đầy đủ thông tin, tài liệu cần thiết và thanh toán đúng hạn; có quyền yêu cầu Bên A hỗ trợ kỹ thuật và bảo hành theo cam kết."
    ])

    add_clause("Điều 4. Cam kết bảo vệ dữ liệu cá nhân (Nghị định 13/2023/NĐ-CP)", [
        "4.1. Các bên cam kết bảo mật tuyệt đối mọi thông tin định danh cá nhân, số CCCD, hình ảnh và dữ liệu nhạy cảm được cung cấp trong quá trình giao kết hợp đồng.",
        "4.2. Dữ liệu chỉ được sử dụng đúng mục đích thực hiện hợp đồng này và không được cung cấp cho bất kỳ bên thứ ba nào khi chưa có sự đồng ý bằng văn bản của chủ thể dữ liệu."
    ])

    add_clause("Điều 5. Điều khoản chung và hiệu lực thi hành", [
        "5.1. Hai bên cam kết thực hiện nghiêm túc các điều khoản đã thỏa thuận trong hợp đồng. Mọi sửa đổi, bổ sung phải được lập thành văn bản phụ lục hợp đồng.",
        "5.2. Trong quá trình thực hiện, nếu phát sinh tranh chấp, hai bên chủ động thương lượng trên tinh thần hợp tác. Trường hợp không giải quyết được sẽ đưa ra Tòa án có thẩm quyền để giải quyết.",
        "5.3. Hợp đồng này có hiệu lực kể từ ngày ký và được lập thành 02 (hai) bản có giá trị pháp lý như nhau, mỗi bên giữ 01 (một) bản."
    ])

    # BẢNG KÝ TÊN 2 BÊN (CHUẨN NGHỊ ĐỊNH 30)
    # Tuyệt đối không in sẵn họ tên người ký để các bên tự ký và tự ghi rõ họ tên.
    # Tiêu đề bên B luôn là BÊN B như thông thường.
    p_sig_space = doc.add_paragraph()
    p_sig_space.paragraph_format.space_before = Pt(12)

    sig_tbl = doc.add_table(rows=1, cols=2)
    sig_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    sig_tbl.autofit = False
    
    cell_s1 = sig_tbl.cell(0, 0)
    cell_s2 = sig_tbl.cell(0, 1)
    cell_s1.width = Mm(82)
    cell_s2.width = Mm(83)

    p_s1 = cell_s1.paragraphs[0]
    p_s1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_s1.add_run("ĐẠI DIỆN BÊN A\n").bold = True
    r_s1_sub = p_s1.add_run("(Ký, ghi rõ họ tên và đóng dấu)\n\n\n\n\n\n")
    r_s1_sub.italic = True

    p_s2 = cell_s2.paragraphs[0]
    p_s2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_s2.add_run("BÊN B\n").bold = True
    r_s2_sub = p_s2.add_run("(Ký, ghi rõ họ tên)\n\n\n\n\n\n")
    r_s2_sub.italic = True

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer
