"""
Chuyển đổi số tiền thành chữ tiếng Việt chuẩn văn phong hợp đồng hành chính
Ví dụ: 150000000 -> Một trăm năm mươi triệu đồng chẵn.
"""

def doc_so_thanh_chu(so_tien: int | float | str) -> str:
    if so_tien is None or str(so_tien).strip() == "":
        return ""
    
    try:
        clean_str = str(so_tien).replace(".", "").replace(",", "").replace(" ", "").replace("đ", "").replace("VND", "").replace("VNĐ", "").strip()
        num = int(clean_str)
    except ValueError:
        return ""

    if num == 0:
        return "Không đồng chẵn"

    chus = ["không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]
    don_vi = ["", "nghìn", "triệu", "tỷ", "nghìn tỷ", "triệu tỷ"]

    def doc_ba_so(n: int, day_du: bool = True) -> str:
        tram = n // 100
        chuc = (n % 100) // 10
        dv = n % 10
        res = []

        if tram > 0 or day_du:
            res.append(f"{chus[tram]} trăm")

        if chuc > 1:
            res.append(f"{chus[chuc]} mươi")
            if dv == 1:
                res.append("mốt")
            elif dv == 5:
                res.append("lăm")
            elif dv > 0:
                res.append(chus[dv])
        elif chuc == 1:
            res.append("mười")
            if dv == 1:
                res.append("một")
            elif dv == 5:
                res.append("lăm")
            elif dv > 0:
                res.append(chus[dv])
        elif chuc == 0:
            if (tram > 0 or day_du) and dv > 0:
                res.append("lẻ")
            if dv > 0:
                res.append(chus[dv])

        return " ".join(res)

    groups = []
    temp = num
    while temp > 0:
        groups.append(temp % 1000)
        temp //= 1000

    parts = []
    for i in range(len(groups) - 1, -1, -1):
        g = groups[i]
        if g > 0:
            day_du = (i != len(groups) - 1)
            g_str = doc_ba_so(g, day_du)
            part = g_str + (f" {don_vi[i]}" if don_vi[i] else "")
            parts.append(part.strip())

    ket_qua = " ".join(parts).strip()
    if ket_qua:
        ket_qua = ket_qua[0].upper() + ket_qua[1:] + " đồng chẵn"
    return ket_qua


if __name__ == "__main__":
    tests = [50000000, 150000000, 1255000000, 2000000, 1000]
    for t in tests:
        print(f"{t:,} đ -> {doc_so_thanh_chu(t)}")
