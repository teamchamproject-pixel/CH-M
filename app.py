import json
import os
import random
import streamlit as st

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="CHẠM - Multiplayer Online Board Game",
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
    </style>
""",
    unsafe_allow_html=True,
)

ROOMS_FILE = "rooms.json"


# --- HÀM QUẢN LÝ PHÒNG TRỰC TUYẾN (JSON STORAGE) ---
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
        "version": "2.0.0",
        "cards": [{
            "id": "0",
            "group": "Mặc định",
            "question": "Chưa tải được dữ liệu câu hỏi",
            "options": ["A"],
            "answer": "A",
            "explanation": "Lỗi",
        }],
    }


q_data = load_questions_data()

# --- TRẠNG THÁI NGƯỜI DÙNG TRONG PHIÊN ---
if "joined_room" not in st.session_state:
  st.session_state.joined_room = None
if "my_role" not in st.session_state:
  st.session_state.my_role = None
if "player_name" not in st.session_state:
  st.session_state.player_name = ""

# --- MÀN HÌNH CHƯA VÀO PHÒNG (SẢNH CHỜ & TẠO PHÒNG) ---
if not st.session_state.joined_room:
  st.markdown(
      '<div class="main-header">🧠 CHẠM – Online Multiplayer Board Game</div>',
      unsafe_allow_html=True,
  )
  st.markdown(
      '<div class="sub-header">“Thấu hiểu để kết nối – Kết nối để sẻ'
      ' chia”</div>',
      unsafe_allow_html=True,
  )

  col1, col2 = st.columns(2)

  with col1:
    st.subheader("🏠 Tạo Phòng Mới")
    st.write(
        "Tạo phòng chơi mới cho nhóm 4 người tham gia qua mã phòng độc quyền."
    )
    creator_name = st.text_input(
        "Tên của bạn:", placeholder="Ví dụ: Gia An", key="creator_input"
    )
    new_room_code = st.text_input(
        "Mã phòng tùy chọn (hoặc để trống):",
        placeholder="Ví dụ: CHAM2026",
        key="code_input",
    )

    if st.button("Tạo Phòng Ngay", type="primary"):
      if not creator_name.strip():
        st.error("Vui lòng nhập tên của bạn!")
      else:
        rooms = load_rooms()
        code = (
            new_room_code.strip().upper()
            if new_room_code.strip()
            else f"CHAM{random.randint(100, 999)}"
        )
        if code in rooms:
          st.error(
              "Mã phòng này đã tồn tại! Vui lòng chọn mã khác hoặc tham gia"
              " phòng."
          )
        else:
          # Khởi tạo phòng chuẩn theo 4 trụ cột[cite: 35] và bản đồ 64 ô[cite: 1]
          rooms[code] = {
              "host": creator_name,
              "players": {
                  "Nghiên cứu (Research)": creator_name,
                  "Công nghệ (Tech)": "",
                  "Chăm sóc (Care)": "",
                  "Cộng đồng (Community)": "",
              },
              "positions": {
                  "Nghiên cứu (Research)": 1,
                  "Công nghệ (Tech)": 1,
                  "Chăm sóc (Care)": 1,
                  "Cộng đồng (Community)": 1,
              },
              "indicators": {
                  "Nghiên cứu (NC)": 4,
                  "Công nghệ (CN)": 4,
                  "Chăm sóc (CS)": 4,
                  "Cộng đồng (CĐ)": 4,
              },  # Khởi đầu ở mốc 4[cite: 8]
              "turn_order": [
                  "Nghiên cứu (Research)",
                  "Công nghệ (Tech)",
                  "Chăm sóc (Care)",
                  "Cộng đồng (Community)",
              ],
              "current_turn_idx": 0,
              "current_card": None,
              "card_revealed": False,
              "game_started": False,
              "logs": [f"Phòng {code} đã được tạo bởi {creator_name}."],
          }
          save_rooms(rooms)
          st.session_state.joined_room = code
          st.session_state.my_role = "Nghiên cứu (Research)"
          st.session_state.player_name = creator_name
          st.success(f"Tạo phòng thành công! Đang vào phòng {code}...")
          st.rerun()

  with col2:
    st.subheader("🔑 Tham Gia Phòng")
    st.write("Nhập mã phòng do bạn bè cung cấp để cùng vào bàn chơi trực tuyến.")
    join_name = st.text_input("Tên của bạn:", placeholder="Ví dụ: Minh Quân")
    join_code = st.text_input(
        "Mã phòng:", placeholder="Ví dụ: CHAM2026"
    ).upper()

    rooms = load_rooms()
    available_roles = []
    if join_code in rooms:
      # Lấy các vai trò còn trống
      available_roles = [
          role
          for role, pname in rooms[join_code]["players"].items()
          if pname == ""
      ]

    chosen_role = st.selectbox(
        "Chọn trụ cột / vai trò của bạn[cite: 35]:", available_roles
    )

    if st.button("Vào Phòng Chơi"):
      if not join_name.strip():
        st.error("Vui lòng nhập tên của bạn!")
      elif join_code not in rooms:
        st.error("Không tìm thấy mã phòng này!")
      elif not chosen_role:
        st.error("Phòng đã đủ người hoặc chưa chọn vai trò!")
      else:
        rooms = load_rooms()
        rooms[join_code]["players"][chosen_role] = join_name
        rooms[join_code]["logs"].append(f"{join_name} đã gia nhập vai trò {chosen_role}.")
        save_rooms(rooms)

        st.session_state.joined_room = join_code
        st.session_state.my_role = chosen_role
        st.session_state.player_name = join_name
        st.success("Tham gia phòng thành công!")
        st.rerun()

  st.stop()

# --- GIAO DIỆN TRONG PHÒNG CHƠI (GAME ROOM) ---
code = st.session_state.joined_room
rooms = load_rooms()

if code not in rooms:
  st.error("Phòng chơi không còn tồn tại hoặc đã bị giải tán!")
  if st.button("Quay lại sảnh chính"):
    st.session_state.joined_room = None
    st.rerun()
  st.stop()

room = rooms[code]

# Nút cập nhật đồng bộ dữ liệu phòng từ server json
col_h1, col_h2, col_h3 = st.columns([3, 1, 1])
with col_h1:
  st.markdown(
      f"### 🧠 Phòng: `{code}` | Vai trò của bạn: **{st.session_state.my_role}**"
      f" ({st.session_state.player_name})"
  )
with col_h2:
  if st.button("🔄 Làm mới dữ liệu", use_container_width=True):
    st.rerun()
with col_h3:
  if st.button("🚪 Rời phòng", use_container_width=True):
    st.session_state.joined_room = None
    st.rerun()

st.markdown("---")

# --- SẢNH CHỜ (LOBBY) TRƯỚC KHI BẮT ĐẦU ---
if not room["game_started"]:
  st.subheader("👥 Sảnh Chờ Người Chơi (Đủ 4 Trụ Cột để Bắt Đầu)")

  col_p1, col_p2 = st.columns(2)
  with col_p1:
    for role, pname in room["players"].items():
      status = f"✅ **{pname}**" if pname else "⏳ *Đang chờ người chơi...*"
      st.markdown(f"- **{role}**: {status}")

  with col_p2:
    st.info(
        "💡 **Hướng dẫn:** Trò chơi yêu cầu đủ 4 người chơi đảm nhận 4 trụ cột"
        " (Nghiên cứu, Công nghệ, Chăm sóc, Cộng đồng) để phối hợp xây dựng hệ"
        " sinh thái ứng phó Alzheimer[cite: 35]."
    )
    # Chỉ Host mới có quyền bấm bắt đầu khi đủ người
    is_host = st.session_state.player_name == room["host"]
    all_ready = all(p != "" for p in room["players"].values())

    if all_ready:
      st.success("Đã đủ 4 người chơi trong phòng!")
      if is_host:
        if st.button("🚀 BẮT ĐẦU VÁN CHƠI", type="primary", use_container_width=True):
          room["game_started"] = True
          room["logs"].append("Ván chơi chính thức bắt đầu!")
          save_rooms(rooms)
          st.rerun()
      else:
        st.warning("Đang chờ chủ phòng (Host) bấm nút bắt đầu...")
    else:
      st.warning("Đang chờ đủ thành viên tham gia vào các ghế trống...")

  st.stop()

# --- BẢN ĐỒ VÀ GIAO DIỆN CHƠI CHÍNH ---
col_board, col_side = st.columns([2, 1])

current_turn_role = room["turn_order"][room["current_turn_idx"]]
is_my_turn = current_turn_role == st.session_state.my_role

with col_board:
  st.subheader("🗺️ Bản Đồ Hành Trình (64 Ô)")
  
  # Hiển thị vị trí hiện tại của các quân cờ trên bàn cờ 64 ô[cite: 1]
  pos_cols = st.columns(4)
  for idx, (role, pos) in enumerate(room["positions"].items()):
    with pos_cols[idx]:
      st.metric(label=role.split()[0], value=f"Ô số {pos}/64")

  st.markdown("---")
  st.markdown(f"👉 Lượt đi hiện tại thuộc về: **{current_turn_role}**")

  if is_my_turn:
    st.success("✨ Đây là lượt đi của bạn!")
    
    c_dice1, c_dice2 = st.columns(2)
    with c_dice1:
      if st.button("🎲 Tung Xúc Xắc (1 - 6)", type="primary", use_container_width=True):
        steps = random.randint(1, 6)
        old_pos = room["positions"][st.session_state.my_role]
        new_pos = min(64, old_pos + steps)
        room["positions"][st.session_state.my_role] = new_pos
        
        # Rút ngẫu nhiên một thẻ từ kho thẻ
        card = random.choice(q_data["cards"])
        room["current_card"] = card
        room["card_revealed"] = False
        
        room["logs"].append(
            f"{st.session_state.player_name} ({st.session_state.my_role})"
            f" tung được {steps} bước, di chuyển từ ô {old_pos} đến ô {new_pos} và rút thẻ {card['id']}."
        )
        save_rooms(rooms)
        st.rerun()
  else:
    st.info(f"Đang chờ **{current_turn_role} thực hiện lượt đi...")

  # Hiển thị thẻ đang rút (nếu có)
  if room["current_card"]:
    card = room["current_card"]
    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    st.markdown(f'<span class="badge">Mã Thẻ: {card["id"]} | {card["group"]}</span>', unsafe_allow_html=True)
    st.markdown(f"### {card['question']}")

    ans = st.radio("Lựa chọn / Đáp án:", card["options"], key="game_ans_choice")

    if not room["card_revealed"]:
      if st.button("Xác nhận đáp án & Tác động tiến độ"):
        room["card_revealed"] = True
        # Tác động cộng điểm vào thanh tiến độ tương ứng
        if ans == card["answer"]:
          target_track = list(room["indicators"].keys())[room["current_turn_idx"]]
          room["indicators"][target_track] = min(10, room["indicators"][target_track] + 1)
          room["logs"].append(f"Trả lời chính xác! Tăng 1 điểm cho thanh {target_track}.")
        else:
          room["logs"].append("Trả lời chưa chính xác. Không thay đổi chỉ số.")
        save_rooms(rooms)
        st.rerun()
    else:
      st.success(f"📌 Đáp án đúng chuẩn: **")
      st.info(f"💡 Giải thích chuyên môn: {card['explanation']}")

      # Nút kết thúc lượt để chuyển sang người chơi kế tiếp
      if is_my_turn:
        if st.button("➡️ Kết thúc lượt & Chuyển người chơi", type="primary"):
          room["current_turn_idx"] = (room["current_turn_idx"] + 1) % 4
          room["current_card"] = None
          room["card_revealed"] = False
          room["logs"].append(f"{st.session_state.player_name} đã kết thúc lượt.")
          save_rooms(rooms)
          st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

with col_side:
  st.subheader("📊 4 Thanh Tiến Độ (0-10)")
  for track_name, val in room["indicators"].items():
    st.progress(val / 10.0, text=f"**{track_name}**: {val}/10[cite: 8]")

  st.markdown("---")
  st.subheader("📜 Nhật Ký Ván Đấu")
  for log_entry in reversed(room["logs"][-8:]):
    st.text(f"• {log_entry}")
      
