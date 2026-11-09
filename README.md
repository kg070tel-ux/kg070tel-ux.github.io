# 허브 홈페이지

인터넷전화 부가서비스 매장 "허브" 홈페이지 (GitHub Pages).

- 주소: https://kg070tel-ux.github.io
- 수정 방법: `src/` 본문 또는 `site.json`(연락처) 고친 뒤 `python build.py` → 생성된 루트 html을 커밋
- 새 부가서비스 추가: `src/새파일.html` 작성 + `build.py`의 `SERVICES`에 한 줄 추가 → 카드·메뉴 자동
- 카카오톡 링크(`KAKAO`)·사업자번호(`BIZNO`)는 `site.json`에 비어 있으면 화면에서 숨김. 채우고 `python build.py`
