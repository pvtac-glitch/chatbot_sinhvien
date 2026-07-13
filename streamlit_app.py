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

# 3. NÚT BẤM VÀ XỬ LÝ
if st.button("🚀 Xem câu trả lời"):
    if not cau_hoi.strip():
        st.warning("Em vui lòng nhập câu hỏi trước khi bấm tìm kiếm nhé!")
    else:
        with st.spinner("Đang tra cứu..."):
            try:
                selected_sheet = MENU_OPTIONS[lua_chon_tieng_viet]
                df = pd.read_excel(filepath, sheet_name=selected_sheet, engine="openpyxl")
                
                # Chuyển tên cột về chữ thường để không bị lỗi lệch pha viết hoa/thường
                df.columns = [str(col).strip().lower() for col in df.columns]
                
                # Tách từ khóa sinh viên nhập thành danh sách các từ
                keywords = [kw.lower() for kw in cau_hoi.split() if len(kw) > 1]
                
                st.subheader("📝 Câu trả lời dành cho em:")
                found = False
                
                for idx, row in df.iterrows():
                    # Chuyển toàn bộ nội dung của hàng thành chữ thường để tìm kiếm
                    row_text = " ".join(str(val).lower() for val in row.values)
                    
                    # Bộ lọc CHẶT: Phải chứa ĐẦY ĐỦ các từ khóa sinh viên gõ thì mới xử lý
                    if all(kw in row_text for kw in keywords):
                        # THÀNH CÔNG: Tìm thấy hàng khớp chặt chẽ
                        
                        # Thử tìm xem trong sheet có cột nào tên là "câu trả lời", "nội dung" hoặc "học phí/số tiền" không
                        ans_col = [col for col in df.columns if "trả lời" in col or "nội dung" in col or "đáp án" in col]
                        
                        if ans_col:
                            # Nếu có cột câu trả lời riêng, CHỈ IN đúng ô đó ra
                            answer_text = row[ans_col[0]]
                            st.info(f"💡 **Trả lời:** {answer_text}")
                        else:
                            # Nếu file Excel hiện tại chưa chia cột câu trả lời, ta nhặt các thông tin cốt lõi nhất
                            clean_items = [f"**{str(k).upper()}:** {str(v)}" for k, v in row.dropna().to_dict().items() if "unnamed" not in str(k).lower()]
                            # Chỉ lấy tối đa 2 thông tin đầu tiên của dòng đó (Siêu ngắn gọn)
                            short_ans = "  \n".join(clean_items[:2])
                            st.info(f"📌 {short_ans}")
                            
                        found = True
                        break # Tìm thấy câu chuẩn nhất rồi thì dừng lại luôn, không in các dòng dưới nữa
                
                if not found:
                    st.error("Không tìm thấy thông tin phù hợp với từ khóa này. Em hãy thử nhập từ khóa khác ngắn hơn nhé!")
                    
            except Exception as e:
                st.error(f"Hệ thống gặp lỗi nhỏ khi lọc danh mục này: {e}")
