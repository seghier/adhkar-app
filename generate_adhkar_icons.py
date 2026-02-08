"""
تطبيق توليد صور أزرار تطبيق الأذكار
Adhkar App Icon Generator using Google GenAI

هذا التطبيق يقوم بتوليد جميع صور الأزرار تلقائياً
ويحفظها في مجلد icons داخل مشروع التطبيق.

الاستخدام:
1. تأكد من تثبيت المكتبة: pip install google-genai
2. قم بتعيين متغير البيئة GOOGLE_API_KEY أو أدخل المفتاح مباشرة
3. شغّل البرنامج: python generate_adhkar_icons.py
"""

import os
import time
from pathlib import Path

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("❌ يرجى تثبيت المكتبة أولاً:")
    print("   pip install google-genai")
    exit(1)

# ===== الإعدادات =====
# 🔑 ضع مفتاح API هنا مباشرة (أو اتركه فارغاً ليطلبه منك البرنامج)
API_KEY = "AIzaSyBvF2OyGb6eqfht-kRh1d_jz0xps3s45Tc"  # مثال: "AIzaSy..."

# مجلد حفظ الصور
OUTPUT_DIR = Path(r"h:\amel\pure\adhkar-app\icons")

# التأخير بين كل طلب (بالثواني) لتجنب rate limiting
DELAY_BETWEEN_REQUESTS = 5

# نموذج توليد الصور
MODEL_NAME = "gemini-3-pro-image-preview" 

# ===== قائمة البرومبتات =====
# كل عنصر يحتوي على: (اسم_الملف, البرومبت)
PROMPTS = [
    # === أذكار الصباح والمساء ===
    ("morning", "Flat vector art of a simple sun rising, soft gradient background, Islamic geometric pattern overlay, serene and minimal, no text"),
    ("evening", "Flat vector art of a simple sunset, warm orange and purple gradient, silhouette of a mosque dome in distance, minimal, no text"),
    ("sleep", "Flat vector art of a crescent moon and hanging lantern (Fanous), dark blue night background, peaceful and Islamic, no text"),
    ("wakeup", "Flat vector art of a sun ray shining through an Islamic arch window, bright and hopeful, minimal design, no text"),
    
    # === أدعية المنزل ===
    ("enter-home", "Flat vector art of an open door with warm welcoming light, simple Islamic arch design, minimal and clean, no text"),
    ("exit-home", "Flat vector art of a path leading out from a door towards nature, simple and symbolic, bright colors, no text"),
    ("enter-bathroom", "Flat vector art of clean water flowing, blue tones, symbol of purity and cleanliness, minimal abstraction, no text"),
    ("exit-bathroom", "Flat vector art of a drop of water and a sparkle, symbol of freshness and purity, minimal and clean, no text"),
    
    # === أدعية الطعام ===
    ("before-food", "Flat vector art of a date (fruit) and a glass of water, simple symbol of blessed food, warm colors, no text"),
    ("after-food", "Flat vector art of two open hands in gratitude (Dua gesture), simple and symbolic, soft background, no text"),
    ("iftar", "Flat vector art of three dates and a cup, simple Ramadan Iftar symbol, clean lines, no text"),
    ("guest-dua", "Flat vector art of a golden Dallah (Arabic coffee pot), symbol of generosity and hospitality, minimal flat style, no text"),
    
    # === أدعية السفر ===
    ("travel", "Flat vector art of an airplane silhouette in a clear sky, simple travel symbol, soft blue background, no text"),
    ("ride-vehicle", "Flat vector art of a car silhouette on a road, simple journey symbol, minimal and clean, no text"),
    ("return-travel", "Flat vector art of a house icon with a heart, symbol of safe return home, warm and welcoming, no text"),
    
    # === أدعية الحج والعمرة ===
    ("talbiyah", "Flat vector art of the Kaaba icon, simple and gold/black colors, central composition, spiritual symbol, no text"),
    ("tawaf", "Flat vector art of circular lines around a central point (Kaaba), symbolizing Tawaf motion, abstract and spiritual, no text"),
    ("arafat", "Flat vector art of a mountain silhouette with a sun behind it, symbol of Arafat day, simple and warm, no text"),
    ("muzdalifah", "Flat vector art of a simple tent icon under stars, symbol of pilgrimage camp, peaceful night, no text"),
    ("jamarat", "Flat vector art of three pillars symbol, simple representation of Jamarat, minimal design, no text"),
    
    # === أدعية المسجد ===
    ("go-mosque", "Flat vector art of footsteps leading to a mosque dome, simple path symbol, spiritual direction, no text"),
    ("enter-mosque", "Flat vector art of an intricate Islamic gate or door, welcoming entrance symbol, detailed geometric pattern, no text"),
    ("exit-mosque", "Flat vector art of a mosque silhouette with a sun setting behind, peaceful departure, warm colors, no text"),
    ("adhan", "Flat vector art of a minaret silhouette, simple call to prayer symbol, clear sky background, no text"),
    
    # === أدعية متنوعة ===
    ("anxiety", "Flat vector art of a heart with a warm glow inside, symbol of finding peace and relief, soft colors, no text"),
    ("istikhara", "Flat vector art of a compass icon pointing to Qibla, symbol of guidance, simple and clean, no text"),
    ("rain", "Flat vector art of a cloud with rain drops, simple blessing symbol, blue and white colors, no text"),
    ("wind", "Flat vector art of trees bending in strong wind with flying leaves, symbol of nature's power, dynamic motion lines, white background, no text"),
    ("new-clothes", "Flat vector art of a white brightness/sparkle on a cloth texture, symbol of newness and purity, clean white, no text"),
    ("mirror", "Flat vector art of a simple mirror frame, symbol of reflection, minimal design, no text"),
    
    # === أيقونات الأقسام الرئيسية ===
    ("category-morning-evening", "Flat vector art of sun and moon merged, day and night symbol, simple and balanced, no text"),
    ("category-home", "Flat vector art of a simple house icon with Islamic arch window, symbol of home, warm colors, no text"),
    ("category-food", "Flat vector art of a bowl/plate icon, symbol of sustenance, simple and inviting, no text"),
    ("category-travel", "Flat vector art of a globe with a path line, symbol of travel, connection, no text"),
    ("category-hajj", "Flat vector art of a simple Kaaba icon, gold and black, clear spiritual symbol, no text"),
    ("category-mosque", "Flat vector art of a green mosque dome icon, simple and recognizable, spiritual symbol, no text"),
    ("category-misc", "Flat vector art of prayer beads (Misbaha) icon, symbol of dhikr, simple and circular, no text"),
]


def generate_image(client, prompt: str, output_path: Path) -> bool:
    """
    توليد صورة واحدة وحفظها
    
    Args:
        client: عميل Google GenAI
        prompt: وصف الصورة
        output_path: مسار حفظ الصورة
    
    Returns:
        True إذا نجح التوليد، False إذا فشل
    """
    try:
        print(f"   ⏳ جاري التوليد...")
        
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
                image_config=types.ImageConfig(
                    aspect_ratio="1:1",
                )
            )
        )
        
        # البحث عن الصورة في الاستجابة
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                # حفظ الصورة
                image_data = part.inline_data.data
                with open(output_path, 'wb') as f:
                    f.write(image_data)
                print(f"   ✅ تم الحفظ: {output_path.name}")
                return True
        
        print(f"   ⚠️ لم يتم العثور على صورة في الاستجابة")
        return False
        
    except Exception as e:
        print(f"   ❌ خطأ: {e}")
        return False


def main():
    print("=" * 60)
    print("🎨 مولّد صور أزرار تطبيق الأذكار")
    print("=" * 60)
    print()
    
    # التحقق من مفتاح API
    api_key = API_KEY or os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        print("⚠️ لم يتم العثور على مفتاح API.")
        api_key = input("أدخل مفتاح Google API: ").strip()
        if not api_key:
            print("❌ يجب إدخال مفتاح API للمتابعة.")
            return
    
    # إنشاء مجلد الإخراج
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"📁 مجلد الحفظ: {OUTPUT_DIR}")
    print()
    
    # إنشاء العميل
    try:
        client = genai.Client(api_key=api_key)
        print("✅ تم الاتصال بـ Google GenAI")
    except Exception as e:
        print(f"❌ فشل الاتصال: {e}")
        return
    
    print()
    print(f"📊 عدد الصور المطلوبة: {len(PROMPTS)}")
    print(f"⏱️ الوقت المتوقع: ~{len(PROMPTS) * (DELAY_BETWEEN_REQUESTS + 10) // 60} دقيقة")
    print()
    
    # بدء التوليد
    success_count = 0
    fail_count = 0
    
    for i, (filename, prompt) in enumerate(PROMPTS, 1):
        print(f"[{i}/{len(PROMPTS)}] 🖼️ {filename}")
        
        output_path = OUTPUT_DIR / f"{filename}.png"
        
        # تخطي الصور الموجودة مسبقاً
        if output_path.exists():
            print(f"   ⏭️ موجودة مسبقاً، تخطي...")
            success_count += 1
            continue
        
        # توليد الصورة
        if generate_image(client, prompt, output_path):
            success_count += 1
        else:
            fail_count += 1
        
        # انتظار قبل الطلب التالي
        if i < len(PROMPTS):
            print(f"   ⏳ انتظار {DELAY_BETWEEN_REQUESTS} ثواني...")
            time.sleep(DELAY_BETWEEN_REQUESTS)
        
        print()
    
    # ملخص النتائج
    print("=" * 60)
    print("📊 ملخص النتائج:")
    print(f"   ✅ نجح: {success_count}")
    print(f"   ❌ فشل: {fail_count}")
    print("=" * 60)
    
    if fail_count == 0:
        print("🎉 تم توليد جميع الصور بنجاح!")
        print()
        print("📝 الخطوة التالية:")
        print("   قم بتحديث ملف adhkar-data.js لاستخدام الصور الجديدة")
    else:
        print("⚠️ بعض الصور لم يتم توليدها. يمكنك تشغيل البرنامج مرة أخرى لإعادة المحاولة.")


if __name__ == "__main__":
    main()
