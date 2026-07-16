import streamlit as st
import google.generativeai as genai
import pandas as pd
import time  # Thêm thư viện thời gian

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
    "Giảng viên-Nhân viên": "GIANGVIEN",
    "Chương trình đào tạo": "CHUONGTRINHDAOTAO",
    "Ngoại ngữ 2-Tin học": "NGOAINGUTINHOC",
    "Nghiên cứu Khoa học": "NGHIENCUUKHOAHOC",
    "Học phí": "HOCPHI",
    "Học bổng": "HOCBONG",
    "Thực tế-Thực tập": "THUCTAP",
    "Ngoại khóa-Câu lạc bộ": "NGOAIKHOACAULACBO",
    "Công tác Xã hội-Đoàn-Hội-Thể thao": "CONGTACXAHOI",
    "Tuyển sinh": "TUYENSINH"
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
# KHỞI TẠO BỘ NHỚ ĐỆM (CACHE) & COOLDOWN TRONG SESSION
# ==========================================
if "last_ask_time" not in st.session_state:
    st.session_state["last_ask_time"] = 0.0

if "qa_cache" not in st.session_state:
    # Lưu các câu hỏi đã có câu trả lời để tránh gọi API trùng lặp
    st.session_state["qa_cache"] = {} 


# ==========================================
# XỬ LÝ KHI BẤM NÚT HỎI AI (ĐÃ TỐI ƯU)
# ==========================================
if st.button("🚀 Hỏi Trợ Lý AI"):

    if not cau_hoi.strip():
        st.warning("Em vui lòng nhập câu hỏi trước nhé!")
        st.stop()

    # --- 1. KIỂM TRA COOLDOWN (CHỐNG SPAM) ---
    current_time = time.time()
    time_passed = current_time - st.session_state["last_ask_time"]
    cooldown_limit = 10  # Số giây sinh viên phải đợi giữa 2 câu hỏi

    if time_passed < cooldown_limit:
        remaining = int(cooldown_limit - time_passed)
        st.warning(f"⚡ Em hỏi nhanh quá! Vui lòng đợi {remaining} giây nữa để hệ thống xử lý nhé.")
        st.stop()

    # Cập nhật lại thời gian hỏi mới nhất
    st.session_state["last_ask_time"] = current_time

    # --- 2. KIỂM TRA TRÙNG CÂU HỎI (TIẾT KIỆM QUOTA) ---
    standardized_question = cau_hoi.strip().lower()
    
    # Tạo một "khóa" gồm lĩnh vực + câu hỏi để kiểm tra trong bộ nhớ đệm
    cache_key = f"{lua_chon_tieng_viet}_{standardized_question}"

    if cache_key in st.session_state["qa_cache"]:
        # Nếu đã có trong cache, hiển thị ngay lập tức, tốn 0đ và 0ms gọi API
        cached_answer = st.session_state["qa_cache"][cache_key]
        st.subheader("📝 Câu trả lời từ Trợ lý AI (Tối ưu từ hệ thống)")
        st.success(cached_answer)
        st.info("💡 Câu trả lời này được lấy từ bộ nhớ đệm để tăng tốc độ phản hồi.")
        st.stop()

    # --- 3. GỌI GEMINI API NẾU LÀ CÂU HỎI MỚI ---
    with st.spinner("🤖 AI đang đọc dữ liệu và xử lý..."):
        try:
            selected_sheet = MENU_OPTIONS[lua_chon_tieng_viet]
            df = load_data_by_sheet(filepath, selected_sheet)
            data_context = df.to_string(index=False)

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

            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(prompt_content)

            if response.text:
                answer = response.text
                
                # Lưu câu trả lời mới vào cache để lần sau dùng lại
                st.session_state["qa_cache"][cache_key] = answer

                st.subheader("📝 Câu trả lời từ Trợ lý AI")
                st.success(answer)
            else:
                st.error("Không nhận được phản hồi từ AI. Vui lòng thử lại!")

        except FileNotFoundError:
            st.error(f"Không tìm thấy file dữ liệu: {filepath}.")
        except Exception as e:
            # Xử lý thông minh khi gặp lỗi quá hạn mức (Error 429) hoặc lỗi khác
            err_str = str(e)
            if "429" in err_str or "ResourceExhausted" in err_str:
                st.error(
                    "⚠️ Hệ thống Trợ lý AI đang có số lượng truy cập quá tải. "
                    "Để nhận thông tin ngay lập tức, em vui lòng liên hệ trực tiếp Văn phòng Khoa "
                    "hoặc thử lại sau 1-2 phút nhé!"
                )
            else:
                st.error(f"Hệ thống gặp lỗi: {err_str}")
