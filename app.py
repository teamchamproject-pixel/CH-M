import json
import random
import streamlit as st

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="CHẠM - Alzheimer Board Game Companion",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="expanded",
)

# --- CSS TÙY CHỈNH GIAO DIỆN (THEO BẢNG MÀU DỰ ÁN) ---
st.markdown(
    """
    <style>
    .main-header {
        font-size: 26px;
        font-weight: 700;
        color: #18324A;
        text-align: center;
        margin-bottom: 5px;
    }
    .sub-header {
        font-size: 15px;
        color: #55A88B;
        text-align: center;
        margin-bottom: 20px;
        font-weight: 600;
    }
    .card-box {
        background-color: #F7F6F1;
        border: 2px solid #3979B9;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .highlight-badge {
        background-color: #7867B5;
        color: white;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 13px;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# --- HÀM TẢI DỮ LIỆU ---
@st.cache_data
def load_questions():
  try:
    with open("questions.json", "r", encoding="utf-8") as f:
      return json.load(f)
  except FileNotFoundError:
    return {
        "version": "2.0.0",
        "cards": [{
            "id": "DEMO-01",
            "group": "Kiến thức",
            "question": "Đang tải dữ liệu hệ thống...",
            "options": ["A", "B", "C", "D"],
            "answer": "A",
            "explanation": "Đang cập nhật.",
        }],
    }


data = load_questions()

# --- KHỞI TẠO TRẠNG THÁI (SESSION STATE) ---
if "authenticated" not in st.session_state:
  st.session_state.authenticated = False

# Khởi tạo 4 thanh tiến độ trung tâm (mặc định mức khởi đầu là 4 theo tài liệu)[cite: 8]
if "indicators" not in st.session_state:
  st.session_state.indicators = {
      "Nghiên cứu (NC)": 4,
      "Công nghệ (CN)": 4,
      "Chăm sóc (CS)": 4,
      "Cộng đồng (CĐ)": 4,
  }

# --- XÁC THỰC MÃ QR ĐỘC QUYỀN ---
if not st.session_state.authenticated:
  st.markdown(
      '<div class="main-header">🧠 CHẠM – Board Game Giáo Dục Alzheimer</div>',
      unsafe_allow_html=True,
  )
  st.markdown(
      '<div class="sub-header">“Thấu hiểu để kết nối – Kết nối để sẻ'
      ' chia”</div>',
      unsafe_allow_html=True,
  )

  with st.container():
    st.info(
        "📷 **Cổng quét mã QR độc quyền:** Vui lòng nhập mã kích hoạt được in"
        " bên trong hộp board game vật lý của bạn để mở khóa phiên bản web app"
        " mở rộng và kho thẻ cập nhật liên tục[cite: 1]."
    )

    access_code = st.text_input(
        "Nhập mã kích hoạt hộp game:",
        type="password",
        placeholder="Ví dụ: CHAM-2026-PRO",
    )

    col1, col2 = st.columns(2)
    with col1:
      if st.button("Xác thực mã QR", type="primary", use_container_width=True):
        valid_codes = ["CHAM-2026-PRO", "CHV-10S", "GIAAN-2026", "DEMO"]
        if access_code.strip() in valid_codes:
          st.session_state.authenticated = True
          st.success("Xác thực thành công! Đang chuyển vào hệ thống...")
          st.rerun()
        else:
          st.error(
              "Mã kích hoạt không hợp lệ. Vui lòng kiểm tra lại trên thẻ đi"
              " kèm hộp game[cite: 1]."
          )
    with col2:
      if st.button("Trải nghiệm nhanh (Demo)", use_container_width=True):
        st.session_state.authenticated = True
        st.warning("Đang vào chế độ Demo trực tuyến.")
        st.rerun()

  st.stop()

# --- GIAO DIỆN CHÍNH SAU KHI ĐĂNG NHẬP ---
st.markdown(
    '<div class="main-header">🧠 CHẠM – Web App Extension</div>',
    unsafe_allow_html=True,
)
st.markdown(
    f'<div class="sub-header">Phiên bản kho thẻ: v{data.get("version", "2.0.0")}'
    " | Đồng bộ 132 Thẻ & 4 Trụ Cột</div>",
    unsafe_allow_html=True,
)

# --- SIDEBAR ĐIỀU HƯỚNG ---
with st.sidebar:
  st.title("📂 Menu Trò Chơi")
  game_mode = st.radio(
      "Chọn tính năng:", [
          "🎴 Rút Thẻ Ngẫu Nhiên (8 Nhóm)",
          "📊 Theo Dõi 4 Thanh Tiến Độ",
          "ℹ️ Giới Thiệu & Nguyên Tắc Dự Án",
      ]
  )

  st.markdown("---")
  st.markdown("### 📊 Trạng thái Hệ Sinh Thái")
  for k, v in st.session_state.indicators.items():
    st.progress(
        v / 10.0, text=f"**{k}**: {v}/10"
    )  # Thang điểm 0-10[cite: 8]

  st.markdown("---")
  if st.button("Đăng xuất / Nhập lại mã"):
    st.session_state.authenticated = False
    st.rerun()

# --- CHẾ ĐỘ 1: RÚT THẺ NGẪU NHIÊN THEO 8 NHÓM ---
if game_mode == "🎴 Rút Thẻ Ngẫu Nhiên (8 Nhóm)":
  st.subheader("🎴 Kho Thẻ Động (132 Thẻ Tích Hợp)")
  st.write(
      "Chọn nhóm thẻ bạn muốn rút hoặc rút ngẫu nhiên toàn bộ hệ thống để hỗ"
      " trợ ván chơi vật lý:"
  )

  # Lọc danh sách nhóm thẻ
  all_groups = list(set(card["group"] for card in data["cards"]))
  selected_group = st.selectbox(
      "Chọn bộ thẻ muốn rút:", ["Tất cả các nhóm"] + all_groups
  )

  if "current_card" not in st.session_state:
    st.session_state.current_card = None
  if "show_ans" not in st.session_state:
    st.session_state.show_ans = False

  if st.button("🎴 Rút Thẻ Ngay", type="primary", use_container_width=True):
    if selected_group == "Tất cả các nhóm":
      filtered_cards = data["cards"]
    else:
      filtered_cards = [
          c for c in data["cards"] if c["group"] == selected_group
      ]

    if filtered_cards:
      st.session_state.current_card = random.choice(filtered_cards)
      st.session_state.show_ans = False

  if st.session_state.current_card:
    card = st.session_state.current_card
    st.markdown("<br>", unsafe_allow_html=True)

    with st.container():
      st.markdown('<div class="card-box">', unsafe_allow_html=True)
      st.markdown(
          f'<span class="highlight-badge">Mã: {card["id"]} | Nhóm: {card["group"]}</span>',
          unsafe_allow_html=True,
      )
      st.markdown(f"### {card['question']}")

      user_choice = st.radio(
          "Lựa chọn / Đáp án của bạn:", card["options"], key=f"ans_{card['id']}"
      )

      if st.button("Kiểm tra kết quả / Hướng dẫn xử lý"):
        st.session_state.show_ans = True

      if st.session_state.show_ans:
        st.markdown("---")
        if user_choice == card["answer"]:
          st.success(
              f"🎉 **Chính xác! Hướng dẫn xử lý chuẩn: **"
          )
        else:
          st.info(f"💡 Đáp án gợi ý từ hệ thống:")

        st.warning(f"📖 Giải thích chuyên môn / Tiêu chí:")

      st.markdown("</div>", unsafe_allow_html=True)

# --- CHẾ ĐỘ 2: THEO DÕI VÀ CẬP NHẬT 4 THANH TIẾN ĐỘ TRUNG TÂM ---
elif game_mode == "📊 Theo Dõi 4 Thanh Tiến Độ":
  st.subheader("⚙️ Quản lý 4 Thanh Tiến Độ Trung Tâm (0 - 10)")
  st.write(
      "Trong quá trình chơi board game quanh bàn đấu, nhóm có thể dùng giao"
      " diện này để cập nhật tiến độ chung của hệ sinh thái[cite: 8]."
  )

  col1, col2 = st.columns(2)
  with col1:
    st.session_state.indicators["Nghiên cứu (NC)"] = st.slider(
        "🔬 Tiến bộ Nghiên cứu (NC)",
        0,
        10,
        st.session_state.indicators["Nghiên cứu (NC)"],
    )
    st.session_state.indicators["Công nghệ (CN)"] = st.slider(
        "💻 Năng lực Công nghệ (CN)",
        0,
        10,
        st.session_state.indicators["Công nghệ (CN)"],
    )
  with col2:
    st.session_state.indicators["Chăm sóc (CS)"] = st.slider(
        "🌿 Chất lượng Chăm sóc (CS)",
        0,
        10,
        st.session_state.indicators["Chăm sóc (CS)"],
    )
    st.session_state.indicators["Cộng đồng (CĐ)"] = st.slider(
        "🤝 Kết nối Cộng đồng (CĐ)",
        0,
        10,
        st.session_state.indicators["Cộng đồng (CĐ)"],
    )

  if st.button("Lưu & Đặt lại mốc mặc định"):
    st.session_state.indicators = {
        "Nghiên cứu (NC)": 4,
        "Công nghệ (CN)": 4,
        "Chăm sóc (CS)": 4,
        "Cộng đồng (CĐ)": 4,
    }
    st.success("Đã thiết lập lại mốc khởi đầu (4 điểm).")
    st.rerun()

# --- CHẾ ĐỘ 3: GIỚI THIỆU DỰ ÁN ---
elif game_mode == "ℹ️ Giới Thiệu & Nguyên Tắc Dự Án":
  st.subheader("ℹ️ Về Dự Án Board Game CHẠM")
  st.markdown(
      "**CHẠM** là board game giáo dục tương tác về Alzheimer, kết hợp giữa"
      " trải nghiệm bàn cờ vật lý và hệ thống web mở rộng qua mã QR[cite: 1]."
  )
  st.markdown(
      "- **Bốn Trụ Cột Phát Triển:** Nghiên cứu (NC), Công nghệ (CN), Chăm sóc"
      " (CS) và Cộng đồng (CĐ)."
  )
  st.markdown(
      "- **Giá trị cốt lõi:** Thấu hiểu để kết nối – Kết nối để sẻ chia. Không"
      " ai phải đi một mình[cite: 1]."
  )
  st.info(
      "💡 **Mẹo phát triển:** Bạn có thể dễ dàng cập nhật thêm các thẻ bài mới"
      " bằng cách chỉnh sửa file `questions.json` trực tiếp trên GitHub mà không"
      " cần thay đổi mã nguồn app."
  )
