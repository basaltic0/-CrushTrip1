# CrushTrip – 日本觀光數網站

CrushTrip 是一個專為熱愛日本旅遊的使用者打造的智慧行程規劃平台。無論是初次造訪或資深旅人，只需幾個步驟，即可輕鬆規劃專屬行程，包含景點推薦與購物車功能。

## 🔧 技術架構
- 前端：HTML / CSS / JavaScript（由組員負責）
- 後端：Python / Django / SQLite
- 資料爬蟲：ChromeDriver + BeautifulSoup
- 部署：Heroku / AWS S3

## 🧑‍💻 我的貢獻
- 使用爬蟲技術擷取日本觀光資料並寫入資料庫
- 將靜態頁面改為動態呈現（購物車、景點推薦模組）
- 負責錯誤排除與功能微調，提升使用者體驗與系統穩定性

## 🚀 如何啟動專案
```bash
git clone https://github.com/basaltic0/-CrushTrip.git
cd CrushTrip
pip install -r requirements.txt
python manage.py runserver
