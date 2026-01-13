/**
 * Utilities & Helper Functions
 */

export const Utils = {
    // === Share Feature ===
    async handleShare(dailyData) {
        if (!dailyData || !dailyData.meditation) return;

        const date = document.getElementById('date-display').textContent;
        const title = dailyData.meditation.title || "오늘의 묵상";
        const content = dailyData.meditation.content;
        const question = dailyData.meditation.question;
        const url = "https://kdbm.netlify.app/";

        const shareText = `[케리그마 매일 묵상] ${date}\n\n<${title}>\n\n${content}\n\n<성찰 질문>\n${question}\n\n${url}`;

        if (navigator.share) {
            try {
                await navigator.share({
                    title: '케리그마 매일 묵상',
                    text: shareText,
                    url: url
                });
            } catch (err) {
                console.log('공유 취소 또는 에러:', err);
            }
        } else {
            try {
                await navigator.clipboard.writeText(shareText);
                this.showToast("클립보드에 복사되었습니다");
            } catch (err) {
                console.error('클립보드 복사 실패:', err);
                this.showToast("복사에 실패했습니다");
            }
        }
    },

    showToast(message) {
        const toast = document.getElementById('toast');
        toast.textContent = message;
        toast.classList.add('visible');

        setTimeout(() => {
            toast.classList.remove('visible');
        }, 3000);
    },

    // === Service Worker ===
    registerServiceWorker() {
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('sw.js')
                .then(reg => console.log('SW registered'))
                .catch(err => console.log('SW registration failed:', err));
        }
    }
};
