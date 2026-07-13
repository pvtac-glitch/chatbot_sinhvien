import streamlit as st
import pandas as pd
import requests
import json

# Cấu hình giao diện gọn gàng cho điện thoại
st.set_page_config(page_title="Hỗ trợ Sinh viên Khoa Ngoại ngữ", page_icon="🤖", layout="centered")

st.title("🤖 TRỢ LÝ AI KHOA NGOẠI NGỮ")
st.write("Chào em! Hãy chọn lĩnh vực thắc mắc, nhập câu hỏi. AI sẽ tự động đọc dữ liệu khoa và tổng hợp câu trả lời chính xác nhất cho em.")

filepath = "DULIEUKHOANGOAINGU.xlsx"

# GIỮ NGUYÊN MÃ KHÓA AQ CHẠY ỔN ĐỊNH CỦA BẠN
GEMINI_API_KEY = "AQ.Ab8RN6J9IeeYDOcxFSZqdh1ZS6zVlwngUwYchFCtg2f3qvbhgA"

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
    else:
        with st.spinner("🤖 AI đang đọc dữ liệu và tổng hợp câu trả lời..."):
            try:
                # 1. Đọc đúng sheet dữ liệu được chọn
                selected_sheet = MENU_OPTIONS[lua_chon_tieng_viet]
                df = pd.read_excel(filepath, sheet_name=selected_sheet, engine="openpyxl")
                
                # 2. Gom toàn bộ bảng dữ liệu thành văn bản
                data_context = df.to_string(index=False)
                
                # 3. Xây dựng yêu cầu gửi cho AI (Prompt)
                prompt_content = f"""
                Bạn là một trợ lý ảo thông minh, thân thiện của Khoa Ngoại ngữ. 
                Nhiệm vụ của bạn là dựa vào BẢNG DỮ LIỆU gốc dưới đây để trả lời câu hỏi của sinh viên một cách chính xác, ngắn gọn, đầy đủ thông tin, không bỏ sót chi tiết quan trọng và không được bịa đặt thông tin nằm ngoài bảng.

                --- BẢNG DỮ LIỆU KHOA CUNG CẤP ---
                {data_context}
                ---------------------------------

                👉 CÂU HỎI CỦA SINH VIÊN: "{cau_hoi}"

                Hãy trả lời bằng tiếng Việt, xưng hô là "Thầy/Cô" hoặc "Trợ lý ảo" và gọi sinh viên là "em". Trình bày rõ ràng, sử dụng các dấu gạch đầu dòng cho dễ đọc trên điện thoại.
                """
                
                # 4. GỬI ĐÚNG GIAO THỨC HTTP
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
                
                headers = {
                    "Authorization": f"Bearer {GEMINI_API_KEY}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "contents": [{
                        "parts": [{"text": prompt_content}]
                    }]
                }
                
                # SỬA LỖI TẠI ĐÂY: Ép dữ liệu phải đóng gói dưới dạng UTF-8 để nhận diện tiếng Việt có dấu
                data_payload = json.dumps(payload, ensure_ascii=False).encode('utf-8')
                
                # Thực hiện gọi API gửi đi dữ liệu đã chuẩn hóa font chữ
                response = requests.post(url, headers=headers, data=data_payload)
                result_json = response.json()
                
                # 5. Kiểm tra kết quả trả về
                if response.status_code == 200:
                    answer = result_json['candidates'][0]['content']['parts'][0]['text']
                    st.subheader("📝 Câu trả lời từ Trợ lý AI:")
                    st.info(answer)
                else:
                    st.error(f"Google từ chối xử lý (Mã lỗi {response.status_code}): {result_json.get('error', {}).get('message', 'Không rõ nguyên nhân')}")
                    
            except Exception as e:
                st.error(f"Hệ thống gặp lỗi kết nối: {e}")
