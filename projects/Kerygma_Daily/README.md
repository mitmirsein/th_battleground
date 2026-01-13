# 케리그마 매일 묵상 (Kerygma Daily)

매일 구약과 신약 말씀을 원어(히브리어/헬라어)와 함께 묵상하는 PWA 웹앱

## 🌐 Live Demo

**https://kdbm.netlify.app**

## ✨ Features

- 📖 **원어 성경** - 히브리어/헬라어 원문과 완전 파싱 정보
- 🔊 **음역 표시** - 한국어 발음 가이드
- 📱 **PWA 지원** - 모바일 홈 화면 설치, 오프라인 사용 가능
- 🌙 **다크모드** - 시스템 설정 자동 연동
- ⛪ **교회력 기반** - 주현절, 사순절 등 절기 반영

## 📁 Structure

```
Kerygma_Daily/
├── index.html          # 메인 페이지
├── install.html        # 앱 설치 안내
├── style.css           # 스타일 (Kerygma Gray 테마)
├── app.js              # 앱 로직 (JSON 데이터 로드)
├── sw.js               # Service Worker (PWA)
├── manifest.json       # PWA 설정
├── data/
│   └── 2026-01.json    # 1월 묵상 데이터 (31일)
└── icons/              # PWA 아이콘 (72~512px)
```

## 📅 Data Format (JSON)

```json
{
  "2026-01-03": {
    "date": "2026-01-03",
    "liturgical": "성탄절기",
    "ot": {
      "ref": "창세기 1:3",
      "kor_std": "개역한글 번역",
      "kor_lit": "원어 직역",
      "focus_text": "וַיֹּאמֶר אֱלֹהִים יְהִי אוֹר וַיְהִי־אוֹר",
      "words": [
        {"text": "וַיֹּאמֶר", "sound": "바요메르", "lemma": "אָמַר", "morph": "...", "gloss": "..."}
      ]
    },
    "nt": { ... },
    "meditation": { "content": "...", "question": "..." }
  }
}
```

## 🚀 Local Development

```bash
# 1. Clone
git clone https://github.com/mitmirsein/kdm.git
cd kdm

# 2. Run local server
python3 -m http.server 8080

# 3. Open browser
open http://localhost:8080
```

## 📱 PWA Installation

1. 모바일 브라우저에서 https://kdbm.netlify.app 접속
2. **홈 화면에 추가** 선택 (Safari/Chrome)
3. 앱처럼 사용 가능 (오프라인 지원)

자세한 설치 방법: https://kdbm.netlify.app/install.html

## 🔧 Deployment

Netlify에 GitHub 리포 연동하여 자동 배포

```
Branch: master
Build: (없음, 정적 사이트)
Publish: 루트
```

## 📝 License

MIT

## 🙏 Credits

**powered by [케리그마출판사](https://kerygma.co.kr)**
