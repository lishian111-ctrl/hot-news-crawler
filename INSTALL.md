# 能源行业热点资讯系统 - 安装指南

## 环境要求

### 必需软件

- **Python**: 3.10 或更高版本（推荐 3.10-3.12）
- **操作系统**: Windows 10/11, Linux, macOS
- **内存**: 至少 2GB 可用内存
- **磁盘**: 至少 500MB 可用空间

### 检查 Python 版本

```bash
python --version
```

如果未安装 Python，请访问 [python.org](https://www.python.org/downloads/) 下载安装。

## 安装步骤

### 1. 克隆或下载项目

```bash
# 如果使用 git
git clone <repository-url>
cd 热点资讯

# 或者直接解压下载的文件
cd 热点资讯
```

### 2. 创建虚拟环境

```bash
cd backend
python -m venv venv
```

### 3. 激活虚拟环境

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. 安装依赖

```bash
pip install -r requirements.txt
```

依赖包括：
- FastAPI - Web 框架
- SQLAlchemy - 数据库 ORM
- Playwright - 网页爬虫
- Pandas - 数据处理
- APScheduler - 定时任务
- 其他工具库

### 5. 安装 Playwright 浏览器

```bash
playwright install
```

### 6. 创建数据目录

```bash
# 系统会自动创建，也可以手动创建
mkdir ..\data
mkdir logs
```

### 7. 初始化数据库

数据库会在首次启动时自动创建。如需手动初始化：

```bash
cd backend
venv\Scripts\activate
python -c "from database import init_db; import asyncio; asyncio.run(init_db())"
```

### 8. 导入信源数据

系统启动后，可通过 API 导入信源 Excel 文件：

```bash
# 使用 API 导入（需要系统运行中）
curl -X POST http://localhost:8000/api/v1/source/import \
  -F "file=@sources/FFML 信源.xlsx"
```

或直接在代码中导入：

```python
from services.excel import ExcelService
from models.source import Source
from sqlalchemy.orm import sessionmaker

excel_service = ExcelService()
result = excel_service.import_sources('../sources/FFML 信源.xlsx')

# 保存到数据库...
```

## 启动系统

### 方式一：使用启动脚本（推荐）

双击 `start.bat` 文件。

### 方式二：命令行启动

```bash
cd backend
venv\Scripts\activate
python main.py
```

### 方式三：使用 uvicorn 直接启动

```bash
cd backend
venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 验证安装

### 1. 检查服务状态

访问：http://localhost:8000/health

预期响应：
```json
{"status": "healthy"}
```

### 2. 查看 API 文档

访问：http://localhost:8000/docs

### 3. 测试信源接口

访问：http://localhost:8000/api/v1/source/list

## 常见问题

### Q1: 端口 8000 被占用

**解决方法**：修改 `backend/config.py` 中的端口号

```python
PORT = 8001  # 改为其他端口
```

### Q2: 数据库文件不存在

**解决方法**：检查 `data` 目录是否存在，系统会自动创建数据库文件。

```bash
# 手动创建目录
mkdir data
```

### Q3: 导入 Excel 失败

**可能原因**：
- 文件格式不正确（需要 .xlsx 格式）
- 缺少必要列（信源名称、URL）

**解决方法**：
1. 确保使用 Excel 2007+ 格式（.xlsx）
2. 检查列名是否包含"信源名称"和"URL"
3. 查看错误日志获取详细信息

### Q4: 爬虫采集失败

**可能原因**：
- 网络连接问题
- 目标网站反爬
- Playwright 未正确安装

**解决方法**：
```bash
# 重新安装 Playwright
playwright install

# 检查浏览器
playwright install chromium
```

### Q5: 中文乱码

**解决方法**：
1. 确保终端使用 UTF-8 编码
2. Windows 可执行：`chcp 65001`
3. 在 `config.py` 中设置正确的日志编码

### Q6: 依赖安装失败

**常见错误**：某些包需要编译

**解决方法**：
```bash
# 安装 Microsoft C++ Build Tools (Windows)
# 下载安装：https://visualstudio.microsoft.com/visual-cpp-build-tools/

# 或使用预编译包
pip install --only-binary :all: -r requirements.txt
```

### Q7: 定时任务不执行

**检查项**：
1. 确认 `SCHEDULER_CONFIG` 中 `enabled: True`
2. 检查日志确认调度器已启动
3. 确认采集间隔设置合理

## 卸载

```bash
# 停用虚拟环境
deactivate

# 删除虚拟环境
rm -rf backend/venv

# 删除数据库（可选）
rm data/hotspot.db

# 删除日志（可选）
rm -rf backend/logs/*
```

## 更新

```bash
cd backend
venv\Scripts\activate
git pull  # 如果使用 git
pip install -r requirements.txt --upgrade
```

## 技术支持

如遇到问题，请查看：
1. `backend/logs/app.log` - 应用日志
2. `http://localhost:8000/docs` - API 文档
3. `README.md` - 项目说明
