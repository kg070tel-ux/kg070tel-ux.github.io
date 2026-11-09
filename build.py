# -*- coding: utf-8 -*-
"""
허브 홈페이지 빌드: src/ 의 본문 + _layout.html + site.json(연락처) → 루트에 html 생성
새 서비스 추가: src/새파일.html 만들고 아래 PAGES에 한 줄 추가 → python build.py
"""
import json, os, datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
PAGES = [
    # (파일, 메뉴 이름(None=메뉴에 없음), 제목, 설명, 상담 제목)
    ("index.html", None, "허브 — 사무실 인터넷전화와 통화 녹취, 법인폰 관리",
     "경기북부 사무실 인터넷전화(LG U+) 설치, 통화 자동 녹취(허브레코딩), 법인폰 통화·문자 관리(허브모바일). 의정부에서 직접 방문 설치합니다.", "설치 상담"),
    ("voip.html", "인터넷전화", "인터넷전화 설치 — 허브 (LG U+ 공식 대리점)",
     "사무실 070 인터넷전화 신규·이사·재약정·통신사 변경. 대표번호, 내선, 착신전환 설정과 전화기·랜 공사까지 한 번에.", "인터넷전화 상담"),
    ("recording.html", "허브레코딩", "허브레코딩 — 사무실 인터넷전화 통화 자동 녹취",
     "사무실 모든 인터넷전화 통화를 자동 녹음. 녹음 파일은 회사 PC에만 저장하고 번호·날짜로 찾아 바로 듣습니다.", "허브레코딩 상담"),
    ("mobile.html", "허브모바일", "허브모바일 — 법인폰 통화·문자·녹음 관리",
     "직원 갤럭시 법인폰의 통화 기록, 통화 녹음, 문자를 회사 PC 한 곳에. 미응대 부재중 표시와 퇴사 시 거래처 이력 인계.", "허브모바일 시연 신청"),
]


def main():
    site = json.load(open(os.path.join(ROOT, "site.json"), encoding="utf-8"))
    layout = open(os.path.join(ROOT, "src", "_layout.html"), encoding="utf-8").read()
    for fn, menu, title, desc, ctitle in PAGES:
        cur = ' aria-current="page"'
        nav = "\n".join(
            f'      <a href="{f}"{cur if f == fn else ""}>{m}</a>'
            for f, m, *_ in PAGES if m)
        body = open(os.path.join(ROOT, "src", fn), encoding="utf-8").read()
        html = layout.replace("{{BODY}}", body).replace("{{NAV}}", nav)
        vals = dict(site, TITLE=title, DESC=desc, CONTACT_TITLE=ctitle,
                    FILE_URL="" if fn == "index.html" else fn)
        for k, v in vals.items():
            html = html.replace("{{" + k + "}}", v)
        open(os.path.join(ROOT, fn), "w", encoding="utf-8").write(html)
        print("만듦:", fn)
    today = datetime.date.today().isoformat()
    urls = "".join(f"<url><loc>{site['SITE_URL']}/{'' if f == 'index.html' else f}</loc><lastmod>{today}</lastmod></url>"
                   for f, *_ in PAGES)
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write(
        f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8").write(
        f"User-agent: *\nAllow: /\nSitemap: {site['SITE_URL']}/sitemap.xml\n")


if __name__ == "__main__":
    main()
