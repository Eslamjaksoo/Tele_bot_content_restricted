# # استخدم صورة Ubuntu الأحدث لضمان توافق GLIBC
# FROM ubuntu:latest

# # تعيين مجلد العمل
# WORKDIR /app

# # تحديث النظام وتثبيت الأدوات الأساسية
# RUN apt-get update && apt-get install -y \
#     software-properties-common \
#     curl \
#     wget \
#     build-essential \
#     gawk \
#     bison \
#     flex

# # تحميل وتثبيت GLIBC 2.38
# RUN wget http://ftp.gnu.org/gnu/libc/glibc-2.38.tar.gz && \
#     tar -xvzf glibc-2.38.tar.gz && \
#     cd glibc-2.38 && \
#     mkdir build && cd build && \
#     ../configure --prefix=/usr && make -j$(nproc) && \
#     make install && \
#     cd /app && rm -rf glibc-2.38 glibc-2.38.tar.gz

# # تثبيت Python 3.9 و pip
# RUN apt-get install -y python3.9 python3-pip

# # تثبيت FFMPEG
# RUN apt-get install -y ffmpeg

# # نسخ الملفات إلى الحاوية
# COPY . .

# # تثبيت المتطلبات
# RUN pip install --no-cache-dir -r requirements.txt

# # تشغيل السكريبت الأساسي
# CMD ["python3", "main.py"]







# استخدام صورة Python الرسمية التي تحتوي على جميع المكتبات الأساسية
FROM python:3.9-slim

# تعيين مجلد العمل
WORKDIR /app

# تثبيت ffmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# نسخ ملفات المشروع
COPY . .

# تثبيت المتطلبات
RUN pip install --no-cache-dir -r requirements.txt

# تشغيل البوت
CMD ["python", "main.py"]
