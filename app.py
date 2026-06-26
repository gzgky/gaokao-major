import streamlit as st
import pandas as pd
from collections import OrderedDict
from majors_data import MAJORS
from sd_scores import SD_SCORES
import importlib, match_data
importlib.reload(match_data)
from match_data import MATCH_DATA

st.set_page_config(page_title='高考志愿·专业大观', page_icon='', layout='wide')

# ═══════════ 模式切换 ═══════════
mode = st.sidebar.radio('模式', ['专业浏览', '志愿匹配'], horizontal=False)

if mode == '志愿匹配':
    st.title('志愿匹配')
    st.caption('输入位次，自动匹配冲稳保学校。数据来源：2025年山东省投档表。')

    col1, col2 = st.columns(2)
    with col1:
        rank = st.number_input('你的位次', 1000, 350000, 195000, step=1000, help='位次比分数更稳定，是报志愿最核心的参考')
    with col2:
        subjects = st.multiselect('选科', ['物理', '化学', '生物', '历史', '地理', '政治'], default=['物理', '化学', '地理'])

    region = st.radio('地域', ['全部', '仅省内', '仅省外'], horizontal=True)

    has_physics = '物理' in subjects
    has_chemistry = '化学' in subjects

    # ── 匹配逻辑（纯位次驱动） ──
    # rank_diff = 你的位次 - 学校录取位次
    # 正数: 学校位次更好(你落后) → 需要冲
    # 负数: 你的位次更好(你领先) → 保底
    results = []
    for item in MATCH_DATA:
        school, tier, province, major, r25 = item
        if region == '仅省内' and province != '山东': continue
        if region == '仅省外' and province == '山东': continue
        rank_diff = rank - r25
        if rank_diff < -40000 or rank_diff > 40000:
            continue
        if 5000 < rank_diff <= 40000:
            label = '冲'    # 学校位次比你明显好，需要冲
        elif -10000 <= rank_diff <= 5000:
            label = '稳'    # 位次接近，匹配
        else:
            label = '保'    # 你的位次比学校好很多，保底
        results.append((label, school, tier, province, major, r25, rank_diff))

    results.sort(key=lambda x: x[6])

    # ── 统计 ──
    chong = [r for r in results if r[0] == '冲']
    wen = [r for r in results if r[0] == '稳']
    bao = [r for r in results if r[0] == '保']
    c1, c2, c3 = st.columns(3)
    c1.metric('🟡 冲', f'{len(chong)}个', f'学校位次 {rank-40000}~{rank-5000}（比你靠前）')
    c2.metric('🟢 稳', f'{len(wen)}个', f'学校位次 {rank-5000}~{rank+10000}（接近）')
    c3.metric('🔵 保', f'{len(bao)}个', f'学校位次 {rank+10000}~{rank+40000}（比你靠后）')

    st.divider()

    # ── 专业分类函数 ──
    def classify(major_name):
        """根据专业名返回 (门类, 专业大类)"""
        kw = major_name
        # 工学
        if any(k in kw for k in ['计算机','软件','网络','信息安全','人工智能','数据科学','大数据','物联网','数字媒体','智能科学']):
            return ('工学', '计算机类')
        if any(k in kw for k in ['电气','电网','电力']):
            return ('工学', '电气类')
        if any(k in kw for k in ['电子信息','电子科学','通信','集成电路','微电子','光电','电磁']):
            return ('工学', '电子信息类')
        if any(k in kw for k in ['自动化','机器人','控制']):
            return ('工学', '自动化类')
        if any(k in kw for k in ['机械','车辆','机电','工业设计','制造','过程装备']):
            return ('工学', '机械类')
        if any(k in kw for k in ['土木','建筑','城乡规划','风景园林','给排水','建环','暖通']):
            return ('工学', '土建类')
        if any(k in kw for k in ['能源','动力','储能','新能源','核工程','制冷']):
            return ('工学', '能源动力类')
        if any(k in kw for k in ['材料','冶金','高分子','无机非']):
            return ('工学', '材料类')
        if any(k in kw for k in ['化工','化学工程','制药','化学与制药','精细化工']):
            return ('工学', '化工制药类')
        if any(k in kw for k in ['交通','运输','轨道交通','航海','航空','飞行器','航天','机场','适航']):
            return ('工学', '交通与航空类')
        if any(k in kw for k in ['环境','环保','生态']):
            return ('工学', '环境类')
        if any(k in kw for k in ['水利','水文','港口','海洋','船舶']):
            return ('工学', '水利与海洋类')
        if any(k in kw for k in ['食品','酿酒','乳品']):
            return ('工学', '食品类')
        if any(k in kw for k in ['生物医学','医疗器械','假肢']):
            return ('工学', '生物医学工程类')
        if any(k in kw for k in ['测控','仪器','精密']):
            return ('工学', '仪器类')
        if any(k in kw for k in ['地质','勘查','采矿','矿物','石油','安全','测绘','遥感','地理信息','GIS']):
            return ('工学', '地矿测绘类')
        if any(k in kw for k in ['纺织','轻化','包装','印刷']):
            return ('工学', '轻纺类')
        if any(k in kw for k in ['工程力学','力学']):
            return ('工学', '力学类')
        if any(k in kw for k in ['生物工程','生物技术','生物制药','发酵']):
            return ('工学', '生物工程类')
        # 理学
        if any(k in kw for k in ['数学','信息与计算','数理']):
            return ('理学', '数学类')
        if any(k in kw for k in ['物理','应用物理','核物理']):
            return ('理学', '物理学类')
        if any(k in kw for k in ['化学(','应用化学']):
            return ('理学', '化学类')
        if any(k in kw for k in ['生物科学','生物技术','生态学','生物信息']):
            return ('理学', '生物科学类')
        if any(k in kw for k in ['统计','数据科学']):
            return ('理学', '统计学类')
        if any(k in kw for k in ['地理科学','地理信息','自然地理','人文地理']):
            return ('理学', '地理科学类')
        if any(k in kw for k in ['大气','气象','海洋科学','地球物理','地质学','天文']):
            return ('理学', '地球与空间类')
        # 医学
        if any(k in kw for k in ['临床','麻醉','医学影像','眼视光','精神医学','儿科学','放射医学']):
            return ('医学', '临床医学类')
        if any(k in kw for k in ['口腔']):
            return ('医学', '口腔医学类')
        if any(k in kw for k in ['中医','针灸','推拿','中西医']):
            return ('医学', '中医学类')
        if any(k in kw for k in ['药学','药物','临床药学','药剂','药事管理']):
            return ('医学', '药学类')
        if any(k in kw for k in ['护理','助产']):
            return ('医学', '护理学类')
        if any(k in kw for k in ['预防医学','公共卫生','卫生检验','妇幼']):
            return ('医学', '公卫与预防类')
        if any(k in kw for k in ['医学检验','医学技术','康复治疗','眼视光学','口腔医学技术']):
            return ('医学', '医学技术类')
        # 农学
        if any(k in kw for k in ['农学','植物','园艺','种子','烟草','茶学','农艺']):
            return ('农学', '植物生产类')
        if any(k in kw for k in ['动物医学','兽医','动物药学','动植物检疫']):
            return ('农学', '动物医学类')
        if any(k in kw for k in ['动物科学','水产','蚕学','蜂学']):
            return ('农学', '动物与水产类')
        if any(k in kw for k in ['林学','园林','森林','草业','草坪']):
            return ('农学', '林学与草学类')
        # 经济学
        if any(k in kw for k in ['金融','保险','投资','精算']):
            return ('经济学', '金融学类')
        if any(k in kw for k in ['经济学','国民经济','数字经济']):
            return ('经济学', '经济学类')
        if any(k in kw for k in ['国际经济','贸易','商务经济']):
            return ('经济学', '经济与贸易类')
        if any(k in kw for k in ['财政','税收']):
            return ('经济学', '财政学类')
        # 管理学
        if any(k in kw for k in ['会计','审计','财务']):
            return ('管理学', '会计与财务类')
        if any(k in kw for k in ['工商管理','市场营销','人力资源','文化产业','物业管理']):
            return ('管理学', '工商管理类')
        if any(k in kw for k in ['管理科学','信息管理','工程管理','大数据管理','应急管理']):
            return ('管理学', '管理科学与工程类')
        if any(k in kw for k in ['公共管理','行政管理','劳动与社会保障','土地资源','城市管理']):
            return ('管理学', '公共管理类')
        if any(k in kw for k in ['物流','供应链','采购']):
            return ('管理学', '物流与供应链类')
        if any(k in kw for k in ['电子商务','跨境电商']):
            return ('管理学', '电子商务类')
        if any(k in kw for k in ['旅游','酒店','会展']):
            return ('管理学', '旅游管理类')
        # 法学
        if any(k in kw for k in ['法学','知识产权','监狱学']):
            return ('法学', '法学类')
        if any(k in kw for k in ['政治','外交','国际政治','国际事务']):
            return ('法学', '政治学类')
        if any(k in kw for k in ['社会学','社会','家政','老年']):
            return ('法学', '社会学类')
        if any(k in kw for k in ['马克思主义','思想政治教育']):
            return ('法学', '马克思主义理论类')
        # 文学
        if any(k in kw for k in ['汉语言','汉语国际','中国语言','应用语言学','古典文献']):
            return ('文学', '中国语言文学类')
        if any(k in kw for k in ['英语','翻译','商务英语','日语','韩语','德语','法语','西班牙语','俄语','阿拉伯语','葡萄牙语']):
            return ('文学', '外国语言文学类')
        if any(k in kw for k in ['新闻','传播','广告','网络与新','广播电视','编辑出版']):
            return ('文学', '新闻传播学类')
        # 教育学
        if any(k in kw for k in ['教育','学前','小学教育','特殊教育','教育技术','科学教育']):
            return ('教育学', '教育学类')
        if any(k in kw for k in ['心理','应用心理']):
            return ('教育学', '心理学类')
        if any(k in kw for k in ['体育','运动','武术','休闲体育']):
            return ('教育学', '体育学类')
        # 历史学
        if any(k in kw for k in ['历史','考古','文物','博物馆','文物保护']):
            return ('历史学', '历史学类')
        # 哲学
        if any(k in kw for k in ['哲学','逻辑学','伦理学','宗教学']):
            return ('哲学', '哲学类')
        # 艺术学
        if any(k in kw for k in ['美术','绘画','雕塑','书法','中国画']):
            return ('艺术学', '美术学类')
        if any(k in kw for k in ['设计','视觉传达','环境设计','产品设计','服装','数字媒体艺术','艺术与科技']):
            return ('艺术学', '设计学类')
        if any(k in kw for k in ['音乐','舞蹈','表演','戏剧','电影','播音','编导','导演']):
            return ('艺术学', '戏剧与影视类')
        return ('其他', '其他类')

    # ── 三栏展示 ──
    if not results:
        st.warning('没有匹配到学校专业，请调整位次')
    else:
        tab_chong, tab_wen, tab_bao = st.tabs([f'🟡 冲 ({len(chong)}个)', f'🟢 稳 ({len(wen)}个)', f'🔵 保 ({len(bao)}个)'])

        for tab, data_list, color in [
            (tab_chong, chong, '#e67e22'),
            (tab_wen, wen, '#27ae60'),
            (tab_bao, bao, '#2980b9'),
        ]:
            with tab:
                if not data_list:
                    st.info('无匹配结果')
                else:
                    # 按门类→大类分组
                    from collections import defaultdict
                    tree = defaultdict(lambda: defaultdict(list))
                    for r in data_list:
                        _, school, tier, _, major, r25, rank_diff = r
                        cat, grp = classify(major)
                        tree[cat][grp].append(r)

                    tier_badge = {'985': '🔴', '211': '🔵', '双非': '⚪', '学院': '⚫'}

                    cat_order = ['工学','理学','医学','经济学','管理学','法学','文学','教育学','农学','历史学','哲学','艺术学','其他']
                    for cat in cat_order:
                        if cat not in tree: continue
                        grps = tree[cat]
                        total_in_cat = sum(len(v) for v in grps.values())
                        with st.expander(f'{cat}（{len(grps)}个大类，{total_in_cat}个）', expanded=total_in_cat <= 30):
                            for grp in sorted(grps.keys()):
                                items = grps[grp]
                                with st.expander(f'{grp}（{len(items)}个）', expanded=len(items) <= 10):
                                    cols = st.columns(2)
                                    for i, item in enumerate(items):
                                        _, school, tier, province, major, r25, rank_diff = item
                                        badge = tier_badge.get(tier, '⚪')
                                        prov_tag = '<span style="background:#27ae60;color:#fff;padding:1px 6px;border-radius:8px;font-size:0.7em">省内</span>' if province == '山东' else '<span style="background:#7f8c8d;color:#fff;padding:1px 6px;border-radius:8px;font-size:0.7em">省外</span>'
                                        diff_str = f'你领先{abs(rank_diff)}名' if rank_diff < 0 else f'你落后{rank_diff}名'
                                        with cols[i % 2]:
                                            st.markdown(f"""
                                            <div style='background:#fafafa;padding:10px 12px;border-radius:6px;border-left:3px solid {color};margin:2px 0'>
                                            <b style='font-size:0.95em;color:#222'>{school}</b> <span style='font-size:0.75em;color:#888'>{badge}{tier}</span> {prov_tag}<br>
                                            <span style='font-size:0.9em;color:#333'>{major}</span><br>
                                            <span style='font-size:0.8em;color:#666'>位次:{r25} ({diff_str})</span>
                                            </div>
                                            """, unsafe_allow_html=True)

    # ── 汇总表 ──
    st.divider()
    st.subheader('完整匹配列表')
    if results:
        df_all = pd.DataFrame(results, columns=['层次', '学校', '层次标签', '省份', '专业', '2025位次', '位次差'])
        df_display = df_all[['层次', '学校', '省份', '专业', '2025位次', '位次差']].copy()
        st.dataframe(
            df_display.sort_values(['层次', '2025位次'], ascending=[True, True]),
            use_container_width=True, hide_index=True,
            column_config={
                '2025位次': st.column_config.NumberColumn(format='%d'),
                '位次差': st.column_config.NumberColumn(format='%d'),
            },
        )

    st.stop()

# ═══════════ 以下为专业浏览模式 ═══════════
st.title('高考志愿·专业大观')
st.caption('每个具体专业 · 完整信息摊开看。数据持续补充中。')

# ═══════════ 侧边栏筛选 ═══════════
st.sidebar.header('筛选条件')

categories = sorted(set(m['category'] for m in MAJORS))
sel_categories = st.sidebar.multiselect('门类', categories, default=categories)

study_filter = st.sidebar.selectbox(
    '深造要求', ['全部', '本科够用', '建议读研', '必须读研读博'],
)
outlook_filter = st.sidebar.selectbox(
    '行业前景', ['全部', '上升赛道', '稳定', '谨慎选择'],
)

# ═══════════ 搜索 ═══════════
search = st.text_input('搜索专业', placeholder='例如：软件工程、口腔医学、新能源材料...')

# ═══════════ 筛选逻辑 ═══════════
def match_study(m, f):
    if f == '全部': return True
    if f == '本科够用': return '本科够用' in m['study'] or m['study'].startswith('本科')
    if f == '建议读研': return '建议读研' in m['study'] or '建议读硕' in m['study']
    if f == '必须读研读博': return '必须' in m['study'] or '强烈建议读研' in m['study']
    return True

def match_outlook(m, f):
    if f == '全部': return True
    if f == '上升赛道': return any(kw in m['outlook'] for kw in ['上升','爆发','增长','看好','利好','上升期','景气','风口'])
    if f == '稳定': return any(kw in m['outlook'] for kw in ['稳定','刚需','持续','长期'])
    if f == '谨慎选择': return any(kw in m['outlook'] for kw in ['谨慎','下行','收缩','饱和','劝退','不热门','泡沫'])
    return True

filtered = [
    m for m in MAJORS
    if m['category'] in sel_categories
    and match_study(m, study_filter)
    and match_outlook(m, outlook_filter)
    and (search == '' or search in m['name'] or search in m['group'] or search in m['category'])
]

st.sidebar.markdown(f'**匹配 {len(filtered)} / {len(MAJORS)} 个专业**')

# ═══════════ 分组统计 ═══════════
cat_counts = {}
for m in filtered:
    cat_counts[m['category']] = cat_counts.get(m['category'], 0) + 1
st.markdown('### 门类分布')
cols = st.columns(len(cat_counts) if cat_counts else 1)
for i, (cat, cnt) in enumerate(sorted(cat_counts.items())):
    cols[i % len(cols)].metric(cat, f'{cnt}个')
st.divider()

# ═══════════ 按门类→大类分组展示 ═══════════
cat_colors = {
    '哲学': '#9b59b6', '经济学': '#e74c3c', '法学': '#e67e22',
    '教育学': '#2ecc71', '文学': '#1abc9c', '历史学': '#8e44ad',
    '理学': '#3498db', '工学': '#2980b9', '农学': '#27ae60',
    '医学': '#c0392b', '管理学': '#f39c12', '艺术学': '#e91e63',
}

# 按门类分组
for cat in sorted(set(m['category'] for m in filtered), key=lambda c: list(cat_colors.keys()).index(c) if c in cat_colors else 99):
    cat_majors = [m for m in filtered if m['category'] == cat]
    color = cat_colors.get(cat, '#95a5a6')

    # 在大类内分组
    groups = OrderedDict()
    for m in cat_majors:
        g = m['group']
        if g not in groups:
            groups[g] = []
        groups[g].append(m)

    for group_name, group_majors in groups.items():
        n = len(group_majors)
        with st.expander(f'{cat} · {group_name}（{n}个专业）', expanded=n <= 2):
            for m in group_majors:
                with st.container():
                    # 标题行
                    st.markdown(
                        f"#### <span style='color:{color}'>{m['name']}</span>",
                        unsafe_allow_html=True,
                    )

                    tab1, tab2, tab3, tab4 = st.tabs(['学什么 & 深造', '就业 & 薪资', '前景 & 院校', '适合谁 & 劝退'])

                    with tab1:
                        col_a, col_b = st.columns([6, 4])
                        with col_a:
                            st.caption('核心课程')
                            st.markdown(f"<div style='background:#f8f9fa;padding:12px;border-radius:8px;font-size:0.9em;line-height:1.8;color:#222'>{m['courses']}</div>", unsafe_allow_html=True)
                        with col_b:
                            st.caption('深造建议')
                            icon = '🟢' if '本科够用' in m['study'][:6] else ('🟡' if '建议' in m['study'][:4] else '🔴')
                            st.info(f'{icon} {m["study"]}')

                    with tab2:
                        col_a, col_b = st.columns([6, 4])
                        with col_a:
                            st.caption('就业方向')
                            st.markdown(f"<div style='background:#f8f9fa;padding:12px;border-radius:8px;font-size:0.9em;line-height:1.8;color:#222'>{m['jobs']}</div>", unsafe_allow_html=True)
                        with col_b:
                            st.caption('薪资水平')
                            st.success(m['salary'])

                    with tab3:
                        col_a, col_b = st.columns([6, 4])
                        with col_a:
                            st.caption('行业前景')
                            outlook_icon = '📈' if any(kw in m['outlook'] for kw in ['上升','爆发','增长','看好','利好','上升期','景气','风口']) else ('📊' if any(kw in m['outlook'] for kw in ['稳定','刚需','持续','长期']) else '⚠️')
                            st.markdown(f'### {outlook_icon}')
                            st.markdown(m['outlook'])
                        with col_b:
                            st.caption('代表院校')
                            st.markdown(f"<div style='background:#fff3e0;padding:12px;border-radius:8px;font-size:0.85em;line-height:1.6;color:#222'>{m['schools']}</div>", unsafe_allow_html=True)

                    with tab4:
                        col_a, col_b = st.columns([6, 4])
                        with col_a:
                            st.caption('适合什么样的人')
                            st.markdown(f"<div style='background:#e8f5e9;padding:12px;border-radius:8px;font-size:0.9em;line-height:1.8;color:#222'>{m['suits']}</div>", unsafe_allow_html=True)
                        with col_b:
                            st.caption('⚠️ 劝退点')
                            st.warning(m['warning'])

                    # 山东录取数据参考
                    sd = SD_SCORES.get(m['name'], [])
                    if sd:
                        with st.expander(f'📋 山东2024录取参考 — {m["name"]}（{len(sd)}所学校）', expanded=False):
                            df_sd = pd.DataFrame(sd, columns=['学校', '层次', '最低分', '最低位次'])
                            st.dataframe(
                                df_sd,
                                use_container_width=True,
                                hide_index=True,
                                column_config={
                                    '最低分': st.column_config.NumberColumn('最低分', format='%d'),
                                    '最低位次': st.column_config.NumberColumn('最低位次', format='%d'),
                                },
                            )
                            st.caption('分数为2024年山东普通类常规批第1次志愿投档最低分（估算），仅供参考')

                    st.markdown('---')

# ═══════════ 底部 ═══════════
if not filtered:
    st.info('没有匹配的专业，换一下筛选条件试试。')

st.caption(f'共收录 {len(MAJORS)} 个具体专业 | 12个门类全覆盖 | 数据持续补充中 | 仅供报考参考，请结合个人情况判断')
