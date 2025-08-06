from django.shortcuts import render, redirect
import datetime
from django.core.mail import send_mail
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.views.decorators.cache import cache_page
from myapp.models import CustomUser
from myapp.forms import CustomUserCreationForm
from django.contrib import messages

from django.contrib.auth import authenticate, login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.messages import get_messages
from django.views.decorators.http import require_GET
from .forms import ForgotUsernameForm
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json, os
from openai import OpenAI
import traceback
from django.core.mail import EmailMessage
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase import pdfmetrics
import io


from django.http import JsonResponse
from selenium import webdriver
from urllib.parse import urljoin
from django.http import JsonResponse
from bs4 import BeautifulSoup
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from django.db import transaction
from myapp.models import crawlers_osusume
from myapp.models import crawlers_main
from myapp.models import CartItem
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
import re
from collections import defaultdict
from django.shortcuts import get_object_or_404

@login_required
def index(request):
    return render(request, 'index.html')

@login_required
def member_view(request):
    return render(request, 'member.html')

# 購物車
@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user).select_related('spot')

    spots = []
    for item in cart_items:
        spot = item.spot
        spots.append({
            'id': spot.id,
            'heading': spot.heading,
            'img': spot.img[0] if spot.img else '',
            'shortDesc': spot.content[:100],  # or其他摘要字段
            'fullUrl': '',  # 若有詳細頁可放連結
        })

    context = {
        'cart_spots': spots,
    }
    return render(request, 'cart.html', context)

    # return render(request, 'cart.html')

# 購物車資料處理
def cart_api(request):
    try:
        cart_items = CartItem.objects.filter(user=request.user).select_related('spot')
        print(request.user) 
        spots = [{
            'id': item.spot.id,
            'name': item.spot.heading,
            'thumbnail': item.spot.img or '',
            'parent_title': item.spot.parent_title,
        } for item in cart_items]
        return JsonResponse({'shoppingCart': spots})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# 購物車刪除資料
@login_required
@require_POST
def cart_remove_view(request):
    try:
        data = json.loads(request.body)
        spot_id = data.get('id')
        CartItem.objects.filter(user=request.user, spot_id=spot_id).delete()
        return JsonResponse({'success': True, 'message': '已移除購物車項目'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'刪除失敗: {str(e)}'})

# 客製化行程加入購物車
@login_required
@require_POST
def cart_add_view(request):
    try:
        data = json.loads(request.body)
        spot_id = data.get('id')
        print(spot_id)
        spot = crawlers_main.objects.get(pk=spot_id)
        cart_item, created = CartItem.objects.get_or_create(user=request.user, spot=spot)
        if created:
            return JsonResponse({'success': True, 'message': '已加入購物車'})
        else:
            return JsonResponse({'success': False, 'message': '已加入過購物車'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'錯誤: {str(e)}'})
    
# 主頁加入購物車
@login_required
@require_POST
def index_add_view(request):
    try:
        data = json.loads(request.body)
        spot_id = data.get('id')
        print(spot_id)
        spot = crawlers_main.objects.get(pk=spot_id)
        cart_item, created = CartItem.objects.get_or_create(user=request.user, spot=spot)
        if created:
            return JsonResponse({'success': True, 'message': '已加入購物車'})
        else:
            return JsonResponse({'success': False, 'message': '已加入過購物車'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'錯誤: {str(e)}'})

# 客製化行程資料處理
@login_required
def spots_view(request,parent_title=None):
    city_map = {
        'sapporo': '札幌與周邊地區',
        'hakodate': '函館與北海道南部',
        'tokyo': '東京',
        'yokohama': '橫濱',
        'saitama': '埼玉新都心',
        'chiba': '千葉',
        'nagoya': '名古屋市中心',
        'fuji': '富士山（山梨）',
        'osaka': '大阪灣地區',
        'kyoto': '京都車站周邊區域及京都南部',
        'nara': '奈良市',
        'kobe': '神戶',
        'fukuoka': '福岡市',
        'kumamoto': '熊本市',
        'kagoshima': '鹿兒島市',
        'nagasaki': '長崎市',
        'miyazaki': '宮崎市',
        'naha': '那霸',
        'ishigaki': '石垣島',
        'miyako': '宮古島',
    }

    # 將英文代號轉為中文名稱，若找不到，則用原樣（可視需求調整）
    city_name = city_map.get(parent_title, parent_title)
    data_list = crawlers_main.objects.filter(parent_title=city_name)
    
    # 將資料和圖片做處理
    spots_data = []
    for item in data_list:
        urls = re.findall(r'https?://\S+', item.content)
        image_urls = [re.sub(r'/upload/[^/]+/', '/upload/', url) for url in urls]
        content_without_urls = item.content
        for url in urls:
            content_without_urls = content_without_urls.replace(url, '')
        text_cleaned = content_without_urls.strip()

        print("item.id:", item.id)
        spots_data.append({
            "id": item.id,                              
            'parent_title': item.parent_title,           #大標題
            'heading': item.heading,                      #內文標題
            'img': image_urls[0] if image_urls else "",   # 取第一張圖片
            'shortDesc': text_cleaned,                     # 簡短敘述
            'fullUrl': item.img,                            # 封面
        })
    grouped_data = defaultdict(list)
    for spot in spots_data:
        grouped_data[spot['parent_title']].append(spot)

    print(f"{city_name} 查詢到 {data_list.count()} 筆資料")
    # {{ grouped_data|json_script:"grouped-data" }}
    # 整理資料
    context = {
        'parent_title': city_name,
        'data_list': data_list,
        'spots_data': spots_data,     
        'grouped_data': grouped_data.items()
    }
    return render(request, 'spots.html',context,)

# 客製化行程子頁內容
@login_required
def spot_detail_view(request,parent_title=None):
    spot = crawlers_main.objects.filter(parent_title=parent_title)

    # 處理圖片與文字（可依照你的資料型態）
    spots_data = []
    for sp in spot:
        urls = re.findall(r'https?://\S+', sp.content)
        image_urls = [re.sub(r'/upload/[^/]+/', '/upload/', url) for url in urls]
        content_without_urls = sp.content 
        for url in urls:
            content_without_urls = content_without_urls.replace(url, '')
        text_cleaned = content_without_urls.strip()

        spots_data.append({
            'spot': sp,
            'image_urls': image_urls,
            'text_cleaned': text_cleaned,
        })

    context = {
        # 'id': spot.id,
        'spots_data':spots_data,
        'parent_title': parent_title,
    }
    print(context)
    return render(request, 'spot_detail.html',context)

#註冊
def register_view(request):
    step = 1  # 預設顯示第一步
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # 等待驗證
            user.save()

            # 發送驗證信
            current_site = get_current_site(request)
            subject = '請啟用您的帳號'
            message = render_to_string('activation_email.txt', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
            messages.success(request, '註冊成功，請至信箱點擊驗證連結完成啟用')
            return render(request, 'login.html')
        else:
            # 根據錯誤的欄位決定回到哪一步
            if any(field in form.errors for field in ['email', 'username', 'first_name', 'last_name', 'gender','avatar']):
                step = 1
            else:
                step = 2
    else:
        form = CustomUserCreationForm()

    return render(request, 'register.html', {
        'form': form,
        'step': step
    })

#驗證帳號
def activate(request, uid, token):
    try:
        uid = force_str(urlsafe_base64_decode(uid))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, '帳號已成功啟用，請登入')
        return redirect('login')
    else:
        messages.error(request, '驗證連結無效')
        return redirect('register')

# 登入
def login_view(request):
    # if request.user.is_authenticated:
    #    return redirect('index')  # 已登入則導回首頁

    username = ''  #  預設空字串，避免未定義錯誤
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember = request.POST.get('remember')  # 取得「記住我」欄位，會是 "on" 或 None

        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:  
                login(request, user)
                # 設定 session 過期時間
                if not remember:
                    request.session.set_expiry(0)  # 瀏覽器關閉即登出
                else:
                    request.session.set_expiry(1209600)  # 14 天（秒）

                
                return redirect('index')  # 登入成功導向
            else:
                messages.error(request, '帳號尚未啟用，請至信箱完成驗證。')
        else:
            messages.error(request, '帳號或密碼錯誤')
    return render(request, 'login.html',{'username': username})


#忘記帳號
User = get_user_model()
def forgot_username_view(request):
    success = False
    error = None

    if request.method == 'POST':
        form = ForgotUsernameForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            users = User.objects.filter(email=email)

            if users.exists():
                usernames = ', '.join([user.username for user in users])
                send_mail(
                    'CrushTrip 帳號查詢通知',
                    f'您註冊的帳號為：{usernames}',
                    'no-reply@crushtrip.com',
                    [email],
                    fail_silently=False,
                )
                success = True
            else:
                error = '查無此信箱對應的帳號，請確認是否輸入正確。'
    else:
        form = ForgotUsernameForm()

    return render(request, 'forgot_username.html', {
        'form': form,
        'success': success,
        'error': error,
    })
#傳送首頁訊息
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt  # 或搭配 CSRF token 做 AJAX，較安全
@require_POST
def send_contact_message(request):
    name = request.POST.get('name')
    email = request.POST.get('email')
    subject = request.POST.get('subject')
    message = request.POST.get('message')

    if not all([name, email, subject, message]):
        return JsonResponse({'success': False, 'error': '所有欄位皆為必填'})

    full_message = f"""
    來自：{name}
    信箱：{email}
    主旨：{subject}
    
    訊息內容：
    {message}
    """

    try:
        send_mail(
            subject=f"[CrushTrip] {subject}",
            message=full_message,
            from_email='laizhaohua88@gmail.com',
            recipient_list=['laizhaohua88@gmail.com'],
        )
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

from .forms import CustomUserUpdateForm
from django.contrib.auth import update_session_auth_hash

# 更新會員資料

@login_required
def update_profile(request):
    user = request.user
    if request.method == "POST":
        form = CustomUserUpdateForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)          
@login_required
def update_profile(request):
    user = request.user
    if request.method == "POST":
        form = CustomUserUpdateForm(request.POST, request.FILES)
        if form.is_valid():
            user.username = form.cleaned_data['username']
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.gender = form.cleaned_data['gender']
            user.travel_partner = form.cleaned_data['travel_partner']
            user.preferred_age_range = form.cleaned_data['preferred_age_range']
            user.preferred_travel=form.cleaned_data['preferred_travel']  
            if form.cleaned_data.get('avatar'):
                user.avatar = form.cleaned_data['avatar']

            if request.POST.get("remove_avatar") == "true":
                if user.avatar:
                    user.avatar.delete(save=False)  # 刪除檔案
                user.avatar = None
            
            user.save()        
            messages.success(request, "會員資料已成功更新！")
            return redirect("update_profile")
    else:        
        form = CustomUserUpdateForm(initial={
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "gender": user.gender,
            "travel_partner": user.travel_partner,
            "preferred_age_range": user.preferred_age_range,
            "preferred_travel": user.preferred_travel,
        })

    return render(request,"update_profile.html",
        {"form": form, "avatar": user.avatar.url if user.avatar else None},
    )


#登出
@require_GET
def custom_logout(request):
    # ✅ 清空所有舊的訊息
    storage = get_messages(request)
    for _ in storage:
        pass  # 迴圈消耗 message queue

    auth_logout(request)
    messages.success(request, '您已成功登出，歡迎下次再次光臨')
    return render(request, 'login.html')


#API處理邏輯
@csrf_exempt
def generate_itinerary(request):
    if request.method != "POST":
        return JsonResponse({"error": "只支援 POST 請求"}, status=405)
    # 1. 先防止 body 不是 JSON
    try:
        data = json.loads(request.body)
    except Exception as e:
        return JsonResponse({"error": "Invalid JSON: {}".format(e)}, status=400)
    # 2. 檢查 prompt
    prompt = data.get("prompt")
    if not prompt:
        return JsonResponse({"error": "Missing prompt"}, status=400)
    print("[DEBUG] prompt 長度：", len(prompt))
    print("[DEBUG] prompt 前 200 字：", prompt[:200])

    # 3. 檢查 api_key
    api_key = settings.OPENAI_API_KEY
    if not api_key:
        return JsonResponse({"error": "OPENAI_API_KEY 環境變數沒設定！"}, status=500)
    # 4. OpenAI 主業務
    try:
        client = OpenAI(api_key=api_key)
        completion = client.chat.completions.create(
            model="gpt-4",
            messages = [
                {"role": "system", "content": "你是旅遊行程規劃專家。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=3000,
            temperature=0.7
        )
        reply = completion.choices[0].message.content
        return JsonResponse({
            "itinerary": reply,
            "bookingLinksHtml": "<a href='#'>立即訂房</a>"
        })
    except Exception as e:
        traceback.print_exc()   # 將完整錯誤堆疊印到終端機
        return JsonResponse({"error": f"OpenAI 調用失敗: {str(e)}"}, status=500)


# 中文字型註冊
pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
max_width = 500  # 最寬文字區域
# pdf文字區塊
def wrap_text(text, font_name, font_size, max_width):
    lines = []
    line = ''
    for char in text:
        test_line = line + char
        if pdfmetrics.stringWidth(test_line, font_name, font_size) > max_width:
            lines.append(line)
            line = char
        else:
            line = test_line
    lines.append(line)
    return lines


# 行程信件寄送
@csrf_exempt  # 可避免 CSRF 驗證失敗造成錯誤，開發時用，部署時請小心
def send_itinerary(request):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    p.setFont('STSong-Light', 12)
    
    if request.method != 'POST':
        return JsonResponse({'error': '只接受POST請求'}, status=405)
    try:
        data = json.loads(request.body)
        email = data.get('email')
        itinerary = data.get('itinerary')
        if not email or not itinerary:
            return JsonResponse({'error': 'email或行程內容不可為空'}, status=400)

        # 產生簡單 PDF
        p.drawString(100, 800, "您的旅遊行程：")
        start_x, start_y = 50, 780
        line_height = 15
        min_y = 50  # 頁面底部邊界
        text_obj = p.beginText(start_x, start_y)

        for line in itinerary.split('\n'):
            wrapped_lines = wrap_text(line, 'STSong-Light', 12, 500)  # 設定最大寬度

            for subline in wrapped_lines:
                if text_obj.getY() < min_y:
                    p.drawText(text_obj)
                    p.showPage()
                    p.setFont('STSong-Light', 12)  # 換頁後需重新設定字型
                    text_obj = p.beginText(start_x, start_y)
                text_obj.textLine(subline)

        p.drawText(text_obj)
        p.save()
        buffer.seek(0)

        # 寄送郵件
        email_msg = EmailMessage(
            subject='您的旅遊行程表',
            body='請參閱附件中的旅遊行程表。祝旅途愉快！',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
        )
        email_msg.attach('itinerary.pdf', buffer.read(), 'application/pdf')
        email_msg.send()

        return JsonResponse({'success': True})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# 無頭模式
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# 必看景點
def cr(request):
    TitleList = []
    LinkList = []
    all_sections = []
    ImageList = []
    driver = webdriver.Chrome(options=options)

    for i in range(1):
        url = "https://www.japan.travel/tw/destinations"
        driver.get(url)
        driver.implicitly_wait(5)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        titles = soup.select("span.mod-image-gallery__text")
        links = soup.select("a.mod-image-gallery__item-inner")
        images = soup.select("div.mod-image-gallery__image img")

        # 塞選重複的圖片
        for img in images:
                img_url = (img.get("data-src") or img.get("src"))
                if img_url and "w_510,h_347" in img_url:
                    continue
                ImageList.append(img_url)
        try:
            for title,link in zip(titles,links):
                TitleList.append(title.text)
                Oldlink = link.get("href")
                NewLink = urljoin(url, Oldlink)
                LinkList.append(NewLink)

                # 子分頁
                driver.get(NewLink)
                driver.implicitly_wait(5)
                element  = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div#anchor_1 div.mod-wysiwyg__body")))
                soup = BeautifulSoup(driver.page_source, "html.parser")
                content_container = soup.select_one('div#anchor_1 div.mod-wysiwyg__body')
                time.sleep(1)

                sections = []
                current_section = None

                # 子分頁內容
                # 爬標題
                for tag in content_container.children:
                    if tag.name == "div" and any(cls in tag.get('class', []) for cls in [
                        'mod-wysiwyg__lead-wrapper',
                        'mod-wysiwyg__howto-get-there-header',
                        'mod-wysiwyg__subheading-wrapper'
                    ]):
                        if current_section:
                            sections.append(current_section)

                        # 將標題存下 並為內文打洞方便後續存取
                        heading_tag = tag.find(['h2', 'h3'])
                        heading_text = heading_tag.get_text(strip=True) if heading_tag else ''
                        current_section = {
                            'heading': heading_text,
                            'content': '',
                            'img': " ",
                        }

                    # 爬內文和圖片
                    
                    elif tag.name == 'div' and 'mod-wysiwyg__text-wrapper' in tag.get('class', []):
                        # 遇到段落，加入當前區塊
                        if current_section:
                            p_tag = tag.find('p', class_='mod-wysiwyg__text')
                            img_tags = tag.find_all('img')
                            if p_tag:
                                text = p_tag.get_text(strip=True)
                                if text:
                                    current_section['content'] += text + '\n'
                                    # current_section['img'] = img_url

                                # 圖片處理
                                for img_tag in img_tags:
                                    img_url = img_tag.get("data-src") or img_tag.get("src")
                                    if "http" not in img_url:
                                        continue
                                    if img_url:
                                        # current_section['content'] += {img_url} 
                                        current_section['content'] += f"{img_url}\n"
                # 最後一個區塊加入列表
                if current_section:
                    sections.append(current_section)

                # 將title的文字加入sections
                for section in sections:
                    section['parent_title'] = title.text

                # 將title的文字加入ImageList形成新的title_img_dict
                title_img_dict = {}
                for title, img in zip(TitleList, ImageList):
                    title_img_dict[title] = img
                
                # 將上面處理好的title_img_dict加到sections
                for section in sections:
                    parent_title = section.get('parent_title', '')
                    section['img'] = title_img_dict.get(parent_title, '')
                    
                all_sections.extend(sections)       

            # 先清空想要覆寫的資料 
            # crawlers_osusume.objects.all().delete()
            crawlers_main.objects.filter(area='osusume').delete()

            with transaction.atomic():
                # 依序將所有 sections 寫入資料庫
                for section in all_sections:
                    # crawlers_osusume.objects.create(
                #         parent_title=section.get('parent_title', ''),
                #         heading=section.get('heading', ''),
                #         content=section.get('content', ''),
                #         image_url=section.get('img', ''),  # 如果你有處理對應的圖片
                #     )
                    crawlers_main.objects.create(
                        parent_title=section.get('parent_title', ''),
                        heading=section.get('heading', ''),
                        content=section.get('content', ''),
                        area='osusume',  # 如果你有處理對應的圖片
                        img=section.get('img', ''),
                    )

        except Exception as e:
            return HttpResponse(f"存入資料庫錯誤: {e}")
        finally:
            driver.quit()

    return JsonResponse({
        "sections": all_sections,
        "img": [{ "title": t, "image_url": i} for t,i in zip(TitleList, ImageList)],
    })

# 主要城市
def cr3(request):
    driver = webdriver.Chrome(options=options)
    all_sections =[]
    
    try:
        base_url = "https://www.japan.travel/tw/destinations/"
        All_url = {
            "北海道": [
                "hokkaido/hokkaido/sapporo-and-around/",
                "hokkaido/hokkaido/hakodate-and-hokkaido-south/",
            ],
            "關東": [
                "kanto/tokyo/",
                "kanto/kanagawa/yokohama-and-around/",
                "kanto/saitama/new-urban-center-area/",
                "kanto/chiba/",
            ],
            "東海": [
                "tokai/aichi/nagoya-station-and-around/",
                "tokai/yamanashi/mt-fuji-and-around/",
            ],
            "關西": [
                "kansai/osaka/osaka-bay-area/",
                "kansai/kyoto/around-kyoto-station/",
                "kansai/nara/nara-city-and-around/",
                "kansai/hyogo/kobe-and-around/"
            ],
            "九州": [
                "kyushu/fukuoka/fukuoka-city/",
                "kyushu/kumamoto/kumamoto/",
                "kyushu/kagoshima/kagoshima-and-around/",
                "kyushu/nagasaki/nagasaki-city-and-around/",
                "kyushu/miyazaki/miyazaki/",
            ],
            "沖繩": [
                "okinawa/okinawa/naha-and-the-main-island/",
                "okinawa/okinawa/ishigaki-island-and-around/",
                "okinawa/okinawa/miyako-island/",
            ],
        }

        for area, urls in All_url.items():
            for url in urls:
                sections = []
                sections_sub = []
                current_section = None
                current_section_sub = None

                full_url = base_url + url
                driver.get(full_url)
                time.sleep(1)

                element  = WebDriverWait(driver, 100).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.mod-image-gallery,div.mod-wysiwyg__body")))
                soup = BeautifulSoup(driver.page_source, "html.parser")

                # 子頁父值
                content_container = soup.select_one ('div#anchor_1 div.mod-wysiwyg__body') or soup.select_one('div.mod-wysiwyg__body')

                if not content_container:
                    print(f"{full_url} 找不到內容容器，跳過")
                    continue

                # 內容
                title = soup.select_one("span.mod-keyvisual__heading-text")
                title_text = title.get_text(strip=True) if title else ''

                ALL_img = soup.select_one("div.mod-keyvisual__image")
                img_urlll = None

                if ALL_img:
                    first_img = ALL_img.find("img")  #  找出第一張 <img>
                    if first_img:
                        img_urlll = first_img.get("data-src") or first_img.get("src")


                for tag in content_container.children:
                    if tag.name == "div" and any(cls in tag.get('class', []) for cls in [
                        'mod-wysiwyg__lead-wrapper',
                        'mod-wysiwyg__howto-get-there-header',
                        'mod-wysiwyg__subheading-wrapper',
                    ]):
                        if current_section:
                            sections.append(current_section)

                        # 將標題存下 並為內文打洞方便後續存取
                        heading_tag = tag.find(['h2', 'h3'])
                        heading_text = heading_tag.get_text(strip=True) if heading_tag else ''
                        current_section = {
                            'heading': heading_text,
                            'content': '',
                            'area':area,
                            'title':title_text,
                            'img':img_urlll,
                        }

                    # 爬內文和圖片
                    if tag.name == "div" and any(cls in tag.get('class', []) for cls in [
                        'mod-wysiwyg__text-wrapper',
                        'mod-wysiwyg__bullet-wrapper',
                    ]):
                        # 遇到段落，加入當前區塊
                        if current_section:
                            p_tag = tag.find('p', class_='mod-wysiwyg__text') or tag.find('p', class_='mod-wysiwyg__bullet') or tag.find('p') or tag.find('div', class_='mod-wysiwyg__text clearfix')
                            img_tags = tag.find_all('img')
                            if p_tag:
                                text = p_tag.get_text(strip=True)
                                if text:
                                    current_section['content'] += text + '\n'

                                # 圖片處理
                                for img_tag in img_tags:
                                    img_url = img_tag.get("data-src") or img_tag.get("src")
                                    if "http" not in img_url:
                                        continue
                                    if img_url:
                                        current_section['content'] += f"{img_url}\n"

                # 最後一個區塊加入列表
                if current_section:
                    sections.append(current_section)

                all_sections.extend(sections)
        try:
                    # 先清空想要覆寫的資料
            crawlers_main.objects.all().delete()

            with transaction.atomic():
                # 依序將所有 sections 寫入資料庫
                for section in all_sections:
                    # print(f"寫入資料：parent_title={section.get('title')}, heading={section.get('heading')}")
                    if not section.get('title'):
                        print("發現空的 parent_title！該筆資料 heading:", section.get('heading'))
                    parent_title = section.get('title', '').strip()
                    if parent_title == "" or parent_title == " ":
                        continue  # 跳過沒標題的資料

                    crawlers_main.objects.create(
                        parent_title=section.get('title', ''),
                        heading=section.get('heading', ''),
                        content=section.get('content', ''),
                        area=section.get('area', ''),  # 如果你有處理對應的圖片
                        img=section.get('img', ''),
                    )

        except Exception as e:
            return HttpResponse(f"存入資料庫錯誤: {e}")    

        # print(all_sections)

        return JsonResponse({
        "sections2" : all_sections,
    })

    finally:
        driver.quit()


# 將資料庫回傳主頁
def index(request):
    data_list = crawlers_main.objects.all()  # 從資料庫抓所有資料
    data_list_osusume = crawlers_main.objects.filter(area='osusume')
    img = CustomUser.objects.all()  # 從資料庫抓取所有 CustomUser 實例
    for obj in data_list_osusume:obj.img = obj.img if obj.img else '/static/white.jpg'

    context = {
        'data_list': data_list,
        'data_list_osusume': data_list_osusume,
        'imgs': img,
    }
    if data_list_osusume.exists():
        print("有資料")
    else:
        print("沒資料")
    return render(request, 'index.html',context)

# 必看景點內文處理和回傳
def cons_detail(request,parent_title):
    # 根據parent_title查詢資料
    data_list = crawlers_osusume.objects.filter(parent_title=parent_title)

    # 將資料和圖片做處理
    for item in data_list:
        urls = re.findall(r'https?://\S+', item.content) 
        item.image_urls = urls  # 這是一個 list，含多個網址
        item.image_urls = [
            re.sub(r'/upload/[^/]+/', '/upload/', url) for url in item.image_urls
        ]

        # 把所有圖片網址從內文中移除，保留純文字
        for url in urls:
            item.content = item.content.replace(url, '')    
        item.text = item.content.strip()

    # 整理資料
    context = {
        'parent_title': parent_title,
        'data_list': data_list
    }

    # 資料測試
    print("parent_title:", parent_title)
    print("筆數：", crawlers_osusume.objects.filter(parent_title=parent_title).count())
    
    return render(request, 'cons.html',context)
