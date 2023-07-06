"""
작성자: 김윤재
최초작성: 2023-07-03(월)
최종수정: 2023-07-06(목) 00:50
"""

# --- import modules
import io
import sqlite3
import sys

import folium
import pandas as pd
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from folium import plugins
from folium.plugins import *
import webbrowser


class FoliumMap(QWidget):
    def __init__(self):
        super().__init__()

        # --- 윈도우창
        self.setWindowTitle('소연과 소년들')
        self.setGeometry(300, 300, 900, 700)

        # --- DB + Query
        self.con = sqlite3.connect('seoul_db.db')
        self.cur = self.con.cursor()

        # --- 판다스 리드
        self.df_food = pd.read_sql('SELECT * FROM food_list', self.con)  # --- 음식점

        # --- 판다스 옵션
        pd.set_option("display.max_columns", None)
        pd.set_option("display.max_rows", None)

        # --- 레이아웃 & 버튼 & 웹엔진뷰
        self.layout = QVBoxLayout()
        self.button = QPushButton('뒤로가기(구글스트릿에서)', self)
        self.web = QWebEngineView()
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)
        self.button.clicked.connect(self.button_clicked_event)

        # --- self.seoul_map 지도 설정
        self.latitude = 37.564214  # 위도
        self.longitude = 127.001699  # 경도
        self.zoom_level = 11
        self.titles = "http://mt0.google.com/vt/lyrs=m&hl=ko&x={x}&y={y}&z={z}"
        self.attr = "Google"
        # self.coordinate = (35.19475778198943, 126.8399771747554)

        # --- folium 맵 설정: 서울 전체 맵
        self.seoul_map = folium.Map(
            tiles=self.titles,  # --- 배경지도 tiles에 대한 속성 (기본값: https://www.openstreetmap.org)
            attr=self.attr,
            zoom_start=self.zoom_level,  # --- 화면 보여줄 거리 / 값이 적을수록 가까이 보여줌
            location=[self.latitude, self.longitude],  # --- 현재 화면에 보여줄 좌표 값
            control_scale=True,  # --- contol_scale: True 시 맵 좌측 하단에 배율을 보여줌
            # zoom_control = False,   # --- zoom_control: False 시 줌 컨트롤러가 사라집니다. (단, 마우스 휠 줌은 가능)
            # scrollWheelZoom = False,  # --- scrollWheelZoom: False 시 스크롤을 사용할 수 없음
            # dragging = False  # --- dragging: False 시 마우스 드래그를 사용할 수 없음
        )
        self.marker_cluster = MarkerCluster().add_to(self.seoul_map)  # --- MakerCluster() 플러그인 적용
        self.mini_map = MiniMap().add_to(self.seoul_map)  # --- MiniMap() 플러그인 적용

        # --- 실행부
        """
        ▼ 메소드 설명:
        self.mapping_tour_all_show()  -> 모든 관광명소를 지도에 마커+클러스트로 표시합니다.
        self.mapping_tour_guname_show()  -> 특정 관광명소를 지도에 마커+클러스트로 표시합니다.
        self.mapping_lodges_all_show()  -> 모든 숙박업소를 지도에 마커+클러스트로 표시합니다.
        self.mapping_lodges_guname_show()  -> 특정 숙박업소를 지도에 마커+클러스트로 표시합니다.
        self.mapping_food_all_show()  -> 모든 음식점을 지도에 마커+클러스트로 표시합니다.
        self.mapping_food_guname_show(guname: str)  -> 특정 음식점을 지도에 마커+클러스트로 표시합니다.  
        """
        self.mapping_food_all_show()
        self.load_map()  # --- 현재 폴더에 index.html 파일을 저장하고, index.html 파일 불러오기

    # --- 메소드
    def mapping_tour_all_show(self):
        """DB의 관광명소 목록을 맵에 마커 + 클러스트로 적용시킵니다"""
        tour_query = pd.read_sql("SELECT 상호명, 신주소, 전화번호, 웹사이트, x_pos, y_pos, img_path FROM seoul_tourist", self.con)
        for index, row in tour_query.iterrows():
            x_pos = row['x_pos']
            y_pos = row['y_pos']
            name = row['상호명']
            info = row['신주소'], row['전화번호']
            link = f"<a href={row['웹사이트']}>웹사이트 접속</a>"
            img = row['img_path']
            roadview = f'<a href="https://www.google.com/maps?layer=c&cbll={str(x_pos)},{str(y_pos)}">구글 거리뷰로 보기</a>'
            icon = folium.Icon(color="purple", icon="glyphicon glyphicon-tag", icon_color="white")
            popup = folium.Popup(f"<img src='{img}'>" + "<br>" + name + f"({str(link)})" + "<br><br>" + str(info) + "<br><br>" + roadview, min_width=500, max_width=500)
            folium.Marker([x_pos, y_pos], tooltip=name, popup=popup, icon=icon).add_to(self.marker_cluster)

    def mapping_tour_guname_show(self, guname: str):
        """DB의 관광명소 목록을 맵에 마커 + 클러스트로 적용시킵니다"""
        tour_query = pd.read_sql(f"SELECT 상호명, 신주소, 전화번호, 웹사이트, x_pos, y_pos, img_path FROM seoul_tourist WHERE 신주소 LIKE '%{guname}%'", self.con)
        for index, row in tour_query.iterrows():
            x_pos = row['x_pos']
            y_pos = row['y_pos']
            name = row['상호명']
            info = row['신주소'], row['전화번호']
            link = f"<a href={row['웹사이트']}>웹사이트 접속</a>"
            img = row['img_path']
            roadview = f'<a href="https://www.google.com/maps?layer=c&cbll={str(x_pos)},{str(y_pos)}">구글 거리뷰로 보기</a>'
            icon = folium.Icon(color="purple", icon="glyphicon glyphicon-tag", icon_color="white")
            popup = folium.Popup(f"<img src='{img}'>" + "<br>" + name + f"({str(link)})" + "<br><br>" + str(info) + "<br><br>" + roadview, min_width=500, max_width=500)
            folium.Marker([x_pos, y_pos], tooltip=name, popup=popup, icon=icon).add_to(self.marker_cluster)

    def mapping_lodges_all_show(self):
        """DB의 숙박지 목록을 맵에 마커 + 클러스트로 적용시킵니다"""
        lodge_query = pd.read_sql("SELECT 사업장명, 도로명주소, 전화번호, x_pos, y_pos, img_path FROM seoul_lodges", self.con)
        for index, row in lodge_query.iterrows():
            x_pos = row['x_pos']
            y_pos = row['y_pos']
            name = row['사업장명']
            info = row['도로명주소'], row['전화번호']
            img = row['img_path']
            roadview = f'<a href="https://www.google.com/maps?layer=c&cbll={str(x_pos)},{str(y_pos)}">구글 거리뷰로 보기</a>'
            icon = folium.Icon(color="blue", icon="glyphicon glyphicon-tag", icon_color="white")
            popup = folium.Popup(f"<img src='{img}'>" + "<br><br>" + name + "<br><br>" + str(info) + "<br><br>" + roadview, min_width=400, max_width=400)
            # icon = plugins.BeautifyIcon(
            #     icon='utensils',
            #     border_color='darkblue',
            #     text_color='darkblue',
            #     icon_shape='triangle',
            # )
            folium.Marker([x_pos, y_pos], tooltip=name, popup=popup, icon=icon).add_to(self.marker_cluster)

    def mapping_lodges_guname_show(self, guname: str):
        """DB의 숙박지 목록을 구별로 맵에 마커 + 클러스트로 적용시킵니다"""
        lodge_query = pd.read_sql(f"SELECT 사업장명, 도로명주소, 전화번호, x_pos, y_pos, img_path FROM seoul_lodges WHERE 도로명주소 LIKE '%{guname}%'", self.con)
        for index, row in lodge_query.iterrows():
            x_pos = row['x_pos']
            y_pos = row['y_pos']
            name = row['사업장명']
            info = row['도로명주소'], row['전화번호']
            img = row['img_path']
            roadview = f'<a href="https://www.google.com/maps?layer=c&cbll={str(x_pos)},{str(y_pos)}">구글 거리뷰로 보기</a>'
            popup = folium.Popup(f"<img src='{img}'>" + "<br><br>" + name + "<br><br>" + str(info) + "<br><br>" + roadview, min_width=400, max_width=400)
            icon = folium.Icon(color="blue", icon="glyphicon glyphicon-tag", icon_color="white")
            folium.Marker([x_pos, y_pos], tooltip=name, popup=popup, icon=icon).add_to(self.marker_cluster)

    def mapping_food_all_show(self):
        """DB의 음식점 목록을 맵에 마커 + 클러스트로 적용시킵니다"""
        food_query = pd.read_sql("SELECT name, address, x_pos, y_pos, img_path FROM food_list", self.con)
        for index, row in food_query.iterrows():
            x_pos = row['x_pos']
            y_pos = row['y_pos']
            name = row['name']
            info = row['address']
            img = row['img_path']
            roadview = f'<a href="https://www.google.com/maps?layer=c&cbll={str(x_pos)},{str(y_pos)}">구글 거리뷰로 보기</a>'
            popup = folium.Popup(f"<img src='{img}'>" + "<br><br>" + name + "<br><br>" + str(info) + "<br><br>" + roadview, min_width=400, max_width=400)
            icon = folium.Icon(color="red", icon="glyphicon glyphicon-tag", icon_color="white")
            folium.Marker([x_pos, y_pos], tooltip=name, popup=popup, icon=icon).add_to(self.marker_cluster)

    def mapping_food_guname_show(self, guname: str):
        """DB의 음식점 목록을 구별로 마커 + 클러스트로 적용시킵니다"""
        food_query = pd.read_sql(f"SELECT gu_name, name, rate, address, x_pos, y_pos, img_path FROM food_list WHERE gu_name = '{guname}'", self.con)
        for index, row in food_query.iterrows():
            x_pos = row['x_pos']
            y_pos = row['y_pos']
            name = row['name']
            info = row['address']
            img = row['img_path']
            popup = folium.Popup(f"<img src='{img}'>" + "<br><br>" + name + "<br><br>" + str(info), min_width=400, max_width=400)
            folium.Marker([x_pos, y_pos], tooltip=name, popup=popup, icon=folium.Icon(color="green")).add_to(self.marker_cluster)

    def load_map(self):
        """self.seoul_map을 index.html 파일로 저장하고, PyQt 레이아웃에 QWebEngineView를 추가합니다"""
        # data = io.BytesIO()
        # self.seoul_map.save(data, close_file=False)
        # web.setHtml(data.getvalue().decode())
        self.seoul_map.save('index.html', close_file=False)
        # webbrowser.open(r'index.html')  # --- 테스트용: 웹브라우저에서도 self.seoul_map 열기
        self.web.setUrl(QUrl("file:///index.html"))  # QWebEngineView 를 이용하여 웹 페이지를 표출
        self.layout.addWidget(self.web)

    def load_map_2(self):
        """미사용"""
        with open('index.html', 'r', encoding="utf-8") as f:
            html = f.read()
            self.webEngineView.setUrl(QUrl(html))

    def button_clicked_event(self):
        """구글 스트릿 뷰 상태에서 뒤로가기 버튼을 클릭하면 원래 화면으로 이동합니다"""
        self.web.page().triggerAction(QWebEnginePage.WebAction.Back)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(''' QWidget { font-size: 35px; }''')
    run = FoliumMap()
    run.show()

    try:
        sys.exit(app.exec_())
    except SystemExit:
        print('Closing Window...')