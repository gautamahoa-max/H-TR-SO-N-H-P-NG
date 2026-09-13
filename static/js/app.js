/**
 * Application Logic for Contract Automation System
 * Apple Design System UI & 3-Button Action Handler
 */

document.addEventListener("DOMContentLoaded", () => {
  // Elements
  const dropzone = document.getElementById("dropzone");
  const fileInput = document.getElementById("fileInput");
  const btnSelectFile = document.getElementById("btnSelectFile");
  const btnUseSampleImage = document.getElementById("btnUseSampleImage");
  const btnQuickSample = document.getElementById("btnQuickSample");
  const dropzoneContent = document.getElementById("dropzoneContent");
  const previewContainer = document.getElementById("previewContainer");
  const previewImage = document.getElementById("previewImage");
  const btnReUpload = document.getElementById("btnReUpload");
  const scanLoading = document.getElementById("scanLoading");
  const scanStatusBadge = document.getElementById("scanStatusBadge");

  // Form Fields
  const inputHoTen = document.getElementById("inputHoTen");
  const inputCCCD = document.getElementById("inputCCCD");
  const inputNgaySinh = document.getElementById("inputNgaySinh");
  const inputGioiTinh = document.getElementById("inputGioiTinh");
  const inputDienThoai = document.getElementById("inputDienThoai");
  const inputDiaChi = document.getElementById("inputDiaChi");
  const inputNgayCap = document.getElementById("inputNgayCap");
  const inputNoiCap = document.getElementById("inputNoiCap");
  const btnClearForm = document.getElementById("btnClearForm");

  // Co-signer
  const chkCoSigner = document.getElementById("chkCoSigner");
  const secCoSigner = document.getElementById("secCoSigner");
  const inputCoTen = document.getElementById("inputCoTen");
  const inputCoCCCD = document.getElementById("inputCoCCCD");
  const inputCoNgaySinh = document.getElementById("inputCoNgaySinh");
  const inputCoQuanHe = document.getElementById("inputCoQuanHe");

  // Contract Details & Templates
  const selectTemplate = document.getElementById("selectTemplate");
  const tplCountBadge = document.getElementById("tplCountBadge");
  const inputTenHD = document.getElementById("inputTenHD");
  const inputGiaTri = document.getElementById("inputGiaTri");
  const inputGiaTriChu = document.getElementById("inputGiaTriChu");
  const inputThoiHan = document.getElementById("inputThoiHan");
  const inputNoiDung = document.getElementById("inputNoiDung");

  // 3 Action Buttons
  const btnPreview = document.getElementById("btnPreview");
  const btnExportPDF = document.getElementById("btnExportPDF");
  const btnExportDocx = document.getElementById("btnExportDocx");

  // Preview Modal
  const modalPreview = document.getElementById("modalPreview");
  const pdfFrame = document.getElementById("pdfFrame");
  const pdfLoading = document.getElementById("pdfLoading");
  const modalBtnClose = document.getElementById("modalBtnClose");
  const modalBtnDownloadPDF = document.getElementById("modalBtnDownloadPDF");

  // Company Profile Modal
  const btnOpenProfile = document.getElementById("btnOpenProfile");
  const btnEditBenAFast = document.getElementById("btnEditBenAFast");
  const modalProfile = document.getElementById("modalProfile");
  const modalProfileClose = document.getElementById("modalProfileClose");
  const btnSaveProfile = document.getElementById("btnSaveProfile");

  // Profile inputs
  const profTen = document.getElementById("profTen");
  const profMST = document.getElementById("profMST");
  const profDiaChi = document.getElementById("profDiaChi");
  const profDaiDien = document.getElementById("profDaiDien");
  const profChucVu = document.getElementById("profChucVu");
  const profCCCD = document.getElementById("profCCCD");
  const profNgayCap = document.getElementById("profNgayCap");
  const profSTK = document.getElementById("profSTK");

  // Display bên A
  const dispBenATen = document.getElementById("dispBenATen");
  const dispBenADaiDien = document.getElementById("dispBenADaiDien");
  const dispBenAChiNhanh = document.getElementById("dispBenAChiNhanh");

  let companyProfile = {};
  let currentPreviewBlobUrl = null;

  // 1. TẢI HỒ SƠ BÊN A TỪ SERVER
  async function loadCompanyProfile() {
    try {
      const res = await fetch("/api/company-profile");
      if (res.ok) {
        companyProfile = await res.json();
        updateCompanyProfileUI();
      }
    } catch (e) {
      console.error("Lỗi tải hồ sơ công ty:", e);
    }
  }

  function updateCompanyProfileUI() {
    if (!companyProfile.ten_to_chuc) return;
    dispBenATen.textContent = companyProfile.ten_to_chuc;
    dispBenADaiDien.textContent = `Đại diện: ${companyProfile.dai_dien || ''} - Chức vụ: ${companyProfile.chuc_vu || ''}`;
    dispBenAChiNhanh.textContent = `MST: ${companyProfile.ma_so_thue || ''} | ${companyProfile.dia_chi || ''}`;

    profTen.value = companyProfile.ten_to_chuc || "";
    profMST.value = companyProfile.ma_so_thue || "";
    profDiaChi.value = companyProfile.dia_chi || "";
    profDaiDien.value = companyProfile.dai_dien || "";
    profChucVu.value = companyProfile.chuc_vu || "";
    profCCCD.value = companyProfile.so_cccd_nguoi_dai_dien || "";
    profNgayCap.value = companyProfile.ngay_cap_cccd_dai_dien || "";
    profSTK.value = companyProfile.so_tai_khoan || "";
  }

  loadCompanyProfile();

  // 1.1 TẢI DANH SÁCH 41 MẪU HỢP ĐỒNG NGUỒN TỪ GOOGLE DRIVE
  async function loadTemplates() {
    try {
      const res = await fetch("/api/templates");
      if (res.ok) {
        const templates = await res.json();
        if (tplCountBadge) {
          tplCountBadge.textContent = `${templates.length} Mẫu Sẵn Có`;
        }
        // Chỉ nạp thêm nếu selectTemplate chưa có sẵn options từ HTML
        if (selectTemplate.options.length <= 1) {
          templates.forEach(tpl => {
            const opt = document.createElement("option");
            opt.value = tpl.filename;
            opt.textContent = tpl.title;
            selectTemplate.appendChild(opt);
          });
        }
      }
    } catch (e) {
      console.error("Lỗi tải danh sách mẫu:", e);
    }
  }

  loadTemplates();

  // Khi chọn mẫu hợp đồng khác
  selectTemplate.addEventListener("change", (e) => {
    const selected = selectTemplate.options[selectTemplate.selectedIndex];
    if (selectTemplate.value) {
      // Làm sạch tiêu đề hiển thị: bỏ số thứ tự ở đầu (vd: "96. HỢP ĐỒNG DỊCH VỤ MÔI GIỚI" -> "HỢP ĐỒNG DỊCH VỤ MÔI GIỚI")
      let cleanTitle = selected.text.replace(/^[0-9]+[\.\-\s]+/, "").trim();
      inputTenHD.value = cleanTitle.toUpperCase();
    } else {
      inputTenHD.value = "HỢP ĐỒNG DỊCH VỤ TƯ VẤN VÀ CUNG CẤP GIẢI PHÁP";
    }
  });

  // Camera Elements
  const btnOpenCamera = document.getElementById("btnOpenCamera");
  const modalCamera = document.getElementById("modalCamera");
  const btnCameraClose = document.getElementById("btnCameraClose");
  const btnCameraSnap = document.getElementById("btnCameraSnap");
  const cameraVideo = document.getElementById("cameraVideo");
  const cameraCanvas = document.getElementById("cameraCanvas");
  const cameraLoading = document.getElementById("cameraLoading");
  let activeCameraStream = null;
  let cameraTarget = 'main'; // 'main' (Khách chính) hoặc 'co_signer' (Vợ/Chồng)

  // Co-signer Elements
  const btnOpenCoCamera = document.getElementById("btnOpenCoCamera");
  const btnSelectCoFile = document.getElementById("btnSelectCoFile");
  const coFileInput = document.getElementById("coFileInput");
  const coScanBadge = document.getElementById("coScanBadge");

  // 2. XỬ LÝ CHỤP CAMERA TRỰC TIẾP
  async function startCamera(target = 'main') {
    cameraTarget = target;
    modalCamera.classList.remove("hidden");
    cameraLoading.classList.remove("hidden");

    try {
      const constraints = {
        video: {
          width: { ideal: 1920 },
          height: { ideal: 1080 },
          facingMode: "environment" // Ưu tiên camera sau nếu là điện thoại/máy tính bảng
        }
      };

      activeCameraStream = await navigator.mediaDevices.getUserMedia(constraints);
      cameraVideo.srcObject = activeCameraStream;
      await cameraVideo.play();
      cameraLoading.classList.add("hidden");
    } catch (err) {
      console.error("Lỗi bật camera:", err);
      alert("Không thể truy cập camera. Vui lòng cấp quyền camera trên trình duyệt hoặc sử dụng tính năng tải ảnh từ máy.");
      stopCamera();
    }
  }

  function stopCamera() {
    if (activeCameraStream) {
      activeCameraStream.getTracks().forEach(track => track.stop());
      activeCameraStream = null;
    }
    cameraVideo.srcObject = null;
    modalCamera.classList.add("hidden");
  }

  if (btnOpenCamera) {
    btnOpenCamera.addEventListener("click", (e) => {
      e.stopPropagation();
      startCamera('main');
    });
  }

  if (btnOpenCoCamera) {
    btnOpenCoCamera.addEventListener("click", (e) => {
      e.stopPropagation();
      startCamera('co_signer');
    });
  }

  if (btnCameraClose) {
    btnCameraClose.addEventListener("click", stopCamera);
  }

  if (btnCameraSnap) {
    btnCameraSnap.addEventListener("click", () => {
      if (!cameraVideo.videoWidth) return;

      cameraCanvas.width = cameraVideo.videoWidth;
      cameraCanvas.height = cameraVideo.videoHeight;
      const ctx = cameraCanvas.getContext("2d");
      ctx.drawImage(cameraVideo, 0, 0, cameraCanvas.width, cameraCanvas.height);

      cameraCanvas.toBlob((blob) => {
        if (blob) {
          const filename = cameraTarget === 'co_signer' ? "cccd_vo_chong.jpg" : "cccd_khach_hang.jpg";
          const file = new File([blob], filename, { type: "image/jpeg" });
          stopCamera();
          if (cameraTarget === 'co_signer') {
            handleCoSignerUpload(file);
          } else {
            handleImageUpload(file);
          }
        }
      }, "image/jpeg", 0.95);
    });
  }

  // 3. XỬ LÝ KÉO THẢ VÀ TẢI ẢNH / FILE PDF CCCD
  btnSelectFile.addEventListener("click", (e) => {
    e.stopPropagation();
    fileInput.click();
  });

  if (btnSelectCoFile && coFileInput) {
    btnSelectCoFile.addEventListener("click", (e) => {
      e.stopPropagation();
      coFileInput.click();
    });

    coFileInput.addEventListener("change", (e) => {
      if (e.target.files.length > 0) {
        handleCoSignerUpload(e.target.files[0]);
      }
    });
  }

  dropzone.addEventListener("click", () => {
    if (previewContainer.classList.contains("hidden")) {
      fileInput.click();
    }
  });

  btnReUpload.addEventListener("click", (e) => {
    e.stopPropagation();
    fileInput.click();
  });

  ["dragenter", "dragover"].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.add("drag-active");
    });
  });

  ["dragleave", "drop"].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.remove("drag-active");
    });
  });

  // Hỗ trợ kéo thả 1 hoặc 2 thẻ CCCD (Vợ & Chồng) cùng lúc
  dropzone.addEventListener("drop", (e) => {
    const files = e.dataTransfer.files;
    if (files.length === 1) {
      handleImageUpload(files[0]);
    } else if (files.length >= 2) {
      // Tự động gán file 1 cho Khách chính và file 2 cho Vợ/Chồng
      handleImageUpload(files[0]);
      chkCoSigner.checked = true;
      secCoSigner.classList.remove("hidden");
      handleCoSignerUpload(files[1]);
    }
  });

  fileInput.addEventListener("change", (e) => {
    const files = e.target.files;
    if (files.length === 1) {
      handleImageUpload(files[0]);
    } else if (files.length >= 2) {
      handleImageUpload(files[0]);
      chkCoSigner.checked = true;
      secCoSigner.classList.remove("hidden");
      handleCoSignerUpload(files[1]);
    }
  });

  // Bóc tách CCCD của Người đồng ký (Vợ/Chồng)
  async function handleCoSignerUpload(file) {
    if (!coScanBadge) return;
    coScanBadge.classList.remove("hidden");
    coScanBadge.className = "text-[10px] px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 font-medium";
    coScanBadge.textContent = "Đang phân tích thẻ...";

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("/api/extract-cccd", {
        method: "POST",
        body: formData
      });
      const data = await res.json();

      if (data.success) {
        if (data.ho_ten) inputCoTen.value = data.ho_ten;
        if (data.so_cccd) inputCoCCCD.value = data.so_cccd;
        if (data.ngay_sinh) inputCoNgaySinh.value = data.ngay_sinh;

        // Tự động nhận diện Vợ/Chồng theo giới tính
        const mainGender = inputGioiTinh ? inputGioiTinh.value : "";
        if (mainGender === "Nữ" && data.gioi_tinh === "Nam") {
          inputCoQuanHe.value = "Chồng";
        } else if (mainGender === "Nam" && data.gioi_tinh === "Nữ") {
          inputCoQuanHe.value = "Vợ";
        } else {
          inputCoQuanHe.value = "Vợ/Chồng";
        }

        coScanBadge.className = "text-[10px] px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 font-medium";
        coScanBadge.textContent = `Đã bóc tách thẻ ${inputCoQuanHe.value}`;
      } else {
        coScanBadge.className = "text-[10px] px-2 py-0.5 rounded-full bg-amber-50 text-amber-700 font-medium";
        coScanBadge.textContent = "Không thấy QR - Nhập tay";
      }
    } catch (e) {
      console.error("Lỗi bóc tách thẻ đồng ký:", e);
      coScanBadge.textContent = "Lỗi đọc file";
    }
  }

  // Gửi file (Ảnh hoặc PDF) lên backend bóc tách
  async function handleImageUpload(file) {
    const isPdf = file.type === "application/pdf" || file.name.toLowerCase().endsWith(".pdf");

    // Hiển thị trạng thái xem trước
    if (!isPdf) {
      const reader = new FileReader();
      reader.onload = (e) => {
        previewImage.src = e.target.result;
        dropzoneContent.classList.add("hidden");
        previewContainer.classList.remove("hidden");
      };
      reader.readAsDataURL(file);
    } else {
      dropzoneContent.classList.add("hidden");
      previewContainer.classList.remove("hidden");
    }

    // Gọi API scan
    scanLoading.classList.remove("hidden");
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("/api/extract-cccd", {
        method: "POST",
        body: formData
      });
      const data = await res.json();

      // Nếu là PDF và backend trả về ảnh trang đầu
      if (data.preview_image) {
        previewImage.src = data.preview_image;
      }

      if (data.success) {
        fillFormData(data);
        scanStatusBadge.classList.remove("hidden");
        scanStatusBadge.className = "text-xs px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 font-medium";
        const fileTypeLabel = isPdf ? "file PDF" : "ảnh";
        scanStatusBadge.textContent = `Đã quét QR từ ${fileTypeLabel} thành công (0.05s)`;
      } else {
        scanStatusBadge.classList.remove("hidden");
        scanStatusBadge.className = "text-xs px-2.5 py-0.5 rounded-full bg-amber-50 text-amber-700 font-medium";
        scanStatusBadge.textContent = isPdf ? "Đã nhận PDF nhưng không thấy QR - Mời bạn nhập tay" : "Không thấy QR - Mời bạn nhập tay";
      }
    } catch (e) {
      console.error("Lỗi bóc tách:", e);
      alert("Không thể kết nối máy chủ phân tích file.");
    } finally {
      scanLoading.classList.add("hidden");
    }
  }

  function fillFormData(data) {
    if (data.ho_ten) inputHoTen.value = data.ho_ten;
    if (data.so_cccd) inputCCCD.value = data.so_cccd;
    if (data.ngay_sinh) inputNgaySinh.value = data.ngay_sinh;
    if (data.gioi_tinh) inputGioiTinh.value = data.gioi_tinh;
    if (data.dia_chi) inputDiaChi.value = data.dia_chi;
    if (data.ngay_cap) inputNgayCap.value = data.ngay_cap;
    if (data.noi_cap) inputNoiCap.value = data.noi_cap;

    // Giá trị hợp đồng mẫu nếu chưa nhập
    if (!inputGiaTri.value) {
      inputGiaTri.value = "150.000.000";
      triggerNumToWords("150.000.000");
    }
  }

  // Dùng CCCD mẫu trực tiếp
  btnUseSampleImage.addEventListener("click", async (e) => {
    e.stopPropagation();
    scanLoading.classList.remove("hidden");
    try {
      const res = await fetch("/api/sample-cccd-image");
      const blob = await res.blob();
      const file = new File([blob], "cccd_mau.jpg", { type: "image/jpeg" });
      handleImageUpload(file);
    } catch (e) {
      console.error(e);
      scanLoading.classList.add("hidden");
    }
  });

  btnQuickSample.addEventListener("click", () => {
    btnUseSampleImage.click();
  });

  // 3. TỰ ĐỘNG DỊCH SỐ TIỀN THÀNH CHỮ TIẾNG VIỆT
  inputGiaTri.addEventListener("input", (e) => {
    let val = e.target.value.replace(/\D/g, "");
    if (val) {
      val = parseInt(val, 10).toLocaleString("vi-VN");
      e.target.value = val;
      triggerNumToWords(val);
    } else {
      inputGiaTriChu.value = "";
    }
  });

  async function triggerNumToWords(soTienStr) {
    try {
      const res = await fetch("/api/num-to-words", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ so_tien: soTienStr })
      });
      if (res.ok) {
        const data = await res.json();
        inputGiaTriChu.value = data.chu || "";
      }
    } catch (e) {
      console.error(e);
    }
  }

  // Tự động viết hoa họ tên khi rời ô
  inputHoTen.addEventListener("blur", (e) => {
    e.target.value = e.target.value.toUpperCase();
  });

  // Checkbox đồng ký kết
  chkCoSigner.addEventListener("change", (e) => {
    if (e.target.checked) {
      secCoSigner.classList.remove("hidden");
    } else {
      secCoSigner.classList.add("hidden");
    }
  });

  // Xóa trắng form
  btnClearForm.addEventListener("click", () => {
    inputHoTen.value = "";
    inputCCCD.value = "";
    inputNgaySinh.value = "";
    inputDienThoai.value = "";
    inputDiaChi.value = "";
    inputNgayCap.value = "";
    inputNoiCap.value = "Cục Cảnh sát quản lý hành chính về trật tự xã hội";
    inputGiaTri.value = "";
    inputGiaTriChu.value = "";
    inputCoTen.value = "";
    inputCoCCCD.value = "";
    chkCoSigner.checked = false;
    secCoSigner.classList.add("hidden");

    previewContainer.classList.add("hidden");
    dropzoneContent.classList.remove("hidden");
    previewImage.src = "";
    fileInput.value = "";
    scanStatusBadge.classList.add("hidden");
  });

  // 4. THU THẬP DỮ LIỆU HỢP ĐỒNG HIỆN TẠI
  function getPayload() {
    return {
      ten_hop_dong: inputTenHD.value || "HỢP ĐỒNG DỊCH VỤ",
      // Bên A
      ben_a_ten: companyProfile.ten_to_chuc || dispBenATen.textContent,
      ben_a_mst: companyProfile.ma_so_thue || "0109888999",
      ben_a_dia_chi: companyProfile.dia_chi || "Hà Nội",
      ben_a_dai_dien: companyProfile.dai_dien || "VÕ VĂN HÒA",
      ben_a_chuc_vu: companyProfile.chuc_vu || "Tổng Giám đốc",
      ben_a_cccd: companyProfile.so_cccd_nguoi_dai_dien || "001085006789",
      ben_a_ngay_cap: companyProfile.ngay_cap_cccd_dai_dien || "15/05/2021",
      ben_a_noi_cap: companyProfile.noi_cap_cccd_dai_dien || "Cục Cảnh sát quản lý hành chính về trật tự xã hội",
      ben_a_stk: companyProfile.so_tai_khoan || "19036888999999",
      // Bên B
      ben_b_ten: inputHoTen.value || "NGUYỄN VĂN AN",
      ben_b_cccd: inputCCCD.value || "001200001234",
      ben_b_ngay_sinh: inputNgaySinh.value || "15/08/1995",
      ben_b_gioi_tinh: inputGioiTinh.value || "Nam",
      ben_b_dia_chi: inputDiaChi.value || "Hà Nội",
      ben_b_ngay_cap: inputNgayCap.value || "25/04/2021",
      ben_b_noi_cap: inputNoiCap.value || "Cục Cảnh sát quản lý hành chính về trật tự xã hội",
      ben_b_dien_thoai: inputDienThoai.value || "",
      // Đồng ký
      has_co_signer: chkCoSigner.checked,
      co_signer_ten: inputCoTen.value || "",
      co_signer_cccd: inputCoCCCD.value || "",
      co_signer_ngay_sinh: inputCoNgaySinh.value || "",
      co_signer_quan_he: inputCoQuanHe.value || "Vợ/Chồng",
      co_signer_dia_chi: inputDiaChi.value || "",
      // Chi tiết
      gia_tri_hop_dong: inputGiaTri.value || "150.000.000",
      gia_tri_bang_chu: inputGiaTriChu.value || "Một trăm năm mươi triệu đồng chẵn",
      thoi_han: inputThoiHan.value || "12 tháng kể từ ngày ký",
      noi_dung_cong_viec: inputNoiDung.value || "Cung cấp giải pháp phần mềm và dịch vụ kỹ thuật.",
      selected_template: selectTemplate ? selectTemplate.value : ""
    };
  }

  // 5. NÚT 1: [XEM TRƯỚC] (PREVIEW MODAL)
  btnPreview.addEventListener("click", async () => {
    modalPreview.classList.remove("hidden");
    pdfLoading.classList.remove("hidden");

    try {
      const payload = getPayload();
      const res = await fetch("/api/preview-pdf", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!res.ok) throw new Error("Không thể tạo bản xem trước PDF");

      const blob = await res.blob();
      if (currentPreviewBlobUrl) {
        URL.revokeObjectURL(currentPreviewBlobUrl);
      }
      currentPreviewBlobUrl = URL.createObjectURL(blob);
      pdfFrame.src = currentPreviewBlobUrl;
    } catch (e) {
      alert("Lỗi khi xem trước PDF: " + e.message);
      modalPreview.classList.add("hidden");
    } finally {
      pdfLoading.classList.add("hidden");
    }
  });

  modalBtnClose.addEventListener("click", () => {
    modalPreview.classList.add("hidden");
    pdfFrame.src = "about:blank";
  });

  modalBtnDownloadPDF.addEventListener("click", () => {
    btnExportPDF.click();
  });

  // 6. NÚT 2: [XUẤT PDF]
  btnExportPDF.addEventListener("click", async () => {
    const originalText = btnExportPDF.innerHTML;
    btnExportPDF.innerHTML = `<div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div><span>Đang tạo PDF...</span>`;
    btnExportPDF.disabled = true;

    try {
      const payload = getPayload();
      const res = await fetch("/api/export-pdf", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!res.ok) throw new Error("Lỗi khi xuất PDF");

      const blob = await res.blob();
      const tenKH = (payload.ben_b_ten || "KHACH_HANG").replace(/\s+/g, "_");
      const filename = `HD_${tenKH}_${new Date().toISOString().slice(0, 10)}.pdf`;

      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (e) {
      alert("Lỗi xuất PDF: " + e.message);
    } finally {
      btnExportPDF.innerHTML = originalText;
      btnExportPDF.disabled = false;
      lucide.createIcons();
    }
  });

  // 7. NÚT 3: [XUẤT DOCX]
  btnExportDocx.addEventListener("click", async () => {
    const originalText = btnExportDocx.innerHTML;
    btnExportDocx.innerHTML = `<div class="w-4 h-4 border-2 border-zinc-700 border-t-transparent rounded-full animate-spin"></div><span>Đang tạo Word...</span>`;
    btnExportDocx.disabled = true;

    try {
      const payload = getPayload();
      const res = await fetch("/api/export-docx", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!res.ok) throw new Error("Lỗi khi xuất Word");

      const blob = await res.blob();
      const tenKH = (payload.ben_b_ten || "KHACH_HANG").replace(/\s+/g, "_");
      const filename = `HD_${tenKH}_${new Date().toISOString().slice(0, 10)}.docx`;

      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (e) {
      alert("Lỗi xuất Word: " + e.message);
    } finally {
      btnExportDocx.innerHTML = originalText;
      btnExportDocx.disabled = false;
      lucide.createIcons();
    }
  });

  // 8. MODAL HỒ SƠ CÔNG TY
  function openProfileModal() {
    modalProfile.classList.remove("hidden");
  }

  btnOpenProfile.addEventListener("click", openProfileModal);
  btnEditBenAFast.addEventListener("click", openProfileModal);

  modalProfileClose.addEventListener("click", () => {
    modalProfile.classList.add("hidden");
  });

  btnSaveProfile.addEventListener("click", async () => {
    const updated = {
      ten_to_chuc: profTen.value,
      ma_so_thue: profMST.value,
      dia_chi: profDiaChi.value,
      dai_dien: profDaiDien.value,
      chuc_vu: profChucVu.value,
      so_cccd_nguoi_dai_dien: profCCCD.value,
      ngay_cap_cccd_dai_dien: profNgayCap.value,
      so_tai_khoan: profSTK.value
    };

    try {
      const res = await fetch("/api/company-profile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updated)
      });
      if (res.ok) {
        companyProfile = updated;
        updateCompanyProfileUI();
        modalProfile.classList.add("hidden");
        alert("Đã cập nhật hồ sơ Bên A thành công!");
      }
    } catch (e) {
      alert("Lỗi lưu hồ sơ: " + e.message);
    }
  });

  // Chuyển đổi tab B2C / C2C
  const tabB2C = document.getElementById("tabB2C");
  const tabC2C = document.getElementById("tabC2C");
  const cardBenAInfo = document.getElementById("cardBenAInfo");

  tabB2C.addEventListener("click", () => {
    tabB2C.classList.add("active");
    tabC2C.classList.remove("active");
    cardBenAInfo.classList.remove("hidden");
  });

  tabC2C.addEventListener("click", () => {
    tabC2C.classList.add("active");
    tabB2C.classList.remove("active");
    alert("Chế độ C2C: Bạn có thể mở 'Hồ sơ Bên A' ở góc trên để đổi nhanh thông tin Bên A thành cá nhân thứ nhất!");
  });
});
