/**
 * تطبيق الأذكار والأدعية
 * Adhkar App Main Logic
 */

class AdhkarApp {
    constructor() {
        // العناصر
        this.splashScreen = document.getElementById('splash-screen');
        this.app = document.getElementById('app');
        this.backBtn = document.getElementById('back-btn');
        this.pageTitle = document.getElementById('page-title');
        this.categoriesPage = document.getElementById('categories-page');
        this.categoriesGrid = document.getElementById('categories-grid');
        this.duasPage = document.getElementById('duas-page');
        this.duasGrid = document.getElementById('duas-grid');

        // عناصر النافذة المنبثقة
        this.modal = document.getElementById('dua-modal');
        this.modalBackdrop = this.modal.querySelector('.modal-backdrop');
        this.closeModalBtn = document.getElementById('close-modal-btn');
        this.modalIcon = document.getElementById('modal-dua-icon');
        this.modalTitle = document.getElementById('modal-dua-title');
        this.modalText = document.getElementById('modal-dua-text');
        this.modalSource = document.getElementById('modal-dua-source');
        this.modalPlayBtn = document.getElementById('modal-play-btn');

        this.audioPlayer = document.getElementById('audio-player');
        this.toast = document.getElementById('toast');

        // الحالة
        this.currentCategory = null;
        this.currentDua = null;
        this.isPlaying = false;

        // تهيئة التطبيق
        this.init();
    }

    init() {
        // إخفاء شاشة التحميل بعد ثانية
        setTimeout(() => {
            this.splashScreen.classList.add('fade-out');
            this.app.classList.remove('hidden');
        }, 1000);

        // بناء الصفحة الرئيسية
        this.renderCategories();

        // أحداث الأزرار
        this.backBtn.addEventListener('click', () => this.goBack());

        // أحداث النافذة المنبثقة
        this.closeModalBtn.addEventListener('click', () => this.closeModal());
        this.modalBackdrop.addEventListener('click', () => this.closeModal());
        this.modalPlayBtn.addEventListener('click', () => this.toggleAudio());

        // إغلاق بالضغط على Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && !this.modal.classList.contains('hidden')) {
                this.closeModal();
            }
        });

        // أحداث الصوت
        this.audioPlayer.addEventListener('ended', () => this.onAudioEnded());
        this.audioPlayer.addEventListener('error', () => this.onAudioError());
    }

    // ===== عرض الأقسام الرئيسية =====
    renderCategories() {
        this.categoriesGrid.innerHTML = '';

        ADHKAR_DATA.categories.forEach(category => {
            const card = this.createCard(category.icon, category.name, () => {
                this.openCategory(category);
            });
            this.categoriesGrid.appendChild(card);
        });
    }

    // ===== عرض الأدعية داخل القسم =====
    renderDuas(categoryId) {
        this.duasGrid.innerHTML = '';
        const duas = ADHKAR_DATA.duas[categoryId] || [];

        duas.forEach(dua => {
            const card = this.createCard(dua.icon, dua.name, () => {
                this.openDuaModal(dua);
            });
            this.duasGrid.appendChild(card);
        });
    }

    // ===== إنشاء بطاقة زر =====
    createCard(icon, title, onClick) {
        const button = document.createElement('button');
        button.className = 'card-btn';
        button.innerHTML = `
            <div class="card-icon">${this.renderIcon(icon)}</div>
            <span class="card-title">${title}</span>
        `;

        button.addEventListener('click', (e) => {
            this.createRipple(e, button);
            onClick();
        });

        return button;
    }

    // ===== عرض الأيقونة (إيموجي أو صورة) =====
    renderIcon(icon) {
        // إذا كانت الأيقونة عبارة عن مسار صورة
        if (icon.includes('/') || icon.includes('.')) {
            return `<img src="icons/${icon}" alt="" loading="lazy">`;
        }
        // إيموجي
        return icon;
    }

    // ===== فتح قسم =====
    openCategory(category) {
        this.currentCategory = category;
        this.pageTitle.textContent = category.name;
        this.showBackButton();

        this.renderDuas(category.id);

        this.categoriesPage.classList.add('hidden');
        this.duasPage.classList.remove('hidden');
    }

    // ===== فتح نافذة الدعاء المنبثقة =====
    openDuaModal(dua) {
        this.currentDua = dua;

        // تعبئة محتوى النافذة
        this.modalIcon.innerHTML = this.renderIcon(dua.icon);
        this.modalTitle.textContent = dua.name;
        this.modalText.textContent = dua.text;
        this.modalSource.textContent = `📚 ${dua.source}`;

        // إعداد الصوت
        this.stopAudio();
        if (dua.audio) {
            this.audioPlayer.src = `audio/${dua.audio}`;
            this.modalPlayBtn.classList.remove('hidden');

            // تشغيل الصوت تلقائياً
            setTimeout(() => {
                this.playAudio();
            }, 300);
        } else {
            this.modalPlayBtn.classList.add('hidden');
        }

        // إظهار النافذة
        this.modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden'; // منع التمرير خلف النافذة
    }

    // ===== إغلاق النافذة المنبثقة =====
    closeModal() {
        // إيقاف الصوت عند الإغلاق
        this.stopAudio();

        // إخفاء النافذة
        this.modal.classList.add('hidden');
        document.body.style.overflow = ''; // إعادة التمرير

        this.currentDua = null;
    }

    // ===== الرجوع =====
    goBack() {
        this.stopAudio();

        if (!this.duasPage.classList.contains('hidden')) {
            // من قائمة الأدعية إلى الأقسام
            this.duasPage.classList.add('hidden');
            this.categoriesPage.classList.remove('hidden');
            this.pageTitle.textContent = 'الأذكار والأدعية';
            this.hideBackButton();
            this.currentCategory = null;
        }
    }

    // ===== إظهار/إخفاء زر الرجوع =====
    showBackButton() {
        this.backBtn.classList.remove('hidden');
    }

    hideBackButton() {
        this.backBtn.classList.add('hidden');
    }

    // ===== التحكم بالصوت =====
    toggleAudio() {
        if (this.isPlaying) {
            this.pauseAudio();
        } else {
            this.playAudio();
        }
    }

    playAudio() {
        const playPromise = this.audioPlayer.play();

        if (playPromise !== undefined) {
            playPromise.then(() => {
                this.isPlaying = true;
                this.modalPlayBtn.classList.add('playing');
            }).catch(error => {
                // في حالة عدم السماح بالتشغيل التلقائي
                console.log('Auto-play prevented, user interaction required');
                this.isPlaying = false;
                this.modalPlayBtn.classList.remove('playing');
            });
        }
    }

    pauseAudio() {
        this.audioPlayer.pause();
        this.isPlaying = false;
        this.modalPlayBtn.classList.remove('playing');
    }

    stopAudio() {
        this.audioPlayer.pause();
        this.audioPlayer.currentTime = 0;
        this.isPlaying = false;
        this.modalPlayBtn.classList.remove('playing');
    }

    onAudioEnded() {
        this.isPlaying = false;
        this.modalPlayBtn.classList.remove('playing');
    }

    onAudioError() {
        this.isPlaying = false;
        this.modalPlayBtn.classList.remove('playing');
        // لا نعرض رسالة خطأ إذا لم يكن هناك ملف صوتي (سلوك طبيعي)
    }

    // ===== تأثير الموجة =====
    createRipple(event, element) {
        const ripple = document.createElement('span');
        ripple.className = 'ripple';

        const rect = element.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);

        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = event.clientX - rect.left - size / 2 + 'px';
        ripple.style.top = event.clientY - rect.top - size / 2 + 'px';

        element.appendChild(ripple);

        ripple.addEventListener('animationend', () => {
            ripple.remove();
        });
    }

    // ===== رسالة منبثقة =====
    showToast(message) {
        this.toast.textContent = message;
        this.toast.classList.remove('hidden');

        setTimeout(() => {
            this.toast.classList.add('hidden');
        }, 3000);
    }
}

// ===== تسجيل Service Worker =====
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('service-worker.js')
            .then(registration => {
                console.log('ServiceWorker registered:', registration.scope);
            })
            .catch(error => {
                console.log('ServiceWorker registration failed:', error);
            });
    });
}

// ===== تشغيل التطبيق =====
document.addEventListener('DOMContentLoaded', () => {
    window.adhkarApp = new AdhkarApp();
});
