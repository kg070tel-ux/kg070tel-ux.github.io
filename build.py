# -*- coding: utf-8 -*-
"""
허브 홈페이지 빌드: src/ 본문 + _layout.html + site.json(연락처) → 루트에 html 생성

새 부가서비스 추가 (2단계):
  1) src/새파일.html 작성 (recording.html 을 복사해서 고치면 편함)
  2) 아래 SERVICES 에 한 줄 추가 → python build.py
     → 첫 화면·부가서비스 목록의 카드와 메뉴 표시가 자동으로 붙음
"""
import json, os, re, datetime, html as H

ROOT = os.path.dirname(os.path.abspath(__file__))

# 부가서비스 (허브 자체 서비스): 파일, 이름, 한 줄 설명, 카드 본문, 특징 2~3개, 아이콘
SERVICES = [
    ("recording.html", "허브레코딩", "사무실 통화 자동 녹취",
     "사무실 모든 인터넷전화 통화를 자동으로 녹음합니다. 전화기마다 따로 설정할 필요가 없습니다.",
     ["녹음 파일은 회사 PC에만 저장", "번호·날짜로 찾아 바로 듣기", "부재중 확인과 회신 관리"], "rec"),
    ("mobile.html", "허브모바일", "법인폰 통화·문자 관리",
     "직원에게 지급한 갤럭시 법인폰의 통화 기록, 통화 녹음, 문자를 회사 PC 한 곳에 모읍니다.",
     ["회신 안 한 부재중을 빨간색으로", "퇴사·담당 변경 때 이력 그대로 인계", "업무시간만 수집, 개인 번호 제외"], "mob"),
]

# 페이지: 파일, 메뉴 그룹, 제목, 설명, 상담 제목
PAGES = [
    ("index.html", None, "허브 — 기업 인터넷전화와 통화 녹취·법인폰 관리",
     "기업 인터넷전화(SK브로드밴드 공식 대리점) 개통·이전·재약정 상담과 설치, 허브 자체 부가서비스 허브레코딩(통화 자동 녹취)·허브모바일(법인폰 통화·문자 관리).", "설치 상담"),
    ("voip.html", "voip", "기업 인터넷전화 — 허브 (SK브로드밴드 공식 대리점)",
     "사무실 070 기업 인터넷전화 신규·이전·재약정·통신사 변경. 대표번호, 내선, 착신전환 설정과 전화기·랜 공사까지 한 번에.", "기업 인터넷전화 상담"),
    ("services.html", "svc", "부가서비스 — 허브 자체 서비스",
     "허브가 직접 만들어 설치·관리하는 사무실 전화 부가서비스. 허브레코딩, 허브모바일.", "부가서비스 상담"),
] + [(f, "svc", f"{n} — {d} | 허브", body, f"{n} 상담") for f, n, d, body, *_ in SERVICES]

NAV = [("voip.html", "voip", "기업인터넷전화"), ("services.html", "svc", "부가서비스"), ("#contact", None, "상담신청")]

ICONS = {
    "rec": '<path d="M12 3a3 3 0 0 0-3 3v6a3 3 0 0 0 6 0V6a3 3 0 0 0-3-3Z"/><path d="M19 11a7 7 0 0 1-14 0M12 18v3"/>',
    "mob": '<rect x="7" y="2.5" width="10" height="19" rx="2.5"/><path d="M11 18.5h2"/>',
}


def svc_cards(link_text="자세히 보기"):
    out = []
    for f, n, d, body, feats, ic in SERVICES:
        li = "".join(f"<li>{H.escape(x)}</li>" for x in feats)
        out.append(f'''      <a class="svc-card" href="{f}">
        <span class="ico"><svg viewBox="0 0 24 24" aria-hidden="true">{ICONS.get(ic, "")}</svg></span>
        <span class="tag-own">허브 자체 서비스</span>
        <h3>{n}</h3><p class="sub">{d}</p>
        <p>{body}</p>
        <ul>{li}</ul>
        <span class="more">{link_text}</span>
      </a>''')
    out.append('''      <div class="svc-card soon">
        <span class="tag-own">준비 중</span>
        <h3>새 서비스 준비 중</h3>
        <p>사무실 전화를 더 편하게 쓰는 부가서비스를 계속 추가합니다.</p>
      </div>''')
    return "\n".join(out)


def main():
    site = json.load(open(os.path.join(ROOT, "site.json"), encoding="utf-8"))
    layout = open(os.path.join(ROOT, "src", "_layout.html"), encoding="utf-8").read()
    cards = svc_cards()
    for fn, grp, title, desc, ctitle in PAGES:
        cur = ' aria-current="page"'
        nav = "\n".join(
            f'      <a href="{f}"{cur if g and g == grp else ""}>{m}</a>' for f, g, m in NAV)
        body = open(os.path.join(ROOT, "src", fn), encoding="utf-8").read()
        html = layout.replace("{{BODY}}", body).replace("{{NAV}}", nav).replace("{{SERVICE_CARDS}}", cards)
        # site.json 에서 비워 둔 항목은 화면에서 뺌 (카카오톡 링크·사업자번호는 받으면 채우기)
        if not site.get("KAKAO"):
            html = re.sub(r'\s*<a[^>]*href="\{\{KAKAO\}\}"[^>]*>[^<]*</a>', "", html)
        if not site.get("BIZNO"):
            html = re.sub(r'<span>사업자등록번호 \{\{BIZNO\}\}</span>', "", html)
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
