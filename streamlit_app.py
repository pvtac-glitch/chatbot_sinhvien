import streamlit as st
import pandas as pd

# Cấu hình giao diện gọn gàng cho điện thoại
st.set_page_config(page_title="Hỗ trợ Sinh viên Khoa Ngoại ngữ", page_icon="🤖", layout="centered")

st.title("🤖 TRỢ LÝ ẢO KHOA NGOẠI NGỮ")
st.write("Chào em! Hãy chọn lĩnh vực thắc mắc, nhập từ khóa câu hỏi và bấm nút để xem câu trả lời ngắn gọn.")

filepath = "DULIEUKHOANGOAINGU.xlsx"

# 1. BẢNG ÁNH XẠ DANH MỤC
MENU_OPTIONS = {
    "Tổng quát về Khoa": "TONGQUAT",
    "Chương trình đào tạo": "CHUONGTRINHDAOTAO",
    "Học phí": "HOCPHI",
    "Học bổng": "HOCBONG",
    "Thực tập": "THUCTAP",
    "Câu lạc bộ": "CAULACBO"
}

# 2. GIAO DIỆN CHỌN VÀ NHẬP
lua_chon_tieng_viet = st.selectbox("👉 Bước 1: Chọn lĩnh vực em muốn hỏi:", list(MENU_OPTIONS.keys()))
cau_hoi = st.text_input("👉 Bước 2: Nhập từ khóa câu hỏi của em:", placeholder="Ví dụ: sư phạm tiếng anh, ielts, học bổng...")

# Hàm hỗ trợ cắt ngắn văn bản dài thành các dòng chọn lọc
def shorten_text(text, max_lines=5):
    if not isinstance(text, str):
        return str(text)
    # Tách đoạn văn thành các dòng dựa trên dấu xuống dòng hoặc dấu chấm
    lines = [line.strip() for line in text.replace('.', '.\n').split('\n') if line.strip()]
    if len(lines) <= max_lines:
        return "\n\n".join(lines)
    else:
        return "\n\n".join(lines[:max_lines]) + "\n\n... *(Em xem thêm trong văn bản hướng dẫn nhé)*"

# 3. NÚT BẤM VÀ XỬ LÝ
if st.button("🚀 Xem câu trả lời"):
    if not cau_hoi.strip():
        st.warning("Em vui lòng nhập câu hỏi trước khi bấm tìm kiếm nhé!")
    else:
        with st.spinner("Đang tra cứu..."):
            try:
                selected_sheet = MENU_OPTIONS[lua_chon_tieng_viet]
                df = pd.read_excel(filepath, sheet_name=selected_sheet, engine="openpyxl")
                
                keywords = [kw.lower() for kw in cau_hoi.split() if len(kw) > 1]
                match_rows = []
                
                for idx, row in df.iterrows():
                    row_text = " ".join(str(val).lower() for val in row.values)
                    if any(kw in row_text for kw in keywords):
                        match_rows.append(row)
                
                st.subheader("📝 Câu trả lời rút gọn dành cho em:")
                
                if match_rows:
                    for row in match_rows:
                        clean_data = {str(k): str(v) for k, v in row.dropna().to_dict().items() if "unnamed" not in str(k).lower()}
                        
                        # --- XỬ LÝ HIỂN THỊ CHỌN LỌC THEO TỪNG DANH MỤC ---
                        if selected_sheet == "HOCPHI" and "ngành" in clean_data and "học phí" in clean_data:
                            st.info(f"📚 Ngành: **{clean_data['ngành']}** \n\n 💰 Học phí: **{clean_data['học phí']}**")
                            
                        elif selected_sheet == "HOCBONG" and "loại học bổng" in clean_data and "số tiền" in clean_data:
                            st.info(f"🎁 Học bổng: **{clean_data['loại học bổng']}** \n\n 🎯 Điều kiện: {clean_data.get('điều kiện', 'Theo quy định')} \n\n 💵 Số tiền: **{clean_data['số tiền']}**")
                            
                        elif selected_sheet == "THUCTAP" and "ngành" in clean_data:
                            st.info(f"📋 Thực tập ngành: **{clean_data['ngành']}** \n\n 📍 Địa điểm: {clean_data.get('địa điểm', 'Chưa rõ')} \n\n ⏳ Thời gian: **{clean_data.get('thời gian', '')}**")
                            
                        elif selected_sheet == "CAULACBO" and "tên câu lạc bộ" in clean_data:
                            st.info(f"🎯 **{clean_data['tên câu lạc bộ']}** \n\n 🕒 Thời gian: {clean_data.get('thời gian tổ chức', '')} \n\n 🚀 Mục tiêu: {clean_data.get('mục tiêu', '')}")
                        
                        else:
                            # Xử lý cho TONGQUAT và CHUONGTRINHDAOTAO (Văn bản siêu dài)
                            keys = list(clean_data.keys())
                            if len(keys) >= 2:
                                tieu_de = clean_data[keys[0]]
                                noi_dung_rut_gon = shorten_text(clean_data[keys[1]], max_lines=4)
                                st.info(f"📌 **{tieu_de}** \n\n {noi_dung_rut_gon}")
                            elif len(keys) == 1:
                                st.info(f"📌 {shorten_text(clean_data[keys[0]], max_lines=4)}")
                else:
                    st.error("Không tìm thấy thông tin phù hợp. Em hãy thử đổi từ khóa ngắn hơn xem sao nhé!")
                    
            except Exception as e:
                st.error(f"Hệ thống gặp lỗi nhỏ khi đọc danh mục này: {e}")
