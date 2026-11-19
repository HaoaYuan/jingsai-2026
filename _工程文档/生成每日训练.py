"""Build the offline daily training editions and teacher distribution lists."""

import base64
import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
TRACKS = ("01_编程闯关", "02_大数分解", "03_图像识别")
# Title, task, worked example or practice input, retest, optional extension.
COURSES = (
    (
        ("分段运费结算", "输入重量（正整数千克）。首 2 千克共 8 元，之后每千克 3 元。输出整数运费。", "5 → 17", "2 → 8；3 → 11", "满 10 千克时运费减 2 元。"),
        ("社团报名名额统计", "输入人数 n 和 n 个年龄。统计 12 到 15 岁（含端点）的人数，输出人数。", "5；11 12 15 16 13 → 3", "4；11 16 12 15 → 2", "另输出第一个符合条件的报名序号，从 1 开始，无人输出 0。"),
        ("值班表处理", "一行输入空格分隔的值班人姓名，再读入一个待查询姓名。输出该姓名出现次数及第一次出现的序号，无记录输出 0 0。", "林 周 林；林 → 2 1", "林 周 林；陈 → 0 0", "输出该姓名所有值班序号。"),
        ("阶段模拟一", "", "", "", ""),
        ("设备日志纠错", "输入一行温度。修正以下逻辑：从下标 1 开始遍历，读数 > 30 时令次数 = 1。要求统计所有大于等于 30 的读数，输出次数。", "30 29 32 30 → 3", "30 → 1；29 → 0", "增加输出最长连续达标次数。"),
        ("候选编号配对", "读一行不同的正整数，再读整数目标值。输出和值为目标的无序数对数，每对编号只计一次。", "1 4 2 3 5；6 → 2", "3；6 → 0", "按每对的较小编号升序打印所有数对。"),
        ("站点数据汇总", "读 n，再读 n 行站点名和非负数量。同名累加，先按总数降序，再按站点名升序输出每行站点名与总数。", "3 行：B 2 / A 3 / B 1 → A 3 / B 3", "2 行：B 0 / A 0 → A 0 / B 0", "另输出占总量一半及以上的站点；总量为零时输出无。"),
        ("阶段模拟二", "1. 判断 17//5 与 17%5 的结果。2. 说出 range(2, 7, 2) 遍历哪些值。3. 编程：读入预算，再读一行从左到右的商品价格。按顺序尝试购买，余额不足则跳过该商品。输出成功件数和余额。4. 编程：读一行小写字母，输出最长连续相同字母的长度，空行输出 0。", "题 3：预算 8；5 4 2 → 2 1。题 4：aabbbaa → 3", "题 3：预算 0；1 2 → 0 0。题 4：a → 1", "检查最后一段最长、余额恰好为零两种情况。"),
        ("重复记录筛查", "输入一行收件编号，按首次出现顺序输出去重后的编号，空行输出空行。", "B A B C A → B A C", "A A A → A", "另输出被去除的记录条数。"),
    ),
    (
        ("批量分解记录", "输入一行大于等于 2 的整数，每个整数输出一行，按质因数升序显示 p^指数，指数为 1 也写。", "12 13 → 2^2 3^1 / 13^1", "49 64 → 7^2 / 2^6", "汇总指数大于 1 的质因数个数。"),
        ("因数筛选汇总", "读入正整数 n。找出它所有为偶数的正因数，输出个数、和、最大值。没有偶因数时三个值均为 0。", "12 → 4 24 12", "9 → 0 0 0；2 → 1 2 2", "用因数成对出现的特点减少枚举，平方根只统计一次。"),
        ("半质数判定", "读整数 n（n≥2）。质因数带重数恰好两个时输出 YES，否则输出 NO。", "49 → YES；18 → NO", "2 → NO；15 → YES", "写程序判断完全数，比较所有真因数的和与 n。"),
        ("核心任务模拟一", "对 360、9973、10007 输出有序质因数分解。比较逐整数试除与先除 2 后跳偶试除：同机、同数据、同重复次数，用 time.perf_counter() 计时并先确认输出一致。提交输入规模、次数、两列实测耗时和结论。", "格式样例：18 → 2^1 3^2。耗时按实测填写。", "追加 99991，核对两种算法结果是否一致。", "用一张流程图解释跳偶版节省了什么。"),
        ("试除计时实验", "编写两个判断质数的函数，分别逐个试除和除 2 后只检查奇数，都在平方根停止。对 97、9973、99991 各重复 1000 次，用 time.perf_counter() 记录总秒数。", "结果表列：数字｜一致性｜次数｜逐个秒数｜跳偶秒数", "加入 9409（97 的平方），两个版本都应判为合数。", "重复三轮，取每个版本的中位数并解释小输入的波动。"),
        ("批量素数筛查", "用逐个试除和埃氏筛分别统计 1 到 N 中的质数，先核对数量，再对 N=1000 和 N=10000 记录耗时。筛法计时包括建筛。", "N=10 → 4；N=1000 → 168", "N=1 → 0；N=10000 → 1229", "把同一筛表复用于多次上界查询，分别记录建表和查询时间。"),
        ("从实验数据写报告", "重跑两种试除算法各三轮。用实测数据画一张标注单位的对比图，画出一个版本的流程图，写三句结论：条件、数据、原因。报告可以在页面填文字稿，图表和流程图可画在纸上。", "条件示例：同机、同一组数、每个版本重复 1000 次。", "检查结论引用的每个数字在记录表中都能找到。", "用一分钟口述结果，并说明一个可能影响计时的因素。"),
        ("核心任务模拟二", "读入 756、1024、99991，逐个输出质因数指数和。用两种试除法得到一致结果后，以相同重复次数记录实测耗时，写报告提纲（题意、流程、数据、结论）。", "样例：72 = 2^3×3^2，指数和为 5。", "输入 49 与 2，检查重复因子和质数边界。", "解释质数输入为何可能比同规模的易分解合数更慢。"),
    ),
    (
        ("点阵体检", "读取全部试题点阵，逐个输出文件名、行数、列数和 1 的个数。检查等宽、非空且只含 0/1。", "示例点阵 010 / 111 → 2 3 4", "复制一个样例，手动删掉某行末尾一列，确认程序报出格式错误。", "报告第一个出错行号。"),
        ("图形平移后怎么认", "输出每张图非零像素的外接框高、宽、面积及填充率。填充率保留两位小数。", "0000 / 0110 / 0100 → 2 2 3 0.75", "在完整矩形画布上给样例增加一行全 0，四个特征应相同。", "约定空点阵的输出，并编写测试。"),
        ("空心与实心", "每行含 1 时，计算最左到最右的跨度。总面积小于所有行跨度之和时，输出本卷约定的“空心”，否则输出“实心”。", "111 / 101 / 111 → 空心", "111 / 111 / 111 → 实心", "兼用首宽、末宽、最大行宽，区分给定数据的六边形、梯形和两类正方形。"),
        ("阶段模拟一", "客观题：写出外接框宽度的计算式，并说明为什么不能按文件名判断。编程：从试题和图库点阵提取填充率与宽高比，距离为两维特征分别相减后取绝对值的总和。为每张试题图输出最接近的模板名、图形类别及距离。距离相同取文件名升序第一项。画流程图并口述一项匹配依据。", "输出格式示例：图形X.txt 模板Z.txt 圆形 0.03（仅示范格式）", "交换图形1和图形2文件内容后重跑，类别应随点阵内容换位。", "用首行跨度占最大跨度比例作为第三维特征。"),
        ("给图形编特征", "为每张图输出宽高比、填充率、首行与末行跨度各占最大行跨度的比例，各保留两位小数。比较这些数值，写下能区分空心和实心正方形的特征。", "111 / 101 / 111 → 1.00 0.89 1.00 1.00", "给点阵外侧增加全 0 边框，特征不变。", "解释六边形与梯形在哪一维更易区分。"),
        ("在图库里找模板", "从图库和试题提取填充率、宽高比。使用两维差的绝对值之和比较距离，选距离最小的模板，同距离按文件名升序。输出文件名、模板名、类别。", "特征 (1.00, 0.80) 到 (1.00, 0.75) 的距离为 0.05。", "交换试题点阵顺序，识别应根据内容变化。", "给出距离最小和次小的两个候选。"),
        ("相似图形复测", "用填充率、宽高比、首末跨度比比较图库和试题。先保存结果，再为一个试题点阵加全零边框，并颠倒处理顺序，记录两次结果和一个可能误判的原因。", "复测表列：数据版本｜选中模板｜类别｜主要匹配特征", "在纯空白边缘加零后，对应模板应保持一致。", "找一组形状相近的候选，写出可增加的区分特征。"),
        ("阶段模拟二", "客观题：区分面积与外接框面积，写出一条避免硬编码文件顺序的规则。编程：提取宽高比、填充率、首末有效行跨度各占最大行跨度的比例，对给定图库进行最近模板匹配，使用各维绝对差之和，同距离取文件名升序。输出模板名、类别和最小距离。画流程图并口述失败时如何复测。", "示例格式：图形X.txt 模板Z.txt 实心正方形 0.00（仅示范格式）", "交换两个试题点阵的内容，确认结果跟随内容变化。", "列出最接近的两个模板，说明何时需要人工复核。"),
    ),
)

LEGACY = (
    {3: "mock02.html", 4: "mock01.html", 6: "ext01.html"},
    {3: "拓展卷01.html", 4: "模拟卷01.html"},
    {3: "拓展练习_多形与空心.html", 4: "全真模拟试卷2.html"},
)

STORAGE_PREFIXES = ("ck_", "ds", "imgrec_")


def grid_files(folder):
    directory = ROOT / TRACKS[2] / "练习与模拟" / "冲刺练习" / folder
    files = {}
    for path in sorted(directory.glob("图形*.txt")):
        data = path.read_bytes()
        rows = data.decode("ascii").splitlines()
        files[path.name] = ("\r\n".join(rows) + "\r\n").encode("ascii")
    assert len(files) == (4 if folder == "data_ext" else 3)
    return files


def image_material(day):
    folder = "data_mock2" if day in (1, 2, 4) else "data_ext"
    grids = grid_files(folder)
    labels = (
        ("等腰三角形", "正五边形", "圆形") if folder == "data_mock2"
        else ("正六边形", "等腰梯形", "空心正方形", "实心正方形")
    )
    if day in (4, 6, 7, 8):
        # Use different canvases for the templates while keeping the shape intact.
        values = list(grids.items())
        for index, (_, value) in enumerate(values):
            rows = value.decode("ascii").splitlines()
            padding = index + 1
            padded = ["0" * (len(rows[0]) + 2 * padding)] * padding
            padded += ["0" * padding + row + "0" * padding for row in rows]
            padded += ["0" * len(padded[0])] * padding
            name = "模板" + chr(ord("A") + index) + ".txt"
            grids[name] = ("\r\n".join(padded) + "\r\n").encode("ascii")
        grids["图库类别.txt"] = "".join(
            "模板" + chr(ord("A") + i) + ".txt " + label + "\r\n"
            for i, label in enumerate(labels)
        ).encode("utf-8")
        if day == 8:
            for index, (name, _) in enumerate(values):
                rows = values[(index + 1) % len(values)][1].decode("ascii").splitlines()
                rows = ["".join(pixel * 2 for pixel in row) for row in rows for _ in (0, 1)]
                grids[name] = ("\r\n".join(rows) + "\r\n").encode("ascii")
    return grids


def write_track(index):
    track = TRACKS[index]
    directory = ROOT / track / "练习与模拟"
    table = []
    for day, lesson in enumerate(COURSES[index], 1):
        title, task, example, retry, extra = lesson
        filename = LEGACY[index].get(day, "训练_D%02d_%s.html" % (day, title))
        if index == 0 and day == 4:
            # Keep the comprehensive mock's original automatic grading and question bank.
            target = directory / filename
            old = target.read_text(encoding="utf-8")
            tag = '<!-- daily training mock -->'
            if tag not in old:
                controls = render(0, day, (title, "完成下方原卷，按时间分配作答。", "", "", ""), {})
                panel = controls.split("<main>", 1)[1].split("</main>", 1)[0]
                script = controls.split("<script>", 1)[1].split("</script>", 1)[0]
                old = old.replace("<body>", "<body>\n" + tag + "\n<section style='max-width:900px;margin:20px auto;padding:16px'>"
                                  + panel.split('<button id="dailyStart">', 1)[0] + "</section>", 1)
                form = panel.split("<h2>作答与提交", 1)[1]
                old = old.replace("</body>", "<section style='max-width:900px;margin:20px auto;padding:16px'>"
                                  + "<h2>导出与复盘</h2>" + form + "</section><script>" + script + "</script>\n</body>", 1)
                old = old.replace('    <p class="crumb"><a href="../index.html">← 返回闯关地图</a></p>\n', "")
                old = old.replace('id="next" href="../index.html">继续', 'id="next" href="#dailyExport">填写练习记录')
                old = old.replace("next.href = nextHref();", 'next.href = "#dailyExport";')
                target.write_text(old, encoding="utf-8")
        else:
            files = image_material(day) if index == 2 else {}
            (directory / filename).write_text(render(index, day, lesson, files), encoding="utf-8")
        kind = "改版" if day in LEGACY[index] else "新编"
        table.append((day, title, kind, filename))
    write_list(directory, track, table)


def write_list(directory, track, table):
    rows = []
    for day, title, kind, filename in table:
        deliverable = ["代码、运行结果与复测结论", "运行结果与复测结论", "识别或特征输出与复测结论"][TRACKS.index(track)]
        if track == TRACKS[1] and day in (4, 5, 6, 7, 8):
            deliverable = "实验数据与结论"
        if track == TRACKS[2] and day in (4, 8):
            deliverable += "，另检查流程图与口述"
        rows.append('<tr><td>%02d</td><td><a href="%s">%s</a></td><td>%s</td><td>%s</td></tr>'
                    % (day, html.escape(filename), html.escape(title), kind, deliverable))
    page = ('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>教师下发清单</title><style>body{font:16px system-ui;max-width:52rem;margin:2rem auto;padding:1rem}td,th{padding:.6rem;border-bottom:1px solid #ccd}</style>'
            '<h1>%s · 教师下发清单</h1><p>每天发一份 HTML。第 4、8 天为阶段模拟。</p>'
            '<table><thead><tr><th>天次</th><th>训练文件</th><th>来源</th><th>交付物</th></tr></thead><tbody>%s</tbody></table></html>')
    (directory / "教师下发清单.html").write_text(page % (track[3:], "\n".join(rows)), encoding="utf-8")


def render(index, day, lesson, files):
    title, task, example, retry, extra = map(html.escape, lesson)
    is_mock = day in (4, 8)
    timing = (
        ("客观题 15 分钟 · 编程 40 分钟 · 自查 5 分钟",
         "分解 20 分钟 · 实测 25 分钟 · 结论 10 分钟 · 自查 5 分钟",
         "客观题 15 分钟 · 实操 35 分钟 · 流程图与口述 10 分钟")[index]
        if is_mock else "读题 5 分钟 · 实操 35 分钟 · 复测 10 分钟 · 订正 10 分钟"
    )
    title = "%s · 第 %02d 天 · %s" % (TRACKS[index][3:], day, title)
    materials = ""
    if files:
        links = [
            '<a download="%s" href="data:application/octet-stream;base64,%s">保存 %s</a>'
            % (html.escape(name), base64.b64encode(value).decode("ascii"), html.escape(name))
            for name, value in files.items()
        ]
        materials = "<h2>题目数据</h2><p>把所需 TXT 和 .py 脚本保存到同一个文件夹，在 IDLE 中运行脚本。</p>" + " ".join(links)
    exercise = "<h2>任务</h2><p>%s</p>" % task
    if example:
        exercise += "<p><b>样例：</b>%s</p><p><b>复测：</b>%s</p><p><b>%s：</b>%s</p>" % (
            example, retry, "交卷前检查" if is_mock else "选做", extra)
    form = """
<h2>作答与提交</h2>
<label>完成情况<select id="dailyStatus"><option>未完成</option><option>主任务已完成</option><option>主任务及选做已完成</option></select></label>
<label>代码草稿或流程说明<textarea id="dailyCode" rows="6"></textarea></label>
<label>客观题答案、运行结果或实验数据<textarea id="dailyOutput" rows="5"></textarea></label>
<label>复测结论或订正记录<textarea id="dailyReview" rows="3"></textarea></label>
<button id="dailyExport">导出练习记录</button>
"""
    # Keep older page keys intact. Revised questions get a separate edition key.
    key = STORAGE_PREFIXES[index] + "daily_training_%02d_v1" % day
    script = """
(function () {
  "use strict";
  var key = KEY;
  var fields = ["dailyStatus", "dailyCode", "dailyOutput", "dailyReview"];
  var end = 0;
  var time = document.getElementById("dailyClock");
  var start = document.getElementById("dailyStart");
  function read(id) { return document.getElementById(id).value; }
  function save() {
    var saved = { end: end };
    fields.forEach(function (id) { saved[id] = read(id); });
    try { localStorage.setItem(key, JSON.stringify(saved)); } catch (error) {}
  }
  try {
    var saved = JSON.parse(localStorage.getItem(key) || "{}");
    end = saved.end || 0;
    fields.forEach(function (id) {
      if (typeof saved[id] === "string") document.getElementById(id).value = saved[id];
    });
  } catch (error) {}
  fields.forEach(function (id) { document.getElementById(id).addEventListener("input", save); });
  function tick() {
    if (!end || !start) return;
    var left = Math.max(0, Math.ceil((end - Date.now()) / 1000));
    time.textContent = left ? Math.floor(left / 60) + ":" + ("0" + left % 60).slice(-2) : "时间到，请导出记录";
    start.disabled = true;
  }
  if (start) start.onclick = function () {
    end = Date.now() + 3600000;
    save();
    tick();
  };
  tick();
  if (start) setInterval(tick, 1000);
  document.getElementById("dailyExport").onclick = function () {
    var text = [TITLE, "完成情况：" + read("dailyStatus"), "代码或流程：", read("dailyCode"),
      "答案、运行结果或实验数据：", read("dailyOutput"), "复测或订正：", read("dailyReview")].join("\\r\\n");
    var a = document.createElement("a");
    var url = URL.createObjectURL(new Blob(["\\ufeff", text], { type: "text/plain;charset=utf-8" }));
    a.href = url;
    a.download = TITLE + "练习记录.txt";
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  };
}());
""".replace("KEY", json.dumps(key)).replace("TITLE", json.dumps(title, ensure_ascii=False))
    return """<!doctype html>
<html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s</title>
<style>
body{margin:0;background:#f1f5f9;color:#18283d;font:16px/1.65 system-ui,sans-serif}
main{max-width:54rem;margin:2rem auto;background:#fff;padding:clamp(1rem,4vw,2.5rem)}
h1,h2{line-height:1.3}h2{margin-top:2rem}textarea,select{box-sizing:border-box;width:100%%;font:inherit;padding:.5rem}
label{display:block;margin:.8rem 0}button,a[download]{display:inline-block;background:#174f99;color:white;
border:0;border-radius:.3rem;padding:.45rem .8rem;margin:.2rem;font:inherit;text-decoration:none;cursor:pointer}
button:disabled{opacity:.55}#dailyClock{font-variant-numeric:tabular-nums}
</style>
<main>
<h1>%s</h1><p>%s</p>
<p>编程任务请在 Python 3.9 的 IDLE 中运行。完成后把结果和复测记录填到本页，再导出提交。</p>
<button id="dailyStart">开始计时</button> <strong id="dailyClock" role="timer">60:00</strong>
%s%s%s
</main><script>%s</script></html>
""" % (title, title, timing, materials, exercise, form, script)


def link_portal(path, hrefs):
    page = path.read_text(encoding="utf-8")
    marker = "<!-- daily distribution links -->"
    if marker in page:
        return
    links = " · ".join('<a href="%s">%s教师下发清单</a>' % (href, label) for href, label in hrefs)
    insert = marker + '<nav aria-label="每日训练" style="margin:1rem auto;padding:1rem;max-width:70rem;background:#fff;color:#18283d">' + links + "</nav>\n"
    # Place the links before the first heading section when the portal has no main element.
    if "<main" in page:
        start = page.index(">", page.index("<main")) + 1
    else:
        start = page.index(">", page.index("<body")) + 1
    path.write_text(page[:start] + "\n" + insert + page[start:], encoding="utf-8")


def connect_portals():
    path = "练习与模拟/教师下发清单.html"
    link_portal(ROOT / "index.html", [(track + "/" + path, track[3:] + " · ") for track in TRACKS])
    for index in range(len(TRACKS)):
        link_track_portal(index)


def link_track_portal(index):
    link_portal(ROOT / TRACKS[index] / "index.html", [("练习与模拟/教师下发清单.html", "")])


if __name__ == "__main__":
    for track_index in range(len(TRACKS)):
        write_track(track_index)
    connect_portals()
