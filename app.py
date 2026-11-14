import json
import os
import random
import streamlit as st

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="CHẠM - Playtest Board Game System",
    page_icon="🧠",
    layout="wide",
)

# --- CSS TÙY CHỈNH GIAO DIỆN ---
st.markdown(
    """
    <style>
    .main-header { font-size: 28px; font-weight: 700; color: #18324A; text-align: center; }
    .sub-header { font-size: 16px; color: #55A88B; text-align: center; font-weight: 600; margin-bottom: 20px; }
    .card-box { background-color: #F7F6F1; border: 2px solid #3979B9; border-radius: 12px; padding: 20px; margin-top: 15px; }
    .badge { background-color: #7867B5; color: white; padding: 4px 10px; border-radius: 6px; font-weight: 600; font-size: 13px; }
    .system-log { background-color: #18324A; color: #F7F6F1; padding: 10px; border-radius: 8px; font-family: monospace; font-size: 12px; }
    </style>
""",
    unsafe_allow_html=True,
)

ROOMS_FILE = "rooms.json"

VALID_SERIAL_CODES = {
    "CHAM-2026-PRO": "Standard Edition Box",
    "CHAM-2026-VIP": "Collector Edition Box",
    "CHV-10S-DEMO": "School Demo License",
    "GIAAN-2026": "Developer License",
}


# --- HÀM QUẢN LÝ DỮ LIỆU PHÒNG TRỰC TUYẾN ---
def load_rooms():
  if os.path.exists(ROOMS_FILE):
    try:
      with open(ROOMS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
    except:
      return {}
  return {}


def save_rooms(rooms):
  with open(ROOMS_FILE, "w", encoding="utf-8") as f:
    json.dump(rooms, f, ensure_ascii=False, indent=4)


@st.cache_data
def load_questions_data():
  try:
    with open("questions.json", "r", encoding="utf-8") as f:
      return json.load(f)
  except:
    return {
        "version": "2.1.0",
        "cards": [{
            "id": "0",
            "group": "Mặc định",
            "question": "Đang cập nhật dữ liệu...",
            "options": ["A"],
            "answer": "A",
            "explanation": "Lỗi",
        }],
    }


q_data = load_questions_data()

# --- KHỞI TẠO SESSION STATE ---
if "activated" not in st.session_state:
  st.session_state.activated = False
if "serial_used" not in st.session_state:
  st.session_state.serial_used = ""
if "joined_room" not in st.session_state:
  st.session_state.joined_room = None
if "my_role" not in st.session_state:
  st.session_state.my_role = None
if "player_name" not in st.session_state:
  st.session_state.player_name = ""


# ==========================================
# BƯỚC 1: XÁC THỰC MÃ KÍCH HOẠT / SỐ SÊ-RI HỘP GAME
# ==========================================
if not st.session_state.activated:
  st.markdown(
      '<div class="main-header">🧠 CHẠM – Cổng Xác Thực Bản Quyền Board Game</div>',
      unsafe_allow_html=True,
  )
  st.markdown(
      '<div class="sub-header">Nhập mã sê-ri đi kèm hộp board game vật lý để'
      " kích hoạt hệ thống</div>",
      unsafe_allow_html=True,
  )

  col1, col2 = st.columns([2, 1])
  with col1:
    input_serial = st.text_input(
        "Nhập mã sê-ri / mã kích hoạt:",
        placeholder="Ví dụ: CHAM-2026-PRO",
    )

    c_btn1, c_btn2 = st.columns(2)
    with c_btn1:
      if st.button(
          "Kích hoạt bản quyền", type="primary", use_container_width=True
      ):
        clean_serial = input_serial.strip().upper()
        if clean_serial in VALID_SERIAL_CODES:
          st.session_state.activated = True
          st.session_state.serial_used = clean_serial
          st.success("Kích hoạt thành công!")
          st.rerun()
        else:
          st.error("Mã sê-ri không hợp lệ. Hãy thử dùng mã Demo bên dưới.")
    with c_btn2:
      if st.button("Dùng thử nhanh (Mã Demo)", use_container_width=True):
        st.session_state.activated = True
        st.session_state.serial_used = "CHV-10S-DEMO"
        st.warning("Đang vào chế độ Demo trực tuyến.")
        st.rerun()
  st.stop()


# ==========================================
# BƯỚC 2: SẢNH CHỜ & TẠO PHÒNG
# ==========================================
if not st.session_state.joined_room:
  st.markdown(
      '<div class="main-header">🧠 CHẠM – Hệ Thống Ván Đấu Trực Tuyến</div>',
      unsafe_allow_html=True,
  )
  st.markdown(
      f'<div class="sub-header">Trạng thái: Đã xác thực (<code>{st.session_state.serial_used}</code>)</div>',
      unsafe_allow_html=True,
  )

  col_l1, col_l2 = st.columns(2)

  with col_l1:
    st.subheader("🏠 Tạo Phòng Ván Đấu Mới")
    creator_name = st.text_input(
        "Tên người chơi (Host):", placeholder="Ví dụ: Gia An"
    )
    custom_room = st.text_input(
        "Mã phòng (để trống sẽ tự sinh):", placeholder="Ví dụ: CHAM64"
    )

    if st.button("Tạo Phòng Mới", type="primary"):
      if not creator_name.strip():
        st.error("Vui lòng nhập tên của bạn!")
      else:
        rooms = load_rooms()
        code = (
            custom_room.strip().upper()
            if custom_room.strip()
            else f"CHAM{random.randint(100, 999)}"
        )
        rooms[code] = {
            "host": creator_name,
            "players": {
                "Nghiên cứu (Research)": creator_name,
                "Công nghệ (Technology)": "",
                "Chăm sóc cộng đồng (Community Care)": "",
                "Chính sách & Hợp tác (Policy & Partnership)": "",
            },
            "positions": {
                "Nghiên cứu (Research)": 1,
                "Công nghệ (Technology)": 1,
                "Chăm sóc cộng đồng (Community Care)": 1,
                "Chính sách & Hợp tác (Policy & Partnership)": 1,
            },
            "indicators": {
                "Tiến bộ Nghiên cứu (R)": 4,
                "Năng lực Công nghệ (T)": 4,
                "Chất lượng Chăm sóc (Q)": 4,
                "Hợp tác & Tiếp cận (G)": 4,
                "Gánh nặng xã hội (B)": 2,
            },
            "turn_order": [
                "Nghiên cứu (Research)",
                "Công nghệ (Technology)",
                "Chăm sóc cộng đồng (Community Care)",
                "Chính sách & Hợp tác (Policy & Partnership)",
            ],
            "current_turn_idx": 0,
            "current_card": None,
            "card_status": "WAITING",
            "game_started": False,
            "logs": [f"Phòng {code} khởi tạo thành công bởi {creator_name}."],
        }
        save_rooms(rooms)
        st.session_state.joined_room = code
        st.session_state.my_role = "Nghiên cứu (Research)"
        st.session_state.player_name = creator_name
        st.success("Tạo phòng thành công!")
        st.rerun()

  with col_l2:
    st.subheader("🔑 Tham Gia Phòng Đã Tạo")
    join_name = st.text_input("Tên của bạn:", placeholder="Ví dụ: Minh Quân")
    join_code = st.text_input(
        "Mã phòng trực tuyến:", placeholder="Ví dụ: CHAM64"
    ).upper()

    rooms = load_rooms()
    available_roles = []
    if join_code in rooms:
      available_roles = [
          role
          for role, pname in rooms[join_code]["players"].items()
          if pname == ""
      ]

    chosen_role = st.selectbox(
        "Chọn vai trò trụ cột của bạn:",
        available_roles if available_roles else ["Nghiên cứu (Research)"],
    )

    if st.button("Vào Phòng Chơi", type="secondary"):
      if not join_name.strip():
        st.error("Vui lòng nhập tên của bạn!")
      elif join_code not in rooms:
        st.error("Không tìm thấy mã phòng này!")
      else:
        rooms = load_rooms()
        # Nếu slot đã đầy, gán đè tên để tiện test nhanh
        rooms[join_code]["players"][chosen_role] = join_name
        rooms[join_code]["logs"].append(
            f"{join_name} đã gia nhập trụ cột {chosen_role}."
        )
        save_rooms(rooms)

        st.session_state.joined_room = join_code
        st.session_state.my_role = chosen_role
        st.session_state.player_name = join_name
        st.success("Vào phòng thành công!")
        st.rerun()

  st.stop()


# ==========================================
# BƯỚC 3: BÀN CHƠI CHÍNH (ĐÃ BỎ QUA GIỚI HẠN 4 NGƯỜI)
# ==========================================
code = st.session_state.joined_room
rooms = load_rooms()

if code not in rooms:
  st.error("Phòng chơi đã bị đóng!")
  if st.button("Quay lại sảnh"):
    st.session_state.joined_room = None
    st.rerun()
  st.stop()

room = rooms[code]

c_h1, c_h2, c_h3 = st.columns([3, 1, 1])
with c_h1:
  st.markdown(
      f"### 🧠 Phòng: `{code}` | Trụ cột của bạn: **{st.session_state.my_role}**"
      f" ({st.session_state.player_name})"
  )
with c_h2:
  if st.button("🔄 Đồng bộ dữ liệu", use_container_width=True):
    st.rerun()
with c_h3:
  if st.button("🚪 Rời phòng", use_container_width=True):
    st.session_state.joined_room = None
    st.rerun()

st.markdown("---")

# 1. Sảnh chờ - Đã nới lỏng điều kiện bắt đầu cho chế độ Playtest
if not room["game_started"]:
  st.subheader("👥 Danh Sách Trụ Cột (Chế độ Chạy thử)")
  c_p1, c_p2 = st.columns(2)

  with c_p1:
    for role, pname in room["players"].items():
      status = f"✅ **{pname}**" if pname else "⏳ *(Trống - Có thể test độc lập)*"
      st.markdown(f"- **{role}**: {status}")

  with c_p2:
    st.success(
        "🛠️ **Chế độ Playtest:** Đã bỏ qua giới hạn bắt buộc đủ 4 thành viên."
        " Bạn có thể bấm nút bắt đầu ngay lập tức để chạy thử hệ thống phán"
        " quyết tự động."
    )
    is_host = st.session_state.player_name == room["host"]

    if st.button(
        "🚀 BẮT ĐẦU CHẠY THỬ (PLAYTEST MODE)",
        type="primary",
        use_container_width=True,
    ):
      room["game_started"] = True
      # Tự động điền tên tạm thời vào các ô trống nếu chưa có người chơi để tránh lỗi lượt đi
      for r_key in room["players"]:
        if not room["players"][r_key]:
          room["players"][r_key] = f"Bot ({r_key.split()[0]})"
      room["logs"].append(
          "Chế độ chạy thử được kích hoạt bởi "
          + st.session_state.player_name
      )
      save_rooms(rooms)
      st.rerun()

  st.stop()


# 2. Ván chơi chính thức (Playtest)
col_map, col_ctrl = st.columns([1.6, 1])

current_turn_role = room["turn_order"][room["current_turn_idx"]]
is_my_turn = current_turn_role == st.session_state.my_role

with col_map:
  st.subheader("🗺️ Bản Đồ & Trạng Thái Hệ Sinh Thái (64 Ô)")

  m_cols = st.columns(2)
  for idx, (role, pos) in enumerate(room["positions"].items()):
    with m_cols[idx % 2]:
      st.metric(
          label=role.split()[0],
          value=f"Ô số {pos} / 64",
          delta="Đang tiến bước",
      )

  st.markdown("---")
  st.subheader("📊 Các Chỉ Số Hệ Sinh Thái")
  ind_cols = st.columns(3)
  keys = list(room["indicators"].keys())
  for i, k in enumerate(keys):
    val = room["indicators"][k]
    with ind_cols[i % 3]:
      st.metric(label=k, value=f"{val} điểm")

  st.markdown("---")
  st.subheader("📜 Nhật Ký Phán Quyết Tự Động")
  log_container = st.container()
  with log_container:
    st.markdown('<div class="system-log">', unsafe_allow_html=True)
    for log in reversed(room["logs"][-10:]):
      st.text(f">> {log}")
    st.markdown("</div>", unsafe_allow_html=True)

with col_ctrl:
  st.subheader("⚙️ Bảng Điều Phối Lượt Đi")
  st.info(f"🎯 Lượt hiện tại thuộc về: **{current_turn_role}")

  # Cho phép người chơi hiện tại hoặc chủ phòng test linh hoạt trong chế độ chạy thử
  if is_my_turn or st.session_state.player_name == room["host"]:
    if is_my_turn:
      st.success("✨ Đến lượt nhân vật của bạn!")
    else:
      st.warning(
          "⚠️ [Chế độ Quản trị Playtest] Bạn đang đóng vai Host và có quyền"
          " thay mặt thao tác."
      )

    # Bước 1: Tung xúc xắc
    if room["current_card"] is None:
      if st.button("🎲 Tung Xúc Xắc (1-6 bước)", type="primary", use_container_width=True):
        steps = random.randint(1, 6)
        old_pos = room["positions"][current_turn_role]
        new_pos = min(64, old_pos + steps)
        room["positions"][current_turn_role] = new_pos

        card = random.choice(q_data["cards"])
        room["current_card"] = card
        room["card_status"] = "WAITING"

        room["logs"].append(
            f"{current_turn_role} tung được {steps} bước, đến ô {new_pos} và rút"
            f" thẻ {card['id']}."
        )
        save_rooms(rooms)
        st.rerun()

    # Bước 2: Phán quyết thẻ tự động
    if room["current_card"] is not None:
      card = room["current_card"]
      st.markdown('<div class="card-box">', unsafe_allow_html=True)
      st.markdown(
          f'<span class="badge">Thẻ {card["id"]} | {card["group"]}</span>',
          unsafe_allow_html=True,
      )
      st.markdown(f"")

      user_ans = st.radio(
          "Lựa chọn đáp án:", card["options"], key="playtest_ans_sel"
      )

      if room["card_status"] == "WAITING":
        if st.button("Xác nhận & Phán quyết tự động"):
          room["card_status"] = "ANSWERED"
          if user_ans == card["answer"]:
            room["indicators"]["Tiến bộ Nghiên cứu (R)"] = min(
                10, room["indicators"]["Tiến bộ Nghiên cứu (R)"] + 1
            )
            room["logs"].append(
                "Phán quyết tự động: CHÍNH XÁC! Tăng +1 điểm Nghiên cứu."
            )
          else:
            room["indicators"]["Gánh nặng xã hội (B)"] = min(
                10, room["indicators"]["Gánh nặng xã hội (B)"] + 1
            )
            room["logs"].append(
                "Phán quyết tự động: CHƯA ĐÚNG. Tăng +1 Gánh nặng xã hội."
            )
          save_rooms(rooms)
          st.rerun()
      else:
        st.success(f"📌 Đáp án chuẩn: **")
        st.info(f"💡 Giải thích: {card['explanation']}")

        if st.button(
            "➡️ Hoàn tất lượt & Chuyển người tiếp theo",
            type="primary",
            use_container_width=True,
        ):
          room["current_turn_idx"] = (room["current_turn_idx"] + 1) % 4
          room["current_card"] = None
          room["card_status"] = "WAITING"
          room["logs"].append(f"Đã chuyển lượt cho người chơi tiếp theo.")
          save_rooms(rooms)
          st.rerun()

      st.markdown("</div>", unsafe_allow_html=True)

  else:
    st.warning(f"Đang chờ lượt của **{current_turn_role}**...")
