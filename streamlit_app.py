import streamlit as st
import pandas as pd
from openai import OpenAI

# Cấu hình giao diện gọn gàng cho điện thoại
st.set_page_config(page_title="Hỗ trợ Sinh viên Khoa Ngoại ngữ", page_icon="🤖", layout="centered")

st.title("🤖 TRỢ LÝ AI KHOA NGOẠI NGỮ")
st.write("Chào em! Hãy chọn lĩnh vực thắc mắc, nhập câu hỏi. AI sẽ tự động đọc dữ liệu khoa và tổng hợp câu trả lời chính xác nhất cho em.")

filepath = "DULIEUKHOANGOAINGU.xlsx"

# CẤU HÌNH API AI (Sử dụng API Key dạng sk-... để tránh hoàn toàn lỗi 401 của Google)
AI_API_KEY = "ĐIỀN_MÃ_API_KEY_CỦA_BẠN"

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
cau_hoi = st.text_input("👉 Bước 2: Nhập câu hỏi của em:", placeholder="Ví dụ: Khoa có bao nhiêu ngành đào tạo?")

# 3. NÚT BẤM VÀ XỬ LÝ
if st.button("🚀 Hỏi Trợ Lý AI"):
    if not cau_hoi.strip():
        st.warning("Em vui lòng nhập câu hỏi trước khi bấm nhé!")
    elif AI_API_KEY == "AQ.Ab8RN6LhkpZ9CSho4ukq-Xunz8wghk4x_HvPzMNE2AgOZZm2kw":
        st.error("Thầy/Cô chưa điền mã API Key mới vào dòng số 14 kìa!")
    else:
        with st.spinner("🤖 AI đang đọc toàn bộ file dữ liệu và tổng hợp câu trả lời..."):
            try:
                # 1. Đọc đúng sheet dữ liệu được chọn
                selected_sheet = MENU_OPTIONS[lua_chon_tieng_viet]
                df = pd.read_excel(filepath, sheet_name=selected_sheet, engine="openpyxl")
                
                # 2. Gom toàn bộ bảng dữ liệu thành một chuỗi văn bản cho AI đọc
                data_context = df.to_string(index=False)
                
                # 3. Xây dựng yêu cầu nghiêm ngặt gửi cho AI xử lý (Prompt)
                prompt_content = f"""
                Bạn là một trợ lý ảo thông minh, thân thiện của Khoa Ngoại ngữ. 
                Nhiệm vụ của bạn là dựa vào BẢNG DỮ LIỆU gốc dưới đây để trả lời câu hỏi của sinh viên một cách chính xác, ngắn gọn, đầy đủ thông tin, không bỏ sót chi tiết quan trọng và không được bịa đặt thông tin nằm ngoài bảng.
                Nếu câu hỏi yêu cầu đếm số lượng hoặc liệt kê (ví dụ: có bao nhiêu ngành, bao nhiêu CLB), hãy quét toàn bộ bảng dữ liệu để đếm chính xác và liệt kê đầy đủ.

                --- BẢNG DỮ LIỆU KHOA CUNG CẤP ---
                {data_context}
                ---------------------------------

                👉 CÂU HỎI CỦA SINH VIÊN: "{cau_hoi}"

                Hãy trả lời bằng tiếng Việt, xưng hô là "Thầy/Cô" hoặc "Trợ lý ảo" và gọi sinh viên là "em". Trình bày rõ ràng, sử dụng các dấu gạch đầu dòng cho dễ đọc trên điện thoại.
                """
                
                # 4. Gọi mô hình Qwen thông qua chuẩn OpenAI Client
                client = OpenAI(
                    api_key=AI_API_KEY,
                    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1" # Đường truyền kết nối Qwen
                )
                
                completion = client.chat.completions.create(
                    model="qwen-plus", # Mô hình đọc hiểu văn bản và bảng biểu cực mạnh
                    messages=[
                        {"role": "user", "content": prompt_content}
                    ]
                )
                
                # 5. Hiển thị kết quả ra màn hình màu xanh đẹp mắt
                st.subheader("📝 Câu trả lời từ Trợ lý AI:")
                st.info(completion.choices[0].message.content)
                    
            except Exception as e:
                st.error(f"Hệ thống gặp lỗi khi kết nối với bộ não AI: {e}")
