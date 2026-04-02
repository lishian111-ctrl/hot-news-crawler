# 能源行业热点资讯系统

一个专业的能源行业信息情报系统，支持自动采集、智能打分、热点识别和资讯管理。

## 功能特点

- **多源采集**：支持 FFML、油气、海上风电等多个板块的信源采集
- **智能打分**：基于行业关键词权重的自动评分系统
- **热点识别**：根据评分自动识别高、中、低热点
- **内容去重**：基于内容哈希的自动去重功能
- **定时任务**：支持定时自动采集更新
- **API 接口**：完整的 RESTful API
- **数据导出**：支持 Excel 导入导出

## 快速开始

### 1. 安装依赖

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 启动系统

双击 `start.bat` 或在命令行执行：

```bash
cd backend
venv\Scripts\activate
python main.py
```

### 3. 访问系统

- **API 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health
- **API 接口**: http://localhost:8000/api/v1

## 目录结构

```
热点资讯/
├── backend/                 # 后端代码
│   ├── main.py             # 应用入口
│   ├── config.py           # 配置文件
│   ├── database.py         # 数据库配置
│   ├── models/             # 数据模型
│   │   ├── news.py        # 新闻模型
│   │   ├── source.py      # 信源模型
│   │   └── favorite.py    # 收藏模型
│   ├── routes/             # API 路由
│   │   ├── news.py        # 新闻接口
│   │   ├── source.py      # 信源接口
│   │   └── hot.py         # 热点接口
│   ├── crawler/            # 爬虫模块
│   │   ├── spider.py      # 通用爬虫
│   │   └── rules/         # 采集规则
│   ├── scheduler/          # 定时任务
│   │   └── tasks.py       # 采集任务
│   └── services/           # 业务服务
│       ├── excel.py       # Excel 处理
│       └── scoring.py     # 评分服务
├── data/                   # 数据目录
│   └── hotspot.db         # SQLite 数据库
├── sources/                # 信源 Excel 文件
├── scripts/                # 工具脚本
└── start.bat              # 启动脚本
```

## 技术栈

- **后端框架**: FastAPI 0.135+
- **数据库**: SQLite + SQLAlchemy 2.0+
- **异步支持**: asyncio + aiosqlite
- **爬虫**: BeautifulSoup4 + httpx
- **数据处理**: Pandas + openpyxl
- **定时任务**: APScheduler 3.10+
- **API 文档**: Swagger UI (内置)

## API 接口

### 新闻接口
- `GET /api/v1/news/list` - 获取新闻列表
- `GET /api/v1/news/{id}` - 获取新闻详情
- `GET /api/v1/hot/ranking` - 获取热点排行

### 信源接口
- `GET /api/v1/source/list` - 获取信源列表
- `GET /api/v1/source/categories` - 获取分类列表
- `POST /api/v1/source/import` - Excel 导入信源
- `GET /api/v1/source/export` - Excel 导出信源

### 收藏接口
- `GET /api/v1/favorite/list` - 获取收藏列表
- `POST /api/v1/favorite/` - 添加收藏
- `DELETE /api/v1/favorite/{id}` - 删除收藏

## 配置说明

主要配置在 `backend/config.py` 中：

- 服务器配置：端口、主机
- 数据库配置：连接字符串、连接池
- 打分规则：行业关键词权重
- 内容类型：政策法规、市场行情等
- 定时任务：采集间隔

## 数据库

系统使用 SQLite 数据库，包含以下核心表：

- `news` - 新闻表
- `source` - 信源表
- `favorite` - 收藏表
- `config` - 配置表

## 项目状态

✅ 数据库初始化
✅ 信源加载
✅ 爬虫采集
✅ API 服务
✅ 定时任务

## 许可证

MIT License
