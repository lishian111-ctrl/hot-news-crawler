"""
项目配置文件
包含基础路径、数据库配置、热点打分规则、内容类型识别等配置
"""
import os
from pathlib import Path
from typing import List, Dict

# ==================== 基础路径配置 ====================
# 项目根目录
BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent

# 各模块目录
CRAWLER_DIR = BASE_DIR / "crawler"
MODELS_DIR = BASE_DIR / "models"
ROUTES_DIR = BASE_DIR / "routes"
SERVICES_DIR = BASE_DIR / "services"
SCHEDULER_DIR = BASE_DIR / "scheduler"
UTILS_DIR = BASE_DIR / "utils"
LOGS_DIR = BASE_DIR / "logs"
DATABASE_DIR = BASE_DIR / "database"

# 日志文件路径
LOG_FILE = LOGS_DIR / "app.log"

# 数据库文件路径
DATABASE_URL = "sqlite+aiosqlite:///" + str(ROOT_DIR / "data" / "hotspot.db")
DATABASE_SYNC_URL = "sqlite:///" + str(ROOT_DIR / "data" / "hotspot.db")

# ==================== 数据库配置 ====================
DB_POOL_SIZE = 10
DB_MAX_OVERFLOW = 20
DB_POOL_TIMEOUT = 30

# ==================== 服务器配置 ====================
HOST = "0.0.0.0"
PORT = 8001
DEBUG = True

# 前端静态文件目录
FRONTEND_DIST_DIR = ROOT_DIR / "frontend" / "dist"

# ==================== 热点打分关键词配置 ====================
# 行业关键词权重
INDUSTRY_KEYWORDS = {
    # 能源行业核心词
    "能源": 10,
    "石油": 8,
    "天然气": 8,
    "煤炭": 7,
    "电力": 9,
    "电网": 8,
    "发电": 8,
    "新能源": 9,
    "光伏": 8,
    "风电": 8,
    "核电": 9,
    "水电": 7,
    "储能": 8,
    "电池": 7,
    "氢能": 8,
    "充电桩": 6,
    
    # 政策相关
    "政策": 7,
    "规划": 6,
    "标准": 5,
    "补贴": 7,
    "碳中和": 9,
    "碳达峰": 9,
    "双碳": 9,
    
    # 市场相关
    "价格": 6,
    "市场": 5,
    "供需": 6,
    "出口": 5,
    "进口": 5,
    "产量": 5,
    "消费": 5,
    
    # 技术相关
    "技术": 5,
    "创新": 5,
    "研发": 5,
    "突破": 7,
    "效率": 5,
}

# 热点级别阈值
HOTSPOT_LEVELS = {
    "high": 50,    # 高热点
    "medium": 30,  # 中热点
    "low": 10,     # 低热点
}

# ==================== 内容类型识别配置 ====================
CONTENT_TYPES = {
    "policy": {
        "name": "政策法规",
        "keywords": ["政策", "法规", "条例", "办法", "规定", "通知", "意见", "方案"],
        "weight": 1.2
    },
    "market": {
        "name": "市场行情",
        "keywords": ["价格", "行情", "涨跌", "交易", "市场", "供需", "库存"],
        "weight": 1.1
    },
    "technology": {
        "name": "技术创新",
        "keywords": ["技术", "研发", "创新", "专利", "突破", "应用", "示范"],
        "weight": 1.0
    },
    "project": {
        "name": "项目动态",
        "keywords": ["项目", "开工", "投产", "签约", "中标", "建设", "进展"],
        "weight": 1.0
    },
    "company": {
        "name": "企业资讯",
        "keywords": ["公司", "企业", "集团", "股份", "有限", "合作", "战略"],
        "weight": 0.9
    },
    "international": {
        "name": "国际动态",
        "keywords": ["国际", "全球", "海外", "出口", "进口", "贸易", "合作"],
        "weight": 1.1
    }
}

# ==================== 源网站配置 ====================
SOURCE_WEBSITES = [
    {
        "name": "国家能源局",
        "url": "http://www.nea.gov.cn",
        "enabled": True,
        "priority": 1
    },
    {
        "name": "中国能源报",
        "url": "https://www.cnenergynews.cn",
        "enabled": True,
        "priority": 2
    },
    {
        "name": "北极星电力网",
        "url": "https://www.bjx.com.cn",
        "enabled": True,
        "priority": 3
    },
    {
        "name": "中国电力网",
        "url": "https://www.chinapower.com.cn",
        "enabled": True,
        "priority": 4
    }
]

# ==================== 爬虫配置 ====================
CRAWLER_CONFIG = {
    "timeout": 30,              # 请求超时时间（秒）
    "retry_times": 3,           # 重试次数
    "delay": 1,                 # 请求延迟（秒）
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "playwright": {
        "headless": True,
        "timeout": 60000,
    }
}

# ==================== 定时任务配置 ====================
SCHEDULER_CONFIG = {
    "crawler_interval": 3600,   # 爬虫执行间隔（秒）
    "cleanup_interval": 86400,  # 清理任务间隔（秒）
    "enabled": True
}

# ==================== CORS 配置 ====================
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
]

# ==================== API 配置 ====================
API_PREFIX = "/api/v1"
API_TITLE = "能源行业热点资讯 API"
API_VERSION = "1.0.0"
API_DESCRIPTION = "能源行业信息情报系统后端 API"
