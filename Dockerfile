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








# استخدام إصدار محدد من Ubuntu بدلاً من latest
FROM ubuntu:22.04

# تعيين مجلد العمل
WORKDIR /app

# تحديث النظام وتثبيت الأدوات الأساسية والمكتبات المطلوبة
RUN apt-get update && apt-get install -y \
    python3.9 \
    python3-pip \
    ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# نسخ الملفات إلى الحاوية
COPY . .

# تثبيت المتطلبات
RUN pip install --no-cache-dir -r requirements.txt

# تعيين متغير بيئة لتحديد نوع الخدمة
ENV SERVICE_TYPE=worker

# تشغيل السكريبت الأساسي بشكل صريح
CMD ["python3", "-u", "main.py"]
