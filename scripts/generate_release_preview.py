"""Generate illustrative release previews from the production legacy renderer."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.export_ecdict_styled import render

RAW = "`3`[ri'li:s] `4`-K5`2`\nn. 释放, 发泄, 豁免, 发行, 释放证书\nvt. 释放, 解除, 放松, 豁免, 免除, 发布, 放弃, 让与\nn. 发布\n[计] 版本, 发布\n`4`时态: released, releasing, releases\n(研四六托雅宝 1120/1232)"

def main():
    body = render('release', RAW.encode())
    for theme, filename in [('dark', 'layout-preview-vnext.html'), ('light', 'layout-preview-light-vnext.html')]:
        bg, fg = ('#202124', '#f2f2f7') if theme == 'dark' else ('#fafafa', '#1d1d1f')
        html = f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ECDICT v1.2.1 · {theme} 查询布局示意</title><link rel="stylesheet" href="../dictionary-source/MyDictionary.css">
<style>html{{color-scheme:{theme}}}body{{max-width:960px;margin:auto;background:{bg};color:{fg}}}.notice{{font:14px -apple-system,sans-serif;margin:20px 0 35px}}</style>
<body><p class="notice">v1.2.1 布局示意 · 非系统录屏，浏览器不模拟 macOS 原生“更多”机制。<a href="lookup-preview.md">说明</a></p>{body}</body></html>'''
        (ROOT / 'docs' / filename).write_text(html)
    # The video timeline owns opacity; retain production CSS unchanged on disk.
    css = (ROOT / 'dictionary-source/MyDictionary.css').read_text().replace('opacity: 1 !important', 'opacity: 1')
    html = '''<!doctype html><html lang="zh-CN" class="apple_client-panel"><head><meta charset="utf-8">
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script><style>''' + css + '''
@font-face{font-family:'PingFang SC';src:local('PingFang SC')}@font-face{font-family:'SFMono-Regular';src:local('SFMono-Regular')}
*{box-sizing:border-box}html,body{width:960px;height:800px;margin:0;padding:0!important;background:#202124;color:#f2f2f7;overflow:hidden}
#root{width:960px;height:800px}.scene-content{width:100%;height:100%;padding:30px 44px;display:flex;flex-direction:column;gap:18px}
.caption{font:22px -apple-system,'PingFang SC',sans-serif;color:#b9bac2;margin:0}.caption strong{color:#f2f2f7}
.panel{padding:24px 30px 30px;border:1px solid #62646b;border-radius:24px;background:#303134;overflow:hidden;font-size:25px}
.brand{font-size:30px;font-weight:600;margin:0 0 22px;color:#f2f2f7}
.entry-header h1{font-size:42px}.badge{font-size:18px!important}.sense{font-size:24px;line-height:1.45}.core-senses{margin-left:0}
.pronunciation,.meta,.badge,.inflections-title,.inflection-kind,.exam-title,.study-meta,.sense-number{color:#b9bac2!important;-webkit-text-fill-color:#b9bac2!important}
.pos,.inflection-word{color:#69b5ff!important;-webkit-text-fill-color:#69b5ff!important}.definition,h1,.sense{color:#f2f2f7!important;-webkit-text-fill-color:#f2f2f7!important}
.inflections,.exam-outline,.study-meta{margin-left:0!important;font-size:20px}.inflections-title,.inflection-kind,.exam-title{font-size:18px!important}
.badge{background:#414349!important;border-color:#6b6d74!important}.more{font-size:23px;color:#69b5ff;margin:0 0 0 auto}.footer{font-size:18px;color:#b9bac2;margin:0}
html.apple_client-panel .caption,html.apple_client-panel .footer{color:#b9bac2!important;-webkit-text-fill-color:#b9bac2!important}
html.apple_client-panel .caption strong,html.apple_client-panel .brand{color:#f2f2f7!important;-webkit-text-fill-color:#f2f2f7!important}
html.apple_client-panel .more{color:#69b5ff!important;-webkit-text-fill-color:#69b5ff!important}
html.apple_client-panel .panel .entry-details span{color:#c8c9d0!important;-webkit-text-fill-color:#c8c9d0!important;opacity:1!important}
</style></head><body><div id="root" data-composition-id="main" data-start="0" data-duration="9" data-width="960" data-height="800">
<div class="scene-content"><p class="caption"><strong>三指查询 Demo</strong> · 界面示意动画，非系统录屏</p>
<div class="panel"><p class="brand">ECDICT 简明英汉字典</p>''' + body + '''</div>
<p class="more">点击「更多」展开详情 ↓</p><p class="footer">首屏看释义 · 展开看词形、考试标签与词频</p></div></div>
<script>window.__timelines=window.__timelines||{};const tl=gsap.timeline({paused:true});
tl.from('.caption',{opacity:0,x:-8,duration:.4,ease:'power2.out'},.1)
.from('.panel',{opacity:0,scale:.985,duration:.55,ease:'power3.out'},.2)
.from('.brand',{opacity:0,duration:.3,ease:'sine.out'},.3)
.from('.entry-header',{opacity:0,y:5,duration:.35,ease:'power2.out'},.4)
.from('.pos-group:not(.pos-continuation)',{opacity:0,duration:.3,stagger:.1,ease:'sine.out'},.55)
.from('.more',{opacity:0,duration:.35,ease:'power3.out'},1.0)
.from('.footer',{opacity:0,duration:.5,ease:'sine.out'},.5)
.from('.pos-continuation,.loose-sense,.entry-details',{opacity:0,y:6,duration:.5,stagger:.08,ease:'power3.out'},3.8)
.to('.more',{opacity:0,duration:.25,ease:'power2.in'},3.6);
window.__timelines.main=tl;</script></body></html>'''
    (ROOT / 'docs/demo/index.html').write_text(html)

if __name__ == '__main__':
    main()
