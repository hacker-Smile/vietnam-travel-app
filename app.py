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
        .stButton>button {
            border-radius: 8px;
            font-weight: 600;
        }
        div.stMetric {
            background-color: #f8f9fa;
            padding: 10px 15px;
            border-radius: 10px;
            border: 1px solid #e9ecef;
        }
    </style>
""", unsafe_allow_html=True)

# Tọa độ mốc gốc: TP. Hồ Chí Minh
HO_CHI_MINH_COORDS = (10.7769, 106.7009)

# ---------------------------------------------------------
# 2. Dữ liệu các điểm du lịch (Mỗi nơi có đúng 8 hình ảnh đặc sắc)
# ---------------------------------------------------------
DESTINATIONS = {
    "Đà Nẵng": {
        "coords": (16.0544, 108.2022),
        "images": [
            "https://images.unsplash.com/photo-1559592413-7cec4d0cae2b?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1578637387939-43c525550085?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1569154941061-e231b4725ef1?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1528127269322-539801943592?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?auto=format&fit=crop&w=800&q=80"
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
            "https://images.unsplash.com/photo-1509042239860-f550ce710b93?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1584968153401-44755f448cbc?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1555881400-74d7acaacd8b?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1569154941061-e231b4725ef1?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1590523277543-a94d2e4eb00b?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1544644181-1484b3fdfc62?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1528127269322-539801943592?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=800&q=80"
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
            "https://images.unsplash.com/photo-1590523277543-a94d2e4eb00b?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1559592413-7cec4d0cae2b?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1578637387939-43c525550085?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1569154941061-e231b4725ef1?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1528127269322-539801943592?auto=format&fit=crop&w=800&q=80"
        ],
        "description": "Thành phố ngàn hoa với khí hậu ôn đới quanh năm mát mẻ, những đồi thông reo và các quán cà phê view thung lũng mộng mơ.",
        "avg_price": "1.800.000 - 3.000.000 VNĐ / người",
        "package_type": "Combo Xe Limousine khứ hồi + Khách sạn view đồi thông 3D2N",
        "highlights": ["Săn mây đồi chè Cầu Đất", "Khám phá Chợ Đêm Đà Lạt", "Check-in Hồ Xuân Hương"],
        "avg_speed_kmh":
