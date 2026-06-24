import streamlit as st
import pandas as pd
from collections import OrderedDict
from majors_data import MAJORS
from sd_scores import SD_SCORES

st.set_page_config(page_title='高考志愿·专业大观', page_icon='', layout='wide')
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
