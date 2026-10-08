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

# Tọa độ mốc gốc: TP. Hồ Chí Minh
HO_CHI_MINH_COORDS = (10.7769, 106.7009)

# ---------------------------------------------------------
# 2. Dữ liệu các điểm du lịch tiêu biểu tại Việt Nam
# (Bao gồm thông tin, giá vé/tour tham khảo từ các trang du lịch)
# ---------------------------------------------------------
DESTINATIONS = {
    "Đà Nẵng": {
        "coords": (16.0544, 108.2022),
        "description": "Thành phố đáng sống nhất Việt Nam với Bãi biển Mỹ Khê, Cầu Vàng (Bà Nà Hills) và Ngũ Hành Sơn.",
        "avg_price": "2.500.000 - 4.000.000 VNĐ / người (Vé máy bay + Khách sạn 3D2N)",
        "highlights": ["Bà Nà Hills", "Cầu Rồng", "Biển Mỹ Khê"],
        "avg_speed_kmh": 60, # Tốc độ di chuyển đường bộ tham khảo
        "flight_time": "1 giờ 20 phút (Bay từ TP.HCM)"
    },
    "Hà Nội": {
        "coords": (21.0285, 105.8542),
        "description": "Thủ đô nghìn năm văn hiến với Hồ Hoàn Kiếm, Phố cổ 36 phố phường và nét ẩm thực độc đáo.",
        "avg_price": "3.200.000 - 5.500.000 VNĐ / người (Tour 4D3N)",
        "highlights": ["Hồ Gươm", "Lăng Bác", "Phố cổ Hà Nội"],
        "avg_speed_kmh": 60,
        "flight_time": "2 giờ 05 phút (Bay từ TP.HCM)"
    },
    "Đà Lạt (Lâm Đồng)": {
        "coords": (11.9404, 108.4583),
        "description": "Thành phố ngàn hoa với khí hậu ôn đới quanh năm, khung cảnh mộng mơ và nhiều điểm check-in hấp dẫn.",
        "avg_price": "1.800.000 - 3.000.000 VNĐ / người (Xe limousine + Khách sạn 3D2N)",
        "highlights": ["Hồ Xuân Hương", "Langbiang", "Chợ Đêm Đà Lạt"],
        "avg_speed_kmh": 50,
        "flight_time": "50 phút (Bay) hoặc 6-7 giờ (Xe khách từ TP.HCM)"
    },
    "Phú Quốc (Kiên Giang)": {
        "coords": (10.2899, 103.9840),
        "description": "Đảo Ngọc thiên đường với bãi cát trắng mịn, nước biển trong xanh và các khu nghỉ dưỡng sang trọng.",
        "avg_price": "3.500.000 - 6.000.000 VNĐ / người (Combo vé bay + Resort 3D2N)",
        "highlights": ["Bãi Sao", "Grand World", "Hòn Thơm"],
        "avg_speed_kmh": 40,
        "flight_time": "1 giờ 00 phút (Bay từ TP.HCM)"
    },
    "Nha Trang (Khánh Hòa)": {
        "coords": (12.2388, 109.1967),
        "description": "Thành phố biển sôi động với các vịnh biển đẹp bậc nhất thế giới và chuỗi công viên giải trí VinWonders.",
        "avg_price": "2.200.000 - 4.200.000 VNĐ / người",
        "highlights": ["VinWonders", "Đảo Hòn Mun", "Tháp Bà Ponagar"],
        "avg_speed_kmh": 60,
        "flight_time": "1 giờ 10 phút (Bay) hoặc 8 giờ (Tàu hỏa/Xe khách)"
    },
    "Vịnh Hạ Long (Quảng Ninh)": {
        "coords": (20.9101, 107.1839),
        "description": "Di sản thiên nhiên thế giới UNESCO với hàng nghìn đảo đá vôi kỳ vĩ rải rác trên làn nước xanh ngọc.",
        "avg_price": "3.800.000 - 6.500.000 VNĐ / người (Tour du thuyền 5 sao)",
        "highlights": ["Hang Sửng Sốt", "Đảo Ti Tốp", "Vịnh Bái Tử Long"],
        "avg_speed_kmh": 60,
        "flight_time": "2 giờ 15 phút (Bay tới Vân Đồn + Xe chuyển tiếp)"
    },
    "Sapa (Lào Cai)": {
        "coords": (22.3364, 103.8438),
        "description": "Thị trấn trong sương nổi tiếng với đỉnh Fansipan - nóc nhà Đông Dương và những thửa ruộng bậc thang tuyệt đẹp.",
        "avg_price": "3.000.000 - 5.000.000 VNĐ / người",
        "highlights": ["Đỉnh Fansipan", "Bản Cát Cát", "Đèo O Quy Hồ"],
        "avg_speed_kmh": 45,
        "flight_time": "Bay ra Hà Nội (2h) + Xe giường nằm (5-6h)"
    }
}

# ---------------------------------------------------------
# 3. Hàm tính toán khoảng cách & thời gian di chuyển
# ---------------------------------------------------------
def calculate_metrics(target_coords, avg_speed_kmh):
    # Tính khoảng cách theo đường chim bay (Geodesic)
    dist_km = geodesic(HO_CHI_MINH_COORDS, target_coords).km
    
    # Ước tính khoảng cách đường bộ (xấp xỉ x 1.3 so với đường chim bay)
    road_dist_km = dist_km * 1.3
    
    # Tính thời gian đường bộ (Giờ)
    drive_hours = road_dist_km / avg_speed_kmh
    hours = int(drive_hours)
    minutes = int((drive_hours - hours) * 60)
    
    return round(road_dist_km, 1), f"{hours} giờ {minutes} phút"

# ---------------------------------------------------------
# 4. Giao diện ứng dụng Streamlit
# ---------------------------------------------------------
st.title("🇻🇳 Khám Phá & Đặt Tour Du Lịch Việt Nam")
st.markdown("---")

# Chia giao diện làm 2 cột: Cột trái hiện bản đồ, Cột phải hiện thông tin địa điểm
col_map, col_info = st.columns([1.2, 1])

# Quản lý trạng thái địa điểm đang được chọn trong Session State
if "selected_place" not in st.session_state:
    st.session_state["selected_place"] = "Đà Nẵng"

with col_map:
    st.subheader("📍 Bản Đồ Việt Nam Interactiv e")
    st.caption("💡 *Bấm vào các điểm mốc trên bản đồ hoặc chọn danh sách bên phải để xem thông tin chi tiết.*")

    # Tạo bản đồ Folium trung tâm tại Việt Nam
   m = folium.Map(
    location=[16.0000, 106.0000],
    zoom_start=5,
    tiles="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png",
    attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
)
    # Đặt Marker mốc TP. Hồ Chí Minh
    folium.Marker(
        location=HO_CHI_MINH_COORDS,
        popup="Mốc xuất phát: TP. Hồ Chí Minh",
        tooltip="📍 Mốc xuất phát: TP. Hồ Chí Minh",
        icon=folium.Icon(color="red", icon="star")
    ).add_to(m)

    # Đặt Marker các địa điểm du lịch
    for name, data in DESTINATIONS.items():
        is_selected = (name == st.session_state["selected_place"])
        marker_color = "orange" if is_selected else "blue"
        
        folium.Marker(
            location=data["coords"],
            popup=name,
            tooltip=f"Xem {name}",
            icon=folium.Icon(color=marker_color, icon="info-sign")
        ).add_to(m)

        # Nếu địa điểm được chọn, vẽ đường nối từ TP.HCM tới điểm đó
        if is_selected:
            folium.PolyLine(
                locations=[HO_CHI_MINH_COORDS, data["coords"]],
                color="red",
                weight=3,
                opacity=0.8,
                dash_array="5, 10"
            ).add_to(m)

    # Hiển thị bản đồ tương tác
    map_data = st_folium(m, width="100%", height=500)

    # Xử lý sự kiện khi bấm vào Marker trên bản đồ
    if map_data and map_data.get("last_object_clicked_popup"):
        clicked_name = map_data["last_object_clicked_popup"]
        if clicked_name in DESTINATIONS and clicked_name != st.session_state["selected_place"]:
            st.session_state["selected_place"] = clicked_name
            st.rerun()

with col_info:
    st.subheader("🔎 Thông Tin Chi Tiết Điểm Đến")
    
    # Selector cho phép chọn nhanh từ danh sách
    selected_option = st.selectbox(
        "Chọn địa điểm khám phá:",
        options=list(DESTINATIONS.keys()),
        index=list(DESTINATIONS.keys()).index(st.session_state["selected_place"])
    )

    if selected_option != st.session_state["selected_place"]:
        st.session_state["selected_place"] = selected_option
        st.rerun()

    current_data = DESTINATIONS[st.session_state["selected_place"]]
    road_dist, drive_time = calculate_metrics(current_data["coords"], current_data["avg_speed_kmh"])

    # Hiển thị thông tin tổng quan bằng hiệu ứng Container
    with st.container(border=True):
        st.markdown(f"### 🚩 **{st.session_state['selected_place']}**")
        st.write(f"📝 {current_data['description']}")
        
        st.markdown("#### 🚗 **Khoảng Cách & Thời Gian (Từ TP.HCM)**")
        col_m1, col_m2 = st.columns(2)
        col_m1.metric(label="Khoảng cách đường bộ (Ước tính)", value=f"{road_dist} km")
        col_m2.metric(label="Thời gian xe chạy", value=drive_time)
        
        st.info(f"✈️ **Thời gian bay dự kiến:** {current_data['flight_time']}")

        st.markdown("#### 💰 **Chi Phí Tham Khảo (Cập nhật từ các trang Booking)**")
        st.success(f"**Mức giá ước tính:** {current_data['avg_price']}")

        st.markdown("#### 🌟 **Điểm Tham Quan Nổi Bật**")
        for tag in current_data["highlights"]:
            st.markdown(f"- {tag}")

        st.markdown("---")
        if st.button(f"🎟️ Đặt Tour Đến {st.session_state['selected_place']} Ngay", type="primary", use_container_width=True):
            st.toast(f"Đã ghi nhận yêu cầu đặt tour đi {st.session_state['selected_place']}!", icon="✅")
