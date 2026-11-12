# -*- coding: utf-8 -*-
"""
허브콜 홈페이지 빌드: src/ 본문 + _layout.html + site.json(연락처) → 루트에 html 생성

새 부가서비스 추가 (2단계):
  1) src/새파일.html 작성 (recording.html 을 복사해서 고치면 편함)
  2) 아래 SERVICES 에 한 줄 추가 → python build.py
     → 첫 화면·부가서비스 목록의 카드와 메뉴 표시가 자동으로 붙음
"""
import json, os, re, datetime, html as H

ROOT = os.path.dirname(os.path.abspath(__file__))

# 부가서비스 (허브콜 자체 서비스): 파일, 이름, 한 줄 설명, 카드 본문, 특징 2~3개, 아이콘
SERVICES = [
    ("recording.html", "허브레코딩", "사무실 통화 자동 녹음",
     "KT·LG U+·SK브로드밴드 인터넷전화 모두, 사무실 모든 통화를 자동으로 녹음합니다. 전화기 대수와 상관없이 월 정액입니다.",
     ["녹음은 회사 PC에 영구 보관", "번호·날짜로 찾아 바로 듣기", "인터넷전화 20회선 이상 함께 가입 시 무료"], "rec"),
    ("mobile.html", "허브모바일", "법인폰·TM폰 통화·문자 관리",
     "영업용 법인폰, 휴대폰으로 일하는 TM폰의 통화 기록·통화 녹음·문자를 회사 PC 한 곳에 모읍니다.",
     ["회신 안 한 부재중을 빨간색으로", "퇴사·담당 변경 때 이력 그대로 인계", "업무시간만 수집, 개인 번호 제외"], "mob"),
    ("holiday.html", "휴무 안내", "휴무일 안내 멘트·착신전환",
     "회사 휴무일·창립기념일·연휴에 안내 멘트를 걸어 두고, 급한 전화는 담당자 휴대폰으로 돌려 드립니다.",
     ["휴무 안내 멘트 제작", "정해진 날짜에만 자동 적용", "담당자 휴대폰으로 착신전환"], "cal"),
    ("night.html", "야간 응대", "퇴근 후 ARS·AI 응대",
     "퇴근 후 걸려 온 전화를 ARS와 AI가 대신 받아 용건을 남겨 둡니다.",
     ["업무시간 후 자동 ARS 전환", "건 사람 번호·용건 기록"], "moon", "출시 예정"),
]

# 페이지: 파일, 메뉴 그룹, 제목, 설명, 상담 제목
PAGES = [
    ("index.html", None, "허브콜 — 사무실 통화녹음·법인폰 관리, 3사 인터넷전화",
     "인터넷전화 부가서비스를 직접 만드는 허브콜. 사무실 통화 자동 녹음(허브레코딩), 법인폰 통화·문자 관리(허브모바일), KT·LG U+·SK브로드밴드 기업 인터넷·전화, 보안, 랜공사.", "설치 상담"),
    ("phone.html", "tel", "기업 인터넷·전화 — KT·LG U+·SK브로드밴드 비교 상담 | 허브콜",
     "사무실 인터넷과 인터넷전화를 3사 모두 비교해서 안내합니다. 신규·이전·재약정, 랜공사 지원, 전화기 무료 조건까지.", "인터넷·전화 상담"),
    ("lg.html", "tel", "LG U+ 기업 인터넷·전화 — 오피스넷·자유통화 요금 | 허브콜",
     "LG U+ 오피스넷 기가 인터넷과 기업070 자유통화 요금, 무료 전화기, 녹취·ARS 포함 조건, DCS, 랜공사 지원 안내 (VAT 별도).", "LG U+ 상담"),
    ("sk.html", "tel", "SK브로드밴드 기업 인터넷·전화 — Biz인터넷·정액제 요금 | 허브콜",
     "SK브로드밴드 Biz인터넷과 기업 인터넷전화 정액제 요금, IP 2개 기본 제공, 전화기 가격 안내 (VAT 별도).", "SK브로드밴드 상담"),
    ("kt.html", "tel", "KT 기업 인터넷·전화 상담 | 허브콜",
     "KT 기업 인터넷과 사무실 인터넷전화 재약정·이전·신규 상담.", "KT 상담"),
    ("security.html", "sec", "사무실 보안 — UTM·PC 백신·랜섬웨어 차단 | 허브콜",
     "개인정보 유출 사고와 2026년 9월 개정 개인정보보호법. UTM과 PC 백신이 왜 필요한지 쉽게 설명하고 사무실 규모에 맞춰 안내합니다.", "보안 상담"),
    ("lan.html", "lan", "랜공사 — 사무실 랜 배선·단자함 정리·와이파이 | 허브콜",
     "사무실·학교 랜 배선, 랜포트 추가·이동, 통신 단자함 정리, 와이파이 AP 설치. 현장 확인 후 견적.", "랜공사 상담"),
    ("cases.html", "case", "시공 사례 — 허브콜",
     "허브콜이 인터넷·전화·랜공사·와이파이를 설치한 실제 현장.", "설치 상담"),
    ("services.html", "svc", "부가서비스 — 허브콜 자체 서비스",
     "허브콜이 직접 만들어 설치·관리하는 사무실 전화 부가서비스. 허브레코딩, 허브모바일, 휴무 안내, 야간 응대.", "부가서비스 상담"),
    ("privacy.html", None, "개인정보 처리방침 — 허브콜",
     "(주)케이지앤아이피 개인정보 처리방침", "상담 문의"),
] + [(f, {"recording.html": "rec", "mobile.html": "mob"}.get(f, "svc"), f"{n} — {d} | 허브콜", body, f"{n} 상담")
     for f, n, d, body, *_ in SERVICES]

# 옛 주소 → 새 주소 (예전 링크가 깨지지 않게)
REDIRECTS = {"voip.html": "phone.html", "internet.html": "phone.html"}

NAV = [("recording.html", "rec", "통화녹음"), ("mobile.html", "mob", "법인폰 관리"), ("phone.html", "tel", "인터넷·전화"),
       ("security.html", "sec", "보안"), ("lan.html", "lan", "랜공사"), ("cases.html", "case", "시공사례"), ("#contact", None, "상담신청")]

ICONS = {
    "rec": '<path d="M12 3a3 3 0 0 0-3 3v6a3 3 0 0 0 6 0V6a3 3 0 0 0-3-3Z"/><path d="M19 11a7 7 0 0 1-14 0M12 18v3"/>',
    "mob": '<rect x="7" y="2.5" width="10" height="19" rx="2.5"/><path d="M11 18.5h2"/>',
    "cal": '<rect x="3.5" y="5" width="17" height="15.5" rx="2.5"/><path d="M3.5 10h17M8 3v4M16 3v4"/>',
    "moon": '<path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5Z"/>',
}


def svc_cards(link_text="자세히 보기"):
    out = []
    for f, n, d, body, feats, ic, *opt in SERVICES:
        tag = opt[0] if opt else "허브콜 자체 서비스"
        li = "".join(f"<li>{H.escape(x)}</li>" for x in feats)
        out.append(f'''      <a class="svc-card" href="{f}">
        <span class="ico"><svg viewBox="0 0 24 24" aria-hidden="true">{ICONS.get(ic, "")}</svg></span>
        <span class="tag-own">{tag}</span>
        <h3>{n}</h3><p class="sub">{d}</p>
        <p>{body}</p>
        <ul>{li}</ul>
        <span class="more">{link_text}</span>
      </a>''')
    return "\n".join(out)


PRODUCTS = ["통화녹음 (허브레코딩)", "법인폰 관리 (허브모바일)", "인터넷·전화 (LG U+·SK·KT)",
            "보안 (UTM·PC 백신)", "랜공사·와이파이", "휴무 안내", "기타"]


def consult_form(pid, card=True):
    opts = "".join(f'<option>{p}</option>' for p in PRODUCTS)
    inner = f'''<form class="consult" novalidate>
        <label for="{pid}-name">이름</label>
        <input id="{pid}-name" name="name" autocomplete="name" placeholder="이름 또는 회사명" required>
        <label for="{pid}-phone">연락처</label>
        <input id="{pid}-phone" name="phone" type="tel" inputmode="tel" autocomplete="tel" placeholder="010-0000-0000" required>
        <div class="row2">
          <div><label for="{pid}-time">희망 시간</label>
          <select id="{pid}-time" name="time"><option>언제든 가능</option><option>오전 (09–12시)</option><option>오후 (13–18시)</option></select></div>
          <div><label for="{pid}-product">관심 상품</label>
          <select id="{pid}-product" name="product">{opts}</select></div>
        </div>
        <label class="agree"><input type="checkbox" name="agree"> 개인정보 수집·이용에 동의합니다 <a href="privacy.html" target="_blank">[보기]</a></label>
        <button type="submit" class="btn block">상담 예약하기</button>
        <p class="form-msg" role="status" aria-live="polite"></p>
      </form>'''
    if not card:
        return "    " + inner
    return f'''      <div class="form-card">
        <p class="form-title">상담 예약</p>
        {inner}
      </div>'''


def main():
    site = json.load(open(os.path.join(ROOT, "site.json"), encoding="utf-8"))
    layout = open(os.path.join(ROOT, "src", "_layout.html"), encoding="utf-8").read()
    cards = svc_cards()
    for fn, grp, title, desc, ctitle in PAGES:
        cur = ' aria-current="page"'
        nav = "\n".join(
            f'      <a href="{f}"{cur if g and g == grp else ""}>{m}</a>' for f, g, m in NAV)
        body = open(os.path.join(ROOT, "src", fn), encoding="utf-8").read()
        html = (layout.replace("{{BODY}}", body).replace("{{NAV}}", nav).replace("{{SERVICE_CARDS}}", cards)
                .replace("{{CONSULT_FORM}}", consult_form("cf")).replace("{{CONSULT_FORM_MODAL}}", consult_form("mf", card=False)))
        # site.json 에서 비워 둔 항목은 화면에서 뺌 (카카오톡 링크·사업자번호는 받으면 채우기)
        if not site.get("KAKAO"):
            html = re.sub(r'\s*<a[^>]*href="\{\{KAKAO\}\}"[^>]*>[^<]*</a>', "", html)
        if not site.get("BIZNO"):
            html = re.sub(r'<span>사업자등록번호 \{\{BIZNO\}\}</span>', "", html)
        vals = dict(site, TITLE=title, DESC=desc, CONTACT_TITLE=ctitle, MONTH=f"{datetime.date.today().month}월",
                    FILE_URL="" if fn == "index.html" else fn)
        for k, v in vals.items():
            html = html.replace("{{" + k + "}}", v)
        open(os.path.join(ROOT, fn), "w", encoding="utf-8").write(html)
        print("만듦:", fn)
    for old, new in REDIRECTS.items():
        open(os.path.join(ROOT, old), "w", encoding="utf-8").write(
            f'<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0; url={new}">'
            f'<link rel="canonical" href="{site["SITE_URL"]}/{new}"><a href="{new}">이동</a>\n')
        print("옮김:", old, "→", new)
    today = datetime.date.today().isoformat()
    urls = "".join(f"<url><loc>{site['SITE_URL']}/{'' if f == 'index.html' else f}</loc><lastmod>{today}</lastmod></url>"
                   for f, *_ in PAGES)
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write(
        f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8").write(
        f"User-agent: *\nAllow: /\nSitemap: {site['SITE_URL']}/sitemap.xml\n")


if __name__ == "__main__":
    main()
