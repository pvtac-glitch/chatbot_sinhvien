import streamlit as st
import pandas as pd

# Cấu hình giao diện hiển thị trên điện thoại/máy tính
st.set_page_config(page_title="Hỗ trợ Sinh viên Khoa Ngoại ngữ", page_icon="🤖", layout="centered")

st.title("🤖 TRỢ LÝ ẢO KHOA NGOẠI NGỮ")
st.write("Chào em! Hãy chọn lĩnh vực thắc mắc, nhập câu hỏi và bấm nút để tra cứu thông tin tự động nhé.")

filepath = "DULIEUKHOANGOAINGU.xlsx"

# 1. KHAI BÁO BẢNG ÁNH XẠ CHÍNH XÁC
MENU_OPTIONS = {
    "Tổng quát về Khoa": "TONGQUAT",
    "Chương trình đào tạo": "CHUONGTRINHDAOTAO",
    "Học phí": "HOCPHI",
    "Học bổng": "HOCBONG",
    "Thực tập": "THUCTAP",
    "Câu lạc bộ": "CAULACBO"
}

# 2. Ô CHỌN LĨNH VỰC
lua_chon_tieng_viet = st.selectbox(
    "👉 Bước 1: Chọn lĩnh vực em muốn hỏi:",
    list(MENU_OPTIONS.keys())
)

# 3. Ô NHẬP CÂU HỎI
cau_hoi = st.text_input("👉 Bước 2: Nhập từ khóa hoặc câu hỏi của em:", placeholder="Ví dụ: sư phạm tiếng anh, học bổng, ielts...")

# 4. NÚT BẤM XỬ LÝ
if st.button("🚀 Xem câu trả lời"):
    if not cau_hoi.strip():
        st.warning("Em vui lòng nhập câu hỏi trước khi bấm tìm kiếm nhé!")
    else:
        with st.spinner("Đang lục tìm dữ liệu..."):
            try:
                selected_sheet = MENU_OPTIONS[lua_chon_tieng_viet]
                
                # Ép kiểu engine="openpyxl" để đọc file xlsx chuẩn xác
                df = pd.read_excel(filepath, sheet_name=selected_sheet, engine="openpyxl")
                
                # Tìm kiếm thông tin dựa trên từ khóa sinh viên gõ
                keywords = [kw.lower() for kw in cau_hoi.split() if len(kw) > 1]
                results = []
                
                for idx, row in df.iterrows():
                    row_text = " ".join(str(val).lower() for val in row.values)
                    if any(kw in row_text for kw in keywords):
                        results.append(row)
                
                st.subheader("📝 Kết quả tìm kiếm:")
                if results:
                    st.success(f"Tìm thấy {len(results)} thông tin liên quan đến câu hỏi của em:")
                    for res in results:
                        with st.container():
                            res_dict = res.dropna().to_dict()
                            for k, v in res_dict.items():
                                if "unnamed" not in str(k).lower():
                                    st.write(f"**{k}:** {v}")
                            st.markdown("---")
                else:
                    st.info("Không tìm thấy dòng khớp chính xác từng từ. Em có thể xem bảng dữ liệu tổng quan dưới đây:")
                    st.dataframe(df)
                    
            except Exception as e:
                st.error(f"Hệ thống gặp lỗi nhỏ khi đọc danh mục này: {e}")
