import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic
import pandas as pd
import requests
from datetime import datetime

# ---------------------------------------------------------
# 1. Cấu hình trang web Streamlit
# ---------------------------------------------------------
st.set_page_config(
    page_title="Mai Travel - Du Lịch Việt Nam",
    page_icon="🇻🇳",
    layout="wide"
)

# ---------------------------------------------------------
# CẤU HÌNH FORMSPREE
# ---------------------------------------------------------
FORMSPREE_URL = "https://formspree.io/f/xrpeylye"  # <--- Thay link Formspree của bạn vào đây

def send_booking_to_email(destination_name, package_price, full_name, phone_number, email_addr, num_adults, num_children, note_text):
    try:
        payload = {
            "Tour": destination_name,
            "Giá": package_price,
            "Họ tên": full_name,
            "Số điện thoại": phone_number,
            "Email": email_addr if email_addr else "Không có",
            "Người lớn": num_adults,
            "Trẻ em": num_children,
            "Ghi chú": note_text if note_text else "Không có"
        }
        response = requests.post(FORMSPREE_URL, data=payload)
        return response.status_code == 200
    except Exception:
        return False

# ---------------------------------------------------------
# QUẢN LÝ SESSION STATE
# ---------------------------------------------------------
if "selected_place" not in st.session_state:
    st.session_state["selected_place"] = "Đà Nẵng"

if "zoom_overview" not in st.session_state:
    st.session_state["zoom_overview"] = False

if "saved_tours" not in st.session_state:
    st.session_state["saved_tours"] = []

if "booked_tours" not in st.session_state:
    st.session_state["booked_tours"] = []

if "current_tab" not in st.session_state:
    st.session_state["current_tab"] = "Trang chủ"

# ---------------------------------------------------------
# CSS TÙY CHỈNH GIAO DIỆN & DỰNG MENU CỐ ĐỊNH Ở ĐÁY
# ---------------------------------------------------------
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');

        html, body, [class*="css"], * {
            font-family: 'Roboto', sans-serif !important;
        }
        
        .stButton>button {
            border-radius: 8px;
            font-weight: 600;
        }

        /* BO TRÒN BẢN ĐỒ */
        div[data-testid="stIFrame"], iframe {
            border-radius: 16px !important;
            overflow: hidden !important;
            box-shadow: 0 6px 18px rgba(0, 0, 0, 0.12) !important;
        }

        #MainMenu, footer, header {visibility: hidden;}

        /* ĐỆM ĐÁY ĐỂ THANH MENU KHÔNG CHE NỘI DUNG */
        .block-container {
            padding-bottom: 90px !important;
        }

        .hero-banner {
            background: linear-gradient(rgba(0, 0, 0, 0.45), rgba(0, 0, 0, 0.45)), 
                        url('https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1600&q=80');
            background-size: cover;
            background-position: center;
            padding: 40px 20px;
            border-radius: 16px;
            color: white;
            text-align: center;
            margin-bottom: 20px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.15);
        }

        /* TẠO THANH NAVIGATION BAR ĐÁY MÀN HÌNH MẶC ĐỊNH BẰNG ST.RADIO */
        div[data-testid="stBottom"] {
            position: fixed !important;
            bottom: 0 !important;
            left: 0 !important;
            right: 0 !important;
            background: #ffffff !important;
            box-shadow: 0 -4px 20px rgba(0,0,0,0.1) !important;
            z-index: 999999 !important;
            padding: 8px 16px !important;
            border-top-left-radius: 16px;
            border-top-right-radius: 16px;
        }

        div[data-testid="stBottom"] div[role="radiogroup"] {
            display: flex !important;
            justify-content: space-around !important;
            align-items: center !important;
            width: 100% !important;
        }

        div[data-testid="stBottom"] label {
            background: transparent !important;
            border: none !important;
            padding: 4px 8px !important;
            margin: 0 !important;
            cursor: pointer !important;
        }
    </style>
""", unsafe_allow_html=True)

# Tọa độ TP. Hồ Chí Minh
HO_CHI_MINH_COORDS = (10.7769, 106.7009)

user_agent = st.context.headers.get("User-Agent", "").lower()
is_phone = "iphone" in user_agent or "ipod" in user_agent or ("android" in user_agent and "mobile" in user_agent)

# ---------------------------------------------------------
# 2. POPUP MODAL ĐẶT TOUR
# ---------------------------------------------------------
@st.dialog("📝 XÁC NHẬN ĐẶT TOUR DU LỊCH")
def booking_modal(destination_name, package_price):
    st.markdown(f"#### 🌟 Tour: **{destination_name}**")
    st.caption(f"💰 Mức giá: **{package_price}**")
    st.write("Vui lòng nhập thông tin cá nhân bên dưới để hoàn tất giữ chỗ:")
    
    with st.form("modal_booking_form"):
        full_name = st.text_input("Họ và tên (*)", placeholder="Ví dụ: Nguyễn Văn A")
        phone_number = st.text_input("Số điện thoại (*)", placeholder="Ví dụ: 0901234567")
        email_addr = st.text_input("Email", placeholder="name@example.com")
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            num_adults = st.number_input("Người lớn", min_value=1, max_value=20, value=1)
        with col_f2:
            num_children = st.number_input("Trẻ em", min_value=0, max_value=20, value=0)
            
        note_text = st.text_area("Ghi chú thêm", placeholder="Yêu cầu về phòng, suất ăn...")
        
        submitted = st.form_submit_button("🚀 XÁC NHẬN ĐẶT TOUR", type="primary", use_container_width=True)
        
        if submitted:
            if not full_name.strip() or not phone_number.strip():
                st.warning("⚠️ Vui lòng nhập đầy đủ Họ tên và Số điện thoại!")
            else:
                send_booking_to_email(
                    destination_name, package_price, full_name,
                    phone_number, email_addr, num_adults, num_children, note_text
                )
                
                st.session_state["booked_tours"].append({
                    "tour": destination_name,
                    "price": package_price,
                    "name": full_name,
                    "phone": phone_number,
                    "adults": num_adults,
                    "children": num_children,
                    "time": datetime.now().strftime("%d/%m/%Y %H:%M")
                })
                
                st.balloons()
                st.success(f"🎉 Chúc mừng quý khách **{full_name}** đã đăng ký thành công!")

# ---------------------------------------------------------
# 3. DỮ LIỆU CÁC ĐIỂM DU LỊCH (SỬ DỤNG ANH TỐI ƯU URL TRỰC TIẾP)
# ---------------------------------------------------------
DEFAULT_IMG = "https://images.unsplash.com/photo-1528127269322-539801943592?auto=format&fit=crop&w=800&q=80"

DESTINATIONS = {
    "Đà Nẵng": {
        "coords": (16.0544, 108.2022),
        "cover": "https://images.unsplash.com/photo-1559592413-7cec4d0cae2b?auto=format&fit=crop&w=800&q=80",
        "description": "Thành phố đáng sống nhất Việt Nam với Bãi biển Mỹ Khê, Cầu Vàng (Bà Nà Hills) và Ngũ Hành Sơn hùng vĩ.",
        "avg_price": "2.500.000 - 4.000.000 VNĐ / người",
        "package_type": "Combo Vé máy bay + Khách sạn 3D2N (Tiêu chuẩn 4 sao)",
        "highlights": ["Check-in Cầu Vàng Bà Nà Hills", "Khám phá Cầu Rồng phun lửa", "Tắm biển Mỹ Khê"],
        "avg_speed_kmh": 60,
        "flight_time": "1 giờ 20 phút (Bay trực tiếp từ TP.HCM)"
    },
    "Hà Nội": {
        "coords": (21.0285, 105.8542),
        "cover": "https://images.unsplash.com/photo-1509030450996-93f2e3d83b3f?auto=format&fit=crop&w=800&q=80",
        "description": "Thủ đô nghìn năm văn hiến lưu giữ dấu ấn lịch sử, Hồ Hoàn Kiếm thơ mộng và văn hóa ẩm thực phố cổ đặc sắc.",
        "avg_price": "3.200.000 - 5.500.000 VNĐ / người",
        "package_type": "Tour Khám phá Phố Cổ & Ẩm thực 4D3N",
        "highlights": ["Dạo quanh Hồ Gươm & Phố Cổ", "Viếng Lăng Chủ tịch Hồ Chí Minh", "Thưởng thức Phở & Cà phê trứng"],
        "avg_speed_kmh": 60,
        "flight_time": "2 giờ 05 phút (Bay trực tiếp từ TP.HCM)"
    },
    "Lâm Đồng": {
        "coords": (11.9404, 108.4583),
        "cover": "https://images.unsplash.com/photo-1583417319070-4a69db38a482?auto=format&fit=crop&w=800&q=80",
        "description": "Thành phố ngàn hoa với khí hậu ôn đới quanh năm mát mẻ, những đồi thông reo và các quán cà phê view thung lũng mộng mơ.",
        "avg_price": "1.800.000 - 3.000.000 VNĐ / người",
        "package_type": "Combo Xe Limousine khứ hồi + Khách sạn view đồi thông 3D2N",
        "highlights": ["Săn mây đồi chè Cầu Đất", "Khám phá Chợ Đêm Đà Lạt", "Check-in Hồ Xuân Hương"],
        "avg_speed_kmh": 50,
        "flight_time": "50 phút (Bay) hoặc 6-7 giờ (Xe Limousine từ TP.HCM)"
    },
    "An Giang": {
        "coords": (10.2899, 103.9840),
        "cover": DEFAULT_IMG,
        "description": "Đảo Ngọc thiên đường nghỉ dưỡng hàng đầu với bãi cát trắng mịn như kem, nước biển trong ngọc bích và hoàng hôn tuyệt mỹ.",
        "avg_price": "3.500.000 - 6.000.000 VNĐ / người",
        "package_type": "Combo Resort 5 sao sát biển + Vé VinWonders 3D2N",
        "highlights": ["Tắm biển Bãi Sao", "Khám phá Grand World Phú Quốc", "Cáp treo vượt biển Hòn Thơm"],
        "avg_speed_kmh": 40,
        "flight_time": "1 giờ 00 phút (Bay trực tiếp từ TP.HCM)"
    },
    "Khánh Hòa": {
        "coords": (12.2388, 109.1967),
        "cover": DEFAULT_IMG,
        "description": "Thành phố biển năng động sở hữu một trong những vịnh biển đẹp nhất hành tinh, thiên đường lặn ngắm san hô và hải sản tươi ngon.",
        "avg_price": "2.200.000 - 4.200.000 VNĐ / người",
        "package_type": "Tour Vịnh biển cao cấp & Nghỉ dưỡng 3D2N",
        "highlights": ["Vui chơi tại VinWonders Nha Trang", "Lặn ngắm san hô đảo Hòn Mun", "Thưởng thức đặc sản nem nướng"],
        "avg_speed_kmh": 60,
        "flight_time": "1 giờ 10 phút (Bay) hoặc 8 giờ (Tàu hỏa/Xe giường nằm)"
    },
    "Quảng Ninh": {
        "coords": (20.9101, 107.1839),
        "cover": DEFAULT_IMG,
        "description": "Kỳ quan thiên nhiên thế giới UNESCO với hàng nghìn hòn đảo đá vôi kỳ vĩ nổi bật trên làn nước xanh ngọc bích huyền ảo.",
        "avg_price": "3.800.000 - 6.500.000 VNĐ / người",
        "package_type": "Tour Du thuyền 5 sao vịnh Hạ Long (Full board)",
        "highlights": ["Ngủ đêm trên du thuyền hạng sang", "Khám phá Hang Sửng Sốt", "Chèo thuyền Kayak đảo Ti Tốp"],
        "avg_speed_kmh": 60,
        "flight_time": "Bay ra Hà Nội (2h) + Xe đưa đón cao tốc tới Quảng Ninh"
    },
    "Lào Cai": {
        "coords": (22.3364, 103.8438),
        "cover": DEFAULT_IMG,
        "description": "Thị trấn trong sương kỳ ảo, nổi tiếng với đỉnh Fansipan - nóc nhà Đông Dương và những bản làng mộc mạc ẩn hiện bên ruộng bậc thang.",
        "avg_price": "3.000.000 - 5.000.000 VNĐ / người",
        "package_type": "Tour Sapa săn mây & Trải nghiệm bản làng 4D3N",
        "highlights": ["Chinh phục đỉnh Fansipan", "Khám phá bản Cát Cát mờ sương", "Check-in đèo Ô Quy Hồ tuyệt đẹp"],
        "avg_speed_kmh": 45,
        "flight_time": "Bay ra Hà Nội (2h) kết hợp xe giường nằm cao tốc lên Sapa"
    }
}

def calculate_metrics(target_coords, avg_speed_kmh):
    dist_km = geodesic(HO_CHI_MINH_COORDS, target_coords).km
    road_dist_km = dist_km * 1.3
    drive_hours = road_dist_km / avg_speed_kmh
    hours = int(drive_hours)
    minutes = int((drive_hours - hours) * 60)
    return round(road_dist_km, 1), f"{hours} giờ {minutes} phút"

st.title("Mai travel \n 🇻🇳 Khám Phá & Đặt Tour Du Lịch Việt Nam")
st.markdown("---")

current_tab = st.session_state["current_tab"]

# =========================================================
# TAB 1: TRANG CHỦ
# =========================================================
if current_tab == "Trang chủ":
    st.markdown("""
        <div class="hero-banner">
            <h1>App Du Lịch Hàng Đầu, Một Chạm Đi Bất Cứ Đâu</h1>
            <p>Trải nghiệm dịch vụ đặt tour, tra cứu khoảng cách và khám phá danh lam thắng cảnh Việt Nam dễ dàng nhất.</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🔥 **Các Tour Du Lịch Hot Nhất Hiện Nay**")
    search_query = st.text_input("🔍 Tìm kiếm nhanh điểm đến (Ví dụ: Đà Nẵng, Sapa, Hà Nội...)", "")

    filtered_destinations = {
        name: data for name, data in DESTINATIONS.items() 
        if search_query.lower() in name.lower() or search_query.lower() in data["description"].lower()
    }

    if not filtered_destinations:
        st.warning("Không tìm thấy điểm đến phù hợp!")
        filtered_destinations = DESTINATIONS

    cols = st.columns(1 if is_phone else 3)
    idx = 0
    for name, data in filtered_destinations.items():
        with cols[0 if is_phone else (idx % 3)]:
            with st.container(border=True):
                st.image(data["cover"], use_container_width=True)
                st.markdown(f"#### **{name}**")
                st.caption(f"📌 {data['package_type']}")
                st.write(data["description"][:85] + "...")
                st.success(f"💰 {data['avg_price'].split(' - ')[0]}")
                
                col_h1, col_h2 = st.columns(2)
                with col_h1:
                    if st.button(f"🚀 Xem tour", key=f"btn_hot_{name}", use_container_width=True):
                        st.session_state["selected_place"] = name
                        st.session_state["current_tab"] = "Bản đồ"
                        st.rerun()
                with col_h2:
                    is_saved = name in st.session_state["saved_tours"]
                    saved_label = "❤️ Đã lưu" if is_saved else "🤍 Lưu tin"
                    if st.button(saved_label, key=f"save_hot_{name}", use_container_width=True):
                        if is_saved:
                            st.session_state["saved_tours"].remove(name)
                        else:
                            st.session_state["saved_tours"].append(name)
                        st.rerun()
        idx += 1

# =========================================================
# TAB 2: BẢN ĐỒ
# =========================================================
elif current_tab == "Bản đồ":
    col_map, col_info = st.columns([1.2, 1]) if not is_phone else (st.container(), st.container())
    
    with col_map:
        st.subheader("📍 Bản Đồ Việt Nam")
        current_coords = DESTINATIONS[st.session_state["selected_place"]]["coords"]
        
        m = folium.Map(
            location=[(HO_CHI_MINH_COORDS[0] + current_coords[0]) / 2, (HO_CHI_MINH_COORDS[1] + current_coords[1]) / 2],
            zoom_start=6,
            tiles="https://mt1.google.com/vt/lyrs=m&hl=vi&x={x}&y={y}&z={z}",
            attr="Google Maps"
        )

        folium.Marker(HO_CHI_MINH_COORDS, popup="TP. Hồ Chí Minh", icon=folium.Icon(color="red", icon="star")).add_to(m)

        for name, data in DESTINATIONS.items():
            is_selected = (name == st.session_state["selected_place"])
            folium.Marker(data["coords"], popup=name, icon=folium.Icon(color="orange" if is_selected else "blue")).add_to(m)

        st_folium(m, width="100%", height=400)

    with col_info:
        selected_option = st.selectbox(
            "✨ Chọn điểm đến:", options=list(DESTINATIONS.keys()),
            index=list(DESTINATIONS.keys()).index(st.session_state["selected_place"])
        )

        if selected_option != st.session_state["selected_place"]:
            st.session_state["selected_place"] = selected_option
            st.rerun()

        current_data = DESTINATIONS[st.session_state["selected_place"]]
        road_dist, drive_time = calculate_metrics(current_data["coords"], current_data["avg_speed_kmh"])

        st.markdown(f"## 🌟 **{st.session_state['selected_place']}**")
        st.write(current_data["description"])
        st.info(f"🚗 Khoảng cách: **{road_dist} km** | Thời gian: **{drive_time}**")
        st.success(f"💰 Giá tham khảo: **{current_data['avg_price']}**")

        if st.button("🚀 ĐẶT TOUR NGAY", type="primary", use_container_width=True):
            booking_modal(st.session_state["selected_place"], current_data["avg_price"])

# =========================================================
# TAB 3: ĐÃ LƯU
# =========================================================
elif current_tab == "Đã lưu":
    st.markdown(f"### ❤️ **Tour Đã Lưu ({len(st.session_state['saved_tours'])})**")
    if not st.session_state["saved_tours"]:
        st.info("Bạn chưa lưu tour nào.")
    else:
        for name in st.session_state["saved_tours"]:
            if name in DESTINATIONS:
                data = DESTINATIONS[name]
                with st.container(border=True):
                    st.markdown(f"#### **{name}**")
                    st.write(f"💰 {data['avg_price']}")
                    if st.button("🗑️ Xóa khỏi lưu", key=f"del_{name}"):
                        st.session_state["saved_tours"].remove(name)
                        st.rerun()

# =========================================================
# TAB 4: ĐÃ ĐẶT
# =========================================================
elif current_tab == "Đã đặt":
    st.markdown(f"### 💼 **Lịch Sử Đặt Tour ({len(st.session_state['booked_tours'])})**")
    if not st.session_state["booked_tours"]:
        st.info("Bạn chưa đặt tour nào.")
    else:
        for booking in st.session_state["booked_tours"]:
            with st.container(border=True):
                st.markdown(f"#### 🌟 **{booking['tour']}**")
                st.write(f"👤 **Họ tên:** {booking['name']} | 📞 **SĐT:** {booking['phone']}")
                st.caption(f"🕒 Thời gian: {booking['time']}")

# =========================================================
# TAB 5: TÀI KHOẢN
# =========================================================
elif current_tab == "Tài khoản":
    st.markdown("### 👤 **Tài Khoản & Cài Đặt**")
    st.write("Phiên bản: 3.0 Ultra-Fast Edition")

# ---------------------------------------------------------
# THANH NAVIGATION CHUYỂN TAB CỰC MƯỢT CỐ ĐỊNH Ở ĐÁY (ST.CONTAINER BOTTOM)
# ---------------------------------------------------------
with st.container():
    tabs = ["Trang chủ", "Bản đồ", "Đã lưu", "Đã đặt", "Tài khoản"]
    
    # Dùng radio native Streamlit ghim đáy giúp chuyển tab ngay lập tức
    selected_tab = st.radio(
        "Navigation",
        options=tabs,
        index=tabs.index(st.session_state["current_tab"]) if st.session_state["current_tab"] in tabs else 0,
        horizontal=True,
        label_visibility="collapsed",
        key="bottom_nav_radio"
    )

    if selected_tab != st.session_state["current_tab"]:
        st.session_state["current_tab"] = selected_tab
        st.rerun()
