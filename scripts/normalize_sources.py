#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
信源 Excel 文件标准化脚本
统一三个信源表格格式，补充权重字段

权重映射表:
- 政府官网：10
- 国际机构：9
- 行业协会：8
- 央企国企：8
- 行业媒体：6
- 一般网站：5

统一表头格式:
序号、网站名称、分类、URL、权重、板块
"""

import pandas as pd
import os

# 权重映射表
WEIGHT_MAP = {
    '政府官网': 10,
    '国际机构': 9,
    '行业协会': 8,
    '央企国企': 8,
    '行业媒体': 6,
    '一般网站': 5,
}


def get_weight(url, category):
    """根据 URL 和分类判断权重"""
    if pd.isna(url):
        return WEIGHT_MAP['一般网站']
    
    url_str = str(url).lower()
    
    # 政府官网 (.gov.cn)
    if '.gov.cn' in url_str:
        return WEIGHT_MAP['政府官网']
    
    # 国际机构/行业协会
    if any(d in url_str for d in ['.org', 'iso.org', 'api.org', 'spe.org', '.int']):
        if '协会' in str(category) or '学会' in str(category):
            return WEIGHT_MAP['国际机构']
        return WEIGHT_MAP['行业协会']
    
    # 央企国企
    if any(k in str(category) for k in ['石油', '石化', '海油', '天然气', '电网', '电力']):
        return WEIGHT_MAP['央企国企']
    
    # 行业媒体
    if any(k in str(category) for k in ['媒体', '新闻', '杂志']):
        return WEIGHT_MAP['行业媒体']
    
    return WEIGHT_MAP['一般网站']


def normalize_gas_oil(df):
    """标准化油气行业信源"""
    cols = df.columns.tolist()
    data = []
    for i, row in df.iterrows():
        data.append({
            '序号': int(row[cols[0]]) if pd.notna(row[cols[0]]) else i + 1,
            '网站名称': row[cols[1]] if pd.notna(row[cols[1]]) else '',
            '分类': row[cols[2]] if pd.notna(row[cols[2]]) else '一般网站',
            'URL': row[cols[3]] if pd.notna(row[cols[3]]) else '',
            '权重': get_weight(row[cols[3]], row[cols[2]]),
            '板块': '油气行业'
        })
    return pd.DataFrame(data)


def normalize_offshore_wind(df):
    """标准化海上风电信源"""
    cols = df.columns.tolist()
    data = []
    for i, row in df.iterrows():
        data.append({
            '序号': int(row[cols[0]]) if pd.notna(row[cols[0]]) else i + 1,
            '网站名称': row[cols[1]] if pd.notna(row[cols[1]]) else '',
            '分类': row[cols[2]] if pd.notna(row[cols[2]]) else '一般网站',
            'URL': row[cols[4]] if pd.notna(row[cols[4]]) else '',
            '权重': get_weight(row[cols[4]], row[cols[2]]),
            '板块': '海上风电'
        })
    return pd.DataFrame(data)


def normalize_ffml(df):
    """标准化 FFML 信源"""
    cols = df.columns.tolist()
    data = []
    for i, row in df.iterrows():
        category = '行业协会' if '标准' in str(row[cols[3]]) else '国际机构'
        data.append({
            '序号': int(row[cols[0]]) if pd.notna(row[cols[0]]) else i + 1,
            '网站名称': row[cols[1]] if pd.notna(row[cols[1]]) else '',
            '分类': category,
            'URL': row[cols[2]] if pd.notna(row[cols[2]]) else '',
            '权重': get_weight(row[cols[2]], category),
            '板块': 'FFML'
        })
    return pd.DataFrame(data)


def verify(sources_dir):
    """验证处理后的信源文件"""
    print('=' * 60)
    print('信源文件验证报告')
    print('=' * 60)
    
    required_cols = ['序号', '网站名称', '分类', 'URL', '权重', '板块']
    files = [
        ('油气行业信源.xlsx', '油气行业'),
        ('海上风电信源.xlsx', '海上风电'),
        ('FFML 信源.xlsx', 'FFML'),
    ]
    
    all_ok = True
    for fn, expected_block in files:
        print()
        print(f'文件：{fn}')
        print('-' * 40)
        
        fp = os.path.join(sources_dir, fn)
        if not os.path.exists(fp):
            print(f'  [ERROR] 文件不存在')
            all_ok = False
            continue
        
        df = pd.read_excel(fp)
        cols = df.columns.tolist()
        
        if cols == required_cols:
            print(f'  [OK] 列名匹配')
        else:
            print(f'  [FAIL] 列名不匹配')
            all_ok = False
        
        print(f'  数据量：{len(df)} 条')
        
        weight_dist = df['权重'].value_counts().sort_index(ascending=False)
        print(f'  权重分布：{weight_dist.to_dict()}')
        
        blocks = df['板块'].unique().tolist()
        if blocks == [expected_block]:
            print(f'  [OK] 板块：{expected_block}')
        else:
            print(f'  [WARN] 板块：{blocks}')
    
    print()
    print('=' * 60)
    print(f'验证结果：{"全部通过" if all_ok else "存在错误"}')
    print('=' * 60)
    
    return all_ok


def main():
    base = r'E:\热点资讯'
    sources_dir = os.path.join(base, 'sources')
    
    print('=' * 60)
    print('信源 Excel 文件标准化处理')
    print('=' * 60)
    print()
    print('权重映射表:')
    for cat, w in WEIGHT_MAP.items():
        print(f'  {cat}: {w}')
    print()
    
    tasks = [
        ('油气行业信源.xlsx', normalize_gas_oil, '油气行业'),
        ('海上风电信源.xlsx', normalize_offshore_wind, '海上风电'),
        ('FFML 信源.xlsx', normalize_ffml, 'FFML'),
    ]
    
    for fn, func, block in tasks:
        print(f'处理：{fn}')
        fp = os.path.join(sources_dir, fn)
        df = pd.read_excel(fp)
        result = func(df)
        result.to_excel(fp, index=False)
        print(f'  行数：{len(result)}')
        print(f'  权重分布：{result["权重"].value_counts().sort_index(ascending=False).to_dict()}')
        print()
    
    verify(sources_dir)


if __name__ == '__main__':
    main()
