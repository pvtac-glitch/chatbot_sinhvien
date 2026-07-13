import streamlit as st
import pandas as pd
import requests
import json

st.set_page_config(page_title="Hỗ trợ Sinh viên Khoa Ngoại ngữ", page_icon="🤖", layout="centered")

st.title("🤖 TRỢ LÝ AI KHOA NGOẠI NGỮ")
st.write("Chào em! Hãy chọn lĩnh vực thắc mắc, nhập câu hỏi để AI tổng hợp dữ liệu nhé.")

filepath = "DULIEUKHOANGOAINGU.xlsx"

# GIỮ NGUYÊN MÃ AQ. CỦA BẠN
GEMINI_API_KEY = "AQ.Ab8RN6J9IeeYDOcxFSZqdh1ZS6zVlwngUwYchFCtg2f3qvbhgA"

MENU_OPTIONS = {
    "Tổng quát về Khoa": "TONGQUAT",
    "Chương trình đào tạo": "CHUONGTRINHDAOTAO",
    "Học phí": "HOCPHI",
    "Học bổng": "HOCBONG",
    "Thực tập": "THUCTAP",
    "Câu lạc bộ": "CAULACBO"
}

lua_chon_tieng_viet = st.selectbox("👉 Chọn lĩnh vực:", list(MENU_OPTIONS.keys()))
cau_hoi = st.text_input("👉 Nhập câu hỏi:")

if st.button("🚀 Hỏi Trợ Lý AI"):
    if not cau_hoi.strip():
        st.warning("Em vui lòng nhập câu hỏi nhé!")
    else:
        with st.spinner("🤖 AI đang tổng hợp câu trả lời..."):
            try:
                selected_sheet = MENU_OPTIONS[lua_chon_tieng_viet]
                df = pd.read_excel(filepath, sheet_name=selected_sheet, engine="openpyxl")
                data_context = df.to_string(index=False)
                
                prompt_content = f"""
                Bạn là một trợ lý ảo thông minh của Khoa Ngoại ngữ. 
                Hãy dựa vào BẢNG DỮ LIỆU dưới đây để trả lời câu hỏi của sinh viên một cách chính xác, ngắn gọn, đầy đủ thông tin, không bỏ sót chi tiết.
                Nếu hỏi số lượng (ví dụ: bao nhiêu ngành), hãy quét toàn bộ để đếm và liệt kê đầy đủ.

                --- BẢNG DỮ LIỆU ---
                {data_context}
                --------------------
                👉 CÂU HỎI: "{cau_hoi}"
                Trả lời bằng tiếng Việt, xưng hô Thầy/Cô và gọi sinh viên là em.
                """
                
                # CHUYỂN SANG ĐƯỜNG TRUYỀN HỖ TRỢ ĐẦU MÃ AQ. (V1 BETA OAUTH)
                url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
                
                headers = {
                    "Authorization": f"Bearer {GEMINI_API_KEY}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "contents": [{
                        "parts": [{"text": prompt_content}]
                    }]
                }
                
                response = requests.post(url, headers=headers, json=payload)
                result_json = response.json()
                
                if response.status_code == 200:
                    answer = result_json['candidates'][0]['content']['parts'][0]['text']
                    st.subheader("📝 Câu trả lời từ Trợ lý AI:")
                    st.info(answer)
                else:
                    st.error(f"Lỗi hệ thống ({response.status_code}): {result_json.get('error', {}).get('message', 'Vui lòng kiểm tra lại loại Key')}")
                    
            except Exception as e:
                st.error(f"Lỗi kết nối: {e}")
