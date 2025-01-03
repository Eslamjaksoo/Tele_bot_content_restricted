import os
import subprocess
import ffmpeg
import nest_asyncio
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.types import DocumentAttributeAudio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from googleapiclient.http import MediaFileUpload
#from googleapiclient.discovery import build
#from google.oauth2.credentials import Credentials
#from google.colab import drive
#drive.mount('/content/drive')

# إعداد Google Drive API
#def initialize_drive():
#    SCOPES = ['https://www.googleapis.com/auth/drive']
#    creds = Credentials.from_authorized_user_file('credentials.json', SCOPES)
#    service = build('drive', 'v3', credentials=creds)
#    return service

# تهيئة Google Drive
#drive_service = initialize_drive()

from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials  # استخدام مكتبة الحساب الخدمي

# معرف المجلد الذي شاركته مع حساب الخدمة
FOLDER_ID = '1KQuUFlVRXkwNA6I11caLJV-W6ALiEN61'

# إعداد Google Drive API باستخدام Service Account
def initialize_drive():
    SCOPES = ['https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_file('service_account.json', scopes=SCOPES)
    service = build('drive', 'v3', credentials=creds)
    return service
#####↓↓↓↓↓↓
FOLDER_ID = '1KQuUFlVRXkwNA6I11caLJV-W6ALiEN61'
try:
    drive_service = initialize_drive()
    print("تم الاتصال بـ Google Drive بنجاح.")
    
    # كود اختبار إنشاء ملف
    file_metadata = {
        'name': 'test_creation.txt',  # اسم الملف
        'parents': [FOLDER_ID],
        'mimeType': 'text/plain',     # نوع الملف
    }
    test_file = drive_service.files().create(body=file_metadata, fields='id').execute()
    print(f"تم إنشاء ملف اختبار بنجاح: File ID: {test_file.get('id')}")

except Exception as e:
    print(f"حدث خطأ أثناء الاتصال بـ Google Drive أو اختبار إنشاء الملف: {e}")
#####^^^^^
# تهيئة Google Drive
#try:
#    drive_service = initialize_drive()
#    print("تم الاتصال بـ Google Drive بنجاح.")
#except Exception as e:
#    print(f"حدث خطأ أثناء الاتصال بـ Google Drive: {e}")

#يعرف اذا كان اداه التحويل موجودة ام لا

try:
    subprocess.run(["ffmpeg", "-version"], check=True)
    print("ffmpeg is installed and available.")
except FileNotFoundError:
    print("ffmpeg is not installed.")



nest_asyncio.apply()

# إعدادات البوت
bot_token = "8159077886:AAEzeVksfosancAMnx4nw1ouESneBnrnk_E"

# مراحل المحادثة
PHONE, CODE, PASSWORD, FILE = range(4)

# تعريف المتغيرات
clients = {}
phone_numbers = {}
CHUNK_SIZE = 49 * 1024 * 1024  # حجم الجزء الواحد (49 ميجابايت)

# مسار تخزين الجلسات على Google Drive
DRIVE_PATH = '/content/drive/MyDrive/sessions/'
os.makedirs(DRIVE_PATH, exist_ok=True)  # إنشاء المجلد إذا لم يكن موجودًا

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id in clients and await clients[user_id].is_user_authorized():
        await update.message.reply_text("تم تسجيل الدخول مسبقًا! أرسل الآن رابط الملف لتحميله.")
        return FILE

    await update.message.reply_text("أدخل رقم الهاتف الخاص بك مع رمز الدولة (مثل: +201234567890):")
    return PHONE

async def process_phone(update, context):
    # إعداد المتغيرات
    user_id = update.message.from_user.id
    phone_number = update.message.text.strip()
    session_file = f"/tmp/session_{user_id}.session"
    api_id = 26466946
    api_hash = '05d7144ca3c5f4594e40c535afb3bd5a'
      
    file_metadata = {
        'name': f'session_{user_id}.session',
        'parents': [FOLDER_ID],
        'mimeType': 'application/octet-stream'
    }

    print(f"مسار ملف الجلسة: {session_file}")
    print(f"رقم المستخدم: {user_id}, رقم الهاتف: {phone_number}")

    # إنشاء جلسة جديدة
    client = TelegramClient(session_file, api_id, api_hash)
    clients[user_id] = client
    phone_numbers[user_id] = phone_number

    try:
        await client.connect()
        print("تم إنشاء الاتصال بـ Telegram.")
        if await client.is_user_authorized():
            print("المستخدم مصرح له مسبقًا.")
            # رفع الجلسة إلى Google Drive
            try:
                if not os.path.exists(session_file):
                    print("خطأ: ملف الجلسة غير موجود محليًا قبل الرفع.")
                    await update.message.reply_text("خطأ: ملف الجلسة غير موجود محليًا قبل الرفع.")
                    return PHONE

                print("بدء عملية الرفع إلى Google Drive...")

                # التحقق من وجود المجلد
                print(f"التحقق من معرف المجلد: {FOLDER_ID}")
                if not FOLDER_ID:
                    print("خطأ: معرف المجلد غير موجود.")
                    await update.message.reply_text("خطأ: معرف المجلد غير موجود.")
                    return PHONE

                # إنشاء MediaFileUpload
                try:
                    upload_media = MediaFileUpload(session_file, resumable=True)
                    print(f"تم إنشاء MediaFileUpload: {upload_media}")
                except Exception as e:
                    print(f"خطأ أثناء إنشاء MediaFileUpload: {e}")
                    await update.message.reply_text("خطأ أثناء إنشاء MediaFileUpload.")
                    return PHONE

                # تنفيذ الرفع
                try:
                    print("رفع الملف إلى Google Drive...")
                    uploaded_file = drive_service.files().create(
                        body=file_metadata,
                        media_body=upload_media,
                        fields='id'
                    ).execute()
                    print(f"تم رفع الجلسة إلى Google Drive بنجاح: File ID: {uploaded_file.get('id')}")
                    await update.message.reply_text("تم تسجيل الدخول بنجاح! أرسل الآن رابط الملف لتحميله.")
                    return FILE
                except Exception as e:
                    print(f"خطأ أثناء رفع الملف إلى Google Drive: {e}")
                    await update.message.reply_text(f"خطأ أثناء رفع الملف إلى Google Drive: {e}")
                    return PHONE

            except Exception as upload_error:
                print(f"خطأ أثناء رفع الجلسة إلى Google Drive: {upload_error}")
                await update.message.reply_text(f"خطأ أثناء رفع الجلسة إلى Google Drive: {upload_error}")
                return PHONE

        # طلب رمز التحقق
        await client.send_code_request(phone_number)
        print("تم إرسال رمز التحقق.")
        await update.message.reply_text("تم إرسال رمز التحقق إلى رقمك. الرجاء إدخال الرمز (مثل: 2 2 9 3 0):")
        return CODE

    except Exception as e:
        print(f"حدث خطأ أثناء إنشاء الجلسة: {e}")
        await update.message.reply_text(f"حدث خطأ أثناء إنشاء الجلسة: {e}")
        return PHONE



async def process_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    code = update.message.text.strip().replace(" ", "")

    client = clients.get(user_id)
    phone_number = phone_numbers.get(user_id)

    if not client or not phone_number:
        await update.message.reply_text("حدث خطأ. الرجاء بدء العملية من جديد باستخدام /start.")
        return ConversationHandler.END

    try:
        await client.sign_in(phone=phone_number, code=code)
        await update.message.reply_text("تم تسجيل الدخول بنجاح! أرسل الآن رابط الملف لتحميله.")
        return FILE
    except SessionPasswordNeededError:
        await update.message.reply_text("التحقق بخطوتين مفعّل. الرجاء إدخال كلمة المرور الخاصة بك:")
        return PASSWORD
    except Exception as e:
        await update.message.reply_text(f"حدث خطأ أثناء تسجيل الدخول: {e}")
        return CODE

async def process_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    password = update.message.text.strip()

    client = clients.get(user_id)

    try:
        await client.sign_in(password=password)
        await update.message.reply_text("تم تسجيل الدخول بنجاح! أرسل الآن رابط الملف لتحميله.")
        return FILE
    except Exception as e:
        await update.message.reply_text(f"حدث خطأ أثناء إدخال كلمة المرور: {e}")
        return PASSWORD

async def process_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    file_link = update.message.text.strip()

    client = clients.get(user_id)
    if not client:
        await update.message.reply_text("لم يتم تسجيل الدخول. الرجاء استخدام /start لبدء العملية.")
        return ConversationHandler.END

    try:
        # تحميل الكيانات مسبقًا
        await client.get_dialogs()

        if "t.me/c/" in file_link:
            parts = file_link.split("/")
            chat_id = int("-100" + parts[-2])
            message_id = int(parts[-1])
        else:
            await update.message.reply_text("الرابط غير صالح. تأكد من أنه رابط رسالة خاص.")
            return

        progress_message = await update.message.reply_text("جاري تحميل الملف...")
        last_percentage = 0

        async def progress_callback(current, total):
            nonlocal last_percentage
            percentage = int((current / total) * 100)
            if percentage > last_percentage:
                await progress_message.edit_text(f"جاري تحميل الملف... {percentage}%")
                last_percentage = percentage

        message = await client.get_messages(chat_id, ids=message_id)
        if message and message.media:
            # تحميل الملف
            file_path = await message.download_media(file="./", progress_callback=progress_callback)

            await progress_message.edit_text("جاري إرسال الملف...")

            if file_path.endswith('.MOV'):  # التحقق إذا كان الملف بصيغة MOV
               mp4_path = os.path.splitext(file_path)[0] + '.mp4'
               try:
                   await update.message.reply_text("جاري محاولة تحويل الملف إلى MP4...")

                    # استخدام مكتبة ffmpeg-python للتحويل
                   ffmpeg.input(file_path).output(
                   mp4_path,
                   vcodec="libx264",  # ترميز الفيديو
                   preset="fast",  # سرعة المعالجة
                   crf=22  # جودة الضغط
                   ).run()

                   # حذف الملف الأصلي بعد التحويل
                   os.remove(file_path)
                   file_path = mp4_path
                   await update.message.reply_text("تم تحويل الملف إلى MP4 بنجاح.")

               except Exception as e:  # التقاط جميع الأخطاء
                      await update.message.reply_text(f"فشل تحويل الملف إلى MP4: {str(e)}. سيتم إرسال الملف كما هو.")
 
            # إرسال الفيديو كرسالة فيديو (Video Note)
            if message.media.document.mime_type.startswith("video"):
                await client.send_file(
                    entity=update.message.chat_id,
                    file=file_path,
                    caption="",
                    supports_streaming=True,
                    video_note=True
                )
                # إرسال الملف كـ Audio إذا كان صوتيًا 
            elif message.media.document.mime_type.startswith("audio"):
                duration = message.media.document.attributes[0].duration if hasattr(message.media.document.attributes[0], "duration") else 0                
                await client.send_file(                    
                   entity=update.message.chat_id,                    
                   file=file_path,                    
                   caption="",                    
                   attributes=[DocumentAttributeAudio(duration=duration)]                
                )
            else:
                await client.send_file(
                    entity=update.message.chat_id,
                    file=file_path,
                    caption=""
                )

            os.remove(file_path)  # حذف الملف بعد الإرسال
            await progress_message.edit_text("تم تحميل الملف وإرساله بنجاح!")
        else:
            await update.message.reply_text("لم يتم العثور على ملف في الرسالة المرسلة.")
    except Exception as e:
        await update.message.reply_text(f"حدث خطأ أثناء تحميل الملف: {e}")

async def disconnect_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    client = clients.get(user_id)

    if client:
        try:
            await client.disconnect()
            clients.pop(user_id, None)  # إزالة العميل من القائمة
            await update.message.reply_text("تم إغلاق الجلسة بنجاح.")
        except Exception as e:
            await update.message.reply_text(f"حدث خطأ أثناء إغلاق الجلسة: {e}")
    else:
        await update.message.reply_text("لا توجد جلسة نشطة لإغلاقها.")

async def connection_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    client = clients.get(user_id)

    if client and await client.is_user_authorized():
        await update.message.reply_text("الحالة: مسجل الدخول.")
    else:
        await update.message.reply_text("الحالة: غير مسجل الدخول. الرجاء استخدام /start لتسجيل الدخول.")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("تم إلغاء العملية.")
    return ConversationHandler.END

if __name__ == "__main__":
    app = ApplicationBuilder().token(bot_token).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start_command)],
        states={
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_phone)],
            CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_code)],
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_password)],
            FILE: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_file)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("connection", connection_command))
    app.add_handler(CommandHandler("disconnect", disconnect_command))

    print("البوت يعمل الآن...")
    app.run_polling()
