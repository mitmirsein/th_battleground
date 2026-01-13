#!/usr/bin/env python3
"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  journal_collector.py — Theological Journal Digest Generator          ┃
┃                                                                       ┃
┃  Secretariat Agent: 스밀조 (Smilzo) - Vibe Coder                       ┃
┃  Usage:                                                               ┃
┃    python journal_collector.py                                        ┃
┃    python journal_collector.py --months 2                             ┃
┃                                                                       ┃
┃  Output: 010 Inbox/저널_다이제스트_YYYY-MM.md                           ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
"""

import argparse
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

# ═══════════════════════════════════════════════════════════════════════════
# 📌 CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

# 수집 대상 신학 저널 목록 (ISSN) - 과레스키님 제공
# 수집 대상 신학 저널 목록 (ISSN) - 돈 까밀로 엄선 (독일 6 : 영어 4)
# 수집 대상 신학 저널 목록 (ISSN) - 돈 까밀로 엄선 (독일 6 : 영어 4)
# User Provided Direct URLs included for scraping fallback
THEOLOGY_JOURNALS = [
    # ═══════════════════════════════════════════════════════════════
    # 1. 조직신학 & 신학 일반 (Systematic Theology & General)
    # ═══════════════════════════════════════════════════════════════
    # German (6)
    {"name": "Zeitschrift für Theologie und Kirche (ZThK)", "issn": "0044-3549", "category": "Systematic", "url": "https://www.mohrsiebeck.com/zeitschrift/zeitschrift-fuer-theologie-und-kirche-zthk/aktuelles-heft/#journalNav"},
    {"name": "Evangelische Theologie (EvTh)", "issn": "0014-3502", "category": "Systematic", "url": "https://www.degruyterbrill.com/journal/key/evth/html?lang=de&srsltid=AfmBOorwbv78FeNTYkx6J8HW22pP7SX4NkTi9AOPbWvyrdLmz1uiG75p#issues"},
    {"name": "Kerygma und Dogma (KuD)", "issn": "0023-0707", "category": "Systematic", "url": "https://www.vandenhoeck-ruprecht-verlage.com/journal-kerygma-und-dogma?srsltid=AfmBOoo7oykZwH9IW4sdth2pXU7d5RJAvBbvCJKPlP6t9-oHBHBIT5W6"},
    {"name": "Neue Zeitschrift für Systematische Theologie (NZSTh)", "issn": "0028-3517", "category": "Systematic", "url": "https://www.degruyterbrill.com/journal/key/nzst/html?lang=de&srsltid=AfmBOoqumQRhCzQyo6Ftr_clCxwgrZ5PBqCibkIRrR2w8BlzqFDLebgo#issues"},
    {"name": "Theologische Rundschau (ThR)", "issn": "0040-5698", "category": "Systematic", "url": "https://www.mohrsiebeck.com/zeitschrift/theologische-rundschau-thr/aktuelles-heft/#journalNav"},
    # ThLZ Removed
    
    # English (4)
    {"name": "Modern Theology", "issn": "0266-7177", "category": "Systematic"},
    {"name": "Scottish Journal of Theology (SJT)", "issn": "0036-9306", "category": "Systematic"},
    {"name": "The Journal of Theological Studies (JTS)", "issn": "0022-5185", "category": "Systematic"},
    {"name": "International Journal of Systematic Theology (IJST)", "issn": "1463-1652", "category": "Systematic"},

    # ═══════════════════════════════════════════════════════════════
    # 2. 성서학 (Biblical Studies: OT & NT)
    # ═══════════════════════════════════════════════════════════════
    # German (6)
    {"name": "Zeitschrift für die alttestamentliche Wissenschaft (ZAW)", "issn": "0044-2526", "category": "Bible", "url": "https://www.degruyterbrill.com/journal/key/zatw/html?lang=de&srsltid=AfmBOoqCtWT3-gPvOZwE5ldN4I4F_RQ3FeTCu3X-ka1j6JKJd8C8Gq8_#issues"},
    {"name": "Zeitschrift für die neutestamentliche Wissenschaft (ZNW)", "issn": "0044-2615", "category": "Bible", "url": "https://www.degruyterbrill.com/journal/key/zntw/html?lang=de&srsltid=AfmBOopVIpxe8UpxG30s0ezTK9ADh7t_OKdW_RZ9r6klFnxgBNymhbR1#issues"},
    {"name": "Biblische Zeitschrift (BZ)", "issn": "0006-2014", "category": "Bible", "url": "https://brill.com/view/journals/bz/bz-overview.xml?language=de&srsltid=AfmBOoqowMN1LEgx-XkvIyDWEXQWWnxU22W1ZD0KhkEDGs--fxHfqMWH&contents=journaltoc"},
    {"name": "Biblische Notizen (BN)", "issn": "0178-2967", "category": "Bible", "url": "https://www.herder.de/bn-nf/hefte/"},
    {"name": "Zeitschrift für Altorientalische und Biblische Rechtsgeschichte (ZABR)", "issn": "0943-8610", "category": "Bible"},
    {"name": "Early Christianity", "issn": "1868-7032", "category": "Bible", "url": "https://www.mohrsiebeck.com/en/journal/early-christianity-ec/current-issue/#journalNav"},
    # English (4)
    {"name": "Journal of Biblical Literature (JBL)", "issn": "1934-3876", "category": "Bible"}, # Updated ISSN (Electronic)
    {"name": "Journal for the Study of the Old Testament (JSOT)", "issn": "0309-0892", "category": "Bible", "url": "https://journals.sagepub.com/home/JOT"},
    {"name": "Journal for the Study of the New Testament (JSNT)", "issn": "0142-064X", "category": "Bible"},
    {"name": "Vetus Testamentum (VT)", "issn": "0042-4935", "category": "Bible"},

    # ═══════════════════════════════════════════════════════════════
    # 3. 역사 / 윤리 / 실천 (History, Ethics, Practical)
    # ═══════════════════════════════════════════════════════════════
    # German (6)
    {"name": "Archiv für Reformationsgeschichte (ARG)", "issn": "0003-9381", "category": "History/Pract", "url": "https://www.degruyterbrill.com/journal/key/arg/html?lang=de&srsltid=AfmBOorW3S5sXL1bWVl5kcnyYkIeyKivtHzQJxnv0GG1GHVyEy36JIOp#issues"},
    {"name": "Zeitschrift für Antikes Christentum (ZAC)", "issn": "0949-9571", "category": "History/Pract", "url": "https://www.degruyterbrill.com/journal/key/zach/html?lang=de&srsltid=AfmBOoq3ZpomUC2GKbUmigrAJLKbL_5_fN__TVktqHOF6ZJNWSgDtQbo#issues"},
    {"name": "Zeitschrift für Evangelische Ethik (ZEE)", "issn": "0044-2674", "category": "History/Pract", "url": "https://www.degruyterbrill.com/journal/key/zee/html#issues"},
    {"name": "Verkündigung und Forschung (V&F)", "issn": "0342-2410", "category": "History/Pract", "url": "https://www.degruyterbrill.com/journal/key/vf/html?lang=de&srsltid=AfmBOooEntodw4k_nqNK-CcgTgHq7OJ45doC3WhywD1j-Zyjhcp_cJr1#issues"},
    {"name": "Pastoraltheologie (PTh)", "issn": "0720-6259", "category": "History/Pract", "url": "https://www.vandenhoeck-ruprecht-verlage.com/journal-pastoraltheologie-ohne-gpm?srsltid=AfmBOoq25qoLTpQo0hqXxBLaIdx35tIFnww9tZAltCh9_xajnnoNkdXq"},
    {"name": "Kirchliche Zeitgeschichte (KZG)", "issn": "0932-9951", "category": "History/Pract", "url": "https://www.vandenhoeck-ruprecht-verlage.com/journal-kirchliche-zeitgeschichte?srsltid=AfmBOoqF93uk3aJnlZyCtqWSgWFwJItNP4ZJxa4Ds0ZH8tH1rwiPR-gP"},
    # English (4)
    {"name": "Church History", "issn": "0009-6407", "category": "History/Pract"},
    {"name": "Studies in Christian Ethics", "issn": "0953-9468", "category": "History/Pract"},
    {"name": "Journal of Religious Ethics", "issn": "0384-9694", "category": "History/Pract"},
    {"name": "International Journal of Practical Theology (IJPT)", "issn": "1430-6921", "category": "History/Pract"},
]

# Crossref API 설정
CROSSREF_API = "https://api.crossref.org"
USER_AGENT = "JournalCollector/1.1 (Secretariat Hub; mailto:your-email@example.com)"

# 출력 경로
def get_output_path() -> Path:
    """볼트 Inbox 경로 탐색"""
    candidates = [
        Path("/Users/msn/Desktop/MS_Brain.nosync/010 Inbox"),
        Path.home() / "Desktop/MS_Brain.nosync/010 Inbox",
    ]
    for path in candidates:
        if path.exists():
            return path
    # 없으면 첫 번째 경로 생성
    candidates[0].mkdir(parents=True, exist_ok=True)
    return candidates[0]


# ═══════════════════════════════════════════════════════════════════════════
# 🛠️ CROSSREF API CLIENT
# ═══════════════════════════════════════════════════════════════════════════

class CrossrefClient:
    """Crossref API 클라이언트"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
    
    def fetch_recent_articles(
        self, 
        issn: str, 
        from_date: str, 
        until_date: str,
        max_results: int = 50
    ) -> List[Dict[str, Any]]:
        """최근 논문 목록 가져오기 (Smart Date Filter)"""
        # API에는 연도 단위로 넓게 요청
        start_year = from_date.split("-")[0]
        end_year = until_date.split("-")[0]
        
        url = f"{CROSSREF_API}/journals/{issn}/works"
        params = {
            "filter": f"from-pub-date:{start_year},until-pub-date:{end_year}",
            "rows": max_results * 2,
            "sort": "published",
            "order": "desc"
        }
        
        try:
            resp = self.session.get(url, params=params, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                items = data.get("message", {}).get("items", [])
                
                # CLIENT-SIDE FILTERING
                filtered_items = []
                for item in items:
                    pub_date = item.get("published", {}).get("date-parts", [[]])[0]
                    if not pub_date:
                        continue
                        
                    try:
                        year = int(pub_date[0])
                        # If simple year match (often used by German journals like ZThK)
                        if len(pub_date) == 1:
                            target_start_year = int(start_year)
                            target_end_year = int(end_year)
                            if target_start_year <= year <= target_end_year:
                                filtered_items.append(item)
                        # If full date available
                        else:
                            month = int(pub_date[1]) if len(pub_date) > 1 else 1
                            day = int(pub_date[2]) if len(pub_date) > 2 else 1
                            item_date = datetime(year, month, day)
                            
                            target_start = datetime.strptime(from_date, "%Y-%m-%d")
                            target_end = datetime.strptime(until_date, "%Y-%m-%d") + timedelta(days=1)
                            
                            if target_start <= item_date < target_end:
                                filtered_items.append(item)
                                
                    except (ValueError, IndexError):
                        continue
                        
                return filtered_items[:max_results]
            else:
                print(f"  ⚠️ API 오류 ({resp.status_code}): {issn}")
                return []
        except Exception as e:
            print(f"  ❌ 요청 실패: {e}")
            return []
    
    def extract_article_info(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """논문 정보 추출"""
        # 제목
        title = "N/A"
        if item.get("title"):
            title = item["title"][0] if isinstance(item["title"], list) else item["title"]
        
        # 저자
        authors = []
        for author in item.get("author", []):
            name = f"{author.get('given', '')} {author.get('family', '')}".strip()
            if name:
                authors.append(name)
        
        # 출판일
        pub_date = "N/A"
        if item.get("published"):
            parts = item["published"].get("date-parts", [[]])[0]
            if parts:
                pub_date = "-".join(str(p).zfill(2) for p in parts)
        
        # DOI
        doi = item.get("DOI", "")
        link = f"https://doi.org/{doi}" if doi else ""
        
        # 초록
        abstract = item.get("abstract", "")
        if abstract:
            import re
            abstract = re.sub(r'<[^>]+>', ' ', abstract).strip()
            abstract = ' '.join(abstract.split())[:300] + "..." if len(abstract) > 300 else abstract
        
        return {
            "title": title,
            "authors": ", ".join(authors) if authors else "N/A",
            "date": pub_date,
            "doi": doi,
            "link": link,
            "abstract": abstract,
            "volume": item.get("volume", ""),
            "issue": item.get("issue", ""),
        }


# ═══════════════════════════════════════════════════════════════════════════
# 📝 MARKDOWN GENERATOR
# ═══════════════════════════════════════════════════════════════════════════

def generate_markdown_report(
    articles_by_journal: Dict[str, List[Dict]], 
    period: str
) -> str:
    """마크다운 보고서 생성"""
    
    lines = [
        f"# 📚 신학 저널 다이제스트 ({period})",
        "",
        f"> **생성일**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"> **수집 저널**: {len(articles_by_journal)}개",
        "",
        "---",
        "",
    ]
    
    total_count = 0
    
    for journal_name, articles in articles_by_journal.items():
        if not articles:
            continue
            
        lines.append(f"## 📖 {journal_name}")
        lines.append("")
        
        for art in articles:
            total_count += 1
            title = art["title"]
            authors = art["authors"]
            date = art["date"]
            link = art["link"]
            abstract = art.get("abstract", "")
            
            # 논문 항목
            if link:
                lines.append(f"### [{title}]({link})")
            else:
                lines.append(f"### {title}")
            
            lines.append(f"- **저자**: {authors}")
            lines.append(f"- **발행일**: {date}")
            
            if art.get("volume"):
                vol_info = f"Vol. {art['volume']}"
                if art.get("issue"):
                    vol_info += f", No. {art['issue']}"
                lines.append(f"- **권호**: {vol_info}")
            
            if abstract:
                lines.append(f"- **초록**: {abstract}")
            
            lines.append("")
        
        lines.append("---")
        lines.append("")
    
    # 요약 통계
    lines.insert(7, f"> **수집 논문**: {total_count}편")
    
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════
# 🚀 MAIN
# ═══════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="스밀조의 신학 저널 수집기 (Crossref API)"
    )
    parser.add_argument(
        "--months", "-m", 
        type=int, 
        default=1,
        help="수집할 기간 (개월, 기본값: 1, start/end 지정 시 무시됨)"
    )
    parser.add_argument(
        "--start",
        type=str,
        help="수집 시작 날짜 (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--end",
        type=str,
        help="수집 종료 날짜 (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--max", 
        type=int, 
        default=20,
        help="저널당 최대 논문 수 (기본값: 20)"
    )
    args = parser.parse_args()
    
    # 기간 계산
    if args.start and args.end:
        from_date = args.start
        until_date = args.end
        period = f"{from_date}_to_{until_date}"
    else:
        today = datetime.now()
        from_date = (today - timedelta(days=30 * args.months)).strftime("%Y-%m-%d")
        until_date = today.strftime("%Y-%m-%d")
        period = today.strftime("%Y-%m")
    
    print(f"🔧 스밀조의 저널 수집기 v1.1 (Smart Filter)")
    print(f"📅 수집 기간: {from_date} ~ {until_date}")
    print(f"📚 대상 저널: {len(THEOLOGY_JOURNALS)}개")
    print("-" * 50)
    
    client = CrossrefClient()
    articles_by_journal = {}
    problematic_journals = []
    
    for journal in THEOLOGY_JOURNALS:
        name = journal["name"]
        issn = journal["issn"]
        
        print(f"📖 수집 중: {name}...", end=" ", flush=True)
        
        items = client.fetch_recent_articles(issn, from_date, until_date, args.max)
        
        if items:
            articles = [client.extract_article_info(item) for item in items]
            articles_by_journal[name] = articles
            print(f"✅ {len(articles)}편")
        else:
            problematic_journals.append(journal)
            print("⚠️ 0편 또는 오류")
    
    print("-" * 50)
    
    # 마크다운 생성
    report = generate_markdown_report(articles_by_journal, period)
    
    # 파일 저장
    output_path = get_output_path()
    filename = f"저널_다이제스트_{period}.md"
    filepath = output_path / filename
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report)
    
    total = sum(len(arts) for arts in articles_by_journal.values())
    print(f"✅ 완료! 총 {total}편 수집")
    print(f"📁 저장 위치: {filepath}")
    
    if problematic_journals:
        print("\n⚠️ 수집 실패 또는 결과 없음 저널 (수동 확인 필요):")
        for p in problematic_journals:
            print(f"  - {p['name']}")
            if "url" in p:
                print(f"    🔗 Direct Link: {p['url']}")

if __name__ == "__main__":
    main()
