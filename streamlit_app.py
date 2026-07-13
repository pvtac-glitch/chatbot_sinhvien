import streamlit as st
import pandas as pd

# Cấu hình giao diện gọn gàng cho điện thoại
st.set_page_config(page_title="Hỗ trợ Sinh viên Khoa Ngoại ngữ", page_icon="🤖", layout="centered")

st.title("🤖 TRỢ LÝ ẢO KHOA NGOẠI NGỮ")
st.write("Chào em! Hãy chọn lĩnh vực thắc mắc, nhập câu hỏi và bấm nút để xem câu trả lời ngắn gọn.")

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
cau_hoi = st.text_input("👉 Bước 2: Nhập câu hỏi hoặc từ khóa của em:", placeholder="Ví dụ: điều kiện xét học bổng...")

# 3. NÚT BẤM VÀ XỬ LÝ
if st.button("🚀 Xem câu trả lời"):
    if not cau_hoi.strip():
        st.warning("Em vui lòng nhập câu hỏi trước khi bấm tìm kiếm nhé!")
    else:
        with st.spinner("Đang tra cứu dữ liệu..."):
            try:
                selected_sheet = MENU_OPTIONS[lua_chon_tieng_viet]
                df = pd.read_excel(filepath, sheet_name=selected_sheet, engine="openpyxl")
                
                # Loại bỏ các cột trống hoàn toàn hoặc vô danh (Unnamed)
                df = df.loc[:, ~df.columns.str.contains('^Unnamed', case=False, na=False)]
                
                # Tách câu hỏi của sinh viên thành các từ khóa có nghĩa (bỏ các từ quá ngắn)
                keywords = [kw.lower() for kw in cau_hoi.split() if len(kw) > 1]
                
                best_row = None
                max_score = 0
                
                # Quét qua từng dòng để tính điểm trùng khớp từ khóa
                for idx, row in df.iterrows():
                    row_text = " ".join(str(val).lower() for val in row.values)
                    
                    # Đếm xem dòng này chứa bao nhiêu từ khóa sinh viên gõ
                    score = sum(1 for kw in keywords if kw in row_text)
                    
                    if score > max_score:
                        max_score = score
                        best_row = row
                
                st.subheader("📝 Câu trả lời dành cho em:")
                
                # Nếu tìm thấy dòng có điểm trùng khớp (lớn hơn 0)
                if best_row is not None and max_score > 0:
                    clean_dict = best_row.dropna().to_dict()
                    cols = list(clean_dict.keys())
                    
                    if len(cols) >= 2:
                        # LẤY CỘT ĐẦU VÀ CỘT CUỐI: Cách lọc siêu gọn gàng
                        tieu_de = clean_dict[cols[0]]
                        cau_tra_loi = clean_dict[cols[-1]] # Lấy giá trị cột cuối cùng của dòng đó
                        
                        st.info(f"📌 **{tieu_de}** \n\n 💡 **Trả lời:** {cau_tra_loi}")
                    else:
                        st.info(f"💡 **Trả lời:** {clean_dict[cols[0]]}")
                        
                else:
                    st.error("Không tìm thấy thông tin nào khớp. Em hãy thử nhập lại bằng các từ khóa ngắn gọn, chính xác hơn nhé (Ví dụ: 'học phí', 'xét học bổng', 'đăng ký thực tập').")
                    
            except Exception as e:
                st.error(f"Hệ thống gặp lỗi nhỏ khi xử lý danh mục này: {e}")
