import streamlit as st

# Ẩn header, menu chính và footer của Streamlit
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic
import pandas as pd
import streamlit.components.v1 as components
import base64
import os

# ---------------------------------------------------------
# 1. Cấu hình trang web Streamlit
# ---------------------------------------------------------
st.set_page_config(
    page_title="Mai Travel - Du Lịch Việt Nam",
    page_icon="🇻🇳",
    layout="wide"
)

# Custom CSS tinh chỉnh giao diện và ép riêng thanh Menu nằm ngang trên điện thoại
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');

        /* Áp dụng phông chữ Roboto cho toàn bộ trang web */
        html, body, [class*="css"], * {
            font-family: 'Roboto', sans-serif !important;
        }
        
        .stButton>button {
            border-radius: 8px;
            font-weight: 600;
            font-family: 'Roboto', sans-serif !important;
        }

        /* Ép riêng khối Menu Nav đầu trang luôn nằm ngang 50% - 50% trên điện thoại */
        div.nav-row > [data-testid="stHorizontalBlock"] {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            gap: 10px !important;
        }
        div.nav-row > [data-testid="stHorizontalBlock"] > div {
            width: 50% !important;
            min-width: 0 !important;
            flex: 1 1 auto !important;
        }

        /* Banner phong cách Traveloka ở trang chủ */
        .hero-banner {
            background: linear-gradient(rgba(0, 0, 0, 0.45), rgba(0, 0, 0, 0.45)), 
                        url('https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1600&q=80');
            background-size: cover;
            background-position: center;
            padding: 60px 20px;
            border-radius: 16px;
            color: white;
            text-align: center;
            margin-bottom: 25px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.15);
        }
        .hero-banner h1 {
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 10px;
        }
        .hero-banner p {
            font-size: 15px;
            font-weight: 300;
        }
    </style>
""", unsafe_allow_html=True)

# Tọa độ mốc gốc: TP. Hồ Chí Minh
HO_CHI_MINH_COORDS = (10.7769, 106.7009)

# ---------------------------------------------------------
# 2. Dữ liệu các điểm du lịch với bộ hình ảnh chuẩn xác
# ---------------------------------------------------------
DESTINATIONS = {
    "Đà Nẵng": {
        "coords": (16.0544, 108.2022),
        "images": [
            "images/DN1.jpg", "images/DN2.jpg", "images/DN3.jpg", "images/DN4.jpg",
            "images/DN5.jpg", "images/DN6.jpg", "images/DN7.jpg", "images/DN8.jpg"
        ],
        "description": "Thành phố đáng sống nhất Việt Nam với Bãi biển Mỹ Khê, Cầu Vàng (Bà Nà Hills) và Ngũ Hành Sơn hùng vĩ.",
        "avg_price": "2.500.000 - 4.000.000 VNĐ / người",
        "package_type": "Combo Vé máy bay + Khách sạn 3D2N (Tiêu chuẩn 4 sao)",
        "highlights": ["Check-in Cầu Vàng Bà Nà Hills", "Khám phá Cầu Rồng phun lửa", "Tắm biển Mỹ Khê"],
        "avg_speed_kmh": 60,
        "flight_time": "1 giờ 20 phút (Bay trực tiếp từ TP.HCM)"
    },
    "Hà Nội": {
        "coords": (21.0285, 105.8542),
        "images": [
            "images/HN1.jpg", "images/HN2.jpg", "images/HN3.jpg", "images/HN4.jpg",
            "images/HN5.jpg", "images/HN6.jpg", "images/HN7.jpg", "images/HN8.jpg"
        ],
        "description": "Thủ đô nghìn năm văn hiến lưu giữ dấu ấn lịch sử, Hồ Hoàn Kiếm thơ mộng và văn hóa ẩm thực phố cổ đặc sắc.",
        "avg_price": "3.200.000 - 5.500.000 VNĐ / người",
        "package_type": "Tour Khám phá Phố Cổ & Ẩm thực 4D3N",
        "highlights": ["Dạo quanh Hồ Gươm & Phố Cổ", "Viếng Lăng Chủ tịch Hồ Chí Minh", "Thưởng thức Phở & Cà phê trứng"],
        "avg_speed_kmh": 60,
        "flight_time": "2 giờ 05 phút (Bay trực tiếp từ TP.HCM)"
    },
    "Đà Lạt (Lâm Đồng)": {
        "coords": (11.9404, 108.4583),
        "images": [
            "images/DL1.jpg", "images/DL2.jpg", "images/DL3.jpg", "images/DL4.jpg",
            "images/DL5.jpg", "images/DL6.jpg", "images/DL7.jpg", "images/DL8.jpg"
        ],
        "description": "Thành phố ngàn hoa với khí hậu ôn đới quanh năm mát mẻ, những đồi thông reo và các quán cà phê view thung lũng mộng mơ.",
        "avg_price": "1.800.000 - 3.000.000 VNĐ / người",
        "package_type": "Combo Xe Limousine khứ hồi + Khách sạn view đồi thông 3D2N",
        "highlights": ["Săn mây đồi chè Cầu Đất", "Khám phá Chợ Đêm Đà Lạt", "Check-in Hồ Xuân Hương"],
        "avg_speed_kmh": 50,
        "flight_time": "50 phút (Bay) hoặc 6-7 giờ (Xe Limousine từ TP.HCM)"
    },
    "Phú Quốc (Kiên Giang)": {
        "coords": (10.2899, 103.9840),
        "images": [
            "images/PQ1.jpg", "images/PQ2.jpg", "images/PQ3.jpg", "images/PQ4.jpg",
            "images/PQ5.jpg", "images/PQ6.jpg", "images/PQ7.jpg", "images/PQ8.jpg"
        ],
        "description": "Đảo Ngọc thiên đường nghỉ dưỡng hàng đầu với bãi cát trắng mịn như kem, nước biển trong ngọc bích và hoàng hôn tuyệt mỹ.",
        "avg_price": "3.500.000 - 6.000.000 VNĐ / người",
        "package_type": "Combo Resort 5 sao sát biển + Vé VinWonders 3D2N",
        "highlights": ["Tắm biển Bãi Sao", "Khám phá Grand World Phú Quốc", "Cáp treo vượt biển Hòn Thơm"],
        "avg_speed_kmh": 40,
        "flight_time": "1 giờ 00 phút (Bay trực tiếp từ TP.HCM)"
    },
    "Nha Trang (Khánh Hòa)": {
        "coords": (12.2388, 109.1967),
        "images": [
            "images/NT1.jpg", "images/NT2.jpg", "images/NT3.jpg", "images/NT4.jpg",
            "images/NT5.jpg", "images/NT6.jpg", "images/NT7.jpg", "images/NT8.jpg"
        ],
        "description": "Thành phố biển năng động sở hữu một trong những vịnh biển đẹp nhất hành tinh, thiên đường lặn ngắm san hô và hải sản tươi ngon.",
        "avg_price": "2.200.000 - 4.200.000 VNĐ / người",
        "package_type": "Tour Vịnh biển cao cấp & Nghỉ dưỡng 3D2N",
        "highlights": ["Vui chơi tại VinWonders Nha Trang", "Lặn ngắm san hô đảo Hòn Mun", "Thưởng thức đặc sản nem nướng"],
        "avg_speed_kmh": 60,
        "flight_time": "1 giờ 10 phút (Bay) hoặc 8 giờ (Tàu hỏa/Xe giường nằm)"
    },
    "Quảng Ninh": {
        "coords": (20.9101, 107.1839),
        "images": [
            "images/HL1.jpg", "images/HL2.jpg", "images/HL3.jpg", "images/HL4.jpg",
            "images/HL5.jpg", "images/HL6.jpg", "images/HL7.jpg", "images/HL8.jpg"
        ],
        "description": "Kỳ quan thiên nhiên thế giới UNESCO với hàng nghìn hòn đảo đá vôi kỳ vĩ nổi bật trên làn nước xanh ngọc bích huyền ảo.",
        "avg_price": "3.800.000 - 6.500.000 VNĐ / người",
        "package_type": "Tour Du thuyền 5 sao vịnh Hạ Long (Full board)",
        "highlights": ["Ngủ đêm trên du thuyền hạng sang", "Khám phá Hang Sửng Sốt", "Chèo thuyền Kayak đảo Ti Tốp"],
        "avg_speed_kmh": 60,
        "flight_time": "Bay ra Hà Nội (2h) + Xe đưa đón cao tốc tới Quảng Ninh"
    },
    "Sapa (Lào Cai)": {
        "coords": (22.3364, 103.8438),
        "images": [
            "images/SP1.jpg", "images/SP2.jpg", "images/SP3.jpg", "images/SP4.jpg",
            "images/SP5.jpg", "images/SP6.jpg", "images/SP7.jpg", "images/SP8.jpg"
        ],
        "description": "Th thị trấn trong sương kỳ ảo, nổi tiếng với đỉnh Fansipan - nóc nhà Đông Dương và những bản làng mộc mạc ẩn hiện bên ruộng bậc thang.",
        "avg_price": "3.000.000 - 5.000.000 VNĐ / người",
        "package_type": "Tour Sapa săn mây & Trải nghiệm bản làng 4D3N",
        "highlights": ["Chinh phục đỉnh Fansipan", "Khám phá bản Cát Cát mờ sương", "Check-in đèo Ô Quy Hồ tuyệt đẹp"],
        "avg_speed_kmh": 45,
        "flight_time": "Bay ra Hà Nội (2h) kết hợp xe giường nằm cao tốc lên Sapa"
    },
    "Cao Bằng": {
        "coords": (22.6656, 106.2607),
        "images": [
            "images/CB1.jpg", "images/CB2.jpg", "images/CB3.jpg", "images/CB4.jpg",
            "images/CB5.jpg", "images/CB6.jpg", "images/CB7.jpg", "images/CB8.jpg"
        ],
        "description": "Cao Bằng là một tỉnh miền núi thuộc vùng Đông Bắc Việt Nam, nổi bật với danh hiệu 'miền non nước ngàn năm' và sở hữu Thác Bản Giốc hùng vĩ.",
        "avg_price": "6.500.000 - 12.500.000 VNĐ / người",
        "package_type": "Tour Non nước Cao Bằng 3D2N",
        "highlights": ["Thác Bản Giốc", "Động Ngườm Ngao", "Hồ Thang Hen"],
        "avg_speed_kmh": 45,
        "flight_time": "Bay ra Hà Nội (2h) kết hợp xe khách lên Cao Bằng"
    },
    "Bắc Kạn": {
        "coords": (22.161335, 105.830498),
        "images": [
            "images/BK1.jpg", "images/BK2.jpg", "images/BK3.jpg", "images/BK4.jpg",
            "images/BK5.jpg", "images/BK6.jpg", "images/BK7.jpg", "images/BK8.jpg"
        ],
        "description": "Bắc Kạn là một tỉnh thuộc vùng Đông Bắc Bộ, Việt Nam, nổi tiếng với hồ Ba Bể thơ mộng và hệ sinh thái nguyên sinh.",
        "avg_price": "5.500.000 - 10.000.000 VNĐ / người",
        "package_type": "Tour Khám phá Hồ Ba Bể 3D2N",
        "highlights": ["Thuyền tham quan hồ Ba Bể", "Động Puông", "Thác Đầu Đẳng"],
        "avg_speed_kmh": 45,
        "flight_time": "Bay ra Hà Nội (2h) kết hợp xe khách lên Bắc Kạn"
    },
    "Tuyên Quang": {
        "coords": (21.8236, 105.2142),
        "images": [
            "images/TQ1.jpg", "images/TQ2.jpg", "images/TQ3.jpg", "images/TQ4.jpg",
            "images/TQ5.jpg", "images/TQ6.jpg", "images/TQ7.jpg", "images/TQ8.jpg"
        ],
        "description": "Bắc Kạn là một tỉnh thuộc vùng Đông Bắc Bộ, Việt Nam, nổi tiếng với hồ Ba Bể thơ mộng và hệ sinh thái nguyên sinh.",
        "avg_price": "5.500.000 - 10.000.000 VNĐ / người",
        "package_type": "Tour Khám phá Hồ Ba Bể 3D2N",
        "highlights": ["Thuyền tham quan hồ Ba Bể", "Động Puông", "Thác Đầu Đẳng"],
        "avg_speed_kmh": 45,
        "flight_time": "Bay ra Hà Nội (2h) kết hợp xe khách lên Bắc Kạn"
    },
    "Lai Châu": {
        "coords": (22.3992, 103.4392),
        "images": [
            "images/LC1.jpg", "images/LC2.jpg", "images/LC3.jpg", "images/LC4.jpg",
            "images/LC5.jpg", "images/LC6.jpg", "images/LC7.jpg", "images/LC8.jpg"
        ],
        "description": " Lai Châu nổi tiếng với thiên nhiên hoang sơ, hùng vĩ của núi rừng Tây Bắc, những cung đèo hiểm trở, biển mây bồng bềnh và các bản làng văn hóa đặc sắc.",
        "avg_price": "5.500.000 - 10.000.000 VNĐ / người",
        "package_type": "Tour Khám phá Hồ Ba Bể 3D2N",
        "highlights": ["Đèo Ô Quy Hồ", "Cao nguyên Sìn Hồ", "Đồi chè Tân Uyên"],
        "avg_speed_kmh": 45,
        "flight_time": "Bay ra Hà Nội (2h) kết hợp xe khách lên Bắc Kạn"
    }
}

# ---------------------------------------------------------
# 3. Hàm tính toán khoảng cách & thời gian di chuyển
# ---------------------------------------------------------
def calculate_metrics(target_coords, avg_speed_kmh):
    dist_km = geodesic(HO_CHI_MINH_COORDS, target_coords).km
    road_dist_km = dist_km * 1.3
    drive_hours = road_dist_km / avg_speed_kmh
    hours = int(drive_hours)
    minutes = int((drive_hours - hours) * 60)
    return round(road_dist_km, 1), f"{hours} giờ {minutes} phút"

def get_image_base64(path):
    if path.startswith("http"):
        return path
    try:
        if os.path.exists(path):
            with open(path, "rb") as f:
                data = f.read()
            encoded = base64.b64encode(data).decode()
            return f"data:image/jpeg;base64,{encoded}"
    except Exception:
        pass
    return path

# Quản lý trạng thái
if "selected_place" not in st.session_state:
    st.session_state["selected_place"] = "Đà Nẵng"

if "zoom_overview" not in st.session_state:
    st.session_state["zoom_overview"] = False

if "nav_page" not in st.session_state:
    st.session_state["nav_page"] = "🏠 Trang Chủ"

# ---------------------------------------------------------
# 4. Thanh điều hướng Tab Nằm Ngang (Đã bọc div.nav-row)
# ---------------------------------------------------------
st.title("Mai travel \n 🇻🇳 Khám Phá & Đặt Tour Du Lịch Việt Nam")

st.markdown('<div class="nav-row">', unsafe_allow_html=True)
nav_col1, nav_col2 = st.columns([1, 1])

with nav_col1:
    btn_type_home = "primary" if st.session_state["nav_page"] == "🏠 Trang Chủ" else "secondary"
    if st.button("🏠 Trang Chủ", type=btn_type_home, use_container_width=True):
        st.session_state["nav_page"] = "🏠 Trang Chủ"
        st.rerun()

with nav_col2:
    btn_type_booking = "primary" if st.session_state["nav_page"] == "🗺️ Tra Cứu & Đặt Tour" else "secondary"
    if st.button("🗺️ Đặt Tour", type=btn_type_booking, use_container_width=True):
        st.session_state["nav_page"] = "🗺️ Tra Cứu & Đặt Tour"
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# =========================================================
# GIAO DIỆN TRANG CHỦ (HOME PAGE)
# =========================================================
if st.session_state["nav_page"] == "🏠 Trang Chủ":
    st.markdown("""
        <div class="hero-banner">
            <h1>App Du Lịch Hàng Đầu, Một Chạm Đi Bất Cứ Đâu</h1>
            <p>Trải nghiệm dịch vụ đặt tour, tra cứu khoảng cách và khám phá danh lam thắng cảnh Việt Nam dễ dàng nhất.</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🔥 **Các Tour Du Lịch Hot Nhất Hiện Nay**")
    st.write("Lựa chọn những điểm đến hàng đầu được yêu thích nhất trong mùa này:")

    # Hiển thị danh sách tour hot dạng lưới 3 cột
    cols = st.columns(3)
    idx = 0
    for name, data in DESTINATIONS.items():
        with cols[idx % 3]:
            with st.container(border=True):
                cover_img = get_image_base64(data["images"][0])
                st.image(cover_img, use_container_width=True)
                st.markdown(f"#### **{name}**")
                st.caption(f"📌 {data['package_type']}")
                st.write(data["description"][:85] + "...")
                st.success(f"💰 {data['avg_price'].split(' - ')[0]}")
                
                if st.button(f"🚀 Xem & Đặt Tour", key=f"btn_hot_{name}", use_container_width=True):
                    st.session_state["selected_place"] = name
                    st.session_state["nav_page"] = "🗺️ Tra Cứu & Đặt Tour"
                    st.rerun()
        idx += 1

# =========================================================
# GIAO DIỆN TRANG ĐẶT TOUR & BẢN ĐỒ (BOOKING PAGE)
# =========================================================
else:
    col_map, col_info = st.columns([1.2, 1])

    with col_map:
        st.subheader("📍 Bản Đồ Việt Nam")
        
        col_btn1, col_btn2 = st.columns([1, 1])
        with col_btn1:
            if st.button("🔍 Focus Điểm Đến", use_container_width=True):
                st.session_state["zoom_overview"] = False
                st.rerun()
        with col_btn2:
            if st.button("🌍 Toàn Cảnh Việt Nam", use_container_width=True):
                st.session_state["zoom_overview"] = True
                st.rerun()

        if st.session_state["zoom_overview"]:
            map_center = [16.0000, 106.0000]
            map_zoom = 5
        else:
            current_coords = DESTINATIONS[st.session_state["selected_place"]]["coords"]
            map_center = [
                (HO_CHI_MINH_COORDS[0] + current_coords[0]) / 2,
                (HO_CHI_MINH_COORDS[1] + current_coords[1]) / 2
            ]
            map_zoom = 7

        m = folium.Map(
            location=map_center,
            zoom_start=map_zoom,
            tiles="https://mt1.google.com/vt/lyrs=m&hl=vi&x={x}&y={y}&z={z}",
            attr="Google Maps",
            attribution_control=False
        )

        folium.Marker(
            location=HO_CHI_MINH_COORDS,
            popup=folium.Popup("<div style='white-space: nowrap;'>Mốc xuất phát: TP. Hồ Chí Minh</div>", max_width=300),
            tooltip="Mốc xuất phát: TP. Hồ Chí Minh",
            icon=folium.Icon(color="red", icon="star")
        ).add_to(m)

        for name, data in DESTINATIONS.items():
            is_selected = (name == st.session_state["selected_place"])
            marker_color = "orange" if is_selected else "blue"
            
            folium.Marker(
                location=data["coords"],
                popup=folium.Popup(f"<div style='white-space: nowrap;'>{name}</div>", max_width=300),
                tooltip=f"Xem {name}",
                icon=folium.Icon(color=marker_color, icon="info-sign")
            ).add_to(m)

            if is_selected:
                folium.PolyLine(
                    locations=[HO_CHI_MINH_COORDS, data["coords"]],
                    color="red",
                    weight=3,
                    opacity=0.8,
                    dash_array="5, 10"
                ).add_to(m)

        map_data = st_folium(m, width="100%", height=485)

        clicked_place = None
        if map_data:
            if map_data.get("last_object_clicked_popup"):
                clicked_place = map_data["last_object_clicked_popup"]
            elif map_data.get("last_clicked"):
                click_coord = (map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"])
                for name, data in DESTINATIONS.items():
                    if geodesic(click_coord, data["coords"]).km < 40:
                        clicked_place = name
                        break

        if clicked_place and clicked_place in DESTINATIONS and clicked_place != st.session_state["selected_place"]:
            st.session_state["selected_place"] = clicked_place
            st.session_state["zoom_overview"] = False
            st.rerun()

    with col_info:
        st.markdown("### ✈️ Tra Cứu & Đặt Tour Du Lịch")
        
        selected_option = st.selectbox(
            "✨ Lựa chọn điểm đến mơ ước của bạn:",
            options=list(DESTINATIONS.keys()),
            index=list(DESTINATIONS.keys()).index(st.session_state["selected_place"])
        )

        if selected_option != st.session_state["selected_place"]:
            st.session_state["selected_place"] = selected_option
            st.session_state["zoom_overview"] = False
            st.rerun()

        current_data = DESTINATIONS[st.session_state["selected_place"]]
        road_dist, drive_time = calculate_metrics(current_data["coords"], current_data["avg_speed_kmh"])
        current_images = current_data["images"]

        with st.container(border=True):
            items_html = ""
            for idx, img_path in enumerate(current_images):
                img_src = get_image_base64(img_path)
                items_html += f"""
                    <div class="tiktok-item">
                        <img src="{img_src}" alt="Image {idx+1}">
                        <div class="tiktok-badge">📷 {idx+1}/{len(current_images)}</div>
                    </div>
                """

            carousel_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
            <style>
                .tiktok-carousel {{
                    display: flex;
                    overflow-x: auto;
                    scroll-snap-type: x mandatory;
                    scroll-behavior: smooth;
                    -webkit-overflow-scrolling: touch;
                    border-radius: 12px;
                    gap: 12px;
                    padding-bottom: 8px;
                }}
                .tiktok-carousel::-webkit-scrollbar {{
                    display: none;
                }}
                .tiktok-carousel {{
                    -ms-overflow-style: none;
                    scrollbar-width: none;
                }}
                .tiktok-item {{
                    flex: 0 0 100%;
                    scroll-snap-align: center;
                    border-radius: 12px;
                    overflow: hidden;
                    position: relative;
                    aspect-ratio: 16 / 9;
                    background-color: #f0f2f5;
                    box-shadow: 0 4px 14px rgba(0,0,0,0.12);
                }}
                .tiktok-item img {{
                    width: 100%;
                    height: 100%;
                    object-fit: cover;
                    border-radius: 12px;
                }}
                .tiktok-badge {{
                    position: absolute;
                    top: 10px;
                    right: 10px;
                    background: rgba(0, 0, 0, 0.65);
                    color: white;
                    padding: 4px 10px;
                    border-radius: 20px;
                    font-size: 12px;
                    font-weight: 500;
                    font-family: 'Roboto', sans-serif;
                }}
            </style>
            </head>
            <body>
                <div class="tiktok-carousel">
                    {items_html}
                </div>
            </body>
            </html>
            """
            components.html(carousel_html, height=310, scrolling=False)

            st.markdown(f"## 🌟 **{st.session_state['selected_place']}**")
            st.caption(f"📌 *{current_data['package_type']}*")
            st.write(current_data["description"])
            
            st.markdown("---")
            st.markdown("##### 🚗 **Thông Tin Di Chuyển (Xuất phát từ TP.HCM)**")
            
            col_m1, col_m2 = st.columns(2)
            col_m1.metric(label="Khoảng cách ước tính", value=f"{road_dist} km")
            col_m2.metric(label="Thời gian ô tô/xe khách", value=drive_time)
            
            st.info(f"✈️ **Gợi ý di chuyển hàng không:** {current_data['flight_time']}")

            st.markdown("##### 💳 **Báo Giá & Ưu Đãi Trọn Gói**")
            st.success(f"**Mức giá tham khảo:** {current_data['avg_price']}")

            st.markdown("##### ⭐ **Điểm Nhấn Trải Nghiệm Nổi Bật**")
            for tag in current_data["highlights"]:
                st.markdown(f"✔️ {tag}")

            st.markdown("---")
            
            col_book1, col_book2 = st.columns([2, 1])
            with col_book1:
                booking_btn = st.button("🚀 ĐẶT TOUR NGAY", type="primary", use_container_width=True)
            with col_book2:
                saved_btn = st.button("❤️ Lưu tin", use_container_width=True)
                
            if booking_btn:
                st.balloons()
                st.success(f"🎉 Đã gửi yêu cầu giữ chỗ tour **{st.session_state['selected_place']}** thành công! Nhân viên tư vấn sẽ liên hệ với bạn trong ít phút.")
            if saved_btn:
                st.toast("Đã thêm vào danh sách yêu thích!", icon="❤️")
