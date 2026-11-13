/* 통화녹음·법인폰 관리 체험 화면. 데이터는 demo-data.js (tools/demo_samples.py 가 만듦) */
(function () {
  var D = window.HUB_DEMO;
  if (!D) return;
  var player = new Audio();
  player.preload = "none";
  var playing = null; // {btn, bar, id}

  function el(tag, cls, html) { var e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; }
  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function mmss(s) { s = Math.round(s || 0); return Math.floor(s / 60) + ":" + ("0" + (s % 60)).slice(-2); }
  function md(d) { var p = d.split("-"); return +p[1] + "/" + +p[2]; }
  function digits(s) { return String(s || "").replace(/[^0-9]/g, ""); }
  function fileName(x, who) { return x.date.replace(/-/g, "") + "_" + x.time.replace(":", "") + "_" + x.kind + "_" + who + "_" + (digits(x.peer) || x.peer) + ".mp3"; }

  function stop() {
    if (!playing) return;
    player.pause();
    playing.btn.classList.remove("on"); playing.btn.setAttribute("aria-label", "듣기");
    playing.row.classList.remove("now");
    playing = null;
  }
  player.addEventListener("timeupdate", function () {
    if (!playing || !player.duration) return;
    playing.bar.style.width = (player.currentTime / player.duration * 100) + "%";
    playing.time.textContent = mmss(player.currentTime) + " / " + mmss(player.duration);
  });
  player.addEventListener("ended", function () { if (playing) { playing.bar.style.width = "0"; playing.time.textContent = mmss(playing.dur); } stop(); });

  function playBtn(x, row) {
    var wrap = el("span", "d-play");
    var btn = el("button", "d-btn play"); btn.type = "button"; btn.setAttribute("aria-label", "듣기");
    var track = el("span", "d-track"); var bar = el("i"); track.appendChild(bar);
    var time = el("span", "d-time", mmss(x.dur));
    btn.addEventListener("click", function () {
      if (playing && playing.id === x.id) {
        if (player.paused) { player.play(); btn.classList.add("on"); } else { player.pause(); btn.classList.remove("on"); }
        return;
      }
      stop();
      player.src = "audio/" + x.id + ".mp3";
      player.play().catch(function () {});
      playing = { id: x.id, btn: btn, bar: bar, time: time, row: row, dur: x.dur };
      btn.classList.add("on"); btn.setAttribute("aria-label", "일시정지"); row.classList.add("now");
    });
    track.addEventListener("click", function (e) {
      if (!playing || playing.id !== x.id || !player.duration) return;
      var r = track.getBoundingClientRect();
      player.currentTime = Math.max(0, Math.min(1, (e.clientX - r.left) / r.width)) * player.duration;
    });
    wrap.appendChild(btn); wrap.appendChild(track); wrap.appendChild(time);
    return wrap;
  }
  function saveBtn(x, who) {
    var a = el("a", "d-btn save"); a.href = "audio/" + x.id + ".mp3"; a.setAttribute("download", fileName(x, who));
    a.setAttribute("aria-label", "녹음 파일 저장"); a.title = "녹음 파일 저장";
    return a;
  }
  function csv(rows, name) {
    var text = "﻿" + rows.map(function (r) { return r.map(function (c) { return '"' + String(c).replace(/"/g, '""') + '"'; }).join(","); }).join("\r\n");
    var a = el("a"); a.href = URL.createObjectURL(new Blob([text], { type: "text/csv;charset=utf-8" })); a.download = name;
    document.body.appendChild(a); a.click(); setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 500);
  }
  function chips(list, onPick) {
    var box = el("div", "d-chips");
    list.forEach(function (c, i) {
      var b = el("button", i ? "" : "on", esc(c.label)); b.type = "button"; b.dataset.v = c.v;
      b.addEventListener("click", function () { box.querySelectorAll("button").forEach(function (o) { o.classList.remove("on"); }); b.classList.add("on"); onPick(c.v); });
      box.appendChild(b);
    });
    return box;
  }
  function frame(root, title, statusText) {
    var app = el("div", "d-app");
    app.innerHTML = '<div class="d-bar"><span class="d-dots" aria-hidden="true"><i></i><i></i><i></i></span><b>' + esc(title) +
      '</b><span class="d-ok"><i aria-hidden="true"></i>' + esc(statusText) + '</span></div>';
    root.appendChild(app);
    return app;
  }
  var KCLS = { "수신": "in", "발신": "out", "부재중": "miss", "내선": "ext", "문자수신": "sms", "문자발신": "sms" };

  // ── 허브레코딩 ──
  function rec(root) {
    var st = { day: "", kind: "", q: "" };
    var days = []; D.rec.forEach(function (x) { if (days.indexOf(x.date) < 0) days.push(x.date); });
    var app = frame(root, "허브레코딩", "녹취 정상 작동 중");
    var tool = el("div", "d-tool");
    var sel = el("select", "d-sel"); sel.setAttribute("aria-label", "날짜");
    sel.innerHTML = '<option value="">전체 기간</option>' + days.map(function (d) { return '<option value="' + d + '">' + md(d) + '</option>'; }).join("");
    sel.addEventListener("change", function () { st.day = sel.value; draw(); });
    var q = el("input", "d-q"); q.type = "search"; q.placeholder = "번호·이름·내선 검색 (예: 6042, 한빛, 201)"; q.setAttribute("aria-label", "검색");
    q.addEventListener("input", function () { st.q = q.value.trim(); draw(); });
    var xl = el("button", "d-xl", "목록 엑셀 저장"); xl.type = "button";
    tool.appendChild(sel); tool.appendChild(q); tool.appendChild(xl);
    var ch = chips([{ label: "전체", v: "" }, { label: "수신", v: "수신" }, { label: "발신", v: "발신" }, { label: "부재중", v: "부재중" }, { label: "내선", v: "내선" }], function (v) { st.kind = v; draw(); });
    var sum = el("p", "d-sum");
    var head = el("div", "d-row d-head rec", "<span>일시</span><span>구분</span><span>내선 · 직원</span><span>상대번호</span><span>녹음</span><span></span>");
    var list = el("div", "d-list");
    app.appendChild(tool); app.appendChild(ch); app.appendChild(sum); app.appendChild(head); app.appendChild(list);
    var shown = [];
    function draw() {
      stop();
      var qd = digits(st.q), ql = st.q.toLowerCase();
      shown = D.rec.filter(function (x) {
        if (st.day && x.date !== st.day) return false;
        if (st.kind && x.kind !== st.kind) return false;
        if (!st.q) return true;
        var hay = [x.name, x.staff, x.ext, x.peer, x.kind].join(" ").toLowerCase();
        return hay.indexOf(ql) >= 0 || (qd.length >= 2 && (digits(x.peer).indexOf(qd) >= 0 || x.ext === qd));
      });
      list.innerHTML = "";
      var talk = shown.filter(function (x) { return x.dur; });
      sum.innerHTML = "<b>" + shown.length + "건</b> · 녹음 " + talk.length + "건 · 총 통화 " + mmss(talk.reduce(function (a, x) { return a + x.dur; }, 0));
      if (!shown.length) { list.appendChild(el("p", "d-empty", "검색 결과가 없습니다. 다른 번호나 이름으로 찾아보세요.")); return; }
      shown.forEach(function (x) {
        var row = el("div", "d-row rec" + (x.kind === "부재중" ? " alert" : ""));
        row.innerHTML = '<span class="d-when"><b>' + md(x.date) + "</b> " + x.time + '</span><span><em class="tag ' + KCLS[x.kind] + '">' + x.kind + "</em></span>" +
          '<span class="d-who"><b>' + (x.ext === "대표" ? "대표번호" : "내선 " + x.ext) + "</b><small>" + esc(x.ext === "대표" ? "아무도 안 받음" : x.staff) + "</small></span>" +
          '<span class="d-who"><b>' + esc(x.peer) + "</b><small>" + esc(x.name || "전화번호부에 없음") + "</small></span>";
        var c5 = el("span", "d-rec"), c6 = el("span", "d-act");
        if (x.dur) { c5.appendChild(playBtn(x, row)); c6.appendChild(saveBtn(x, x.ext)); }
        else c5.appendChild(el("span", "d-need", "회신 필요"));
        row.appendChild(c5); row.appendChild(c6); list.appendChild(row);
      });
    }
    xl.addEventListener("click", function () {
      csv([["날짜", "시각", "구분", "내선", "직원", "상대번호", "거래처", "통화시간"]].concat(shown.map(function (x) {
        return [x.date, x.time, x.kind, x.ext, x.staff, x.peer, x.name, x.dur ? mmss(x.dur) : ""];
      })), "허브레코딩_통화기록_샘플.csv");
    });
    draw();
  }

  // ── 허브모바일 ──
  function mob(root) {
    var st = { phone: "", kind: "", q: "" };
    var app = frame(root, "허브모바일", "법인폰 3대 연결됨");
    var tool = el("div", "d-tool");
    var sel = el("select", "d-sel"); sel.setAttribute("aria-label", "법인폰");
    sel.innerHTML = '<option value="">전체 폰</option>' + D.phones.map(function (p) { return '<option value="' + esc(p.name) + '">' + esc(p.name) + " (" + esc(p.team) + ")</option>"; }).join("");
    sel.addEventListener("change", function () { st.phone = sel.value; draw(); });
    var q = el("input", "d-q"); q.type = "search"; q.placeholder = "거래처·번호·문자 내용 검색 (예: 세움, 납품)"; q.setAttribute("aria-label", "검색");
    q.addEventListener("input", function () { st.q = q.value.trim(); draw(); });
    var xl = el("button", "d-xl", "목록 엑셀 저장"); xl.type = "button";
    tool.appendChild(sel); tool.appendChild(q); tool.appendChild(xl);
    var ch = chips([{ label: "전체", v: "" }, { label: "통화", v: "call" }, { label: "문자", v: "sms" }, { label: "부재중", v: "miss" }], function (v) { st.kind = v; draw(); });
    var sum = el("p", "d-sum");
    var head = el("div", "d-row d-head mob", "<span>일시</span><span>구분</span><span>법인폰</span><span>상대</span><span>내용</span><span></span>");
    var list = el("div", "d-list");
    app.appendChild(tool); app.appendChild(ch); app.appendChild(sum); app.appendChild(head); app.appendChild(list);
    var shown = [];
    function grp(x) { return x.kind === "부재중" ? "miss" : x.kind.indexOf("문자") === 0 ? "sms" : "call"; }
    function draw() {
      stop();
      var qd = digits(st.q), ql = st.q.toLowerCase();
      shown = D.mob.filter(function (x) {
        if (st.phone && x.phone !== st.phone) return false;
        if (st.kind && grp(x) !== st.kind && !(st.kind === "call" && grp(x) === "miss")) return false;
        if (!st.q) return true;
        var hay = [x.name, x.phone, x.peer, x.text, x.kind, x.note].join(" ").toLowerCase();
        return hay.indexOf(ql) >= 0 || (qd.length >= 2 && digits(x.peer).indexOf(qd) >= 0);
      });
      list.innerHTML = "";
      var open = D.mob.filter(function (x) { return x.state === "미응대"; }).length;
      sum.innerHTML = "<b>" + shown.length + "건</b>" + (open ? ' · <span class="d-red">회신 안 한 부재중 ' + open + "건</span>" : "");
      if (!shown.length) { list.appendChild(el("p", "d-empty", "검색 결과가 없습니다. 다른 거래처나 번호로 찾아보세요.")); return; }
      shown.forEach(function (x) {
        var miss = x.kind === "부재중", todo = x.state === "미응대";
        var label = miss ? x.state : x.kind.replace("문자", "문자 ");
        var cls = miss ? (todo ? "miss" : "done") : KCLS[x.kind];
        var row = el("div", "d-row mob" + (todo ? " alert" : ""));
        row.innerHTML = '<span class="d-when"><b>' + md(x.date) + "</b> " + x.time + '</span><span><em class="tag ' + cls + '">' + label + "</em></span>" +
          '<span class="d-who"><b>' + esc(x.phone) + "</b><small>" + esc(x.team) + "</small></span>" +
          '<span class="d-who"><b>' + esc(x.name || x.peer) + "</b><small>" + esc(x.name ? x.peer : "전화번호부에 없음") + "</small></span>";
        var c5 = el("span", "d-rec"), c6 = el("span", "d-act");
        if (x.dur) { c5.appendChild(playBtn(x, row)); c6.appendChild(saveBtn(x, x.phone.replace(" ", ""))); }
        else if (x.text) c5.appendChild(el("span", "d-text", esc(x.text)));
        else c5.appendChild(el("span", todo ? "d-need" : "d-note", esc(todo ? "아무도 회신 안 함" : x.note || "")));
        if (x.note && x.dur) c5.appendChild(el("span", "d-note", esc(x.note)));
        row.appendChild(c5); row.appendChild(c6); list.appendChild(row);
      });
    }
    xl.addEventListener("click", function () {
      csv([["날짜", "시각", "구분", "법인폰", "상대번호", "거래처", "통화시간", "문자 내용", "상태"]].concat(shown.map(function (x) {
        return [x.date, x.time, x.kind, x.phone, x.peer, x.name, x.dur ? mmss(x.dur) : "", x.text || "", x.state || x.note || ""];
      })), "허브모바일_통화문자_샘플.csv");
    });
    draw();
  }

  document.querySelectorAll("[data-demo]").forEach(function (root) {
    (root.dataset.demo === "mob" ? mob : rec)(root);
  });
})();
