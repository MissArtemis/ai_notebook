"""生成 1541 两平台图卡、题解与文案；沿用 1021 配色、字体和插画。

运行：python leetcode/note/production/1541/make_materials.py
依赖：Pillow，Windows 微软雅黑与 Consolas 字体。
"""
from pathlib import Path
import io
import json
import keyword
import shutil
import tokenize
import zipfile
from PIL import Image, ImageDraw, ImageFont, ImageOps

REPO = next(p for p in Path(__file__).resolve().parents if (p / "leetcode").is_dir())
ROOT = REPO / "leetcode/note/publish/LeetCode1541_12张图文"
SRC = ROOT / "源文件"
IMG = ROOT / "图片"
VERT = ROOT / "抖音竖版"
COPY = ROOT / "文案"
NOTE = REPO / "leetcode/note/leetcode_1541_minimum_insertions.md"
OLD_ART = ROOT.parent / "LeetCode1021_8张图文/源文件/学习少女插画.png"
W, H, S = 1080, 1440, 2
INK, MUTED, ACCENT, ROSE = "#142338", "#52687B", "#267AAC", "#B94E70"
BLUE, PINK, YELLOW, GREEN = "#E7F3FE", "#FDE5EC", "#FFF1C6", "#E6F3E8"
FONTS = {"body": "C:/Windows/Fonts/msyh.ttc", "bold": "C:/Windows/Fonts/msyhbd.ttc", "code": "C:/Windows/Fonts/consola.ttf"}
CACHE, LAYOUT = {}, []

PAGES = [
    dict(name="一个右括号变两个", title="一个右括号，变成两个", tag="1541 × 1021 · 思路迁移", subtitle="匹配单位变了，计数规则也要跟着变。",
         xhs_title="括号题升级：一个右括号变两个", xhs="上一题 1021，一个左括号匹配一个右括号；这次 1541，一个左括号匹配两个连续右括号。我保留了左括号计数的思路，却踩到两个坑：检查下一个字符的边界收紧了一位，末尾又忘记补齐剩余左括号。这 12 张图从我的修正版讲到 need 写法，再解释为什么计数器可以代替同类括号栈。", douyin="从 1021 到 1541，右括号从一个变成连续两个。我踩了两处坑，也终于弄懂括号题到底在数什么。", cta="先记住：这里要求的是连续的 ))。"),
    dict(name="1021与1541对照", title="1021 和 1541，差在哪里？", tag="对照 · 先换匹配单位", subtitle="同样扫描括号，任务和状态更新却不同。",
         xhs_title="1021和1541不能照搬同一口诀", xhs="1021 输入已经合法，任务是删每个原语的外层括号；一个右括号让 depth 减一。1541 输入可能不平衡，任务是补齐；两个连续右括号组成的一组，才消耗一个左括号。1021 的左先判断、右先减是在识别外层，1541 则要判断缺什么，并在结束后结算需求。", douyin="1021：一个右括号关闭一层，输入合法。1541：两个连续右括号关闭一层，输入可能不合法，最后还得补齐。", cta="拿 () 比一比：1021 删成空串，1541 要补一次。"),
    dict(name="为什么统计左括号", title="为什么常统计左括号？", tag="核心状态 · 待匹配量", subtitle="计数器保存的是还没闭合的结构。",
         xhs_title="括号题为什么常用左括号计数", xhs="从左到右，左括号建立一个等待闭合的结构，右括号尝试关闭它。这里数的是当前未匹配左括号，不是出现总数。只有一种括号，又不需要匹配位置时，栈里全是相同元素，只记长度就够了。1541 分组法一次处理完整的右括号组；逐字符法则要额外表达有没有半组。多类型括号仍要保留类型和顺序。", douyin="左括号计数其实是同类括号栈的长度。重点是未匹配数量，不是总数量；遇到多种括号，光数数量就不够了。", cta="能说明白状态含义，再写加一或减一。"),
    dict(name="我的右括号分组法", title="我的解法：把 )) 当一组", tag="Solution 1 · 保留我的思路", subtitle="一组右括号，匹配一个待匹配左括号。",
         xhs_title="1541我用左括号计数这样做", xhs="遇到左括号，left_cnt 加一。遇到右括号，先看有没有左括号：有就消耗一个，没有就补一个。然后检查后一位是不是右括号；是就一起读掉，否则补一个右括号完成这一组。这样每轮结束都没有半组，最后每个剩余左括号直接补两个右括号。", douyin="看到 )) 就当一组；只看到一个 ) 就补另一个。有左括号就匹配，没有就插入。结束后剩几个左括号，就补两倍的右括号。", cta="用 ))())( 推演，答案应是 3。"),
    dict(name="分组法完整代码", title="分组法：完整 Python 代码", tag="Solution 1 · 可直接提交", subtitle="合并两个判断条件，与我的修正版等价。",
         xhs_title="1541分组法Python完整代码", xhs="这版仍是我的 left_cnt 解法，把边界检查与后一个字符判断合并，减少一层嵌套。and 会短路，只有 i + 1 仍在字符串内时，才读取 s[i + 1]。遇到连续两个右括号跳两位，否则跳一位并补一个。最后返回已插入次数加 2 * left_cnt。时间 O(n)，额外空间 O(1)。", douyin="完整代码在这里。向后看一位之前先检查边界，连续两个右括号跳两位，最后别忘了 2 * left_cnt。", cta="遮住代码，自己写出单个 ) 的处理。"),
    dict(name="两处真实踩坑", title="两个最小反例，定位两处坑", tag="踩坑 · 边界与收尾", subtitle="()) 检查边界，( 检查剩余需求。",
         xhs_title="1541我错在边界和最后一行", xhs="原来写 i < len(s) - 2，但我要读的是 s[i + 1]，所以只需 i < len(s) - 1。用 ())，i=1 时后一位存在，却被旧条件挡住，原始代码错算成 3，正确是 0。另一个坑是直接返回 insert_cnt：输入一个左括号时返回 0，实际应该补两个右括号。修复是结尾加 2 * left_cnt。", douyin="()) 本来不用插入，我却把它错算成 3；一个 ( 应该补两次，我又算成 0。前者是边界差一位，后者是漏掉末尾欠账。", cta="改完以后，再分别跑这两个最小反例。"),
    dict(name="为什么贪心最少", title="为什么这样补，次数最少？", tag="正确性 · 尽量复用已有字符", subtitle="只有当前匹配无法完成时，才需要插入。",
         xhs_title="1541贪心为什么可以放心配对", xhs="连续两个右括号直接成组，不花插入次数；拆开反而需要补齐更多组。右括号后是左括号或到末尾，原字符不能重排，这一组至少要补一个邻接右括号。右括号组前没有可用左括号，后面的左括号又不能倒过来匹配，至少要插入一个左括号。末尾剩余左括号每个必须再配两个右括号。", douyin="已有 )) 直接用，孤立 ) 至少补一个，没有左括号至少补一个 (，末尾剩下的 ( 每个补两个 )。每次都只补匹配必须用的数量。", cta="用 ))( 反驳“左右数量对上就行”。"),
    dict(name="need的奇数分支", title="need 是奇数，为什么先补？", tag="Solution 2 · 两个右括号必须连续", subtitle="need：当前前缀还欠多少个右括号。",
         xhs_title="need奇数不是口诀是半组状态", xhs="逐字符扫描时，一个左括号增加两个右括号需求。need 是奇数，说明上一组只读了第一个右括号。如果这时读到新的左括号，就得先在它前面插一个右括号，完成旧组，再给新左括号增加需求。用 ()(：读完 () 还欠 1，在新左括号前补 )，最后新左括号再补两个，答案为 3。", douyin="need 是奇数，意味着有半组右括号。新左括号会拆断这组，所以先补第二个右括号，再增加两个新需求。", cta="只把普通括号的 +1 改成 +2，还不够。"),
    dict(name="need减到负一", title="need 到 -1，为什么变成 1？", tag="Solution 2 · 缺少左括号", subtitle="插入一个左括号，当前右括号已经配了一半。",
         xhs_title="need减到负一后为什么设为一", xhs="读到右括号先让 need 减一；变成 -1，说明这个右括号没有现有左括号可匹配，先在它前面补一个左括号。新左括号需要两个右括号，当前这个已经满足一个，所以还欠一个，need 应设为 1。输入只有一个 ) 时，需要补一个 ( 和一个 )，答案为 2。最后加 need 是结算全部剩余需求。", douyin="need 变成 -1 就补一个左括号。它需要两个右括号，眼前这个已经算一个，还差一个，所以 need=1。", cta="输入 )，想清楚为什么不能设成 0 或 2。"),
    dict(name="need法完整代码", title="need 法：逐字符扫描", tag="Solution 2 · 可直接提交", subtitle="代码更简洁；两种解法的复杂度相同。",
         xhs_title="1541不用下标的need写法", xhs="need 法不用向后看字符，只要维护欠下的右括号数和已插入次数。遇到左括号先补齐旧半组；遇到右括号减需求，必要时补左括号。最后把 need 加入答案。奇偶性保存半组信息，因此不是一个机械的加二减一计数器。与分组法一样，时间 O(n)，额外空间 O(1)，没有做实际运行速度比较。", douyin="need 代码记住三处：新左括号前处理奇数，右括号后处理 -1，结束后加剩余 need。两种写法都已经是线性时间。", cta="合上代码，解释三处特殊处理各在补什么。"),
    dict(name="四字符跑通三个分支", title="四个字符，跑通三个分支", tag="推演 · s = )()(", subtitle="负需求、奇数半组、末尾结算，一次看清。",
         xhs_title="四个字符看懂1541所有分支", xhs="用 )()( 推演：第一个右括号让 need 到 -1，补左括号后 need=1、插入数=1。接着左括号先补齐半组，再新增两个需求，need=2、插入数=2。第三个右括号令 need=1。最后左括号又触发半组补齐，need=2、插入数=3。结束加上剩余需求 2，答案是 5。", douyin="拿 )()( 跑一遍：先补左括号，两次补齐半组，最后补两个右括号，总插入数是 5。", cta="换成 ))())( 自己画表，答案应是 3。"),
    dict(name="状态迁移与复盘", title="迁移思路：先定义状态", tag="复盘 · 从匹配单位出发", subtitle="先想清楚数什么，再决定怎么更新。",
         xhs_title="从1021到1541我记住这三件事", xhs="第一，关闭单位变了：1021 是一个右括号，1541 是连续两个。第二，计数器保存待匹配量；分组法用 left_cnt，逐字符法用 need 并靠奇偶性表达半组。第三，输入不保证平衡时，必须补齐末尾剩余需求。两种 1541 解法都是 O(n) 时间、O(1) 额外空间；多类型括号或要匹配位置时，需要保存更多信息。", douyin="先看一个左括号需要什么关闭单位，再看状态能不能保存半组，最后检查还有没有欠账。括号题的计数，数的是待匹配量。", cta="解释清楚状态，比背住加减规则更有用。"),
]

GROUP_COPY = """小红书整组文案（12 图按 01—12 上传）

推荐标题：括号题升级：一个右括号变两个
备选标题：1541踩坑：右括号成对还得连续
备选标题：从1021到1541，计数器到底数什么

正文：
今天的刷题记录：LeetCode 1541「平衡括号字符串的最少插入次数」。

上一题 1021，一个左括号配一个右括号，输入已经合法，我们只删每个原语的外层。
这一题，一个左括号要配两个连续右括号，而且输入可能缺括号，要计算最少补多少次。

我先保留“统计未匹配左括号”的思路，把 )) 当一组。
有左括号就消耗一个，没有就补一个；只有单个 ) 就补另一个。
思路没问题，我却踩了两处坑：
① 看 s[i+1]，边界写成了 i<len(s)-2，让 ()) 错算成 3，正确是 0。
② 读完直接返回，忘了每个剩余左括号还缺两个右括号，让 ( 错算成 0，正确是 2。

后来用 need 记录还欠多少个右括号，写法更简洁。
但不能只是左括号加二、右括号减一：
need 为奇数时有半组右括号，新左括号前要先补齐；
need 减到 -1 时，补一个左括号后，当前右括号已满足一半，令 need=1；
扫描完再加剩余 need。

为什么这类题常数左括号？
因为从左到右，左括号建立等待闭合的结构；只有一种括号、只关心数量时，可以把栈压缩成长度。
数的是“当前未匹配量”，不是出现总数。多类型括号还要保留类型和顺序。
也不一定非数左括号不可，need 数右括号需求同样有效。

12 张图：1021 对照、我的分组法、真实踩坑、两种完整代码、贪心理由和逐字符推演。
两种解法都是 O(n) 时间、O(1) 额外空间，未比较实际运行速度。

收藏后试着解释：need=-1 时，为什么修正成 1？

话题：#力扣 #LeetCode #Python #算法学习 #刷题笔记 #每日一题

--------------------------------------------------
抖音整组图文文案

推荐标题：右括号变两个，计数规则怎么改？

正文：
从 1021 到 1541，一个左括号从匹配一个右括号，变成匹配两个连续右括号。
我把 )) 当一组，用未匹配左括号计数，却踩到边界差一位和末尾漏补两个坑。
另一种 need 写法：左括号前补齐旧半组，右括号后处理 -1，最后结算需求。
12 张图，含两种 Python 代码、1021 对照和状态推演。
时间 O(n)，额外空间 O(1)。记住：统计的是当前待匹配量。
收藏后用 )()( 走一遍，答案应该是 5。

话题：#力扣 #编程 #Python #算法 #学习记录 #每日一题

置顶评论备选：
need=-1 时，补一个左括号后为什么还欠 1 个右括号？拿只有一个 ) 的输入解释一下。

题目：https://leetcode.cn/problems/minimum-insertions-to-balance-a-parentheses-string/
对照：https://leetcode.cn/problems/remove-outermost-parentheses/description/
这是个人每日刷题记录；图文编号不表示平台当天指定题目。
"""

# 口播是另一个编辑版本，时码用于剪辑，实际录音后可调整。
SEGMENTS = [
    (0, 10, 1, "上一题一左配一右，这一题一左配两个连续右括号。同样是括号计数，规则要怎么改？"),
    (10, 22, 2, "1021 的输入已经合法，只删除每个原语的外层。1541 输入可能不平衡，我们要计算最少插入多少次。"),
    (22, 35, 3, "为什么常统计左括号？因为从左到右，左括号建立等待闭合的结构。同类括号只关心数量时，栈就能压缩成一个计数器。"),
    (35, 48, 4, "我把两个连续右括号当一组。有左括号就匹配，没有就补一个。单个右括号补另一个，最后剩余左括号每个补两个。"),
    (48, 58, 5, "代码重点在向后看一位之前检查边界。现有两个右括号一起读取，不要拆开。"),
    (58, 73, 6, "我最初把边界收紧了一位，完整的左括号加两个右括号，反而错算成三次。又忘了末尾补齐，单个左括号错算成零。"),
    (73, 84, 7, "贪心尽量使用已有字符。现有的一组成对使用，孤立的补齐，没有左括号就补一个，末尾再结算。"),
    (84, 100, 8, "也可以用 need 统计欠下的右括号。need 是奇数，说明只读了半组，新的左括号会把它拆断，所以先补齐旧组，再增加两个需求。"),
    (100, 112, 9, "右括号让 need 减到负一，就先补左括号。新左括号需要两个右括号，眼前这个满足一个，所以还欠一个。"),
    (112, 122, 10, "need 法不用下标，但两种解法复杂度相同：时间线性，额外空间常数。结束后都要补齐欠账。"),
    (122, 135, 11, "用右、左、右、左四个字符推演：补一个左括号，两次补齐半组，最后补两个右括号，合计五次。"),
    (135, 146, 12, "记住三个问题：关闭单位是什么？状态有没有保留半组信息？结束后还欠多少？先解释状态，再背加减规则。"),
]


def font(size=36, kind="body"):
    key = size, kind
    if key not in CACHE:
        CACHE[key] = ImageFont.truetype(FONTS[kind], round(size * S))
    return CACHE[key]


class Poster:
    def __init__(self, number):
        self.number, self.checks = number, []
        self.im = Image.new("RGB", (W*S, H*S), "#F8FAF6")
        self.d = ImageDraw.Draw(self.im)
        self.box(22, 22, 1036, 1396, "#FFFFFF", outline="#BBD9E7", stroke=3)
        self.box(48, 42, 984, 6, "#C7E6F4", radius=3)
        self.box(62, 68, 245, 44, BLUE, radius=15)
        self.text(184, 90, "算法拆解笔记", 24, "bold", ACCENT, "mm")
        self.text(998, 90, f"{number:02d} / 12", 26, "bold", anchor="rm")
        self.line([(64, 1337), (1016, 1337)], "#D8E5EA", 2)
        self.text(64, 1362, "LeetCode 1541 · 平衡括号的最少插入", 23, color=MUTED)
        self.text(1016, 1390, "Python / 每日刷题记录", 23, color=MUTED, anchor="rm")

    def box(self, x, y, w, h, fill=BLUE, radius=22, outline=None, stroke=1):
        self.d.rounded_rectangle((round(x*S), round(y*S), round((x+w)*S), round((y+h)*S)), radius=round(radius*S), fill=fill, outline=outline, width=round(stroke*S))

    def line(self, points, fill=INK, width=3):
        self.d.line([(round(x*S), round(y*S)) for x,y in points], fill=fill, width=round(width*S))

    def measure(self, text, size=36, kind="body"):
        return self.d.textlength(str(text), font=font(size, kind))/S

    def text(self, x, y, text, size=36, kind="body", color=INK, anchor="lt"):
        text = str(text)
        xy = round(x*S), round(y*S)
        bbox = self.d.textbbox(xy, text, font=font(size, kind), anchor=anchor)
        assert bbox[0] >= 22*S and bbox[2] <= 1058*S and bbox[3] <= 1418*S, (self.number, text, bbox)
        self.d.text(xy, text, font=font(size, kind), fill=color, anchor=anchor)
        self.checks.append(dict(text=text, bbox=[round(v/S,1) for v in bbox], size=size))

    def wrap(self, text, width, size=36, kind="body"):
        lines=[]
        for paragraph in text.split("\n"):
            current=""
            for ch in paragraph:
                if current and self.measure(current+ch,size,kind)>width:
                    lines.append(current)
                    current=ch
                else:
                    current+=ch
            lines.append(current)
        return lines

    def para(self, x, y, text, width=904, size=36, kind="body", color=INK, leading=1.45, bottom=1317):
        lines=self.wrap(text,width,size,kind)
        for i,line in enumerate(lines):
            self.text(x,y+i*size*leading,line,size,kind,color)
        actual=y+(len(lines)-1)*size*leading+size*1.22
        assert actual<=bottom, (self.number,text,actual,bottom)
        return y+len(lines)*size*leading

    def header(self):
        page=PAGES[self.number-1]
        self.text(66,141,page["tag"],25,"bold",ACCENT)
        size=59
        while self.measure(page["title"],size,"bold")>952:
            size-=1
        self.text(64,184,page["title"],size,"bold")
        self.para(66,269,page["subtitle"],952,32,color=MUTED,bottom=319)

    def card(self, y, title, body, fill=BLUE, size=36, accent=ACCENT, height=None):
        assert self.measure(title,40,"bold")<=894, (self.number,title)
        lines=self.wrap(body,894,size)
        required=105+len(lines)*size*1.45
        h=height or required
        assert h>=required-12
        assert y+h<=1317,(self.number,title,y+h)
        self.box(64,y,952,h,fill)
        self.box(64,y+22,6,h-44,accent,radius=3)
        self.text(92,y+25,title,40,"bold",accent)
        self.para(92,y+88,body,894,size,bottom=y+h-12)
        return y+h+24

    def note(self,y,body,fill=YELLOW,size=33,height=None):
        h=height or 45+len(self.wrap(body,904,size))*size*1.45
        assert y+h<=1317,(self.number,body,y+h)
        self.box(64,y,952,h,fill)
        self.para(88,y+22,body,904,size,bottom=y+h-12)
        return y+h+24

    def code(self,y,code,size=32):
        lines=code.splitlines()
        while max(self.measure(line,size,"code") for line in lines)>904:
            size-=1
        while y+86+len(lines)*size*1.2>1170:
            size-=1
        assert size>=29,(self.number,"code font",size)
        lh=size*1.2
        h=86+len(lines)*lh
        self.box(64,y,952,h,"#14202D")
        self.box(64,y,952,58,"#213345")
        self.box(64,y+30,952,28,"#213345",radius=0)
        self.text(94,y+16,"Python · 完整 Solution",26,"bold","#D7E7EF")
        spans={}
        for t in tokenize.generate_tokens(io.StringIO(code).readline):
            if t.start[0]!=t.end[0] or t.type in (tokenize.INDENT,tokenize.DEDENT,tokenize.NEWLINE,tokenize.NL,tokenize.ENDMARKER):
                continue
            color="#E1E9F1"
            if t.type==tokenize.STRING: color="#C4E69C"
            elif t.type==tokenize.NUMBER: color="#F3C982"
            elif t.type==tokenize.COMMENT: color="#88A5B6"
            elif t.type==tokenize.NAME and keyword.iskeyword(t.string): color="#F6A9D4"
            spans.setdefault(t.start[0]-1,[]).append((t.start[1],t.end[1],color))
        for i,line in enumerate(lines):
            baseline=y+78+i*lh+font(size,"code").getmetrics()[0]/S
            for start,end,color in spans.get(i,[]):
                self.text(88+self.measure(line[:start],size,"code"),baseline,line[start:end],size,"code",color,"ls")
        return y+h+24

    def save(self):
        filename=f"{self.number:02d}_{PAGES[self.number-1]['name']}.png"
        rendered=self.im.resize((W,H),Image.Resampling.LANCZOS)
        rendered.save(IMG/filename,optimize=True,dpi=(144,144))
        # 使用同一高分辨率排版稿，不从成品 PNG 再放大。
        vertical=Image.new("RGB",(W*S,1920*S),"#EDF5FA")
        vertical.paste(self.im,(0,168*S))
        draw=ImageDraw.Draw(vertical)
        draw.text((64*S,104*S),"1541 × 1021  /  括号计数进阶",font=font(30,"bold"),fill=ACCENT,anchor="lt")
        draw.text((64*S,1646*S),"滑动继续 →" if self.number<12 else "收藏后，自己推演一次",font=font(32,"bold"),fill=INK,anchor="lt")
        lines=self.wrap(PAGES[self.number-1]["cta"],850,30)
        for i,line in enumerate(lines):
            draw.text((64*S,(1710+i*44)*S),line,font=font(30),fill=MUTED,anchor="lt")
        vertical.resize((W,1920),Image.Resampling.LANCZOS).save(VERT/filename,optimize=True,dpi=(144,144))
        LAYOUT.append(dict(page=self.number,file=filename,checks=self.checks))


def make(number,codes):
    p=Poster(number)
    if number==1:
        p.text(64,153,"LeetCode 1541 × 1021",34,"bold",ACCENT)
        p.text(60,230,"一个右括号",92,"bold")
        p.text(60,345,"变成两个，怎么数？",83,"bold")
        p.box(64,482,448,136,BLUE)
        p.box(536,482,480,136,PINK)
        p.text(92,505,"1021 · 普通括号",31,"bold",ACCENT)
        p.text(288,580,"( ↔ )",60,"code",anchor="mm")
        p.text(564,505,"1541 · 双右括号",31,"bold",ROSE)
        p.text(776,580,"( ↔ ))",60,"code",ROSE,"mm")
        p.para(68,654,"未匹配左括号 × 连续右括号组\n我的两处踩坑，和 need 的半组状态。",940,41,"bold",bottom=803)
        with Image.open(SRC/"学习少女插画.png") as original:
            art=ImageOps.contain(original.convert("RGB"),(952*S,397*S),Image.Resampling.LANCZOS)
            p.im.paste(art,((W*S-art.width)//2,820*S))
        p.box(80,1240,920,77,YELLOW)
        p.text(540,1280,"12 张图 · 对比 / 踩坑 / 双解法 / 推演",32,"bold",anchor="mm")
    else:
        p.header()
        if number==2:
            p.box(64,338,952,707,"#F6F8FC")
            p.box(64,338,952,79,BLUE)
            for x,t in [(90,"对比点"),(331,"1021"),(659,"1541")]: p.text(x,362,t,34,"bold")
            rows=[("匹配单位","一个 )","连续的 ))"),("输入","已经合法","可能不平衡"),("任务","删除外层","最少插入"),("右括号更新","每个 ) 减一","每组 )) 减一"),("扫描结束","深度归零","结算剩余需求"),("结果存储","字符串 O(n)","次数 O(1)")]
            for i,row in enumerate(rows):
                y=437+i*100
                for x,t in zip((90,331,659),row): p.text(x,y,t,32,"bold" if x==90 else "body")
                p.line([(84,y+77),(997,y+77)],"#D7E3EC",1)
            y=p.note(1057,"()：1021 删除后为空；1541 要补一个 )。",BLUE,35)
            p.note(y,"“左先判断，右先减”用于 1021 的外层判断。\n1541 要换成补齐匹配的逻辑。",YELLOW,32)
        elif number==3:
            y=p.card(338,"① 从左到右：建立 → 闭合","( 建立等待闭合的结构，右括号关闭它。\n数的是当前未匹配量，不是左括号总数。",BLUE,36)
            y=p.card(y,"② 计数器 = 同类括号栈的长度","只有一种括号，且不需要匹配位置时，\n栈里元素相同，只记还剩几个就够了。",PINK,36,ROSE)
            y=p.card(y,"③ 状态必须保存足够的信息","1541 逐字符处理，还要知道有没有半组。\n多种括号要保留类型与顺序，通常用栈。",GREEN,36,"#33795B")
            p.note(y,"也可以数右括号需求 need，并非必须数左括号。",YELLOW,32)
        elif number==4:
            y=p.card(338,"遇到 (：新增一个待匹配左括号","left_cnt += 1\n当前字符处理完，向后走一位。",BLUE,37)
            y=p.card(y,"遇到 ))：一组匹配一个左括号","有现成的左括号，就消耗一个。\n没有，就插入一个 (；向后走两位。",GREEN,37,"#33795B")
            y=p.card(y,"遇到单个 )：补齐这一组","后一位是 ( 或没有后一位，补一个 )。\n这一组也要匹配一个 (；向后走一位。",PINK,36,ROSE)
            p.note(y,"每轮都完成整组，结束后补 2 * left_cnt。",YELLOW,34)
        elif number==5:
            code=codes["group"]
            code="\n".join(line.split("  #")[0] for line in code.splitlines() if line.strip())
            y=p.code(338,code,32)
            p.note(y,"边界先判断，再读取 s[i + 1]。\n每个剩余左括号都完整地缺两个右括号。",YELLOW,33)
        elif number==6:
            y=p.card(338,"坑一：边界收紧了一位","旧条件：i < len(s) - 2\n正确条件：i + 1 < len(s)\n()) 中 i = 1 时，后一位明明存在。\n原始代码错算成 3；正确答案是 0。",PINK,36,ROSE)
            y=p.card(y,"坑二：读完字符串，漏掉收尾","输入 (：只累计 left_cnt，没有发生插入。\n直接返回 insert_cnt，会错算成 0。\n每个剩余 ( 还需要两个 )，正确答案是 2。",BLUE,36)
            p.note(y,"修正：return insert_cnt + 2 * left_cnt\n1021 输入合法会归零；1541 需要补齐欠账。",YELLOW,33)
        elif number==7:
            y=p.card(338,"现有 ))：直接组成一组","不用插入，就完成一个关闭单位。\n拆成两组会多补右括号、占用更多左括号。",BLUE,36)
            y=p.card(y,"孤立 )：至少补一个邻接右括号","后面是 ( 或已到末尾，原字符不能重排。\n补一个 ) 就能完成这一组。",PINK,36,ROSE)
            y=p.card(y,"缺左括号、剩左括号：分别补齐","组前没有可用 (，至少插入一个。\n最后每个剩余 (，都完整地缺两个 )。",GREEN,36,"#33795B")
            p.note(y,"只看总数不够：))( 左 1 右 2，仍要插入 3 次。",YELLOW,32)
        elif number==8:
            y=p.card(338,"need：还欠多少个右括号","一个新的 (，增加两个右括号需求。\nneed 为奇数，说明当前已有半组右括号。",BLUE,37)
            y=p.card(y,"新 ( 之前，先补齐旧组","否则新左括号会隔开两个右括号。\n先 insert_cnt += 1，need -= 1；\n然后为新 ( 执行 need += 2。",PINK,36,ROSE)
            y=p.card(y,"例子 ()(：答案为 3","读完 ()，need = 1。在新 ( 前补一个 )，\n再增加 2 个需求；结束再补两个 )。",GREEN,36,"#33795B")
            p.note(y,"不能只改成“左加二、右减一”，还要管连续性。",YELLOW,31)
        elif number==9:
            y=p.card(338,"遇到 )：先执行 need -= 1","若变成 -1，说明当前右括号没有\n对应的左括号，要在它前面补一个 (。",BLUE,38)
            y=p.card(y,"补完 (，还欠一个右括号","新 ( 需要两个 )，当前这个满足一个。\n因此 insert_cnt += 1，need = 1。\n不能设成 0，也不能设成 2。",PINK,36,ROSE)
            y=p.card(y,"输入只有 )：答案为 2","补左括号：()；再补右括号：())。\n结束后还要把剩余 need 加到答案中。",GREEN,37,"#33795B")
            p.note(y,"最终：return insert_cnt + need",YELLOW,37)
        elif number==10:
            code="\n".join(line for line in codes["need"].splitlines() if line.strip())
            y=p.code(338,code,34)
            p.note(y,"三处关键：奇数遇到 (、需求到 -1、末尾结算。\n时间 O(n)，额外空间 O(1)。",YELLOW,33)
        elif number==11:
            p.note(338,"s = )()(    ·    初始 need = 0，插入数 = 0",BLUE,34)
            top=458
            p.box(64,top,952,508,"#F6F8FC")
            p.box(64,top,952,79,BLUE)
            for x,t in [(90,"下标"),(223,"字符"),(363,"need"),(554,"插入数"),(745,"本轮动作")]: p.text(x,top+25,t,29,"bold")
            rows=[("0",")","1","1","补一个 ("),("1","(","2","2","补齐半组"),("2",")","1","2","消耗需求"),("3","(","2","3","补齐半组"),("结束","—","2","3","还缺两个 )")]
            for i,row in enumerate(rows):
                y=top+98+i*80
                for x,t in zip((93,245,389,594,748),row): p.text(x,y,t,33,"code" if x==245 else "body")
                p.line([(84,y+65),(997,y+65)],"#D7E3EC",1)
            y=p.card(991,"已插入 3 次 + 末尾需求 2 = 5","每次处理后，need 都表示还欠几个 )。\n“插入数”这一列只统计已经补的字符。",YELLOW,34,"#9B6A1E")
            p.note(y,"自行练习：))())( → 3，()( → 3。",GREEN,32)
        elif number==12:
            y=p.card(338,"① 匹配单位先换对","1021：一个 ) 关闭一层。\n1541：连续的 )) 才关闭一层。",BLUE,38)
            y=p.card(y,"② 统计待匹配量，保留半组信息","分组法一次处理整组，只存 left_cnt。\n逐字符法用 need，奇偶性表达半组。",PINK,36,ROSE)
            y=p.card(y,"③ 结束后结算所有剩余需求","分组法加 2 * left_cnt；need 法加 need。\n两种解法：时间 O(n)，额外空间 O(1)。",GREEN,36,"#33795B")
            p.note(y,"同类栈可压缩成数量；多类型或位置匹配需更多状态。",YELLOW,30)
    p.save()


def timecode(seconds, srt=False):
    h=seconds//3600
    m=seconds//60%60
    s=seconds%60
    return f"{h:02d}:{m:02d}:{s:02d},000" if srt else f"{m:02d}:{s:02d}"


def write_copy(codes):
    full=["# LeetCode 1541｜12 张图逐张文案\n", "整组发布优先使用《整组发布文案.txt》，以下也可用于单张内容。\n"]
    for i,page in enumerate(PAGES,1):
        filename=f"{i:02d}_{page['name']}"
        body=f"对应图片：{filename}.png\n\n小红书标题：{page['xhs_title']}\n\n小红书正文：\n{page['xhs']}\n\n抖音图文文案：\n{page['douyin']}\n\n可选收尾：{page['cta']}\n\n话题：#力扣 #LeetCode #Python #算法学习 #刷题笔记\n"
        (COPY/f"{filename}.txt").write_text(body,encoding="utf-8-sig")
        full.append(f"## {i:02d}｜{page['name']}\n\n**小红书标题：{page['xhs_title']}**\n\n{page['xhs']}\n\n**抖音：** {page['douyin']}\n\n**可选收尾：** {page['cta']}\n")
    (ROOT/"逐张文案汇总.md").write_text("\n".join(full),encoding="utf-8")
    (ROOT/"整组发布文案.txt").write_text(GROUP_COPY,encoding="utf-8-sig")
    (SRC/"图文内容.json").write_text(json.dumps(dict(pages=PAGES,code=codes),ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    script=["# 抖音口播与分镜｜约 2 分 26 秒\n", "时码为剪辑建议，按最终录音调整。画面使用抖音竖版 01—12；展示代码页时可适当延长停留。字幕另附可编辑 SRT，尚未匹配实际录音。\n"]
    subtitles=[]
    seq=0
    for start,end,page,voice in SEGMENTS:
        script.append(f"## {timecode(start)}—{timecode(end)}｜{page:02d} {PAGES[page-1]['name']}\n\n画面：`抖音竖版/{page:02d}_{PAGES[page-1]['name']}.png`\n\n口播：{voice}\n")
        sentences=[t+"。" for t in voice.split("。") if t]
        chunks=[sentence[k:k+40] for sentence in sentences for k in range(0,len(sentence),40)]
        duration=end-start
        for j,chunk in enumerate(chunks):
            seq+=1
            a=start+duration*j//len(chunks)
            b=start+duration*(j+1)//len(chunks)
            # 按两行排字幕，防止整段话塞在一个屏幕上。
            lines=[chunk[k:k+20] for k in range(0,len(chunk),20)]
            subtitles.append(f"{seq}\n{timecode(a,True)} --> {timecode(b,True)}\n"+"\n".join(lines)+"\n")
    (ROOT/"抖音口播与分镜.md").write_text("\n".join(script),encoding="utf-8")
    (ROOT/"抖音字幕_草稿.srt").write_text("\n".join(subtitles),encoding="utf-8-sig")
    shutil.copyfile(NOTE,ROOT/"力扣题解.md")
    (ROOT/"力扣题解.txt").write_text(NOTE.read_text(encoding="utf-8"),encoding="utf-8-sig")
    shutil.copyfile(REPO/"leetcode/daily_challenge/1541.ipynb",SRC/"1541.ipynb")
    shutil.copyfile(REPO/"leetcode/note/leetcode_1541_pitfalls_and_1021_comparison.md",ROOT/"踩坑与对比笔记.md")


def main():
    for path in (ROOT,SRC,IMG,VERT,COPY): path.mkdir(parents=True,exist_ok=True)
    local_art=SRC/"学习少女插画.png"
    if not local_art.exists(): shutil.copyfile(OLD_ART,local_art)
    (SRC/"插画来源.txt").write_text("复用 1021 发布包中的学习少女插画，文件保持原样。\n沿用浅蓝、粉红、粉黄卡片；中文、代码、表格由 Pillow 排版。\n未调用新的图像生成服务。\n",encoding="utf-8-sig")
    codes={"group":(SRC/"提交版_分组.py").read_text(encoding="utf-8").strip(),"need":(SRC/"提交版_need.py").read_text(encoding="utf-8").strip()}
    for number in range(1,13):
        make(number,codes)
        print(f"Generated {number:02d}/12",flush=True)
    files=sorted(IMG.glob("*.png"))
    assert len(files)==12 and len(list(VERT.glob("*.png")))==12
    sheet=Image.new("RGB",(2160,2160),"#D4E6EC")
    for i,path in enumerate(files):
        with Image.open(path) as im:
            assert im.size==(1080,1440) and im.mode=="RGB"
            sheet.paste(im.resize((532,712),Image.Resampling.LANCZOS),((i%4)*540+4,(i//4)*720+4))
        with Image.open(VERT/path.name) as im: assert im.size==(1080,1920) and im.mode=="RGB"
    sheet.save(ROOT/"预览总览.jpg",quality=94,subsampling=0)
    write_copy(codes)
    (SRC/"排版校验.json").write_text(json.dumps(LAYOUT,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    validation=json.loads((SRC/"代码校验.json").read_text(encoding="utf-8"))
    (ROOT/"校验记录.txt").write_text(f"图片：12 张 1080×1440 RGB PNG；另有 12 张 1080×1920 抖音竖版。\n页码：01/12—12/12，独立图与竖版对应一致。\n排版：文字边界、正文高度、代码字号检查通过；代码字号不低于 29 px。\n代码：原修正版、等价紧凑版、need 版均通过独立 Dijkstra 校验。\n穷举 1—9 长度全部 {validation['exhaustive_strings']} 个括号串，另有 100 个随机用例和 3 个大规模用例。\n样例：Notebook 两种解法各通过 13 个样例。\n未实际提交力扣评测；未做性能基准。\nSRT 为剪辑草稿，时码需按实际录音校准。\n",encoding="utf-8-sig")
    readme="""# LeetCode 1541｜12 张图文发布包

- `图片/`：12 张 1080×1440 PNG，3:4，沿用 1021 图文风格。
- `抖音竖版/`：相同 12 页的 1080×1920 PNG，9:16，教学卡片完整保留。
- `力扣题解.md`、`力扣题解.txt`：完整解法在前，随后解释思路、1021 对比、踩坑、need 法、正确性和复杂度。
- `踩坑与对比笔记.md`：独立的快速复盘笔记，含最小反例、1021 迁移对照、状态含义与测试清单。
- `整组发布文案.txt`：小红书、抖音整组标题、正文、话题和评论建议。
- `文案/`、`逐张文案汇总.md`：逐页两平台文案。
- `抖音口播与分镜.md`：约 2 分 26 秒的口播稿和逐页分镜。
- `抖音字幕_草稿.srt`：可导入剪辑工具，按最终录音调整时码。
- `预览总览.jpg`：4×3 缩略图总览；发布使用各目录的独立图。
- `源文件/`：排版脚本、图文内容、原样复用插画、两种提交代码、Notebook 和校验记录。

按 01—12 上传。重点页：02 题目对照；03 左括号计数；06 真实踩坑；08—09 两个 need 分支。
代码页 05、10 可直接对照文本源文件；建议给观众足够停留时间。
只生成本地素材，未发布到力扣、小红书或抖音。
发布包位于仓库忽略的 publish/ 目录；可追踪题解与制作脚本保存在 leetcode/note/ 中。

仓库 Notebook：leetcode/daily_challenge/1541.ipynb。
仓库题解：leetcode/note/leetcode_1541_minimum_insertions.md。
制作脚本：leetcode/note/production/1541/prepare_and_verify.py、make_materials.py。
先运行 prepare_and_verify.py，再运行 make_materials.py。
图片绘制使用 Pillow；字体使用 Windows 微软雅黑与 Consolas；封面插画复用 1021 素材。
压缩包包含重新制作需要的内容，需保留图片来源目录或源文件中的复用插画。

“每日一题”为个人学习记录，没有宣称这是平台当天指定的题目。
两种解法都为 O(n) 时间、O(1) 额外空间；未声称哪一种实际更快。
对题意使用官方来源，对状态设计与贪心证明使用本次独立分析。
"""
    (ROOT/"使用说明.md").write_text(readme,encoding="utf-8")
    here=Path(__file__).resolve().parent
    for name in ("make_materials.py","prepare_and_verify.py"):
        origin=here/name
        dest=SRC/name
        if origin!=dest and origin.exists(): shutil.copyfile(origin,dest)
    archive=ROOT.parent/(ROOT.name+"_发布包.zip")
    with zipfile.ZipFile(archive,"w",zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for path in sorted(ROOT.rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts: z.write(path,path.relative_to(ROOT.parent))
    print(f"Completed: 24 PNGs, copy, notebook, solutions, ZIP ({archive.stat().st_size} bytes)",flush=True)


if __name__=="__main__":
    main()
