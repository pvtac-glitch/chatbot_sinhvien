import streamlit as st
import google.generativeai as genai
import pandas as pd
import time  # Thêm thư viện thời gian
import re    # Thêm thư viện Regular Expression để lọc ký tự markdown

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
# 2. ĐỊNH NGHĨA DANH MỤC SHEET & ĐỌC FILE
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
# 3. ĐỊNH NGHĨA CSS TÙY CHỈNH THEO NHẬN DIỆN THƯƠNG HIỆU
# ==========================================
brand_css = """
<style>
/* Khung chứa câu trả lời */
.brand-answer-box {
    background-color: #F0F6FB !important;        /* Nền xanh biển cực nhạt, dịu mắt, sạch sẽ */
    border-left: 6px solid #005088 !important;   /* Thanh viền nhấn bên trái màu xanh biển đậm thương hiệu */
    border-radius: 8px !important;               /* Bo góc nhẹ nhàng hiện đại */
    padding: 24px !important;                    /* Khoảng cách đệm bên trong rộng rãi */
    margin-top: 20px !important;                 /* Khoảng cách với phần tử phía trên */
    margin-bottom: 20px !important;              /* Khoảng cách với phần tử phía dưới */
    box-shadow: 0 4px 12px rgba(0, 80, 136, 0.05) !important; /* Đổ bóng mờ nhẹ tông xanh tạo chiều sâu */
}

/* Thanh đầu đề của khung câu trả lời */
.brand-answer-header {
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
    border-bottom: 1.5px solid #D0E1FD !important; /* Đường kẻ ngang mờ phân chia tiêu đề */
    padding-bottom: 10px !important;
    margin-bottom: 15px !important;
}

/* Tiêu đề chính */
.brand-header-title {
    color: #004070 !important;                   /* Chữ màu xanh biển đậm */
    font-size: 1.25rem !important;               /* Cỡ chữ lớn hơn một chút */
    font-weight: 700 !important;                 /* Chữ in đậm nổi bật */
}

/* Nhãn hiển thị trạng thái Bộ nhớ đệm (Cache) */
.brand-badge {
    background-color: #E0ECFB !important;
    color: #005088 !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    padding: 4px 12px !important;
    border-radius: 20px !important;
    border: 1.5px solid #B0D0F5 !important;
}

/* Định dạng nội dung chi tiết bên trong câu trả lời */
.brand-answer-content {
    color: #102A43 !important;                   /* Chữ màu xanh Navy tối (Đảm bảo độ tương phản cao, cực kỳ dễ đọc) */
    font-size: 1.05rem !important;               /* Cỡ chữ tiêu chuẩn */
    line-height: 1.7 !important;                 /* Giúp văn bản thoáng, dễ theo dõi */
}

/* Khoảng cách cho các đoạn văn */
.brand-answer-content p {
    margin-bottom: 10px !important;
}

/* Định dạng danh sách dạng bullet point */
.brand-answer-content ul {
    margin-top: 8px !important;
    margin-bottom: 15px !important;
    padding-left: 20px !important;               /* Lùi lề cho danh sách */
    list-style-type: disc !important;            /* Đảm bảo luôn hiện chấm tròn */
}

.brand-answer-content li {
    margin-bottom: 6px !important;               /* Khoảng cách giữa các dòng trong danh sách */
    color: #102A43 !important;
}

/* Định dạng chữ nhấn mạnh (Bold) */
.brand-answer-content strong {
    color: #005088 !important;                   /* Điểm nhấn tên giảng viên/thông tin bằng màu xanh thương hiệu */
    font-weight: 700 !important;
}
</style>
"""
# Nhúng CSS tùy chỉnh vào ứng dụng
st.markdown(brand_css, unsafe_allow_html=True)


# ==========================================
# 4. HÀM TỰ ĐỘNG CHUYỂN ĐỔI MARKDOWN SANG HTML THƯƠNG HIỆU
# ==========================================
def display_brand_answer(raw_text, title="Câu trả lời từ Trợ lý AI", is_cached=False):
    """
    Hàm nhận diện cấu trúc văn bản trả về của Gemini (danh sách, in đậm) 
    và đóng gói lại thành giao diện chuẩn xanh nhận diện thương hiệu của Khoa.
    """
    lines = raw_text.split("\n")
    html_lines = []
    in_list = False
    
    for line in lines:
        line_stripped = line.strip()
        
        # Nếu dòng trống, kết thúc danh sách nếu có
        if not line_stripped:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            continue
            
        # Kiểm tra nếu là dòng gạch đầu dòng (bullet point)
        if line_stripped.startswith("* ") or line_stripped.startswith("- "):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            # Lọc bỏ ký tự bullet mặc định ở đầu
            content = line_stripped[2:]
            # Chuyển đổi cú pháp in đậm **thành phần** -> <strong>thành phần</strong>
            content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)
            html_lines.append(f"<li>{content}</li>")
        else:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            # Chuyển đổi cú pháp in đậm cho dòng thông thường
            content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line_stripped)
            html_lines.append(f"<p>{content}</p>")
            
    # Kết thúc thẻ danh sách nếu vẫn còn đang mở ở cuối chuỗi
    if in_list:
        html_lines.append("</ul>")
        
    formatted_html_content = "".join(html_lines)
    
    # Tạo nhãn badge bộ nhớ đệm nếu câu hỏi được tối ưu hóa lấy trực tiếp từ session_state
    cache_badge = '<span class="brand-badge">⚡ Câu trả lời tối ưu từ hệ thống</span>' if is_cached else ''
    
    # Thiết kế Layout HTML kết quả đồng bộ
    html_layout = f"""
    <div class="brand-answer-box">
        <div class="brand-answer-header">
            <span class="brand-header-title">📘 {title}</span>
            {cache_badge}
        </div>
        <div class="brand-answer-content">
            {formatted_html_content}
        </div>
    </div>
    """
    st.markdown(html_layout, unsafe_allow_html=True)


# ==========================================
# 5. GIAO DIỆN ỨNG DỤNG (UI)
# ==========================================
col1, col2 = st.columns([1, 5])

with col1:
    # Thay 'logo_khoa.png' bằng tên file ảnh bạn đã lưu trong thư mục dự án
    st.image("logo_khoa.png", width=100) 

with col2:
    st.markdown(
        "<h1 style='color: #005088; margin-bottom: 0;'>Chatbot Hỗ Trợ Sinh Viên 🎓</h1>", 
        unsafe_allow_html=True
    )
    st.subheader("🤖 TRỢ LÝ AI KHOA NGOẠI NGỮ")

st.write(
    "Chào Anh/Chị! Hãy chọn lĩnh vực mà mình quan tâm, sau đó nhập câu hỏi ô bên dưới. " 
    "AI sẽ tự động đọc dữ liệu và tổng hợp câu trả lời chính xác nhất cho Anh/Chị."
)

# --- BƯỚC 1 ---
st.markdown("👉 <span style='color: #005088; font-weight: bold;'>Bước 1: Chọn lĩnh vực Anh/Chị muốn hỏi:</span>", unsafe_allow_html=True)
lua_chon_tieng_viet = st.selectbox(
    "Bước 1: Chọn lĩnh vực Anh/Chị muốn hỏi:", # Giữ label cho accessibility
    list(MENU_OPTIONS.keys()),
    label_visibility="collapsed" # Giấu label mặc định đi
)

# --- BƯỚC 2 ---
st.markdown("👉 <span style='color: #005088; font-weight: bold;'>Bước 2: Nhập câu hỏi của Anh/Chị vào ô bên dưới:</span>", unsafe_allow_html=True)
cau_hoi = st.text_input(
    "Bước 2: Nhập câu hỏi của Anh/Chị vào ô bên dưới:", # Giữ label cho accessibility
    placeholder="Ví dụ: Khoa có bao nhiêu ngành đào tạo?",
    label_visibility="collapsed" # Giấu label mặc định đi
)


# ==========================================
# 6. KHỞI TẠO BỘ NHỚ ĐỆM (CACHE) & COOLDOWN TRONG SESSION
# ==========================================
if "last_ask_time" not in st.session_state:
    st.session_state["last_ask_time"] = 0.0

if "qa_cache" not in st.session_state:
    # Lưu các câu hỏi đã có câu trả lời để tránh gọi API trùng lặp
    st.session_state["qa_cache"] = {} 


# ==========================================
# 7. XỬ LÝ KHI BẤM NÚT HỎI AI
# ==========================================
if st.button("🚀 Trợ Lý AI Trả Lời"):

    if not cau_hoi.strip():
        st.warning("Anh/Chị vui lòng nhập câu hỏi trước nhé!")
        st.stop()

    # --- KIỂM TRA COOLDOWN (CHỐNG SPAM CỦA SINH VIÊN) ---
    current_time = time.time()
    time_passed = current_time - st.session_state["last_ask_time"]
    cooldown_limit = 10  # Số giây sinh viên phải đợi giữa 2 câu hỏi

    if time_passed < cooldown_limit:
        remaining = int(cooldown_limit - time_passed)
        st.warning(f"⚡ Anh/Chị hỏi nhanh quá! Vui lòng đợi {remaining} giây nữa để hệ thống xử lý nhé.")
        st.stop()

    # Cập nhật lại thời gian hỏi mới nhất
    st.session_state["last_ask_time"] = current_time

    # --- KIỂM TRA TRÙNG CÂU HỎI (TIẾT KIỆM QUOTA & TRẢ VỀ TỨC THÌ) ---
    standardized_question = cau_hoi.strip().lower()
    
    # Tạo một "khóa" gồm lĩnh vực + câu hỏi để kiểm tra trong bộ nhớ đệm
    cache_key = f"{lua_chon_tieng_viet}_{standardized_question}"

    if cache_key in st.session_state["qa_cache"]:
        # Sử dụng hàm định dạng CSS thương hiệu mới cho câu trả lời từ cache
        cached_answer = st.session_state["qa_cache"][cache_key]
        display_brand_answer(cached_answer, title="Câu trả lời từ Trợ lý AI", is_cached=True)
        st.stop()

    # --- GỌI GEMINI API NẾU LÀ CÂU HỎI MỚI ---
    with st.spinner("🤖 Vui lòng đợi. AI đang chuẩn bị câu trả lời..."):
        try:
            selected_sheet = MENU_OPTIONS[lua_chon_tieng_viet]
            df = load_data_by_sheet(filepath, selected_sheet)
            data_context = df.to_string(index=False)

            prompt_content = f"""
Bạn là Trợ lý AI của Khoa Ngoại ngữ.
Chỉ được phép trả lời dựa trên dữ liệu được cung cấp dưới đây.
Không được tự bịa đặt thông tin nằm ngoài dữ liệu.
Nếu không tìm thấy câu trả lời trong dữ liệu thì hãy trả lời chính xác câu sau:
"Xin lỗi Anh/Chị, hiện tại Trợ lý AI chưa tìm thấy thông tin này trong cơ sở dữ liệu của Khoa. Anh/Chị vui lòng liên hệ Văn phòng Khoa để được hỗ trợ thêm."

DỮ LIỆU KHOA CUNG CẤP:
{data_context}

CÂU HỎI CỦA SINH VIÊN:
{cau_hoi}

Yêu cầu câu trả lời:
- Trả lời hoàn toàn bằng tiếng Việt.
- Xưng hô lịch sự (Trợ lý AI - Anh/Chị).
- Ngắn gọn, rõ ràng, dễ đọc trên điện thoại.
- Nếu có danh sách thông tin, bắt buộc dùng gạch đầu dòng.
"""

            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(prompt_content)

            if response.text:
                answer = response.text
                
                # Lưu câu trả lời mới vào cache để lần sau dùng lại
                st.session_state["qa_cache"][cache_key] = answer

                # Sử dụng hàm hiển thị theo chuẩn thương hiệu mới
                display_brand_answer(answer, title="Câu trả lời từ Trợ lý AI")
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
                    "Để nhận thông tin ngay lập tức, Anh/Chị vui lòng liên hệ trực tiếp Văn phòng Khoa "
                    "hoặc thử lại sau 1-2 phút nhé!"
                )
            else:
                st.error(f"Hệ thống gặp lỗi: {err_str}")
