import streamlit as st
import pandas as pd
import requests

# =========================
# CẤU HÌNH GIAO DIỆN
# =========================
st.set_page_config(
    page_title="Hỗ trợ Sinh viên Khoa Ngoại ngữ",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 TRỢ LÝ AI KHOA NGOẠI NGỮ")

st.write(
    "Chào em! Hãy chọn lĩnh vực thắc mắc, nhập câu hỏi. "
    "AI sẽ tự động đọc dữ liệu khoa và tổng hợp câu trả lời chính xác nhất cho em."
)

# =========================
# FILE DỮ LIỆU
# =========================
filepath = "DULIEUKHOANGOAINGU.xlsx"

# =========================
# API KEY GEMINI
# =========================

# Tạm thời dùng trực tiếp
GEMINI_API_KEY = "AQ.Ab8RN6J9IeeYDOcxFSZqdh1ZS6zVlwngUwYchFCtg2f3qvbhgA"

# Sau này nên dùng:
# GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

# =========================
# DANH MỤC
# =========================
MENU_OPTIONS = {
    "Tổng quát về Khoa": "TONGQUAT",
    "Chương trình đào tạo": "CHUONGTRINHDAOTAO",
    "Học phí": "HOCPHI",
    "Học bổng": "HOCBONG",
    "Thực tập": "THUCTAP",
    "Câu lạc bộ": "CAULACBO"
}

# =========================
# GIAO DIỆN NHẬP DỮ LIỆU
# =========================

lua_chon_tieng_viet = st.selectbox(
    "👉 Bước 1: Chọn lĩnh vực em muốn hỏi:",
    list(MENU_OPTIONS.keys())
)

cau_hoi = st.text_input(
    "👉 Bước 2: Nhập câu hỏi của em:",
    placeholder="Ví dụ: Khoa có bao nhiêu ngành đào tạo?"
)

# =========================
# NÚT HỎI AI
# =========================

if st.button("🚀 Hỏi Trợ Lý AI"):

    if not cau_hoi.strip():
        st.warning("Em vui lòng nhập câu hỏi trước nhé!")
        st.stop()

    with st.spinner("🤖 AI đang đọc dữ liệu..."):

        try:

            # -------------------------
            # ĐỌC SHEET ĐƯỢC CHỌN
            # -------------------------
            selected_sheet = MENU_OPTIONS[lua_chon_tieng_viet]

            df = pd.read_excel(
                filepath,
                sheet_name=selected_sheet,
                engine="openpyxl"
            )

            data_context = df.to_string(index=False)

            # -------------------------
            # PROMPT
            # -------------------------
            prompt_content = f"""
Bạn là Trợ lý AI của Khoa Ngoại ngữ.

Chỉ được phép trả lời dựa trên dữ liệu được cung cấp.

Không được bịa đặt thông tin.

Nếu không tìm thấy câu trả lời trong dữ liệu thì trả lời:

"Xin lỗi em, hiện tại Thầy/Cô chưa tìm thấy thông tin này trong cơ sở dữ liệu của Khoa. Em vui lòng liên hệ Văn phòng Khoa để được hỗ trợ thêm."

DỮ LIỆU:

{data_context}

CÂU HỎI:

{cau_hoi}

Yêu cầu:
- Trả lời bằng tiếng Việt.
- Xưng hô lịch sự.
- Ngắn gọn.
- Dễ đọc trên điện thoại.
- Nếu có danh sách thì dùng gạch đầu dòng.
"""

            # -------------------------
            # GỌI GEMINI API
            # -------------------------
            url = (
                "https://generativelanguage.googleapis.com/v1beta/"
                f"models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
            )

            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt_content
                            }
                        ]
                    }
                ]
            }

            headers = {
                "Content-Type": "application/json"
            }

            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=60
            )

            # -------------------------
            # KIỂM TRA KẾT QUẢ
            # -------------------------
            if response.status_code == 200:

                result = response.json()

                answer = (
                    result["candidates"][0]
                    ["content"]["parts"][0]
                    ["text"]
                )

                st.subheader("📝 Câu trả lời từ Trợ lý AI")

                st.success(answer)

            else:

                try:
                    error_json = response.json()
                    error_msg = error_json["error"]["message"]
                except Exception:
                    error_msg = response.text

                st.error(
                    f"Lỗi Gemini API ({response.status_code})\n\n{error_msg}"
                )

        except FileNotFoundError:
            st.error("Không tìm thấy file DULIEUKHOANGOAINGU.xlsx")

        except Exception as e:
            st.error(f"Hệ thống gặp lỗi:\n\n{str(e)}")
