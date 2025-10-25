import sys
import os
import pandas as pd
import re
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QComboBox, QPushButton, QScrollArea, QFrame, QTextEdit, QTextBrowser, QGroupBox, QTabWidget, QMainWindow, QSpinBox, QSplitter, QGridLayout, QMessageBox, QDialog, QMenu, QFileDialog, QCompleter
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QFont, QClipboard
from PyQt5.QtGui import QFont, QTextOption, QTextBlockFormat, QTextCursor
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWidgets import QLabel
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import arabic_reshaper
from bidi.algorithm import get_display
import json
import unicodedata

class QuranSearchApp(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app  # QApplication referansı
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        self.setWindowTitle('Açık Kur’an Araştırmacısı (PyQt5)')
        self.setGeometry(100, 100, 1400, 800)
        self.font_arabic = QFont('Arial Unicode MS', 20)
        self.font_turkish = QFont('Arial', 12)
        self.player = QMediaPlayer()
        self.ARAP_HARFLER = ['ا','ب','ت','ث','ج','ح','خ','د','ذ','ر','ز','س','ش','ص','ض','ط','ظ','ع','غ','ف','ق','ك','ل','م','ن','ه','و','ي','ء','ى']
        self.ebced = {'ا':1, 'ب':2, 'ج':3, 'د':4, 'ه':5, 'و':6, 'ز':7, 'ح':8, 'ط':9, 'ي':10, 'ك':20, 'ل':30, 'م':40, 'ن':50, 'س':60, 'ع':70, 'ف':80, 'ص':90, 'ق':100, 'ر':200, 'ش':300, 'ت':400, 'ث':500, 'خ':600, 'ذ':700, 'ض':800, 'ظ':900, 'غ':1000}
        self.harekeler = ['\u064b', '\u064c', '\u064d', '\u064e', '\u064f', '\u0650', '\u0651', '\u0652', '\u0653', '\u0654', '\u0655', '\u0656', '\u0657', '\u0658', '\u0659', '\u065a', '\u065b', '\u065c', '\u065d', '\u065e', '\u065f', '\u06ea']
        # Sure ayet sayıları (basit dict)
        self.verse_counts = {
            1: 7, 2: 286, 3: 200, 4: 176, 5: 120, 6: 165, 7: 206, 8: 75, 9: 129, 10: 109,
            11: 123, 12: 111, 13: 43, 14: 52, 15: 99, 16: 128, 17: 111, 18: 110, 19: 98, 20: 135,
            21: 112, 22: 78, 23: 118, 24: 64, 25: 77, 26: 227, 27: 93, 28: 88, 29: 69, 30: 60,
            31: 34, 32: 30, 33: 73, 34: 54, 35: 45, 36: 83, 37: 182, 38: 88, 39: 75, 40: 85,
            41: 54, 42: 53, 43: 89, 44: 59, 45: 37, 46: 35, 47: 38, 48: 29, 49: 18, 50: 45,
            51: 60, 52: 49, 53: 62, 54: 55, 55: 78, 56: 96, 57: 29, 58: 22, 59: 24, 60: 13,
            61: 14, 62: 11, 63: 11, 64: 18, 65: 12, 66: 12, 67: 30, 68: 52, 69: 52, 70: 44,
            71: 28, 72: 28, 73: 20, 74: 56, 75: 40, 76: 31, 77: 50, 78: 40, 79: 46, 80: 42,
            81: 29, 82: 19, 83: 36, 84: 25, 85: 22, 86: 17, 87: 19, 88: 26, 89: 30, 90: 20,
            91: 15, 92: 21, 93: 11, 94: 8, 95: 8, 96: 19, 97: 5, 98: 8, 99: 8, 100: 11,
            101: 11, 102: 8, 103: 3, 104: 9, 105: 5, 106: 4, 107: 7, 108: 3, 109: 6, 110: 3,
            111: 5, 112: 4, 113: 5, 114: 6
        }
        # Sure isimleri (basit dict, Türkçe kısaltmalar)
        self.sure_names = {
            'fatiha': 1, 'bakara': 2, 'aliimran': 3, 'nisa': 4, 'maide': 5, 'enam': 6, 'araf': 7,
            'enfal': 8, 'tevbe': 9, 'yunus': 10, 'hud': 11, 'yusuf': 12, 'rad': 13, 'ibrahim': 14,
            'hicr': 15, 'nahil': 16, 'isra': 17, 'kehf': 18, 'meryem': 19, 'taha': 20, 'enbiya': 21,
            'hac': 22, 'muminun': 23, 'nur': 24, 'furkan': 25, 'suara': 26, 'neml': 27, 'kasas': 28,
            'ankebut': 29, 'rum': 30, 'lokman': 31, 'secde': 32, 'ahzab': 33, 'seba': 34, 'fatir': 35,
            'yasin': 36, 'saffat': 37, 'sad': 38, 'zumer': 39, 'mumin': 40, 'fussilet': 41, 'sura': 42,
            'zukruf': 43, 'dukhan': 44, 'casiye': 45, 'ahkaf': 46, 'muhammed': 47, 'fetih': 48, 'hucurat': 49,
            'kaf': 50, 'zarciyat': 51, 'tur': 52, 'necm': 53, 'kamer': 54, 'rahman': 55, 'vakia': 56,
            'hadid': 57, 'mucadele': 58, 'hasr': 59, 'mumtahine': 60, 'saff': 61, 'cuma': 62, 'munafikun': 63,
            'tegabun': 64, 'talak': 65, 'tahrim': 66, 'mulk': 67, 'kalem': 68, 'hakka': 69, 'maaric': 70,
            'nuh': 71, 'cin': 72, 'muzzemmil': 73, 'muddessir': 74, 'kiyamet': 75, 'insan': 76, 'mursalat': 77,
            'nebe': 78, 'naziat': 79, 'abese': 80, 'tekvir': 81, 'infitar': 82, 'mutaffifin': 83, 'inşikak': 84,
            'buruc': 85, 'tarik': 86, 'ala': 87, 'gasiye': 88, 'fecr': 89, 'balad': 90, 'şems': 91, 'leyil': 92,
            'duha': 93, 'inşirah': 94, 'tin': 95, 'alak': 96, 'kadir': 97, 'beyyine': 98, 'zilzal': 99, 'adiyat': 100,
            'karia': 101, 'tekasur': 102, 'asr': 103, 'humeze': 104, 'fil': 105, 'kureys': 106, 'maun': 107, 'kevser': 108,
            'kafirun': 109, 'nasr': 110, 'tebbet': 111, 'ihlas': 112, 'felak': 113, 'nas': 114
        }
        self.meal_files = self.get_meal_files()
        self.meal_df = None
        self.favorites_meal_df = None  # Favoriler için Türkçe meal
        self.arapca_df = None
        self.morph_df = None
        self.transcript_df = None
        # Tema sistemi
        self.current_theme = "light"  # "light" veya "dark"
        self.themes = {}
        self.load_themes()
        self.load_theme_preference()
        self.initUI()
        self.load_data()
        self.load_favorites()
        self.apply_theme()  # Tema uygula
        # Kök listesini combo'ya ekle
        if self.kok_df is not None:
            # Tüm kökleri ekle (performans için alfabetik sıralı)
            kok_listesi = sorted(self.kok_df['kelime'].tolist())
            self.root_input.addItems(kok_listesi)
            # QCompleter ekle - tüm köklerle arama önerisi
            completer = QCompleter(kok_listesi)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            completer.setFilterMode(Qt.MatchContains)
            completer.popup().setFont(QFont('Arial Unicode MS', 16))
            completer.popup().setStyleSheet("""
                QListView {
                    font-family: 'Arial Unicode MS';
                    font-size: 16px;
                    padding: 5px;
                }
                QListView::item {
                    padding: 5px;
                    border-bottom: 1px solid #ddd;
                }
                QListView::item:hover {
                    background-color: #e6f3ff;
                }
            """)
            self.root_input.setCompleter(completer)

    def get_verse_count(self, sure):
        return self.verse_counts.get(sure, 0)

    def get_sure_number(self, name):
        name_lower = name.lower().replace(' ', '').replace('ı', 'i').replace('ğ', 'g').replace('ü', 'u').replace('ş', 's').replace('ö', 'o').replace('ç', 'c')
        return self.sure_names.get(name_lower, None)

    def parse_input(self, text):
        text = text.strip()
        if '/' in text:
            parts = text.split('/')
            if len(parts) == 2:
                try:
                    sure = int(parts[0])
                    ayet = int(parts[1])
                    return sure, ayet
                except:
                    pass
        elif text.isdigit():
            total = int(text)
            if 1 <= total <= 6236:
                cumulative = 0
                for s in range(1, 115):
                    vc = self.get_verse_count(s)
                    if cumulative + vc >= total:
                        ayet = total - cumulative
                        return s, ayet
                    cumulative += vc
        else:
            parts = text.split()
            if len(parts) == 2:
                sure_name = parts[0]
                ayet_str = parts[1]
                try:
                    ayet = int(ayet_str)
                    sure = self.get_sure_number(sure_name)
                    if sure:
                        return sure, ayet
                except:
                    pass
        return None, None

    def get_meal_files(self):
        folder = 'tum_mealler'
        files = [f for f in os.listdir(folder) if f.endswith('.csv') and 'arapca' not in f.lower() and 'sozl' not in f.lower() and 'mekki' not in f.lower()]
        return files

    def initUI(self):
        # Araç çubuğu
        self.toolbar = self.addToolBar('Ana Araç Çubuğu')
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        # Tema geçiş butonu
        self.theme_btn = QPushButton("🌙 Karanlık Tema")
        self.theme_btn.clicked.connect(self.toggle_theme)
        self.theme_btn.setFixedSize(140, 35)
        self.toolbar.addWidget(self.theme_btn)

        self.tabs = QTabWidget()
        # Arama sekmesi
        search_tab = QWidget()
        search_layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        self.meal_combo = QComboBox()
        self.meal_combo.addItems(self.meal_files)
        self.meal_combo.setCurrentText("Abdel_Khalek_Himmat.csv")  # Default Türkçe meal
        self.meal_combo.currentIndexChanged.connect(self.load_data)
        top_layout.addWidget(QLabel('Meâl Seç:'))
        top_layout.addWidget(self.meal_combo)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Kelime, ayet numarası veya sure (örn: namaz, 3/7, 1, kok:الله)')
        self.search_input.returnPressed.connect(self.search)
        top_layout.addWidget(self.search_input)
        self.ileri_btn = QPushButton("İleri")
        self.ileri_btn.clicked.connect(self.on_next_clicked)
        self.ileri_btn.setFixedSize(100, 35)
        self.ileri_btn.setStyleSheet("background-color: #FF5722; color: white; font-weight: bold;")
        top_layout.addWidget(self.ileri_btn)
        self.geri_btn = QPushButton("Geri")
        self.geri_btn.clicked.connect(self.on_prev_clicked)
        self.geri_btn.setFixedSize(100, 35)
        self.geri_btn.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold;")
        top_layout.addWidget(self.geri_btn)
        self.search_btn = QPushButton('Ara')
        self.search_btn.clicked.connect(self.search)
        top_layout.addWidget(self.search_btn)
        search_layout.addLayout(top_layout)
        # Sonuçlar için scrollable alan
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.results_widget = QWidget()
        self.results_layout = QVBoxLayout()
        self.results_widget.setLayout(self.results_layout)
        self.scroll.setWidget(self.results_widget)
        search_layout.addWidget(self.scroll)
        search_tab.setLayout(search_layout)
        self.tabs.addTab(search_tab, "Arama")
        # Kök arama sekmesi
        root_tab = QWidget()
        root_layout = QVBoxLayout()
        root_layout.addWidget(QLabel("Kök Arama"))
        self.root_input = QComboBox()
        self.root_input.setEditable(True)
        self.root_input.setPlaceholderText('Arapça kök girin, örn: الله')
        # Arapça font ayarı - daha büyük ve net görünüm için
        self.root_input.setFont(QFont('Arial Unicode MS', 16))
        # Combobox popup listesi için de font ayarı
        self.root_input.setStyleSheet("""
            QComboBox {
                font-family: 'Arial Unicode MS';
                font-size: 16px;
                padding: 5px;
            }
            QComboBox QAbstractItemView {
                font-family: 'Arial Unicode MS';
                font-size: 16px;
                padding: 5px;
            }
        """)
        root_layout.addWidget(self.root_input)
        self.root_btn = QPushButton('Kök Ara')
        self.root_btn.clicked.connect(self.root_search)
        root_layout.addWidget(self.root_btn)
        # Arama içeriği açıklaması
        info_label = QLabel("<b>Arama İçeriği: Harf, Kelime, Fihristi</b>")
        info_label.setStyleSheet("font-size: 12px; color: #555;")
        root_layout.addWidget(info_label)
        # Osmanlıca klavye
        keyboard_layout = QGridLayout()
        arabic_letters = ['ا','ب','ت','ث','ج','ح','خ','د','ذ','ر','ز','س','ش','ص','ض','ط','ظ','ع','غ','ف','ق','ك','ل','م','ن','ه','و','ي','ء','ى']
        row, col = 0, 0
        for letter in arabic_letters:
            btn = QPushButton(letter)
            btn.clicked.connect(lambda checked, char=letter: self.root_input.setEditText(self.root_input.currentText() + char))
            keyboard_layout.addWidget(btn, row, col)
            col += 1
            if col > 9:  # 10 sütun
                col = 0
                row += 1
        root_layout.addLayout(keyboard_layout)
        self.root_results = QTextBrowser()
        self.root_results.setReadOnly(True)
        self.root_results.anchorClicked.connect(self.on_root_link_clicked)
        root_layout.addWidget(self.root_results)
        root_tab.setLayout(root_layout)
        self.tabs.addTab(root_tab, "Kök Arama")
        # Harf analizi sekmesi
        letter_tab = QWidget()
        letter_layout = QVBoxLayout()
        letter_layout.addWidget(QLabel("Harf Analizi"))
        self.letter_input = QLineEdit()
        self.letter_input.setPlaceholderText('Sure/Ayet girin, örn: 1/1')
        letter_layout.addWidget(self.letter_input)
        self.letter_btn = QPushButton('Harfleri Say')
        self.letter_btn.clicked.connect(self.letter_analysis)
        letter_layout.addWidget(self.letter_btn)
        self.letter_results = QTextEdit()
        self.letter_results.setReadOnly(True)
        letter_layout.addWidget(self.letter_results)
        letter_tab.setLayout(letter_layout)
        self.tabs.addTab(letter_tab, "Harf Analizi")
        # Meal karşılaştırma sekmesi
        comparison_tab = QWidget()
        comparison_layout = QVBoxLayout()
        comparison_layout.addWidget(QLabel("Meal Karşılaştırma"))
        self.meal_list = QListWidget()
        for meal in self.meal_files:
            item = QListWidgetItem(meal)
            item.setCheckState(Qt.Unchecked)
            self.meal_list.addItem(item)
        comparison_layout.addWidget(self.meal_list)
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Ayet:"))
        self.comp_input = QLineEdit("")
        self.comp_input.setPlaceholderText("6236, 114/4, Nas 6")
        self.comp_input.setMaximumWidth(200)
        self.comp_input.returnPressed.connect(self.compare_meals)
        input_layout.addWidget(self.comp_input)
        self.prev_btn = QPushButton('Önceki')
        self.prev_btn.clicked.connect(self.prev_verse)
        input_layout.addWidget(self.prev_btn)
        self.next_btn = QPushButton('Sonraki')
        self.next_btn.clicked.connect(self.next_verse)
        input_layout.addWidget(self.next_btn)
        self.comp_btn = QPushButton('Karşılaştır')
        self.comp_btn.clicked.connect(self.compare_meals)
        input_layout.addWidget(self.comp_btn)
        comparison_layout.addLayout(input_layout)
        # Vertical layout for comparison results
        self.left_text = QTextEdit()
        self.left_text.setReadOnly(True)
        self.right_text = QTextEdit()
        self.right_text.setReadOnly(True)
        comparison_layout.addWidget(self.left_text)
        comparison_layout.addWidget(self.right_text)
        comparison_tab.setLayout(comparison_layout)
        self.tabs.addTab(comparison_tab, "Meal Karşılaştırma")
        # Favoriler sekmesi
        favorites_tab = QWidget()
        favorites_layout = QVBoxLayout()

        # Üst kısım: Kontroller
        controls_layout = QHBoxLayout()

        # Arama kutusu
        search_label = QLabel("Ara:")
        self.favorites_search = QLineEdit()
        self.favorites_search.setPlaceholderText("Favorilerde ara...")
        self.favorites_search.textChanged.connect(self.filter_favorites)

        # Sıralama seçeneği
        sort_label = QLabel("Sırala:")
        self.favorites_sort = QComboBox()
        self.favorites_sort.addItems(["Tarih (Yeni-Eski)", "Tarih (Eski-Yeni)", "Sure (Artan)", "Sure (Azalan)", "Ayet (Artan)", "Ayet (Azalan)"])
        self.favorites_sort.currentTextChanged.connect(self.sort_favorites)

        controls_layout.addWidget(search_label)
        controls_layout.addWidget(self.favorites_search)
        controls_layout.addWidget(sort_label)
        controls_layout.addWidget(self.favorites_sort)
        controls_layout.addStretch()

        favorites_layout.addLayout(controls_layout)

        # Favoriler listesi
        self.favorites_list = QListWidget()
        self.favorites_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.favorites_list.customContextMenuRequested.connect(self.show_favorites_context_menu)
        self.favorites_list.itemDoubleClicked.connect(self.show_favorite_ayet)
        favorites_layout.addWidget(self.favorites_list)

        # Alt kısım: İstatistikler ve butonlar
        bottom_layout = QHBoxLayout()

        # İstatistikler
        stats_group = QGroupBox("İstatistikler")
        stats_layout = QVBoxLayout()
        self.stats_label = QLabel("Henüz favori yok")
        stats_layout.addWidget(self.stats_label)
        stats_group.setLayout(stats_layout)
        bottom_layout.addWidget(stats_group)

        # Butonlar
        buttons_layout = QVBoxLayout()
        export_btn = QPushButton("Dışa Aktar")
        export_btn.clicked.connect(self.export_favorites)
        clear_btn = QPushButton("Tümünü Temizle")
        clear_btn.clicked.connect(self.clear_all_favorites)
        buttons_layout.addWidget(export_btn)
        buttons_layout.addWidget(clear_btn)
        buttons_layout.addStretch()
        bottom_layout.addLayout(buttons_layout)

        favorites_layout.addLayout(bottom_layout)

        favorites_tab.setLayout(favorites_layout)
        self.tabs.addTab(favorites_tab, "Favoriler")
        # Ayet ve Sure Bilgileri sekmesi
        info_tab = QWidget()
        info_layout = QVBoxLayout()
        info_layout.addWidget(QLabel("Ayet ve Sure Bilgileri"))
        # Sure seçimi
        sure_layout = QHBoxLayout()
        sure_layout.addWidget(QLabel("Sure:"))
        self.info_sure_combo = QComboBox()
        self.info_sure_combo.addItems([f"{i} - {self.get_sure_name(i)}" for i in range(1, 115)])
        self.info_sure_combo.currentIndexChanged.connect(self.update_ayet_spin)
        sure_layout.addWidget(self.info_sure_combo)
        # Ayet seçimi
        sure_layout.addWidget(QLabel("Ayet:"))
        self.info_ayet_spin = QSpinBox()
        self.info_ayet_spin.setMinimum(1)
        self.info_ayet_spin.setMaximum(7)  # Default Fatiha
        self.info_ayet_spin.valueChanged.connect(self.show_verse_info)
        sure_layout.addWidget(self.info_ayet_spin)
        info_layout.addLayout(sure_layout)
        # Bilgiler gösterimi
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        info_layout.addWidget(self.info_text)
        # Mekki ve Medeni sureler
        lists_layout = QHBoxLayout()
        self.mekki_list = QListWidget()
        self.mekki_list.setMaximumHeight(200)
        lists_layout.addWidget(QLabel("Mekki Sureler:"))
        lists_layout.addWidget(self.mekki_list)
        self.medeni_list = QListWidget()
        self.medeni_list.setMaximumHeight(200)
        lists_layout.addWidget(QLabel("Medeni Sureler:"))
        lists_layout.addWidget(self.medeni_list)
        info_layout.addLayout(lists_layout)
        # Not ekleme
        info_layout.addWidget(QLabel("Not Ekle:"))
        note_layout = QHBoxLayout()
        note_layout.addWidget(QLabel("Etiket:"))
        self.note_tag = QComboBox()
        self.note_tag.addItems(["Genel", "Tefsir", "Hatırlatma", "Araştırma", "Diğer"])
        note_layout.addWidget(self.note_tag)
        info_layout.addLayout(note_layout)
        self.note_text = QTextEdit()
        info_layout.addWidget(self.note_text)
        btn_layout = QHBoxLayout()
        save_note_btn = QPushButton("Notu Kaydet")
        save_note_btn.clicked.connect(self.save_note)
        btn_layout.addWidget(save_note_btn)
        edit_note_btn = QPushButton("Düzenle")
        edit_note_btn.clicked.connect(self.edit_note)
        btn_layout.addWidget(edit_note_btn)
        delete_note_btn = QPushButton("Notu Sil")
        delete_note_btn.clicked.connect(self.delete_note)
        btn_layout.addWidget(delete_note_btn)
        info_layout.addLayout(btn_layout)
        info_tab.setLayout(info_layout)
        self.tabs.addTab(info_tab, "Ayet ve Sure Bilgileri")
        self.tabs.addTab(self.create_audio_tab(), "Sesli Tilavet")
        # Ana widget
        self.setCentralWidget(self.tabs)
        self.result_count_label = QLabel("")
        # Status bar'a ekle
        self.statusBar().addWidget(self.result_count_label)
        self.load_data()
        self.populate_lists()

    def load_data(self):
        folder = 'tum_mealler'
        files = [f for f in os.listdir(folder) if f.endswith('.csv') and 'arapca' not in f.lower() and 'sozl' not in f.lower() and 'mekki' not in f.lower()]
        meal_file = self.meal_combo.currentText() if hasattr(self, 'meal_combo') and self.meal_combo.currentText() else (files[0] if files else None)
        files = [f for f in os.listdir(folder) if f.endswith('.csv') and 'arapca' not in f.lower() and 'sozl' not in f.lower() and 'mekki' not in f.lower()]
        meal_file = self.meal_combo.currentText() if hasattr(self, 'meal_combo') and self.meal_combo.currentText() else (files[0] if files else None)
        try:
            if meal_file:
                self.meal_df = pd.read_csv(os.path.join(folder, meal_file), dtype=str, encoding='utf-8-sig', engine='python', quoting=0, on_bad_lines='skip')
        except Exception as e:
            print(f"Exception loading meal_df: {e}")
            self.meal_df = None

        # Favoriler için Türkçe meal yükle (Erhan Aktaş 10. Baskı)
        favorites_meal_path = os.path.join(folder, 'Erhan_Aktaş_(10_Baskı).csv')
        try:
            if os.path.exists(favorites_meal_path):
                self.favorites_meal_df = pd.read_csv(favorites_meal_path, dtype=str, encoding='utf-8-sig', engine='python', quoting=0, on_bad_lines='skip')
            else:
                self.favorites_meal_df = self.meal_df  # Yedek olarak ana meal'i kullan
        except Exception as e:
            print(f"Exception loading favorites_meal_df: {e}")
            self.favorites_meal_df = self.meal_df  # Yedek olarak ana meal'i kullan

        # Önce arapca_ayetler.csv'yi dene
        arapca_csv_path = os.path.join(folder, 'arapca_ayetler.csv')
        try:
            if os.path.exists(arapca_csv_path):
                self.arapca_df = pd.read_csv(arapca_csv_path, dtype=str, encoding='utf-8-sig', engine='python', quoting=0, on_bad_lines='skip')
                if self.arapca_df is not None:
                    self.arapca_df['metin'] = self.arapca_df['metin'].apply(lambda x: unicodedata.normalize('NFC', x))
            else:
                self.arapca_df = None
        except Exception as e:
            print(f"Exception loading arapca_df: {e}")
            self.arapca_df = None
        # Transkript için kuran_meali_abay_yazilisi_6236_besmele.csv'yi yükle
        transcript_csv_path = os.path.join(folder, 'kuran_meali_abay_yazilisi_6236_besmele.csv')
        try:
            if os.path.exists(transcript_csv_path):
                self.transcript_df = pd.read_csv(transcript_csv_path, dtype=str, encoding='utf-8-sig', engine='python', quoting=1, on_bad_lines='skip')
            else:
                self.transcript_df = None
        except Exception as e:
            print(f"Exception loading transcript_df: {e}")
            self.transcript_df = None
        # Kök kelime verisini yükle
        kok_csv_path = 'kokkelime.csv'
        try:
            if os.path.exists(kok_csv_path):
                self.kok_df = pd.read_csv(kok_csv_path, header=None, names=['kelime', 'frekans'], dtype=str, encoding='utf-8-sig', engine='python', quoting=3, on_bad_lines='skip')
            else:
                self.kok_df = None
        except Exception as e:
            print(f"Exception loading kok_df: {e}")
            self.kok_df = None
        # Morfoloji verisini yükle
        morph_csv_path = 'morphology.csv'
        try:
            if os.path.exists(morph_csv_path):
                self.morph_df = pd.read_csv(morph_csv_path, dtype=str, encoding='utf-8-sig', engine='python', quoting=3, on_bad_lines='skip')
            else:
                self.morph_df = None
        except Exception as e:
            print(f"Exception loading morph_df: {e}")
            self.morph_df = None
        # Mekki Medeni verisini yükle
        mekki_csv_path = 'mekki_medeni.csv'
        try:
            if os.path.exists(mekki_csv_path):
                self.mekki_df = pd.read_csv(mekki_csv_path, dtype=str, encoding='utf-8-sig', engine='python', quoting=3, on_bad_lines='skip')
            else:
                self.mekki_df = None
        except Exception as e:
            print(f"Exception loading mekki_df: {e}")
            self.mekki_df = None
        # Arapça json yükle
        try:
            with open('quran_arabic_6236.json', 'r', encoding='utf-8') as f:
                self.arapca_json = json.load(f)
        except Exception as e:
            print(f"Exception loading arapca_json: {e}")
            self.arapca_json = []

    def load_favorites(self):
        try:
            with open('favorites.json', 'r', encoding='utf-8') as f:
                self.favorites = json.load(f)
                self.update_favorites_list()
        except:
            self.favorites = []

    def save_favorites(self):
        with open('favorites.json', 'w', encoding='utf-8') as f:
            json.dump(self.favorites, f)

    def add_favorite(self, sure, ayet):
        if (sure, ayet) not in self.favorites:
            self.favorites.append((sure, ayet))
            self.save_favorites()
            self.update_favorites_list()

    def remove_favorite(self, sure, ayet):
        if (sure, ayet) in self.favorites:
            self.favorites.remove((sure, ayet))
            self.save_favorites()
            self.update_favorites_list()

    def update_favorites_list(self):
        self.favorites_list.clear()
        for sure, ayet in self.favorites:
            # Ayetin kısa metnini al (favoriler için Türkçe meal kullan)
            meal_text = ""
            meal_df_to_use = self.favorites_meal_df if self.favorites_meal_df is not None else self.meal_df
            if meal_df_to_use is not None:
                meal_row = meal_df_to_use[(meal_df_to_use['sure'] == str(sure)) & (meal_df_to_use['ayet'] == str(ayet))]
                if not meal_row.empty:
                    meal_text = meal_row.iloc[0]['metin'][:50] + "..." if len(meal_row.iloc[0]['metin']) > 50 else meal_row.iloc[0]['metin']

            # Zengin öğe oluştur
            display_text = f"{sure}:{ayet} - {meal_text}"
            item = QListWidgetItem(display_text)
            item.setToolTip(f"Sure {sure}, Ayet {ayet}\n{meal_text}")
            self.favorites_list.addItem(item)

        self.update_favorites_stats()

    def show_favorite_ayet(self, item):
        text = item.text()
        # "sure:ayet - meal_text" formatından sure:ayet kısmını al
        sure_ayet_part = text.split(' - ')[0]
        sure, ayet = sure_ayet_part.split(':')
        sure = int(sure)
        ayet = int(ayet)
        self.on_root_link_clicked(f"{sure}/{ayet}")

    def update_favorites_stats(self):
        if not self.favorites:
            self.stats_label.setText("Henüz favori yok")
            return

        total_favs = len(self.favorites)
        sure_counts = {}
        for sure, ayet in self.favorites:
            sure_counts[sure] = sure_counts.get(sure, 0) + 1

        most_fav_sure = max(sure_counts.items(), key=lambda x: x[1]) if sure_counts else (0, 0)
        sure_name = self.get_sure_name(most_fav_sure[0]) if most_fav_sure[0] else "Bilinmiyor"

        stats_text = f"""Toplam Favori: {total_favs}
En Çok Favorilenen Sure: {most_fav_sure[0]} - {sure_name} ({most_fav_sure[1]} ayet)
Farklı Sure Sayısı: {len(sure_counts)}"""

        self.stats_label.setText(stats_text)

    def filter_favorites(self):
        search_text = self.favorites_search.text().lower()
        for i in range(self.favorites_list.count()):
            item = self.favorites_list.item(i)
            item.setHidden(search_text not in item.text().lower())

    def sort_favorites(self):
        sort_type = self.favorites_sort.currentText()

        if sort_type == "Tarih (Yeni-Eski)":
            # Favoriler listesi zaten eklenme sırasına göre
            pass
        elif sort_type == "Tarih (Eski-Yeni)":
            self.favorites.reverse()
        elif sort_type == "Sure (Artan)":
            self.favorites.sort(key=lambda x: x[0])
        elif sort_type == "Sure (Azalan)":
            self.favorites.sort(key=lambda x: x[0], reverse=True)
        elif sort_type == "Ayet (Artan)":
            self.favorites.sort(key=lambda x: x[1])
        elif sort_type == "Ayet (Azalan)":
            self.favorites.sort(key=lambda x: x[1], reverse=True)

        self.update_favorites_list()

    def export_favorites(self):
        from PyQt5.QtWidgets import QFileDialog
        filename, _ = QFileDialog.getSaveFileName(self, "Favorileri Dışa Aktar", "", "JSON Files (*.json);;CSV Files (*.csv)")

        if filename:
            if filename.endswith('.json'):
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.favorites, f, indent=2)
            elif filename.endswith('.csv'):
                import csv
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Sure', 'Ayet', 'Metin'])
                    meal_df_to_use = self.favorites_meal_df if self.favorites_meal_df is not None else self.meal_df
                    for sure, ayet in self.favorites:
                        meal_text = ""
                        if meal_df_to_use is not None:
                            meal_row = meal_df_to_use[(meal_df_to_use['sure'] == str(sure)) & (meal_df_to_use['ayet'] == str(ayet))]
                            if not meal_row.empty:
                                meal_text = meal_row.iloc[0]['metin']
                        writer.writerow([sure, ayet, meal_text])

    def clear_all_favorites(self):
        reply = QMessageBox.question(self, 'Tüm Favorileri Temizle',
                                   'Tüm favori ayetleri kaldırmak istediğinizden emin misiniz?',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.favorites.clear()
            self.save_favorites()
            self.update_favorites_list()

    def load_themes(self):
        """Tema dosyalarını yükle"""
        import os
        themes_dir = "themes"
        if not os.path.exists(themes_dir):
            os.makedirs(themes_dir)

        # Varsayılan temaları yükle
        self.themes = {}  # Temizle

        self.themes["light"] = {
            "name": "Açık Tema",
            "is_dark": False,
            "colors": {
                "primary": "#4CAF50",
                "secondary": "#2196F3",
                "accent": "#FF9800",
                "background": "#f5f5f5",
                "surface": "#ffffff",
                "text": "#212121",
                "text_secondary": "#757575",
                "border": "#e0e0e0",
                "hover": "#f0f0f0",
                "selected": "#e3f2fd",
                "error": "#f44336",
                "success": "#4CAF50",
                "warning": "#FF9800"
            }
        }

        self.themes["dark"] = {
            "name": "Karanlık Tema",
            "is_dark": True,
            "colors": {
                "primary": "#81C784",
                "secondary": "#64B5F6",
                "accent": "#FFB74D",
                "background": "#121212",
                "surface": "#1e1e1e",
                "text": "#ffffff",
                "text_secondary": "#b0b0b0",
                "border": "#333333",
                "hover": "#2a2a2a",
                "selected": "#333333",
                "error": "#ef5350",
                "success": "#81C784",
                "warning": "#FFB74D"
            }
        }

        print(f"Temalar yüklendi: {list(self.themes.keys())}")  # Debug

    def apply_theme(self):
        """Mevcut temayı uygula"""
        if self.current_theme not in self.themes:
            return

        theme = self.themes[self.current_theme]
        colors = theme["colors"]

        # Qt Style Sheet oluştur
        qss = f"""
        QMainWindow {{
            background-color: {colors['background']};
            color: {colors['text']};
        }}

        QTabWidget::pane {{
            border: 1px solid {colors['border']};
            background-color: {colors['surface']};
        }}

        QTabBar::tab {{
            background-color: {colors['background']};
            color: {colors['text']};
            padding: 8px 16px;
            border: 1px solid {colors['border']};
            margin-right: 2px;
            border-radius: 4px;
        }}

        QTabBar::tab:selected {{
            background-color: {colors['surface']};
            border-bottom: 2px solid {colors['primary']};
        }}

        QTabBar::tab:hover {{
            background-color: {colors['hover']};
        }}

        QListWidget {{
            background-color: {colors['surface']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            border-radius: 4px;
        }}

        QListWidget::item:hover {{
            background-color: {colors['hover']};
        }}

        QListWidget::item:selected {{
            background-color: {colors['selected']};
        }}

        QPushButton {{
            background-color: {colors['surface']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            padding: 6px 12px;
            border-radius: 4px;
        }}

        QPushButton:hover {{
            background-color: {colors['hover']};
        }}

        QPushButton:pressed {{
            background-color: {colors['selected']};
        }}

        QLineEdit {{
            background-color: {colors['surface']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            padding: 4px;
            border-radius: 4px;
        }}

        QComboBox {{
            background-color: {colors['surface']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            padding: 4px;
            border-radius: 4px;
        }}

        QComboBox::drop-down {{
            border: none;
        }}

        QGroupBox {{
            font-weight: bold;
            border: 2px solid {colors['border']};
            border-radius: 5px;
            margin-top: 1ex;
            color: {colors['text']};
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }}

        QTextEdit {{
            background-color: {colors['surface']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            border-radius: 4px;
        }}

        QLabel {{
            color: {colors['text']};
        }}

        QScrollBar:vertical {{
            background-color: {colors['background']};
            width: 12px;
            border-radius: 6px;
        }}

        QScrollBar::handle:vertical {{
            background-color: {colors['border']};
            border-radius: 6px;
        }}

        QScrollBar::handle:vertical:hover {{
            background-color: {colors['text_secondary']};
        }}
        """

        # QApplication'a QSS uygula
        self.app.setStyleSheet(qss)

        # Tema buton metnini güncelle
        theme_name = self.themes[self.current_theme]["name"]
        icon = "☀️" if self.current_theme == "light" else "🌙"
        self.theme_btn.setText(f"{icon} {theme_name}")

        # Özel widget'lar için ek stiller
        self.update_widget_styles()

    def update_widget_styles(self):
        """Özel widget'lar için tema stillerini güncelle"""
        theme = self.themes[self.current_theme]
        colors = theme["colors"]

        # Favori butonları için özel stiller
        fav_button_style = f"""
        QPushButton {{
            background-color: {colors['accent']};
            color: {'#000000' if theme['is_dark'] else '#ffffff'};
            font-weight: bold;
            font-size: 12px;
            padding: 8px 12px;
            border: 2px solid {colors['primary']};
            border-radius: 5px;
        }}
        QPushButton:hover {{
            background-color: {colors['primary']};
        }}
        QPushButton:pressed {{
            background-color: {colors['secondary']};
        }}
        """

        # Arama sonuçlarındaki oynat butonları
        play_button_style = f"""
        QPushButton {{
            background-color: {colors['success']};
            color: white;
            font-weight: bold;
            font-size: 12px;
            padding: 8px 12px;
            border: 2px solid {colors['primary']};
            border-radius: 5px;
        }}
        QPushButton:hover {{
            background-color: {colors['primary']};
        }}
        QPushButton:pressed {{
            background-color: {colors['secondary']};
        }}
        """

        # Tüm butonları güncelle (bu biraz agresif olabilir, ama çalışır)
        for button in self.findChildren(QPushButton):
            if "Favoriye Ekle" in button.text():
                button.setStyleSheet(fav_button_style)
            elif "▶ Oynat" in button.text():
                button.setStyleSheet(play_button_style)

    def toggle_theme(self):
        """Tema değiştir"""
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme()
        # Tema buton metnini güncelle
        theme_name = self.themes[self.current_theme]["name"]
        icon = "☀️" if self.current_theme == "light" else "🌙"
        self.theme_btn.setText(f"{icon} {theme_name}")
        # Tema tercihini kaydet
        self.save_theme_preference()

    def save_theme_preference(self):
        """Tema tercihini kaydet"""
        try:
            with open('theme_preference.json', 'w', encoding='utf-8') as f:
                json.dump({"current_theme": self.current_theme}, f)
        except Exception as e:
            print(f"Tema tercihi kaydetme hatası: {e}")

    def load_theme_preference(self):
        """Tema tercihini yükle"""
        try:
            with open('theme_preference.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.current_theme = data.get("current_theme", "light")
        except:
            self.current_theme = "light"

    def show_favorites_context_menu(self, position):
        menu = QMenu()
        remove_action = menu.addAction("Kaldır")
        copy_action = menu.addAction("Metni Kopyala")
        export_action = menu.addAction("Bu Ayeti Dışa Aktar")

        action = menu.exec_(self.favorites_list.mapToGlobal(position))
        if action == remove_action:
            item = self.favorites_list.itemAt(position)
            if item:
                text = item.text()
                sure, ayet = text.split(':')[0], text.split(':')[1].split(' - ')[0]
                self.remove_favorite(int(sure), int(ayet))
        elif action == copy_action:
            item = self.favorites_list.itemAt(position)
            if item:
                QApplication.clipboard().setText(item.toolTip())
        elif action == export_action:
            item = self.favorites_list.itemAt(position)
            if item:
                text = item.text()
                sure, ayet = text.split(':')[0], text.split(':')[1].split(' - ')[0]
                sure, ayet = int(sure), int(ayet)

                filename, _ = QFileDialog.getSaveFileName(self, f"Ayet {sure}:{ayet} Dışa Aktar", "", "Text Files (*.txt)")
                if filename:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(f"Ayet {sure}:{ayet}\n\n")
                        meal_df_to_use = self.favorites_meal_df if self.favorites_meal_df is not None else self.meal_df
                        if meal_df_to_use is not None:
                            meal_row = meal_df_to_use[(meal_df_to_use['sure'] == str(sure)) & (meal_df_to_use['ayet'] == str(ayet))]
                            if not meal_row.empty:
                                f.write(f"Türkçe: {meal_row.iloc[0]['metin']}\n\n")

                        arapca = self.get_arabic_text(sure, ayet)
                        if arapca:
                            f.write(f"Arapça: {arapca}\n\n")

                        transcript = self.get_transcript_text(sure, ayet)
                        if transcript:
                            f.write(f"Transkript: {transcript}\n")

    def populate_lists(self):
        if self.mekki_df is not None:
            mekki = self.mekki_df[self.mekki_df['tur'] == 'Mekki']
            medeni = self.mekki_df[self.mekki_df['tur'] == 'Medeni']
            for _, row in mekki.iterrows():
                self.mekki_list.addItem(f"{row['sure']} - {row['sure_adi']}")
            for _, row in medeni.iterrows():
                self.medeni_list.addItem(f"{row['sure']} - {row['sure_adi']}")

    def get_arabic_text(self, sure, ayet):
        # Önce arapca_ayetler.csv'den al
        if self.arapca_df is not None:
            match = self.arapca_df[(self.arapca_df['sure'] == str(sure)) & (self.arapca_df['ayet'] == str(ayet))]
            if not match.empty:
                return match.iloc[0]['metin']
        # Eksikse quran_arabic_6236.json'dan al
        if self.arapca_json:
            for item in self.arapca_json:
                if str(item.get('sure')) == str(sure) and str(item.get('ayet')) == str(ayet):
                    return item.get('metin')
        return ''

    def get_transcript_text(self, sure, ayet):
        # kuran_meali_abay_yazilisi_6236_besmele.csv'den al
        if self.transcript_df is not None:
            match = self.transcript_df[(self.transcript_df['Sure'] == str(sure)) & (self.transcript_df['Ayet'] == str(ayet))]
            if not match.empty:
                return match.iloc[0]['Metin']
        return ''

    def highlight_text(self, text, keyword):
        if not keyword:
            return text
        # Metni ve keyword'i normalize et
        normalized_text = self.normalize_text(text)
        normalized_keyword = self.normalize_text(keyword)
        # Case insensitive vurgu
        pattern = re.compile(re.escape(normalized_keyword), re.IGNORECASE)
        # Orijinal metinde vurgula
        highlighted_normalized = pattern.sub(f'<span style="background-color: yellow;">\\g<0></span>', normalized_text)
        # Ama vurgulanmış kısımları orijinal metinden al
        # Bu karmaşık, basitçe orijinal text'te normalized_keyword ile ara
        # Ama normalized_keyword orijinal text'te olmayabilir
        # Daha iyi: normalized_text'te highlight yap, ama span içinde orijinal karakterleri kullan
        # Bu zor, basitçe normalized_text'te highlight yap, ama kullanıcıya gösterirken sorun olmaz mı?
        # Hayır, çünkü highlight sadece görünüm için, ama text normalize edilmiş olmaz.
        # Aslında, highlight HTML'de yapılır, ama text normalize edilmiş olmaz.
        # Daha iyi yol: text'i normalize et, highlight yap, ama span içinde normalize edilmiş kısmı kullan.
        # Ama kullanıcı normalize edilmiş text görmek istemez.
        # Doğru yol: orijinal text'te, normalize edilmiş keyword'e karşılık gelen orijinal substring'i bul.
        # Bu regex ile zor.
        # Basit yol: text'i normalize et, highlight yap, ama span'ları orijinal text'e map et.
        # Çok karmaşık.
        # Alternatif: highlight_text'i değiştir, text'i normalize etmeden, keyword'i normalize et, ama case insensitive ile ara.
        # Ama özel karakterler için case insensitive çalışmaz.
        # re.IGNORECASE sadece ASCII için.
        # Bu yüzden normalize gerekli.
        # En iyi: text'i normalize et, highlight yap, ama HTML'de span'ları orijinal text'e göre ayarla.
        # Ama bu çok zor.
        # Basit çözüm: arama normalize ile, highlight da normalize edilmiş text'te normalize edilmiş keyword ile, ama kullanıcıya normalize edilmiş text göster.
        # Ama kullanıcı orijinal text görmek istiyor.
        # Bu yüzden, highlight_text'te text'i normalize et, highlight yap, ama span içinde orijinal karakterleri kullan.
        # Nasıl?
        # pattern.sub ile, ama sub fonksiyonu kullan, orijinal text'ten al.
        # Evet, pattern normalized_text'te çalışır, ama sub fonksiyonunda orijinal text'ten karakterleri al.
        # Bu mümkün değil kolayca.
        # Daha basit: highlight_text'i iki parametre al, normalized_text ve orijinal_text, ama karmaşık.
        # Alternatif: highlight_text içinde text'i normalize et, highlight yap, döndür, ama kullanıcı normalize edilmiş text görür, ama highlight ile.
        # Ama orijinal karakterler korunur mu? Normalize sadece değiştirir, ama highlight span ekler.
        # Hayır, normalize 'â' -> 'a' yapar, kullanıcı 'a' görür.
        # Bu yanlış.
        # Doğru yol: highlight_text'i değiştir, keyword'i normalize et, text'i normalize etme, ama pattern ile ara, ama özel karakterler için.
        # re.IGNORECASE çalışmaz 'â' için.
        # Bu yüzden, text'i normalize et, highlight yap, ama span'ları orijinal text'e map et.
        # Nasıl?
        # normalized_text'te match bul, pozisyon al, orijinal text'te aynı pozisyonda span ekle.
        # Evet, bu mümkün.
        # Ama karmaşık.
        # Basit çözüm: normalize_text'i kullan, ama highlight için orijinal keyword ile ara, case insensitive ile, ama özel karakterler için normalize kullan.
        # Ama 'â' ve 'a' farklı.
        # Kullanıcı "amnetu" aradı, "âmentu" bulundu, highlight "âmentu" içinde "âmentu" yi highlight etmeli, ama keyword "amnetu".
        # Bu yüzden, highlight_text'te keyword'i normalize etme, text'i normalize etme, ama pattern ile re.escape(keyword), re.IGNORECASE, ama 'â' != 'a'.
        # Bu çalışmaz.
        # Çözüm: highlight_text'te text'i normalize et, keyword'i normalize et, highlight yap, ama döndürülen HTML'de span'ları orijinal text'e göre ayarla.
        # Nasıl?
        # normalized_text'te pattern.sub yap, ama sub fonksiyonunda, match.start() ve match.end() al, orijinal text'ten o pozisyondaki substring'i al, span içine koy.
        # Evet, bu çalışır.
        # Python'da pattern.sub(lambda m: f'<span...>{text[m.start():m.end()]}</span>', normalized_text)
        # Evet!
        # text orijinal, normalized_text normalize edilmiş.
        # pattern normalized_keyword ile normalized_text'te çalışır.
        # sub lambda ile, m.start() ve m.end() ile orijinal text'ten al.
        # Evet. 

        normalized_text = self.normalize_text(text)
        normalized_keyword = self.normalize_text(keyword)
        pattern = re.compile(re.escape(normalized_keyword), re.IGNORECASE)
        def replacer(match):
            start = match.start()
            end = match.end()
            original_part = text[start:end]  # orijinal text'ten al
            return f'<span style="background-color: yellow; font-weight: bold; font-size: 14px;">{original_part}</span>'
        return pattern.sub(replacer, normalized_text)

    def normalize_text(self, text):
        # Türkçe karakterleri normalize et
        normalize_map = {
            'â': 'a', 'Â': 'a', 'î': 'i', 'Î': 'i', 'û': 'u', 'Û': 'u',
            'ş': 's', 'Ş': 's', 'ğ': 'g', 'Ğ': 'g', 'ü': 'u', 'Ü': 'u',
            'ö': 'o', 'Ö': 'o', 'ç': 'c', 'Ç': 'c', 'ı': 'i', 'İ': 'i'
        }
        for old, new in normalize_map.items():
            text = text.replace(old, new)
        return text.lower()

    def normalize_arabic(self, text):
        for harf in self.harekeler:
            text = text.replace(harf, '')
        return text

    def search(self):
        # Önceki sonuçları temizle
        for i in reversed(range(self.results_layout.count())):
            widget = self.results_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        self.result_count_label.setText("")
        orijinal_keyword = self.search_input.text().strip()
        keyword = self.normalize_text(orijinal_keyword)
        if not keyword:
            return
        # Harf arama kontrolü: tek harf Arapça ise, o harfle başlayan kökleri göster
        arabic_letters = ['ا','ب','ت','ث','ج','ح','خ','د','ذ','ر','ز','س','ش','ص','ض','ط','ظ','ع','غ','ف','ق','ك','ل','م','ن','ه','و','ي','ء','ى']
        if len(orijinal_keyword) == 1 and orijinal_keyword in arabic_letters:
            if self.kok_df is not None:
                starting_roots = self.kok_df[self.kok_df['kelime'].str.startswith(orijinal_keyword)]
                if not starting_roots.empty:
                    for _, row in starting_roots.head(10).iterrows():  # İlk 10 kökü göster
                        kok = row['kelime']
                        frekans = row['frekans']
                        # Kök için ayetleri bul
                        arapca_matches = []
                        if self.arapca_df is not None:
                            found = self.arapca_df[self.arapca_df['metin'].apply(self.normalize_arabic).str.contains(re.escape(kok), regex=True, na=False)]
                            for _, arow in found.iterrows():
                                match = self.meal_df[(self.meal_df['sure'] == arow['sure']) & (self.meal_df['ayet'] == arow['ayet'])]
                                if not match.empty:
                                    arapca_matches.append({'meal': match.iloc[0], 'arapca': arow['metin']})
                        results = pd.DataFrame(arapca_matches)
                        # Sonuçları göster
                        text = f"<h3>Kök '{kok}' (Harf: {orijinal_keyword}) ebced: {sum(self.ebced.get(h, 0) for h in kok)}, frekans: {frekans}</h3>"
                        text += f"<p>Bulunan ayet sayısı: {len(results)}</p>"
                        for _, r in results.iterrows():
                            arapca_text = r['arapca']
                            normalized = self.normalize_arabic(arapca_text)
                            ayet_ebced = sum(self.ebced.get(harf, 0) for harf in normalized)
                            text += f"<h4>{r['meal']['sure']}:{r['meal']['ayet']}</h4>"
                            text += f"<p><b>Arapça:</b> {self.highlight_text(arapca_text, kok)}</p>"
                            text += f"<p><b>Türkçe:</b> {self.highlight_text(r['meal']['metin'], orijinal_keyword)}</p>"
                            text += f"<p><b>Ayet Ebced:</b> {ayet_ebced}</p>"
                            text += "<hr>"
                        # Sonuç kutusu ekle
                        result_box = QFrame()
                        result_box.setFrameStyle(QFrame.Box)
                        result_layout = QVBoxLayout()
                        result_text = QTextEdit()
                        result_text.setReadOnly(True)
                        result_text.setHtml(text)
                        result_text.setTextInteractionFlags(Qt.TextSelectableByMouse)
                        result_layout.addWidget(result_text)
                        result_box.setLayout(result_layout)
                        self.results_layout.addWidget(result_box)
                    self.result_count_label.setText(f"{len(starting_roots)} kök bulundu (ilk 10 gösterildi)")
                    return
        # Kök arama kontrolü
        if orijinal_keyword.startswith('kok:'):
            kok = orijinal_keyword[4:].strip()
            if self.morph_df is not None:
                kok_row = self.morph_df[self.morph_df['kelime'] == kok]
                if not kok_row.empty:
                    frekans = kok_row['frekans'].values[0]
                    # Kök içeren ayetleri bul
                    arapca_matches = []
                    if self.arapca_df is not None:
                        found = self.arapca_df[self.arapca_df['metin'].str.contains(kok, na=False)]
                        for _, arow in found.iterrows():
                            match = self.meal_df[(self.meal_df['sure'] == arow['sure']) & (self.meal_df['ayet'] == arow['ayet'])]
                            if not match.empty:
                                arapca_matches.append(match.iloc[0])
                    results = pd.DataFrame(arapca_matches)
                    self.result_count_label.setText(f"Kök '{kok}' {frekans} kez geçiyor, {len(results)} ayet bulundu")
                    self.show_results(results, kok)
                    return
                else:
                    self.result_count_label.setText(f"Kök '{kok}' bulunamadı")
                    return
            else:
                self.result_count_label.setText("Kök verisi yüklenemedi")
                return
        else:
            # Normal arama
            # Ayet/sure arama
            sure, ayet = self.parse_input(orijinal_keyword)
            if sure and ayet:
                # Tek ayet göster
                results = self.meal_df[(self.meal_df['sure'] == str(sure)) & (self.meal_df['ayet'] == str(ayet))]
            elif keyword.isdigit():
                results = self.meal_df[self.meal_df['sure'] == int(keyword)]
            else:
                # Normalize edilmiş metinlerde ara
                results = self.meal_df[self.meal_df['metin'].apply(self.normalize_text).str.contains(keyword, na=False)]
                arapca_matches = []
                if self.arapca_df is not None:
                    arapca_found = self.arapca_df[self.arapca_df['metin'].apply(self.normalize_text).str.contains(keyword, na=False)]
                    for _, arow in arapca_found.iterrows():
                        match = self.meal_df[(self.meal_df['sure'] == arow['sure']) & (self.meal_df['ayet'] == arow['ayet'])]
                        if not match.empty:
                            arapca_matches.append(match.iloc[0])
                # Transkript'te ara
                transcript_matches = []
                if self.transcript_df is not None:
                    transcript_found = self.transcript_df[self.transcript_df['Metin'].apply(self.normalize_text).str.contains(keyword, na=False)]
                    for _, trow in transcript_found.iterrows():
                        match = self.meal_df[(self.meal_df['sure'] == str(trow['Sure'])) & (self.meal_df['ayet'] == str(trow['Ayet']))]
                        if not match.empty:
                            transcript_matches.append(match.iloc[0])
                if arapca_matches or transcript_matches:
                    results = pd.concat([results, pd.DataFrame(arapca_matches + transcript_matches)], ignore_index=True).drop_duplicates()
            self.show_results(results, keyword)

    def show_results(self, results, keyword):
        for _, row in results.iterrows():
            arapca_raw = self.get_arabic_text(row['sure'], row['ayet'])
            arapca = ''
            transcript = self.get_transcript_text(row['sure'], row['ayet'])
            if arapca_raw:
                reshaped = arabic_reshaper.reshape(arapca_raw)
                arapca = reshaped
            # Sonuç kutusu: Türkçe, Arapça ve Transkript ayrı kutucuklarda
            result_box = QFrame()
            result_box.setFrameStyle(QFrame.Box)
            result_layout = QVBoxLayout()
            # Play butonu
            s = str(row['sure'])
            a = str(row['ayet'])
            play_btn = QPushButton("▶ Oynat")
            play_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    font-weight: bold;
                    font-size: 12px;
                    padding: 8px 12px;
                    border: 2px solid #45a049;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
                QPushButton:pressed {
                    background-color: #3e8e41;
                }
            """)
            play_btn.setFixedSize(100, 35)
            play_btn.clicked.connect(lambda checked, s=s, a=a: self.play_verse_audio(int(s), int(a)))
            result_layout.addWidget(play_btn)
            # Türkçe kutucuk
            turk_group = QGroupBox("Türkçe Meâl")
            turk_layout = QVBoxLayout()
            turk_text = QTextEdit()
            turk_text.setReadOnly(True)
            turk_text.setFont(self.font_turkish)
            turk_text.setHtml(self.highlight_text(f"[{row['sira']}] {row['sure']}/{row['ayet']}\n{row['metin']}", keyword))
            turk_text.setTextInteractionFlags(Qt.TextSelectableByMouse)
            turk_layout.addWidget(turk_text)
            turk_group.setLayout(turk_layout)
            result_layout.addWidget(turk_group)
            # Arapça kutucuk
            if arapca:
                arap_group = QGroupBox("Arapça Metin")
                arap_layout = QVBoxLayout()
                arap_text = QTextEdit()
                arap_text.setReadOnly(True)
                arap_text.setFont(self.font_arabic)
                arap_text.setHtml(self.highlight_text(arapca, keyword))
                arap_text.setAlignment(Qt.AlignRight)
                arap_text.setLayoutDirection(Qt.RightToLeft)
                arap_text.setTextInteractionFlags(Qt.TextSelectableByMouse)
                arap_layout.addWidget(arap_text)
                # Ayet ebced hesapla
                normalized = self.normalize_arabic(arapca_raw)
                ayet_ebced = sum(self.ebced.get(harf, 0) for harf in normalized)
                ebced_label = QLabel(f"Ayet Ebced: {ayet_ebced}")
                arap_layout.addWidget(ebced_label)
                arap_group.setLayout(arap_layout)
                result_layout.addWidget(arap_group)
            # Transkript kutucuk
            if transcript:
                trans_group = QGroupBox("Transkript (Abay Yazılışı)")
                trans_layout = QVBoxLayout()
                trans_text = QTextEdit()
                trans_text.setReadOnly(True)
                trans_text.setFont(self.font_turkish)
                trans_text.setHtml(self.highlight_text(transcript, keyword))
                trans_text.setTextInteractionFlags(Qt.TextSelectableByMouse)
                trans_layout.addWidget(trans_text)
                trans_group.setLayout(trans_layout)
                result_layout.addWidget(trans_group)
            # Favoriye Ekle butonu
            fav_btn = QPushButton("⭐ Favoriye Ekle")
            fav_btn.setStyleSheet("""
                QPushButton {
                    background-color: #FFD700;
                    color: black;
                    font-weight: bold;
                    font-size: 12px;
                    padding: 8px 12px;
                    border: 2px solid #FFA500;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #FFA500;
                }
                QPushButton:pressed {
                    background-color: #FF8C00;
                }
            """)
            fav_btn.setFixedSize(150, 35)
            fav_btn.clicked.connect(lambda checked, s=row['sure'], a=row['ayet']: self.add_favorite(s, a))
            result_layout.addWidget(fav_btn)
            result_box.setLayout(result_layout)
            self.results_layout.addWidget(result_box)
        self.result_count_label.setText(f"{len(results)} sonuç bulundu")

    def on_next_clicked(self):
        sure, ayet = self.parse_input(self.search_input.text())
        if sure and ayet:
            max_ayet = self.get_verse_count(sure)
            if ayet < max_ayet:
                ayet += 1
            else:
                sure += 1
                if sure > 114:
                    sure = 1
                ayet = 1
            self.search_input.setText(f"{sure}/{ayet}")
            self.search()
        print("Next button clicked")

    def on_prev_clicked(self):
        sure, ayet = self.parse_input(self.search_input.text())
        if sure and ayet:
            if ayet > 1:
                ayet -= 1
            else:
                sure -= 1
                if sure < 1:
                    sure = 114
                ayet = self.get_verse_count(sure)
            self.search_input.setText(f"{sure}/{ayet}")
            self.search()
        print("Prev button clicked")

    def root_search(self):
        kok = self.root_input.currentText().strip()
        if not kok:
            self.root_results.setText("Kök girin.")
            return
        kok = self.normalize_arabic(kok)  # Hareke çıkar
        if self.kok_df is None:
            self.root_results.setText("Kök verisi yüklenemedi.")
            return
        kok_row = self.kok_df[self.kok_df['kelime'] == kok]
        if kok_row.empty:
            self.root_results.setText(f"Kök '{kok}' bulunamadı.")
            return
        frekans = kok_row['frekans'].values[0]
        kok_ebced = sum(self.ebced.get(harf, 0) for harf in kok)
        # Morfoloji bilgisi
        morph_info = ""
        if self.morph_df is not None:
            morph_row = self.morph_df[self.morph_df['kelime'] == kok]
            if not morph_row.empty:
                tur = morph_row['tur'].values[0]
                aciklama = morph_row['aciklama'].values[0]
                morph_info = f", Tür: {tur}, Açıklama: {aciklama}"
        text = f"<h3>Kök '{kok}' ebced: {kok_ebced}, frekans: {frekans}{morph_info}</h3>"
        # Kök içeren ayetleri bul
        arapca_matches = []
        found = pd.DataFrame()  # default empty
        if self.arapca_df is not None:
            found = self.arapca_df[self.arapca_df['metin'].apply(self.normalize_arabic).str.contains(re.escape(kok), regex=True, na=False)]
            for _, arow in found.iterrows():
                match = self.meal_df[(self.meal_df['sure'] == arow['sure']) & (self.meal_df['ayet'] == arow['ayet'])]
                if not match.empty:
                    arapca_matches.append({'meal': match.iloc[0], 'arapca': arow['metin']})
        results = pd.DataFrame(arapca_matches)
        text += f"<p>Bulunan satır sayısı: {len(found)}</p><p>{len(results)} ayet bulundu.</p>"
        for _, row in results.iterrows():
            arapca_text = row['arapca']
            normalized = self.normalize_arabic(arapca_text)
            ayet_ebced = sum(self.ebced.get(harf, 0) for harf in normalized)
            text += f"<h4><a href='{row['meal']['sure']}/{row['meal']['ayet']}'>{row['meal']['sure']}:{row['meal']['ayet']}</a></h4>"
            text += f"<p><b>Arapça:</b> <span style='font-size: 16px; font-family: Arial Unicode MS;'>{arapca_text}</span></p>"
            text += f"<p><b>Türkçe:</b> {row['meal']['metin']}</p>"
            text += f"<p><b>Ayet Ebced:</b> {ayet_ebced}</p>"
            text += "<hr>"
        self.root_results.setHtml(text)

    def on_root_link_clicked(self, url):
        if isinstance(url, str):
            sure_ayet = url
        else:
            sure_ayet = url.toString()
        sure, ayet = sure_ayet.split('/', 1)
        sure = int(sure)
        ayet = int(ayet)
        # Ayrı pencere aç, ayeti göster
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Ayet {sure}:{ayet}")
        layout = QVBoxLayout()
        # İleri geri butonları
        button_layout = QHBoxLayout()
        geri_btn = QPushButton("Geri")
        ileri_btn = QPushButton("İleri")
        button_layout.addWidget(geri_btn)
        button_layout.addWidget(ileri_btn)
        # Favoriye Ekle butonu
        fav_btn = QPushButton("⭐ Favoriye Ekle")
        fav_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFD700;
                color: black;
                font-weight: bold;
                font-size: 12px;
                padding: 8px 12px;
                border: 2px solid #FFA500;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #FFA500;
            }
            QPushButton:pressed {
                background-color: #FF8C00;
            }
        """)
        fav_btn.setFixedSize(150, 35)
        fav_btn.clicked.connect(lambda checked, s=sure, a=ayet: self.add_favorite(s, a))
        button_layout.addWidget(fav_btn)
        layout.addLayout(button_layout)
        # İçerik alanı
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_widget.setLayout(content_layout)
        layout.addWidget(content_widget)
        dialog.setLayout(layout)
        dialog.resize(600, 400)

        def update_ayet():
            # Önceki içeriği temizle
            for i in reversed(range(content_layout.count())):
                widget = content_layout.itemAt(i).widget()
                if widget:
                    widget.setParent(None)
            # Yeni ayet göster
            arapca_raw = self.get_arabic_text(sure, ayet)
            arapca = ''
            transcript = self.get_transcript_text(sure, ayet)
            if arapca_raw:
                reshaped = arabic_reshaper.reshape(arapca_raw)
                arapca = reshaped
            meal_row = self.favorites_meal_df[(self.favorites_meal_df['sure'] == str(sure)) & (self.favorites_meal_df['ayet'] == str(ayet))]
            if not meal_row.empty:
                row = meal_row.iloc[0]
                # Başlık
                title_label = QLabel(f"<h2>{sure}:{ayet}</h2>")
                content_layout.addWidget(title_label)
                # Türkçe kutucuk
                turk_group = QGroupBox("Türkçe Meâl")
                turk_layout = QVBoxLayout()
                turk_text = QTextEdit()
                turk_text.setReadOnly(True)
                turk_text.setFont(self.font_turkish)
                turk_text.setHtml(self.highlight_text(f"[{row['sira']}] {row['sure']}/{row['ayet']}\n{row['metin']}", ''))
                turk_text.setTextInteractionFlags(Qt.TextSelectableByMouse)
                turk_layout.addWidget(turk_text)
                turk_group.setLayout(turk_layout)
                content_layout.addWidget(turk_group)
                # Arapça kutucuk
                if arapca:
                    arap_group = QGroupBox("Arapça Metin")
                    arap_layout = QVBoxLayout()
                    arap_text = QTextEdit()
                    arap_text.setReadOnly(True)
                    arap_text.setFont(self.font_arabic)
                    arap_text.setHtml(self.highlight_text(arapca, ''))
                    arap_text.setAlignment(Qt.AlignRight)
                    arap_text.setLayoutDirection(Qt.RightToLeft)
                    arap_text.setTextInteractionFlags(Qt.TextSelectableByMouse)
                    # Ayet ebced hesapla
                    normalized = self.normalize_arabic(arapca_raw)
                    ayet_ebced = sum(self.ebced.get(harf, 0) for harf in normalized)
                    ebced_label = QLabel(f"Ayet Ebced: {ayet_ebced}")
                    arap_layout.addWidget(ebced_label)
                    arap_layout.addWidget(arap_text)
                    arap_group.setLayout(arap_layout)
                    content_layout.addWidget(arap_group)
                # Transkript kutucuk
                if transcript:
                    trans_group = QGroupBox("Transkript (Abay Yazılışı)")
                    trans_layout = QVBoxLayout()
                    trans_text = QTextEdit()
                    trans_text.setReadOnly(True)
                    trans_text.setFont(self.font_turkish)
                    trans_text.setHtml(self.highlight_text(transcript, ''))
                    trans_text.setTextInteractionFlags(Qt.TextSelectableByMouse)
                    trans_layout.addWidget(trans_text)
                    trans_group.setLayout(trans_layout)
                    content_layout.addWidget(trans_group)

        update_ayet()

        def on_geri():
            nonlocal ayet, sure
            if ayet > 1:
                ayet -= 1
            else:
                sure -= 1
                if sure < 1:
                    sure = 114
                ayet = self.get_verse_count(sure)
            update_ayet()

        def on_ileri():
            nonlocal ayet, sure
            max_ayet = self.get_verse_count(sure)
            if ayet < max_ayet:
                ayet += 1
            else:
                sure += 1
                if sure > 114:
                    sure = 1
                ayet = 1
            update_ayet()

        geri_btn.clicked.connect(on_geri)
        ileri_btn.clicked.connect(on_ileri)

        dialog.exec_()

    def letter_analysis(self):
        ref = self.letter_input.text().strip()
        if not ref or '/' not in ref:
            self.letter_results.setText("Sure/Ayet girin, örn: 1/1")
            return
        sure, ayet = ref.split('/', 1)
        arapca = self.get_arabic_text(sure, ayet)
        if not arapca:
            self.letter_results.setText("Arapça metin bulunamadı.")
            return
        counts = {harf: arapca.count(harf) for harf in self.ARAP_HARFLER if arapca.count(harf) > 0}
        ebced_total = sum(self.ebced.get(harf, 0) * count for harf, count in counts.items())
        text = ""
        for harf, count in counts.items():
            text += f"{harf}: {count}\n"
        text += f"\nEbced Toplamı: {ebced_total}"
        self.letter_results.setText(text)

    def compare_meals(self):
        input_text = self.comp_input.text().strip()
        sure, ayet = self.parse_input(input_text)
        if sure is None or ayet is None:
            self.left_text.setText("Geçersiz giriş. Örnek: 6236, 114/4, Nas 6")
            self.right_text.setText("")
            return
        selected_meals = []
        for i in range(self.meal_list.count()):
            item = self.meal_list.item(i)
            if item.checkState() == Qt.Checked:
                selected_meals.append(item.text())
        if len(selected_meals) == 0:
            self.left_text.setText("En az bir meal seçin.")
            self.right_text.setText("")
            return
        left_meal = selected_meals[0]
        right_meal = selected_meals[1] if len(selected_meals) > 1 else None
        left_text = f"Süre {sure}, Ayet {ayet} - {left_meal}\n\n"
        right_text = f"Süre {sure}, Ayet {ayet} - {right_meal}\n\n" if right_meal else ""
        try:
            df_left = pd.read_csv(os.path.join('tum_mealler', left_meal), dtype=str, encoding='utf-8-sig')
            match_left = df_left[(df_left['sure'] == str(sure)) & (df_left['ayet'] == str(ayet))]
            if not match_left.empty:
                left_text += match_left.iloc[0]['metin']
            else:
                left_text += "Bulunamadı"
        except Exception as e:
            left_text += f"Hata: {str(e)}"
        if right_meal:
            try:
                df_right = pd.read_csv(os.path.join('tum_mealler', right_meal), dtype=str, encoding='utf-8-sig')
                match_right = df_right[(df_right['sure'] == str(sure)) & (df_right['ayet'] == str(ayet))]
                if not match_right.empty:
                    right_text += match_right.iloc[0]['metin']
                else:
                    right_text += "Bulunamadı"
            except Exception as e:
                right_text += f"Hata: {str(e)}"
        if len(selected_meals) > 2:
            right_text += f"\n\nNot: İlk iki meal karşılaştırıldı. Toplam {len(selected_meals)} meal seçili."
        self.left_text.setText(left_text)
        self.right_text.setText(right_text)

    def prev_verse(self):
        input_text = self.comp_input.text().strip()
        sure, ayet = self.parse_input(input_text)
        if sure is None or ayet is None:
            return
        if ayet > 1:
            ayet -= 1
        elif sure > 1:
            sure -= 1
            ayet = self.get_verse_count(sure)
        self.comp_input.setText(f"{sure}/{ayet}")
        self.compare_meals()

    def next_verse(self):
        input_text = self.comp_input.text().strip()
        sure, ayet = self.parse_input(input_text)
        if sure is None or ayet is None:
            return
        max_ayet = self.get_verse_count(sure)
        if ayet < max_ayet:
            ayet += 1
        elif sure < 114:
            sure += 1
            ayet = 1
        self.comp_input.setText(f"{sure}/{ayet}")
        self.compare_meals()

    def get_sure_name(self, sure_num):
        for name, num in self.sure_names.items():
            if num == sure_num:
                return name.capitalize()
        return "Bilinmiyor"

    def update_ayet_spin(self):
        sure = self.info_sure_combo.currentIndex() + 1
        max_ayet = self.get_verse_count(sure)
        self.info_ayet_spin.setMaximum(max_ayet)
        self.show_verse_info()

    def show_verse_info(self):
        sure = self.info_sure_combo.currentIndex() + 1
        ayet = self.info_ayet_spin.value()
        info = f"Süre: {sure} - {self.get_sure_name(sure)}\nAyet: {ayet}\n\n"
        if self.mekki_df is not None:
            match = self.mekki_df[self.mekki_df['sure'] == str(sure)]
            if not match.empty:
                info += f"Mekki/Medeni: {match.iloc[0]['tur']}\n"
        # İniş sırası için basit bir dict, gerçek veriye göre güncelle
        inis_sirasi = {1: 5, 2: 87, 3: 89, 4: 92, 5: 112, 6: 55, 7: 39, 8: 88, 9: 113, 10: 51, 11: 52, 12: 53, 13: 96, 14: 72, 15: 54, 16: 70, 17: 50, 18: 69, 19: 44, 20: 45, 21: 73, 22: 103, 23: 74, 24: 102, 25: 42, 26: 47, 27: 48, 28: 49, 29: 85, 30: 84, 31: 57, 32: 75, 33: 90, 34: 58, 35: 43, 36: 41, 37: 56, 38: 38, 39: 59, 40: 60, 41: 61, 42: 62, 43: 63, 44: 64, 45: 65, 46: 66, 47: 95, 48: 111, 49: 106, 50: 34, 51: 67, 52: 76, 53: 23, 54: 37, 55: 97, 56: 46, 57: 94, 58: 105, 59: 101, 60: 91, 61: 109, 62: 110, 63: 104, 64: 108, 65: 99, 66: 107, 67: 77, 68: 2, 69: 78, 70: 79, 71: 71, 72: 40, 73: 3, 74: 4, 75: 31, 76: 98, 77: 33, 78: 80, 79: 81, 80: 24, 81: 7, 82: 82, 83: 86, 84: 83, 85: 27, 86: 36, 87: 8, 88: 68, 89: 10, 90: 35, 91: 26, 92: 9, 93: 11, 94: 12, 95: 28, 96: 1, 97: 25, 98: 100, 99: 93, 100: 14, 101: 30, 102: 16, 103: 13, 104: 32, 105: 19, 106: 29, 107: 17, 108: 15, 109: 18, 110: 20, 111: 21, 112: 22, 113: 6, 114: 114}
        if sure in inis_sirasi:
            info += f"İniş Sırası: {inis_sirasi[sure]}\n"
        # Açıklamalar için basit dict, gerçek veriye göre güncelle
        aciklamalar = {1: "Kur'an'ın girişi, dualar.", 2: "En uzun sure, çeşitli konular.", 3: "İman esasları, aile hukuku."}  # Kısa örnek
        if sure in aciklamalar:
            info += f"Açıklama: {aciklamalar[sure]}\n"
        # Not yükle
        notes_file = 'notes.json'
        if os.path.exists(notes_file):
            with open(notes_file, 'r', encoding='utf-8') as f:
                notes = json.load(f)
            key = f"{sure}-{ayet}"
            if key in notes:
                note_data = notes[key]
                if isinstance(note_data, dict):
                    info += f"\nNot ({note_data.get('tag', 'Genel')}): {note_data['note']}"
                else:
                    # Eski format için
                    info += f"\nNot: {note_data}"
        self.info_text.setText(info)

    def save_note(self):
        sure = self.info_sure_combo.currentIndex() + 1
        ayet = self.info_ayet_spin.value()
        note = self.note_text.toPlainText().strip()
        tag = self.note_tag.currentText()
        if not note:
            return
        notes_file = 'notes.json'
        if os.path.exists(notes_file):
            with open(notes_file, 'r', encoding='utf-8') as f:
                notes = json.load(f)
        else:
            notes = {}
        key = f"{sure}-{ayet}"
        notes[key] = {"note": note, "tag": tag}
        with open(notes_file, 'w', encoding='utf-8') as f:
            json.dump(notes, f, ensure_ascii=False, indent=4)
        self.note_text.clear()
        self.show_verse_info()

    def edit_note(self):
        sure = self.info_sure_combo.currentIndex() + 1
        ayet = self.info_ayet_spin.value()
        notes_file = 'notes.json'
        if os.path.exists(notes_file):
            with open(notes_file, 'r', encoding='utf-8') as f:
                notes = json.load(f)
            key = f"{sure}-{ayet}"
            if key in notes:
                note_data = notes[key]
                if isinstance(note_data, dict):
                    self.note_text.setPlainText(note_data['note'])
                    self.note_tag.setCurrentText(note_data.get('tag', 'Genel'))
                else:
                    self.note_text.setPlainText(note_data)
                    self.note_tag.setCurrentText('Genel')

    def delete_note(self):
        sure = self.info_sure_combo.currentIndex() + 1
        ayet = self.info_ayet_spin.value()
        notes_file = 'notes.json'
        if os.path.exists(notes_file):
            with open(notes_file, 'r', encoding='utf-8') as f:
                notes = json.load(f)
            key = f"{sure}-{ayet}"
            if key in notes:
                del notes[key]
                with open(notes_file, 'w', encoding='utf-8') as f:
                    json.dump(notes, f, ensure_ascii=False, indent=4)
        self.note_text.clear()
        self.show_verse_info()  # Güncelle

    def create_audio_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        hlayout = QHBoxLayout()
        hlayout.addWidget(QLabel("Sure:"))
        self.audio_sure = QSpinBox()
        self.audio_sure.setRange(1, 114)
        self.audio_sure.valueChanged.connect(self.update_ayet_range)
        hlayout.addWidget(self.audio_sure)
        hlayout.addWidget(QLabel("Ayet:"))
        self.audio_ayet = QSpinBox()
        self.audio_ayet.setRange(1, 7)  # default for sure 1
        hlayout.addWidget(self.audio_ayet)
        self.play_button = QPushButton("Oynat")
        self.play_button.clicked.connect(self.play_audio)
        hlayout.addWidget(self.play_button)
        self.stop_button = QPushButton("Durdur")
        self.stop_button.clicked.connect(self.stop_audio)
        hlayout.addWidget(self.stop_button)
        layout.addLayout(hlayout)
        self.audio_status = QLabel("Hazır")
        layout.addWidget(self.audio_status)
        widget.setLayout(layout)
        return widget

    def update_ayet_range(self):
        sure = self.audio_sure.value()
        max_ayet = self.get_verse_count(sure)
        self.audio_ayet.setMaximum(max_ayet)
        if self.audio_ayet.value() > max_ayet:
            self.audio_ayet.setValue(max_ayet)

    def play_audio(self):
        sure = self.audio_sure.value()
        ayet = self.audio_ayet.value()
        file_name = f"{sure:03d}{ayet:03d}.mp3"
        folder = 'kuran (arabic) sesli'
        file_path = os.path.join(folder, file_name)
        if os.path.exists(file_path):
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(file_path)))
            self.player.play()
            self.audio_status.setText(f"Oynatılıyor: {sure}:{ayet}")
        else:
            self.audio_status.setText("Ses dosyası bulunamadı")

    def stop_audio(self):
        self.player.stop()
        self.audio_status.setText("Durduruldu")

    def play_verse_audio(self, sure, ayet):
        file_name = f"{sure:03d}{ayet:03d}.mp3"
        folder = 'kuran (arabic) sesli'
        file_path = os.path.join(folder, file_name)
        if os.path.exists(file_path):
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(file_path)))
            self.player.play()
            self.audio_status.setText(f"Oynatılıyor: {sure}:{ayet}")
        else:
            self.audio_status.setText("Ses dosyası bulunamadı")



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QuranSearchApp(app)
    window.show()
    window.raise_()
    window.activateWindow()
    sys.exit(app.exec_())
