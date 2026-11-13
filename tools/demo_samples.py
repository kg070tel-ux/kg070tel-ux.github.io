# -*- coding: utf-8 -*-
"""
체험 화면(통화녹음·법인폰 관리)용 샘플 데이터와 샘플 녹음 만들기

  python tools/demo_samples.py          → demo-data.js 만들고, 없는 녹음만 기계음성으로 생성
  python tools/demo_samples.py --force  → 녹음도 전부 다시 생성

실제 녹음으로 바꾸려면: audio/ 폴더의 같은 이름 파일(r01.mp3 …)을 덮어쓰고,
아래 각 통화의 "dur"(통화시간 초)만 실제 길이로 고친 뒤 이 스크립트를 다시 돌리면 됨.
(기계음성 생성에는 pip install espeakng-loader 와 ffmpeg 가 필요. 실제 녹음만 쓸 땐 필요 없음)

등장 회사·번호는 전부 가상. 실제 번호와 겹치지 않게 지어낸 것.
"""
import json, os, sys, wave, subprocess, tempfile, ctypes

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO = os.path.join(ROOT, "audio")

# 목소리: 우리 직원(S) / 상대방(C)
F, M = "ko+f3", "ko+m3"

COMPANY = {"name": "허브상사", "tel": "02-1234-5600"}
STAFF = {"201": ("김민지", F), "202": ("이수진", F), "203": ("박준호", M), "204": ("최현우", M)}

# ── 허브레코딩: 사무실 전화 ────────────────────────────────
# kind: 수신/발신/부재중/내선, ext: 내선, peer: 상대번호, name: 거래처(전화번호부)
REC = [
    dict(id="r01", date="2026-11-13", time="15:02", kind="발신", ext="203", peer="010-5521-6042", name="대성물류 기사님", cv=M, lines=[
        ("S", "기사님, 허브상사 박준호입니다. 오늘 오후 납품 건 때문에 전화드렸어요."),
        ("C", "네네, 지금 출발했습니다. 네 시 전에는 도착할 것 같아요."),
        ("S", "아, 다행이네요. 이번엔 정문 말고 뒤쪽 하역장으로 와 주세요."),
        ("C", "뒤쪽 하역장이요. 알겠습니다. 도착하면 전화드릴게요."),
        ("S", "네, 감사합니다. 조심히 오세요."),
    ]),
    dict(id="r02", date="2026-11-13", time="14:37", kind="수신", ext="201", peer="031-855-2990", name="한빛상사", cv=M, lines=[
        ("S", "감사합니다, 허브상사 김민지입니다."),
        ("C", "안녕하세요, 한빛상사인데요. 에이포 복사용지 견적 좀 받고 싶어서요."),
        ("S", "네, 수량은 어느 정도 생각하세요?"),
        ("C", "한 달에 이백 박스 정도요. 매달 정기로 받으려고 합니다."),
        ("S", "이백 박스 정기 납품이면 박스당 이만 이천 원에 맞춰 드릴 수 있어요. 견적서는 메일로 보내 드릴게요."),
        ("C", "네, 좋습니다. 메일 주소는 문자로 보내 드릴게요."),
    ]),
    dict(id="r03", date="2026-11-13", time="14:21", kind="부재중", ext="대표", peer="02-3412-5678", name="세움건축"),
    dict(id="r04", date="2026-11-13", time="13:50", kind="수신", ext="204", peer="010-7784-1203", name="", cv=F, lines=[
        ("S", "허브상사 에이에스 담당 최현우입니다."),
        ("C", "저번 달에 산 복합기가 자꾸 종이가 걸려서요."),
        ("S", "불편하셨겠네요. 모델명이 기기 앞에 적혀 있는데 불러 주시겠어요?"),
        ("C", "에이치에스 삼천이라고 적혀 있어요."),
        ("S", "네, 접수했습니다. 내일 오전에 기사님이 방문드릴게요."),
    ]),
    dict(id="r05", date="2026-11-13", time="11:42", kind="발신", ext="201", peer="02-578-3300", name="세움건축 구매팀", cv=M, lines=[
        ("S", "과장님, 허브상사 김민지입니다. 지난주 통화 때 말씀드린 단가 건으로 연락드렸어요."),
        ("C", "아, 네. 박스당 이만 삼천 원으로 하기로 했었죠?"),
        ("S", "네 맞아요. 그 단가로 이번 달 말까지 발주 주시면 됩니다."),
        ("C", "알겠습니다. 다음 주 월요일에 발주서 보낼게요."),
    ]),
    dict(id="r06", date="2026-11-13", time="11:05", kind="내선", ext="201", peer="내선 202", name="이수진 (경리)", cv=F, lines=[
        ("S", "수진 씨, 영업팀 김민지예요. 한빛상사 세금계산서 오늘 발행 가능할까요?"),
        ("C", "네, 오후에 일괄 발행하니까 그때 같이 끊을게요."),
        ("S", "고마워요. 금액은 메신저로 보내 둘게요."),
    ]),
    dict(id="r07", date="2026-11-13", time="10:18", kind="수신", ext="202", peer="031-922-4410", name="그린마트", cv=M, lines=[
        ("S", "허브상사 경리팀 이수진입니다."),
        ("C", "그린마트입니다. 어제 대금 입금했는데 확인 부탁드리려고요."),
        ("S", "잠시만요. 네, 어제 오후 세 시에 백이십만 원 입금 확인됐습니다."),
        ("C", "아 네, 감사합니다."),
    ]),
    dict(id="r08", date="2026-11-13", time="09:47", kind="발신", ext="204", peer="010-3398-7720", name="", cv=F, lines=[
        ("S", "안녕하세요, 허브상사 최현우입니다. 오늘 오후 두 시 방문 예정이었는데요."),
        ("C", "네, 맞아요."),
        ("S", "앞 일정이 늦어져서 세 시로 옮겨도 괜찮으실까요?"),
        ("C", "세 시도 괜찮아요. 오시기 전에 전화만 한 번 주세요."),
    ]),
    dict(id="r09", date="2026-11-12", time="17:31", kind="수신", ext="201", peer="02-6248-1190", name="", cv=M, lines=[
        ("S", "감사합니다, 허브상사 김민지입니다."),
        ("C", "홈페이지 보고 연락드렸는데요, 사무용품 거래처를 바꿔 볼까 해서요."),
        ("S", "네, 반갑습니다. 직원분은 몇 분 정도 계세요?"),
        ("C", "삼십 명 정도요. 복사용지랑 토너가 제일 많이 들어가요."),
        ("S", "그럼 내일 오전에 품목표랑 단가표 들고 찾아뵐게요."),
    ]),
    dict(id="r10", date="2026-11-12", time="16:08", kind="발신", ext="203", peer="031-544-8800", name="우진택배", cv=F, lines=[
        ("S", "우진택배죠? 허브상사 박준호입니다. 반품 회수 요청하려고요."),
        ("C", "네, 회수 주소 말씀해 주세요."),
        ("S", "저희 창고에서 열 박스입니다. 내일 오전에 와 주실 수 있나요?"),
        ("C", "내일 오전 열한 시쯤 기사님 보내 드릴게요."),
    ]),
    dict(id="r11", date="2026-11-12", time="15:20", kind="수신", ext="202", peer="02-2287-0450", name="명성인쇄", cv=M, lines=[
        ("S", "허브상사 이수진입니다."),
        ("C", "명성인쇄입니다. 이번 달 결제일이 언제인지 여쭤보려고요."),
        ("S", "매달 이십오 일에 지급하고 있어요. 이번 달도 이십오 일에 들어갑니다."),
        ("C", "네, 확인 감사합니다."),
    ]),
]

# ── 허브모바일: 법인폰 ────────────────────────────────────
PHONES = {"박 대리": ("010-2201-3301", M, "영업1팀"), "김 팀장": ("010-2201-3302", M, "영업1팀"), "이 주임": ("010-2201-3303", F, "TM팀")}

MOB = [
    dict(id="m01", date="2026-11-13", time="16:10", kind="부재중", phone="박 대리", peer="02-578-3300", name="세움건축", state="미응대"),
    dict(id="m02", date="2026-11-13", time="15:32", kind="발신", phone="김 팀장", peer="031-855-2990", name="한빛상사", cv=M, note="부재중 회신", lines=[
        ("S", "한빛상사죠? 허브상사 김 팀장입니다. 아까 박 대리한테 전화 주셨다고 해서요."),
        ("C", "아, 네. 다음 주 납품 수량을 좀 늘리고 싶어서요."),
        ("S", "얼마나 더 필요하세요?"),
        ("C", "오십 박스 정도 추가해 주세요."),
        ("S", "네, 반영해서 수정 견적 다시 보내 드리겠습니다."),
    ]),
    dict(id="m03", date="2026-11-13", time="15:05", kind="부재중", phone="박 대리", peer="031-855-2990", name="한빛상사", state="처리됨", note="김 팀장이 15:32에 회신"),
    dict(id="m04", date="2026-11-13", time="14:12", kind="수신", phone="이 주임", peer="010-4410-2387", name="", cv=M, lines=[
        ("S", "네, 허브상사 이 주임입니다."),
        ("C", "아까 문자 받고 연락드렸어요. 정수기 렌탈 상담받고 싶은데요."),
        ("S", "네, 사무실에서 쓰실 거예요, 가정에서 쓰실 거예요?"),
        ("C", "사무실이요. 열 명 정도 써요."),
        ("S", "그럼 냉온수 스탠드형이 맞으실 것 같아요. 견적 문자로 보내 드릴게요."),
    ]),
    dict(id="m05", date="2026-11-13", time="13:58", kind="문자수신", phone="박 대리", peer="010-5521-6042", name="대성물류 기사님", text="내일 오전 납품 가능합니다. 9시까지 도착 예정입니다."),
    dict(id="m06", date="2026-11-13", time="13:40", kind="발신", phone="이 주임", peer="010-6623-0915", name="", cv=F, lines=[
        ("S", "안녕하세요, 허브상사 이 주임입니다. 지난주 정수기 상담 신청하셔서 연락드렸어요."),
        ("C", "아, 네. 지금 운전 중이라서요. 한 시간 뒤에 다시 전화 주시겠어요?"),
        ("S", "네, 그럼 세 시쯤 다시 연락드릴게요."),
    ]),
    dict(id="m07", date="2026-11-13", time="11:20", kind="발신", phone="박 대리", peer="010-5521-6042", name="대성물류 기사님", cv=M, lines=[
        ("S", "기사님, 허브상사 박 대리입니다. 내일 납품 가능하신지 여쭤보려고요."),
        ("C", "확인해 보고 오후에 문자 드릴게요."),
        ("S", "네, 기다리겠습니다."),
    ]),
    dict(id="m08", date="2026-11-13", time="10:45", kind="문자발신", phone="김 팀장", peer="02-578-3300", name="세움건축", text="과장님, 요청하신 견적서 메일로 보내드렸습니다. 확인 부탁드립니다. - 허브상사 김 팀장"),
    dict(id="m09", date="2026-11-13", time="10:02", kind="수신", phone="김 팀장", peer="02-6248-1190", name="", cv=M, lines=[
        ("S", "네, 허브상사 김 팀장입니다."),
        ("C", "어제 사무실로 전화드렸던 회사인데요, 미팅 시간을 잡고 싶어서요."),
        ("S", "네, 목요일 오전 열 시 어떠세요?"),
        ("C", "좋습니다. 그때 뵙겠습니다."),
    ]),
    dict(id="m10", date="2026-11-12", time="17:40", kind="발신", phone="이 주임", peer="010-8851-4420", name="", cv=F, lines=[
        ("S", "안녕하세요, 허브상사 이 주임입니다. 정수기 필터 교체 시기가 돼서 안내드리려고요."),
        ("C", "아, 벌써 그렇게 됐나요? 언제 오시는데요?"),
        ("S", "이번 주 금요일 오후에 방문 가능합니다."),
        ("C", "네, 금요일 좋아요."),
    ]),
]


# ── 기계음성 생성 ────────────────────────────────────────
class TTS:
    def __init__(self):
        import espeakng_loader as e
        self.lib = ctypes.CDLL(e.get_library_path())
        self.buf = []
        CB = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.POINTER(ctypes.c_short), ctypes.c_int, ctypes.c_void_p)

        def cb(wav, n, ev):
            if wav and n > 0:
                self.buf.append(ctypes.string_at(wav, n * 2))
            return 0
        self._cb = CB(cb)
        self.sr = self.lib.espeak_Initialize(1, 500, e.get_data_path().encode(), 0)
        self.lib.espeak_SetSynthCallback(self._cb)

    def say(self, text, voice, pitch):
        self.buf.clear()
        self.lib.espeak_SetVoiceByName(voice.encode())
        self.lib.espeak_SetParameter(1, 160, 0)    # 속도
        self.lib.espeak_SetParameter(3, pitch, 0)  # 높낮이
        b = text.encode("utf-8")
        self.lib.espeak_Synth(b, len(b) + 1, 0, 0, 0, 1, None, None)
        self.lib.espeak_Synchronize()
        return b"".join(self.buf)


def make_audio(tts, item, sv, cv):
    gap = b"\x00\x00" * int(tts.sr * 0.45)
    pcm = gap
    for who, text in item["lines"]:
        voice, pitch = (sv, 52) if who == "S" else (cv, 38 if cv == M else 62)
        pcm += tts.say(text, voice, pitch) + gap
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as t:
        tmp = t.name
    with wave.open(tmp, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(tts.sr); w.writeframes(pcm)
    out = os.path.join(AUDIO, item["id"] + ".mp3")
    # 전화 소리처럼: 300~3400Hz 대역, 8kHz로 한 번 낮췄다가 16kHz mp3로 저장
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-af",
                    "highpass=f=300,lowpass=f=3400,aresample=8000,aresample=16000,volume=1.6",
                    "-ac", "1", "-ar", "16000", "-b:a", "32k", out], check=True)
    os.unlink(tmp)


def duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True)
    return round(float(r.stdout.strip() or 0))


def main():
    force = "--force" in sys.argv
    os.makedirs(AUDIO, exist_ok=True)
    tts = None
    for item, sv in [(x, STAFF[x["ext"]][1]) for x in REC if "lines" in x] + \
                    [(x, PHONES[x["phone"]][1]) for x in MOB if "lines" in x]:
        path = os.path.join(AUDIO, item["id"] + ".mp3")
        if force or not os.path.exists(path):
            tts = tts or TTS()
            make_audio(tts, item, sv, item["cv"])
            print("녹음 생성:", item["id"])
        item["dur"] = item.get("dur") or duration(path)

    def clean(x):
        return {k: v for k, v in x.items() if k not in ("lines", "cv")}
    rec = [dict(clean(x), staff=STAFF.get(x["ext"], ("대표번호",))[0]) for x in REC]
    mob = [dict(clean(x), team=PHONES[x["phone"]][2], phoneNo=PHONES[x["phone"]][0]) for x in MOB]
    data = {"company": COMPANY, "rec": rec, "mob": mob,
            "phones": [{"name": k, "no": v[0], "team": v[2]} for k, v in PHONES.items()]}
    js = "/* tools/demo_samples.py 가 만드는 파일. 직접 고치지 말 것 */\nwindow.HUB_DEMO = " + \
         json.dumps(data, ensure_ascii=False, indent=1) + ";\n"
    open(os.path.join(ROOT, "demo-data.js"), "w", encoding="utf-8").write(js)
    print("만듦: demo-data.js")


if __name__ == "__main__":
    main()
