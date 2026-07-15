import streamlit as st
import google.generativeai as genai
import pandas as pd
st.set_page_config(
    page_title="Trợ lý AI Khoa Ngoại ngữ",
    page_icon="🤖",
    layout="centered", # Giúp giao diện co giãn vừa vặn màn hình dọc điện thoại
    initial_sidebar_state="collapsed" # Ẩn thanh menu thừa bên cạnh nếu có
)
# ==========================================
# 1. CẤU HÌNH API KEY (Lấy từ Streamlit Secrets)
# ==========================================
try:
    # Đảm bảo bạn đã điền API Key dạng AIzaSy... vào file .streamlit/secrets.toml
    # Cấu trúc file secrets.toml: GEMINI_API_KEY = "AIzaSy..."
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except KeyError:
    st.error("Chưa cấu hình GEMINI_API_KEY trong Streamlit Secrets!")
    st.stop()

# ==========================================
# 2. ĐỊNH NGHĨA DANH MỤC SHEET
# ==========================================
filepath = "DULIEUKHOANGOAINGU.xlsx"

MENU_OPTIONS = {
    "Tổng quát về Khoa": "TONGQUAT",
    "Chương trình đào tạo": "CHUONGTRINHDAOTAO",
    "Học phí": "HOCPHI",
    "Học bổng": "HOCBONG",
    "Thực tập": "THUCTAP",
    "Câu lạc bộ": "CAULACBO"
}

# Hàm tối ưu hóa việc đọc dữ liệu theo từng sheet và lưu vào cache
@st.cache_data
def load_data_by_sheet(file_path, sheet_name):
    return pd.read_excel(file_path, sheet_name=sheet_name, engine="openpyxl")


# ==========================================
# 3. GIAO DIỆN ỨNG DỤNG (UI)
# ==========================================
st.title("Chatbot Hỗ Trợ Sinh Viên 🎓")
st.subheader("🤖 TRỢ LÝ AI KHOA NGOẠI NGỮ")

st.write(
    "Chào em! Hãy chọn lĩnh vực thắc mắc, nhập câu hỏi. "
    "AI sẽ tự động đọc dữ liệu khoa và tổng hợp câu trả lời chính xác nhất cho em."
)

lua_chon_tieng_viet = st.selectbox(
    "👉 Bước 1: Chọn lĩnh vực em muốn hỏi:",
    list(MENU_OPTIONS.keys())
)

cau_hoi = st.text_input(
    "👉 Bước 2: Nhập câu hỏi của em:",
    placeholder="Ví dụ: Khoa có bao nhiêu ngành đào tạo?"
)

# ==========================================
# 4. XỬ LÝ KHI BẤM NÚT HỎI AI
# ==========================================
if st.button("🚀 Hỏi Trợ Lý AI"):

    if not cau_hoi.strip():
        st.warning("Em vui lòng nhập câu hỏi trước nhé!")
        st.stop()

    with st.spinner("🤖 AI đang đọc dữ liệu và xử lý..."):
        try:
            # Lấy tên sheet tương ứng từ lựa chọn
            selected_sheet = MENU_OPTIONS[lua_chon_tieng_viet]
            
            # Đọc dữ liệu từ cache (tối ưu hiệu năng)
            df = load_data_by_sheet(filepath, selected_sheet)
            data_context = df.to_string(index=False)

            # Cấu hình Prompt cho AI
            prompt_content = f"""
Bạn là Trợ lý AI của Khoa Ngoại ngữ.
Chỉ được phép trả lời dựa trên dữ liệu được cung cấp dưới đây.
Không được tự bịa đặt thông tin nằm ngoài dữ liệu.
Nếu không tìm thấy câu trả lời trong dữ liệu thì hãy trả lời chính xác câu sau:
"Xin lỗi em, hiện tại Thầy/Cô chưa tìm thấy thông tin này trong cơ sở dữ liệu của Khoa. Em vui lòng liên hệ Văn phòng Khoa để được hỗ trợ thêm."

DỮ LIỆU KHOA CUNG CẤP:
{data_context}

CÂU HỎI CỦA SINH VIÊN:
{cau_hoi}

Yêu cầu câu trả lời:
- Trả lời hoàn toàn bằng tiếng Việt.
- Xưng hô lịch sự (Thầy/Cô - Em).
- Ngắn gọn, rõ ràng, dễ đọc trên điện thoại.
- Nếu có danh sách thông tin, bắt buộc dùng gạch đầu dòng.
"""

            # Gọi Gemini API thông qua thư viện chính thức thay vì requests
            # Sử dụng model gemini-2.5-flash tối tân và tiết kiệm phí
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(prompt_content)

            # Hiển thị kết quả ra giao diện
            if response.text:
                st.subheader("📝 Câu trả lời từ Trợ lý AI")
                st.success(response.text)
            else:
                st.error("Không nhận được phản hồi từ AI. Vui lòng thử lại!")

        except FileNotFoundError:
            st.error(f"Không tìm thấy file dữ liệu: {filepath}. Vui lòng kiểm tra lại đường dẫn file trên GitHub.")
        except Exception as e:
            # Bắt các lỗi phân tích cú pháp hoặc lỗi hệ thống khác
            st.error(f"Hệ thống gặp lỗi: {str(e)}")
