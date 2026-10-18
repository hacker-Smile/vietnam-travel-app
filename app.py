import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic
import pandas as pd
import streamlit.components.v1 as components
import base64
import os
import requests
import json
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
FORMSPREE_URL = "https://formspree.io/f/xrpeylye"

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
# HỆ THỐNG ĐỒNG BỘ TRẠNG THÁI VỚI URL
# ---------------------------------------------------------
def save_state_to_query_params():
    st.query_params["tab"] = st.session_state.get("current_tab", "home")
    
    if st.session_state.get("saved_tours"):
        st.query_params["saved"] = ",".join(st.session_state["saved_tours"])
    else:
        st.query_params.pop("saved", None)
        
    if st.session_state.get("booked_tours"):
        try:
            json_str = json.dumps(st.session_state["booked_tours"], ensure_ascii=False)
            b64_str = base64.urlsafe_b64encode(json_str.encode("utf-8")).decode("utf-8")
            st.query_params["booked"] = b64_str
        except Exception:
            pass
    else:
        st.query_params.pop("booked", None)

def load_state_from_query_params():
    if "selected_place" not in st.session_state:
        st.session_state["selected_place"] = "Đà Nẵng"
    if "zoom_overview" not in st.session_state:
        st.session_state["zoom_overview"] = False

    if "tab" in st.query_params:
        st.session_state["current_tab"] = st.query_params["tab"]
    else:
        if "current_tab" not in st.session_state:
            st.session_state["current_tab"] = "home"

    if "saved" in st.query_params:
        val = st.query_params["saved"]
        st.session_state["saved_tours"] = val.split(",") if val else []
    else:
        if "saved_tours" not in st.session_state:
            st.session_state["saved_tours"] = []

    if "booked" in st.query_params:
        try:
            b64_str = st.query_params["booked"]
            json_str = base64.urlsafe_b64encode(b64_str.encode("utf-8")).decode("utf-8")
            st.session_state["booked_tours"] = json.loads(json_str)
        except Exception:
            st.session_state["booked_tours"] = []
    else:
        if "booked_tours" not in st.session_state:
            st.session_state["booked_tours"] = []

load_state_from_query_params()

# ---------------------------------------------------------
# CSS TÙY CHỈNH GIAO DIỆN (ĐÃ FIX DƯ THỪA KHUNG VÀ ĐÉO BỊ BỊ LÒI MẾP)
# ---------------------------------------------------------
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');

        /* GIỮ THANH CUỘN MƯỢT MÀ VẪN HOẠT ĐỘNG */
        html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"], .main {
            font-family: 'Roboto', sans-serif !important;
            overflow-y: auto !important;
            height: auto !important;
        }
        
        .stButton>button {
            border-radius: 8px;
            font-weight: 600;
            font-family: 'Roboto', sans-serif !important;
        }

        div[data-testid="stIFrame"], 
        iframe {
            border-radius: 16px !important;
            overflow: hidden !important;
            box-shadow: 0 6px 18px rgba(0, 0, 0, 0.12) !important;
        }

        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        .block-container, [data-testid="stMainBlockContainer"] {
            padding-top: 0rem !important;
            padding-bottom: 120px !important;
            max-width: 100% !important;
            overflow: visible !important;
        }

        /* LÀM TRONG SUỐT NỀN TRẮNG CỦA LOGO */
        .transparent-logo {
            height: 36px !important;
            object-fit: contain !important;
            mix-blend-mode: multiply;
            background: transparent !important;
        }

        /* 1. GIAO DIỆN MÁY TÍNH (DESKTOP) */
        @media (min-width: 769px) {
            .traveloka-hero-wrapper {
                background: linear-gradient(rgba(0, 0, 0, 0.35), rgba(0, 0, 0, 0.45)), 
                            url('https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1600&q=80');
                background-size: cover;
                background-position: center;
                padding: 40px 5rem 400px 5rem !important;
                margin-left: -5rem;
                margin-right: -5rem;
                margin-top: -3.5rem;
                color: white;
                position: relative;
            }

            .traveloka-brand-top-left {
                font-size: 2.2rem;
                font-weight: 800;
                text-align: left;
                margin-top: 10px;
                margin-left: -3rem !important;
                margin-bottom: 20px;
                color: white !important;
                text-shadow: 0 2px 6px rgba(0,0,0,0.6);
            }

            .traveloka-hero-title {
                font-size: 2.4rem;
                font-weight: 700;
                text-align: center;
                margin-bottom: 12px;
                color: white !important;
                text-shadow: 0 2px 6px rgba(0,0,0,0.5);
            }
            
            .traveloka-hero-subtitle {
                font-size: 1.15rem;
                text-align: center;
                opacity: 0.95;
                max-width: 750px;
                margin: 0 auto;
                color: white !important;
                text-shadow: 0 1px 4px rgba(0,0,0,0.5);
            }

            div.element-container:has(div.search-box-marker) {
                position: relative !important;
                margin-top: -250px !important;
                z-index: 999 !important;
                max-width: 950px;
                margin-left: auto;
                margin-right: auto;
            }
        }

        /* 2. GIAO DIỆN ĐIỆN THOẠI (MOBILE RESPONSIVE) */
        @media (max-width: 768px) {
            .traveloka-hero-wrapper {
                background: linear-gradient(rgba(0, 0, 0, 0.4), rgba(0, 0, 0, 0.5)), 
                            url('https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1000&q=80');
                background-size: cover;
                background-position: center;
                padding: 30px 1rem 100px 1rem !important;
                margin-left: -1rem;
                margin-right: -1rem;
                margin-top: -1rem !important;
                color: white;
                position: relative;
            }

            .traveloka-brand-top-left {
                font-size: 1.6rem;
                font-weight: 800;
                text-align: left;
                margin-top: 5px !important;
                margin-bottom: 12px;
                color: white !important;
                text-shadow: 0 2px 4px rgba(0,0,0,0.5);
            }

            .traveloka-hero-title {
                font-size: 1.4rem;
                font-weight: 700;
                text-align: center;
                margin-bottom: 8px;
                color: white !important;
                text-shadow: 0 2px 4px rgba(0,0,0,0.5);
            }
            
            .traveloka-hero-subtitle {
                font-size: 0.85rem;
                text-align: center;
                color: white !important;
                opacity: 0.95;
            }

            div.element-container:has(div.search-box-marker) {
                position: relative !important;
                margin-top: -70px !important;
                z-index: 999 !important;
                width: 100% !important;
                padding-left: 8px;
                padding-right: 8px;
            }
        }

        /* KHUNG CHỨA TÌM KIẾM CỐ ĐỊNH TRONG SUỐT HOÀN TOÀN - TRIỆT TIỆU KHUNG DƯ LÒI BÊN DƯỚI */
        div.element-container:has(div.search-box-marker) div[data-testid="stVerticalBlockBorderWrapper"],
        div.element-container:has(div.search-box-marker) div[data-testid="stVerticalBlock"] {
            border: none !important;
            box-shadow: none !important;
            background-color: transparent !important;
            background: transparent !important;
            padding: 0px !important;
        }

        div.element-container:has(div.search-box-marker) h3,
        div.element-container:has(div.search-box-marker) div,
        div.element-container:has(div.search-box-marker) span,
        div.element-container:has(div.search-box-marker) p {
            color: #ffffff !important;
        }
    </style>
""", unsafe_allow_html=True)

HO_CHI_MINH_COORDS = (10.7769, 106.7009)

user_agent = st.context.headers.get("User-Agent", "").lower()
is_phone = "iphone" in user_agent or "ipod" in user_agent or ("android" in user_agent and "mobile" in user_agent)

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
                with st.spinner("Đang gửi thông tin đặt tour..."):
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
                    "note": note_text if note_text else "Không có",
                    "time": datetime.now().strftime("%d/%m/%Y %H:%M")
                })
                
                save_state_to_query_params()
                st.rerun()

DESTINATIONS = {
    "Đà Nẵng": {
        "coords": (16.0544, 108.2022),
        "images": ["images/DN1.jpg", "images/DN2.jpg", "images/DN3.jpg", "images/DN4.jpg", "images/DN5.jpg", "images/DN6.jpg", "images/DN7.jpg", "images/DN8.jpg"],
        "description": "Thành phố đáng sống nhất Việt Nam với Bãi biển Mỹ Khê, Cầu Vàng (Bà Nà Hills) và Ngũ Hành Sơn hùng vĩ.",
        "avg_price": "2.500.000 - 4.000.000 VNĐ / người",
        "package_type": "Combo Vé máy bay + Khách sạn 3D2N (Tiêu chuẩn 4 sao)",
        "highlights": ["Check-in Cầu Vàng Bà Nà Hills", "Khám phá Cầu Rồng phun lửa", "Tắm biển Mỹ Khê"],
        "avg_speed_kmh": 60,
        "flight_time": "1 giờ 20 phút (Bay trực tiếp từ TP.HCM)"
    },
    "Hà Nội": {
        "coords": (21.0285, 105.8542),
        "images": ["images/HN1.jpg", "images/HN2.jpg", "images/HN3.jpg", "images/HN4.jpg", "images/HN5.jpg", "images/HN6.jpg", "images/HN7.jpg", "images/HN8.jpg"],
        "description": "Thủ đô nghìn năm văn hiến lưu giữ dấu ấn lịch sử, Hồ Hoàn Kiếm thơ mộng và văn hóa ẩm thực phố cổ đặc sắc.",
        "avg_price": "3.200.000 - 5.500.000 VNĐ / người",
        "package_type": "Tour Khám phá Phố Cổ & Ẩm thực 4D3N",
        "highlights": ["Dạo quanh Hồ Gươm & Phố Cổ", "Viếng Lăng Chủ tịch Hồ Chí Minh", "Thưởng thức Phở & Cà phê trứng"],
        "avg_speed_kmh": 60,
        "flight_time": "2 giờ 05 phút (Bay trực tiếp từ TP.HCM)"
    },
    "Lâm Đồng": {
        "coords": (11.9404, 108.4583),
        "images": ["images/DL1.jpg", "images/DL2.jpg", "images/DL3.jpg", "images/DL4.jpg", "images/DL5.jpg", "images/DL6.jpg", "images/DL7.jpg", "images/DL8.jpg"],
        "description": "Thành phố ngàn hoa với khí hậu ôn đới quanh năm mát mẻ, những đồi thông reo và các quán cà phê view thung lũng mộng mơ.",
        "avg_price": "1.800.000 - 3.000.000 VNĐ / người",
        "package_type": "Combo Xe Limousine khứ hồi + Khách sạn view đồi thông 3D2N",
        "highlights": ["Săn mây đồi chè Cầu Đất", "Khám phá Chợ Đêm Đà Lạt", "Check-in Hồ Xuân Hương"],
        "avg_speed_kmh": 50,
        "flight_time": "50 phút (Bay) hoặc 6-7 giờ (Xe Limousine từ TP.HCM)"
    },
    "An Giang": {
        "coords": (10.2899, 103.9840),
        "images": ["images/PQ1.jpg", "images/PQ2.jpg", "images/PQ3.jpg", "images/PQ4.jpg", "images/PQ5.jpg", "images/PQ6.jpg", "images/PQ7.jpg", "images/PQ8.jpg"],
        "description": "Đảo Ngọc thiên đường nghỉ dưỡng hàng đầu với bãi cát trắng mịn như kem, nước biển trong ngọc bích và hoàng hôn tuyệt mỹ.",
        "avg_price": "3.500.000 - 6.000.000 VNĐ / người",
        "package_type": "Combo Resort 5 sao sát biển + Vé VinWonders 3D2N",
        "highlights": ["Tắm biển Bãi Sao", "Khám phá Grand World Phú Quốc", "Cáp treo vượt biển Hòn Thơm"],
        "avg_speed_kmh": 40,
        "flight_time": "1 giờ 00 phút (Bay trực tiếp từ TP.HCM)"
    },
    "Khánh Hòa": {
        "coords": (12.2388, 109.1967),
        "images": ["images/NT1.jpg", "images/NT2.jpg", "images/NT3.jpg", "images/NT4.jpg", "images/NT5.jpg", "images/NT6.jpg", "images/NT7.jpg", "images/NT8.jpg"],
        "description": "Thành phố biển năng động sở hữu một trong những vịnh biển đẹp nhất hành tinh, thiên đường lặn ngắm san hô và hải sản tươi ngon.",
        "avg_price": "2.200.000 - 4.200.000 VNĐ / người",
        "package_type": "Tour Vịnh biển cao cấp & Nghỉ dưỡng 3D2N",
        "highlights": ["Vui chơi tại VinWonders Nha Trang", "Lặn ngắm san hô đảo Hòn Mun", "Thưởng thức đặc sản nem nướng"],
        "avg_speed_kmh": 60,
        "flight_time": "1 giờ 10 phút (Bay) hoặc 8 giờ (Tàu hỏa/Xe giường nằm)"
    },
    "Quảng Ninh": {
        "coords": (20.9101, 107.1839),
        "images": ["images/HL1.jpg", "images/HL2.jpg", "images/HL3.jpg", "images/HL4.jpg", "images/HL5.jpg", "images/HL6.jpg", "images/HL7.jpg", "images/HL8.jpg"],
        "description": "Kỳ quan thiên nhiên thế giới UNESCO với hàng nghìn hòn đảo đá vôi kỳ vĩ nổi bật trên làn nước xanh ngọc bích huyền ảo.",
        "avg_price": "3.800.000 - 6.500.000 VNĐ / người",
        "package_type": "Tour Du thuyền 5 sao vịnh Hạ Long (Full board)",
        "highlights": ["Ngủ đêm trên du thuyền hạng sang", "Khám phá Hang Sửng Sốt", "Chèo thuyền Kayak đảo Ti Tốp"],
        "avg_speed_kmh": 60,
        "flight_time": "Bay ra Hà Nội (2h) + Xe đưa đón cao tốc tới Quảng Ninh"
    },
    "Lào Cai": {
        "coords": (22.3364, 103.8438),
        "images": ["images/SP1.jpg", "images/SP2.jpg", "images/SP3.jpg", "images/SP4.jpg", "images/SP5.jpg", "images/SP6.jpg", "images/SP7.jpg", "images/SP8.jpg"],
        "description": "Thị trấn trong sương kỳ ảo, nổi tiếng với đỉnh Fansipan - nóc nhà Đông Dương và những bản làng mộc mạc ẩn hiện bên ruộng bậc thang.",
        "avg_price": "3.000.000 - 5.000.000 VNĐ / người",
        "package_type": "Tour Sapa săn mây & Trải nghiệm bản làng 4D3N",
        "highlights": ["Chinh phục đỉnh Fansipan", "Khám phá bản Cát Cát mờ sương", "Check-in đèo Ô Quy Hồ tuyệt đẹp"],
        "avg_speed_kmh": 45,
        "flight_time": "Bay ra Hà Nội (2h) kết hợp xe giường nằm cao tốc lên Sapa"
    },
    "Cao Bằng": {
        "coords": (22.6656, 106.2607),
        "images": ["images/CB1.jpg", "images/CB2.jpg", "images/CB3.jpg", "images/CB4.jpg", "images/CB5.jpg", "images/CB6.jpg", "images/CB7.jpg", "images/CB8.jpg"],
        "description": "Cao Bằng là một tỉnh miền núi thuộc vùng Đông Bắc Việt Nam, nổi bật với danh hiệu miền non nước ngàn năm và sở hữu Thác Bản Giốc hùng vĩ.",
        "avg_price": "6.500.000 - 12.500.000 VNĐ / người",
        "package_type": "Tour Non nước Cao Bằng 3D2N",
        "highlights": ["Thác Bản Giốc", "Động Ngườm Ngao", "Hồ Thang Hen"],
        "avg_speed_kmh": 45,
        "flight_time": "Bay ra Hà Nội (2h) kết hợp xe khách lên Cao Bằng"
    },
    "Tuyên Quang": {
        "coords": (21.8236, 105.2142),
        "images": ["images/TQ1.jpg", "images/TQ2.jpg", "images/TQ3.jpg", "images/TQ4.jpg", "images/TQ5.jpg", "images/TQ6.jpg", "images/TQ7.jpg", "images/TQ8.jpg"],
        "description": "Tuyên Quang là tỉnh giàu truyền thống cách mạng, nổi tiếng với di tích lịch sử Tân Trào và lễ hội Trung thu lớn nhất Việt Nam.",
        "avg_price": "5.500.000 - 10.000.000 VNĐ / người",
        "package_type": "Tour Về Miền Di Tích & Khám Phá Tuyên Quang 3D2N",
        "highlights": ["Thăm Khu di tích quốc gia đặc biệt Tân Trào", "Check-in Suối Khoáng Mỹ Lâm", "Tham gia Lễ hội Thành Tuyên"],
        "avg_speed_kmh": 45,
        "flight_time": "Bay ra Hà Nội (2h) kết hợp xe khách lên Tuyên Quang"
    },
    "Lai Châu": {
        "coords": (22.3992, 103.4392),
        "images": ["images/LC1.jpg", "images/LC2.jpg", "images/LC3.jpg", "images/LC4.jpg", "images/LC5.jpg", "images/LC6.jpg", "images/LC7.jpg", "images/LC8.jpg"],
        "description": "Lai Châu nổi tiếng với thiên nhiên hoang sơ, hùng vĩ của núi rừng Tây Bắc, những cung đèo hiểm trở, biển mây bồng bềnh và các bản làng văn hóa đặc sắc.",
        "avg_price": "5.500.000 - 10.000.000 VNĐ / người",
        "package_type": "Tour Khám phá Tây Bắc 3D2N",
        "highlights": ["Đèo Ô Quy Hồ", "Cao nguyên Sìn Hồ", "Đồi chè Tân Uyên"],
        "avg_speed_kmh": 45,
        "flight_time": "Bay ra Hà Nội (2h) kết hợp xe khách lên Lai Châu"
    },
    "Thái Nguyên": {
        "coords": (21.5942, 105.8482),
        "images": ["images/TN1.jpg", "images/TN2.jpg", "images/TN3.jpg", "images/TN4.jpg", "images/TN5.jpg", "images/TN6.jpg", "images/TN7.jpg", "images/TN8.jpg"],
        "description": "Thái Nguyên là một tỉnh miền núi và trung du thuộc vùng Đông Bắc Bộ, nổi bật với các điểm đến sinh thái, đồi chè xanh mướt và văn hóa trà lâu đời.",
        "avg_price": "5.500.000 - 10.000.000 VNĐ / người",
        "package_type": "Tour Trải nghiệm Vùng Trà & Sinh Thái 3D2N",
        "highlights": ["Đồi chè Tân Cương", "Hồ Núi Cốc", "Khu di tích lịch sử ATK Định Hóa"],
        "avg_speed_kmh": 45,
        "flight_time": "Bay ra Hà Nội (2h) kết hợp xe khách lên Thái Nguyên"
    },
    "Điện Biên": {
        "coords": (21.38602, 103.02301),
        "images": ["images/ĐB1.jpg", "images/ĐB2.jpg", "images/ĐB3.jpg", "images/ĐB4.jpg", "images/ĐB5.jpg", "images/ĐB6.jpg", "images/ĐB7.jpg", "images/ĐB8.jpg"],
        "description": "Điện Biên là điểm đến Tây Bắc nổi bật với thiên nhiên hùng vĩ, bề dày lịch sử vẻ vang và các bản làng văn hóa độc đáo.",
        "avg_price": "5.500.000 - 10.000.000 VNĐ / người",
        "package_type": "Tour Về Miền Lịch Sử Điện Biên Phủ 3D2N",
        "highlights": ["Cánh đồng Mường Thanh", "Đồi A1", "Hầm De Castries"],
        "avg_speed_kmh": 45,
        "flight_time": "Bay trực tiếp hoặc qua Hà Nội lên Điện Biên"
    },
    "Lạng Sơn": {
        "coords": (21.8526, 106.7610),
        "images": ["images/LS1.jpg", "images/LS2.jpg", "images/LS3.jpg", "images/LS4.jpg", "images/LS5.jpg", "images/LS6.jpg", "images/LS7.jpg", "images/LS8.jpg"],
        "description": "Lạng Sơn là tỉnh miền núi biên giới nổi tiếng với phong cảnh núi non hùng vĩ, các di tích lịch sử và văn hóa tâm linh đặc sắc.",
        "avg_price": "5.500.000 - 10.000.000 VNĐ / người",
        "package_type": "Tour Khám Phá Xứ Lạng 3D2N",
        "highlights": ["Ải Chi Lăng", "Động Tam Thanh", "Chợ Kỳ Lừa"],
        "avg_speed_kmh": 45,
        "flight_time": "Bay ra Hà Nội (2h) kết hợp xe khách lên Lạng Sơn"
    }
}

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

current_tab = st.session_state["current_tab"]

# =========================================================
# TAB 1: TÌM KIẾM / TRANG CHỦ
# =========================================================
if current_tab == "home":
    st.markdown("""
        <div class="traveloka-hero-wrapper">
            <div class="traveloka-brand-top-left">Mai Travel</div>
            <div class="traveloka-hero-title">Đưa bạn bay tới bất cứ đâu</div>
            <div class="traveloka-hero-subtitle">Khám phá hàng loạt điểm đến tuyệt vời, đặt tour nhanh chóng và tận hưởng chuyến đi trọn vẹn.</div>
        </div>
    """, unsafe_allow_html=True)

    # KHÔNG DÙNG BORDER TẠO CONTAINER TRẮNG NỮA
    with st.container():
        st.markdown("<div class='search-box-marker'></div>", unsafe_allow_html=True)
        st.markdown("### ✈️ **Tìm Kiếm Nhanh Điểm Đến & Tour Du Lịch**")
        st.markdown("<div style='font-size: 14px; font-weight: 500; color: #ffffff; margin-bottom: 6px;'>🔍 Nhập tên tỉnh thành hoặc từ khóa (Ví dụ: Đà Nẵng, Sapa, Hà Nội...)</div>", unsafe_allow_html=True)
        search_query = st.text_input("SearchLabel", "", label_visibility="collapsed", placeholder="Thành phố, điểm đến hoặc tên tour...")
        
        logo1_base64 = get_image_base64("images/logo1.jpg")
        logo2_base64 = get_image_base64("images/logo2.jpg")
        logo3_base64 = get_image_base64("images/logo3.jpg")
        
        st.markdown(f"""
            <div style="display: flex; align-items: center; justify-content: center; gap: 18px; margin-top: 14px; flex-wrap: wrap;">
                <span style="font-size: 14px; font-weight: 700; color: #ffffff !important; font-style: italic; text-shadow: 0 1px 4px rgba(0,0,0,0.6);">Trusted by</span>
                <img src="{logo1_base64}" class="transparent-logo">
                <img src="{logo2_base64}" class="transparent-logo">
                <img src="{logo3_base64}" class="transparent-logo">
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
    st.markdown("### 🔥 **Các Tour Du Lịch Hot Nhất Hiện Nay**")

    filtered_destinations = {
        name: data for name, data in DESTINATIONS.items() 
        if search_query.lower() in name.lower() or search_query.lower() in data["description"].lower()
    }

    if not filtered_destinations:
        st.warning("Không tìm thấy điểm đến phù hợp với từ khóa của bạn!")
        filtered_destinations = DESTINATIONS

    if is_phone:
        for name, data in filtered_destinations.items():
            with st.container(border=True):
                cover_img = get_image_base64(data["images"][0])
                st.image(cover_img, use_container_width=True)
                st.markdown(f"#### **{name}**")
                st.caption(f"📌 {data['package_type']}")
                st.write(data["description"][:85] + "...")
                st.success(f"💰 {data['avg_price'].split(' - ')[0]}")
                
                col_h1, col_h2 = st.columns(2)
                with col_h1:
                    if st.button(f"🚀 Xem tour", key=f"btn_hot_{name}", use_container_width=True):
                        st.session_state["selected_place"] = name
                        st.session_state["current_tab"] = "map"
                        save_state_to_query_params()
                        st.rerun()
                with col_h2:
                    is_saved = name in st.session_state["saved_tours"]
                    saved_label = "❤️ Đã lưu" if is_saved else "🤍 Lưu tin"
                    if st.button(saved_label, key=f"save_hot_{name}", use_container_width=True):
                        if is_saved:
                            st.session_state["saved_tours"].remove(name)
                        else:
                            st.session_state["saved_tours"].append(name)
                        save_state_to_query_params()
                        st.rerun()
    else:
        cols = st.columns(3)
        idx = 0
        for name, data in filtered_destinations.items():
            with cols[idx % 3]:
                with st.container(border=True):
                    cover_img = get_image_base64(data["images"][0])
                    st.image(cover_img, use_container_width=True)
                    st.markdown(f"#### **{name}**")
                    st.caption(f"📌 {data['package_type']}")
                    st.write(data["description"][:85] + "...")
                    st.success(f"💰 {data['avg_price'].split(' - ')[0]}")
                    
                    col_h1, col_h2 = st.columns(2)
                    with col_h1:
                        if st.button(f"🚀 Xem tour", key=f"btn_hot_{name}", use_container_width=True):
                            st.session_state["selected_place"] = name
                            st.session_state["current_tab"] = "map"
                            save_state_to_query_params()
                            st.rerun()
                    with col_h2:
                        is_saved = name in st.session_state["saved_tours"]
                        saved_label = "❤️ Đã lưu" if is_saved else "🤍 Lưu tin"
                        if st.button(saved_label, key=f"save_hot_{name}", use_container_width=True):
                            if is_saved:
                                st.session_state["saved_tours"].remove(name)
                            else:
                                st.session_state["saved_tours"].append(name)
                            save_state_to_query_params()
                            st.rerun()
            idx += 1

# =========================================================
# TAB 2: ĐẶT TOUR & BẢN ĐỒ
# =========================================================
elif current_tab == "map":
    st.title("Mai travel \n 🇻🇳 Khám Phá & Đặt Tour Du Lịch Việt Nam")
    st.markdown("---")

    def render_map_content():
        st.subheader("📍 Bản Đồ Việt Nam")
        
        col_btn1, col_btn2 = st.columns([1, 1])
        with col_btn1:
            if st.button("🔍 Focus Điểm Đến", use_container_width=True):
                st.session_state["zoom_overview"] = False
                save_state_to_query_params()
                st.rerun()
        with col_btn2:
            if st.button("🌍 Toàn Cảnh VN", use_container_width=True):
                st.session_state["zoom_overview"] = True
                save_state_to_query_params()
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
            popup="Mốc xuất phát: TP. Hồ Chí Minh",
            tooltip="Mốc xuất phát: TP. Hồ Chí Minh",
            icon=folium.Icon(color="red", icon="star")
        ).add_to(m)

        for name, data in DESTINATIONS.items():
            is_selected = (name == st.session_state["selected_place"])
            marker_color = "orange" if is_selected else "blue"
            
            folium.Marker(
                location=data["coords"],
                popup=name,
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

        map_data = st_folium(m, width="100%", height=420)

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
            save_state_to_query_params()
            st.rerun()

    def render_info_content():
        st.markdown("### ✈️ Tra Cứu & Đặt Tour Du Lịch")
        
        selected_option = st.selectbox(
            "✨ Lựa chọn điểm đến mơ ước của bạn:",
            options=list(DESTINATIONS.keys()),
            index=list(DESTINATIONS.keys()).index(st.session_state["selected_place"])
        )

        if selected_option != st.session_state["selected_place"]:
            st.session_state["selected_place"] = selected_option
            st.session_state["zoom_overview"] = False
            save_state_to_query_params()
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
            components.html(carousel_html, height=290, scrolling=False)

            st.markdown(f"## 🌟 **{st.session_state['selected_place']}**")
            st.caption(f"📌 *{current_data['package_type']}*")
            st.write(current_data["description"])
            
            st.markdown("---")
            st.markdown("##### 🚗 **Thông Tin Di Chuyển (Xuất phát từ TP.HCM)**")
            
            col_m1, col_m2 = st.columns(2)
            col_m1.metric(label="Khoảng cách ước tính", value=f"{road_dist} km")
            col_m2.metric(label="Thời gian di chuyển", value=drive_time)
            
            st.info(f"✈️ **Gợi ý di chuyển hàng không:** {current_data['flight_time']}")

            st.markdown("##### 💳 **Báo Giá & Ưu Đãi Trọn Gói**")
            st.success(f"**Mức giá tham khảo:** {current_data['avg_price']}")

            st.markdown("##### ⭐ **Điểm Nhấn Trải Nghiệm Nổi Bật**")
            for tag in current_data["highlights"]:
                st.markdown(f"✔️ {tag}")

            st.markdown("---")
            
            col_book1, col_book2 = st.columns([2, 1])
            with col_book1:
                if st.button("🚀 ĐẶT TOUR NGAY", type="primary", use_container_width=True):
                    booking_modal(st.session_state["selected_place"], current_data["avg_price"])
            with col_book2:
                is_saved = st.session_state["selected_place"] in st.session_state["saved_tours"]
                save_btn_label = "❤️ Đã lưu" if is_saved else "🤍 Lưu tin"
                if st.button(save_btn_label, key=f"save_map_{st.session_state['selected_place']}", use_container_width=True):
                    if is_saved:
                        st.session_state["saved_tours"].remove(st.session_state["selected_place"])
                        st.toast("Đã xóa khỏi danh sách yêu thích!")
                    else:
                        st.session_state["saved_tours"].append(st.session_state["selected_place"])
                        st.toast("Đã thêm vào danh sách yêu thích!")
                    save_state_to_query_params()
                    st.rerun()

    if is_phone:
        render_map_content()
        st.markdown("---")
        render_info_content()
    else:
        col_map, col_info = st.columns([1.2, 1])
        with col_map:
            render_map_content()
        with col_info:
            render_info_content()

# =========================================================
# TAB 3: ĐÃ LƯU
# =========================================================
elif current_tab == "saved":
    st.title("Mai travel \n 🇻🇳 Khám Phá & Đặt Tour Du Lịch Việt Nam")
    st.markdown("---")
    st.markdown("### ❤️ **Danh Sách Tour Đã Lưu Yêu Thích**")
    
    if not st.session_state["saved_tours"]:
        st.info("Bạn chưa lưu điểm đến nào. Hãy bấm nút **'Lưu tin'** ở các tour bạn quan tâm nhé!")
    else:
        for name in st.session_state["saved_tours"]:
            if name in DESTINATIONS:
                data = DESTINATIONS[name]
                with st.container(border=True):
                    col_s1, col_s2 = st.columns([1, 2])
                    with col_s1:
                        cover_img = get_image_base64(data["images"][0])
                        st.image(cover_img, use_container_width=True)
                    with col_s2:
                        st.markdown(f"#### **{name}**")
                        st.caption(f"📌 {data['package_type']}")
                        st.success(f"💰 {data['avg_price']}")
                        
                        col_b1, col_b2 = st.columns(2)
                        with col_b1:
                            if st.button(f"🚀 Xem tour", key=f"go_{name}", use_container_width=True):
                                st.session_state["selected_place"] = name
                                st.session_state["current_tab"] = "map"
                                save_state_to_query_params()
                                st.rerun()
                        with col_b2:
                            if st.button(f"🗑️ Xóa", key=f"del_{name}", use_container_width=True):
                                st.session_state["saved_tours"].remove(name)
                                save_state_to_query_params()
                                st.rerun()

# =========================================================
# TAB 4: TOUR ĐÃ ĐẶT
# =========================================================
elif current_tab == "bookings":
    st.title("Mai travel \n 🇻🇳 Khám Phá & Đặt Tour Du Lịch Việt Nam")
    st.markdown("---")
    st.markdown("### 💼 **Lịch Sử Đặt Tour Của Bạn**")
    
    if not st.session_state["booked_tours"]:
        st.info("Bạn chưa có đơn đặt tour nào. Hãy chọn tour và tiến hành đặt giữ chỗ ngay trên hệ thống!")
    else:
        for idx, booking in enumerate(st.session_state["booked_tours"]):
            with st.container(border=True):
                st.markdown(f"#### 🌟 **{booking['tour']}**")
                st.caption(f"🕒 Thời gian đặt: {booking['time']}")
                st.write(f"👤 **Họ tên:** {booking['name']} | 📞 **SĐT:** {booking['phone']}")
                st.write(f"👥 **Số lượng:** {booking['adults']} Người lớn, {booking['children']} Trẻ em")
                if booking.get('note') and booking['note'] != "Không có":
                    st.info(f"💬 **Ghi chú:** {booking['note']}")
                st.success(f"💰 **Mức giá:** {booking['price']}")

# =========================================================
# TAB 5: TÀI KHOẢN & CÀI ĐẶT
# =========================================================
elif current_tab == "account":
    st.title("Mai travel \n 🇻🇳 Khám Phá & Đặt Tour Du Lịch Việt Nam")
    st.markdown("---")
    st.markdown("### 👤 **Tài Khoản & Cài Đặt**")
    
    with st.container(border=True):
        st.markdown("#### **Thông Tin Ứng Dụng**")
        st.write("**Tên ứng dụng:** Mai Travel - Du Lịch Việt Nam")
        st.write("**Phiên bản:** 2.0 (Streamlit Cloud Ready)")
        st.write("**Liên hệ hỗ trợ:** support@maitravel.vn | Hotline: 1900 1234")
        st.markdown("---")
        if st.button("🗑️ Xóa toàn bộ lịch sử đặt tour & yêu thích", type="secondary"):
            st.session_state["saved_tours"] = []
            st.session_state["booked_tours"] = []
            save_state_to_query_params()
            st.success("Đã làm sạch dữ liệu phiên làm việc!")
            st.rerun()

save_state_to_query_params()

# ---------------------------------------------------------
# THANH MENU ĐIỀU HƯỚNG CỐ ĐỊNH DƯỚI MÀN HÌNH
# ---------------------------------------------------------
saved_val = st.query_params.get('saved', '')
booked_val = st.query_params.get('booked', '')
params_str = f"{f'&saved={saved_val}' if saved_val else ''}{f'&booked={booked_val}' if booked_val else ''}"

is_tab_saved = 'active' if current_tab == 'saved' else ''
is_tab_home = 'active' if current_tab == 'home' else ''
is_tab_map = 'active' if current_tab == 'map' else ''
is_tab_bookings = 'active' if current_tab == 'bookings' else ''
is_tab_account = 'active' if current_tab == 'account' else ''

menu_html = f"""
<style>
    .bottom-nav {{
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #ffffff;
        display: flex;
        justify-content: space-around;
        align-items: center;
        box-shadow: 0 -4px 20px rgba(0,0,0,0.18);
        padding: 10px 0;
        z-index: 999999;
        border-top-left-radius: 16px;
        border-top-right-radius: 16px;
        border-top: 1px solid rgba(128, 128, 128, 0.25);
    }}
    @media (prefers-color-scheme: dark) {{
        .bottom-nav {{
            background-color: #0e1117 !important;
        }}
    }}
    .nav-item {{
        text-align: center;
        text-decoration: none !important;
        color: inherit;
        font-family: 'Roboto', sans-serif;
        font-size: 12px;
        font-weight: 500;
        flex: 1;
        cursor: pointer;
        opacity: 0.75;
        transition: 0.2s;
    }}
    .nav-item:hover {{
        text-decoration: none !important;
        opacity: 1;
        color: #ff4b4b;
    }}
    .nav-item.active {{
        text-decoration: none !important;
        color: #ff4b4b;
        font-weight: 700;
        opacity: 1;
    }}
    .nav-icon {{
        font-size: 20px;
        display: block;
        margin-bottom: 2px;
    }}
</style>

<div class="bottom-nav">
    <a href="?tab=home{params_str}" target="_self" class="nav-item {is_tab_home}">
        <span class="nav-icon">🏠</span>Trang chủ
    </a>
    <a href="?tab=map{params_str}" target="_self" class="nav-item {is_tab_map}">
        <span class="nav-icon">🗺️</span>Bản đồ
    </a>
    <a href="?tab=saved{params_str}" target="_self" class="nav-item {is_tab_saved}">
        <span class="nav-icon">❤️</span>Đã lưu ({len(st.session_state['saved_tours'])})
    </a>
    <a href="?tab=bookings{params_str}" target="_self" class="nav-item {is_tab_bookings}">
        <span class="nav-icon">💼</span>Đã đặt ({len(st.session_state['booked_tours'])})
    </a>
    <a href="?tab=account{params_str}" target="_self" class="nav-item {is_tab_account}">
        <span class="nav-icon">👤</span>Tài khoản
    </a>
</div>
"""

st.markdown(menu_html, unsafe_allow_html=True)
