import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic
import pandas as pd

# ---------------------------------------------------------
# 1. Cấu hình trang web Streamlit
# ---------------------------------------------------------
st.set_page_config(
    page_title="Việt Nam Travel & Booking Guide",
    page_icon="🇻🇳",
    layout="wide"
)

# Custom CSS tinh chỉnh giao diện chuyên nghiệp
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');

        /* Áp dụng phông chữ Roboto cho toàn bộ trang web và các thành phần */
        html, body, [class*="css"], * {
            font-family: 'Roboto', sans-serif !important;
        }
        
        .stButton>button {
            border-radius: 8px;
            font-weight: 600;
            font-family: 'Roboto', sans-serif !important;
        }
    </style>
""", unsafe_allow_html=True)

# Tọa độ mốc gốc: TP. Hồ Chí Minh
HO_CHI_MINH_COORDS = (10.7769, 106.7009)

# ---------------------------------------------------------
# 2. Dữ liệu các điểm du lịch với bộ hình ảnh chuẩn xác tuyệt đối 100%
# ---------------------------------------------------------
DESTINATIONS = {
    "Đà Nẵng": {
        "coords": (16.0544, 108.2022),
        "images": [
            "images/DN1.jpg",
            "images/DN2.jpg",
            "images/DN3.jpg",
            "images/DN4.jpg",
            "images/DN5.jpg",
            "images/DN6.jpg",
            "images/DN7.jpg",
            "images/DN8.jpg"
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
            "images/HN1.jpg",
            "images/HN2.jpg",
            "images/HN3.jpg",
            "images/HN4.jpg",
            "images/HN5.jpg",
            "images/HN6.jpg",
            "images/HN7.jpg",
            "images/HN8.jpg"
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
            "images/DL1.jpg",
            "images/DL2.jpg",
            "images/DL3.jpg",
            "images/DL4.jpg",
            "images/DL5.jpg",
            "images/DL6.jpg",
            "images/DL7.jpg",
            "images/DL8.jpg"
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
            "images/PQ1.jpg",
            "images/PQ2.jpg",
            "images/PQ3.jpg",
            "images/PQ4.jpg",
            "images/PQ5.jpg",
            "images/PQ6.jpg",
            "images/PQ7.jpg",
            "images/PQ8.jpg"
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
            "images/NT1.jpg",
            "images/NT2.jpg",
            "images/NT3.jpg",
            "images/NT4.jpg",
            "images/NT5.jpg",
            "images/NT6.jpg",
            "images/NT7.jpg",
            "images/NT8.jpg"
        ],
        "description": "Thành phố biển năng động sở hữu một trong những vịnh biển đẹp nhất hành tinh, thiên đường lặn ngắm san hô và hải sản tươi ngon.",
        "avg_price": "2.200.000 - 4.200.000 VNĐ / người",
        "package_type": "Tour Vịnh biển cao cấp & Nghỉ dưỡng 3D2N",
        "highlights": ["Vui chơi tại VinWonders Nha Trang", "Lặn ngắm san hô đảo Hòn Mun", "Thưởng thức đặc sản nem nướng"],
        "avg_speed_kmh": 60,
        "flight_time": "1 giờ 10 phút (Bay) hoặc 8 giờ (Tàu hỏa/Xe giường nằm)"
    },
    "Vịnh Hạ Long (Quảng Ninh)": {
        "coords": (20.9101, 107.1839),
        "images": [
            "images/HL1.jpg",
            "images/HL2.jpg",
            "images/HL3.jpg",
            "images/HL4.jpg",
            "images/HL5.jpg",
            "images/HL6.jpg",
            "images/HL7.jpg",
            "images/HL8.jpg"
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
            "images/SP1.jpg",
            "images/SP2.jpg",
            "images/SP3.jpg",
            "images/SP4.jpg",
            "images/SP5.jpg",
            "images/SP6.jpg",
            "images/SP7.jpg",
            "images/SP8.jpg"
        ],
        "description": "Thị trấn trong sương kỳ ảo, nổi tiếng với đỉnh Fansipan - nóc nhà Đông Dương và những bản làng mộc mạc ẩn hiện bên ruộng bậc thang.",
        "avg_price": "3.000.000 - 5.000.000 VNĐ / người",
        "package_type": "Tour Sapa săn mây & Trải nghiệm bản làng 4D3N",
        "highlights": ["Chinh phục đỉnh Fansipan", "Khám phá bản Cát Cát mờ sương", "Check-in đèo Ô Quy Hồ tuyệt đẹp"],
        "avg_speed_kmh": 45,
        "flight_time": "Bay ra Hà Nội (2h) kết hợp xe giường nằm cao tốc lên Sapa"
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

# ---------------------------------------------------------
# 4. Giao diện ứng dụng Streamlit
# ---------------------------------------------------------
st.title("Mai travel \n 🇻🇳 Khám Phá & Đặt Tour Du Lịch Việt Nam")
st.markdown("---")

col_map, col_info = st.columns([1.2, 1])

# Quản lý trạng thái
if "selected_place" not in st.session_state:
    st.session_state["selected_place"] = "Đà Nẵng"

if "zoom_overview" not in st.session_state:
    st.session_state["zoom_overview"] = False

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

    # Đưa white-space: nowrap thẳng vào HTML của Popup để chữ luôn nằm ngang hàng tuyệt đối
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

    # Bắt sự kiện đổi địa điểm linh hoạt: Bằng Popup hoặc bằng khoảng cách tọa độ click chuột trực tiếp lên bản đồ
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
        st.session_state[f"img_idx_{selected_option}"] = 0
        st.rerun()

    current_data = DESTINATIONS[st.session_state["selected_place"]]
    road_dist, drive_time = calculate_metrics(current_data["coords"], current_data["avg_speed_kmh"])

    current_images = current_data["images"]

    with st.container(border=True):
        img_key = f"img_idx_{st.session_state['selected_place']}"
        if img_key not in st.session_state:
            st.session_state[img_key] = 0

        current_idx = st.session_state[img_key]

        st.image(current_images[current_idx], use_container_width=True)

        col_prev, col_text, col_next = st.columns([1, 4, 1])

        with col_prev:
            if st.button("◀", key=f"prev_{st.session_state['selected_place']}", use_container_width=True):
                if st.session_state[img_key] > 0:
                    st.session_state[img_key] -= 1
                else:
                    st.session_state[img_key] = len(current_images) - 1
                st.rerun()

        with col_text:
            st.markdown(f"<div style='text-align: center; padding-top: 8px; font-weight: 600; color: #495057; font-size: 14px;'>📷 Đang xem hình {current_idx + 1} / {len(current_images)}</div>", unsafe_allow_html=True)

        with col_next:
            if st.button("▶", key=f"next_{st.session_state['selected_place']}", use_container_width=True):
                if st.session_state[img_key] < len(current_images) - 1:
                    st.session_state[img_key] += 1
                else:
                    st.session_state[img_key] = 0
                st.rerun()

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
