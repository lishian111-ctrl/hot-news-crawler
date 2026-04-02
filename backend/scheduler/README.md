# 定时任务调度模块

## 文件说明

- `__init__.py` - 模块初始化文件
- `tasks.py` - 采集任务实现
- `run_task.py` - 独立运行脚本（供 Windows 任务计划调用）
- `windows_task.xml` - Windows 任务计划配置文件

## 使用方式

### 1. FastAPI 应用内启动（推荐）

启动 FastAPI 应用时会自动启动定时任务调度器：

```bash
cd E:/热点资讯/backend
python main.py
```

或者使用 uvicorn：

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Windows 任务计划程序

#### 方式一：使用命令行注册

以管理员身份运行 PowerShell：

```powershell
# 导入任务计划
schtasks /Create /TN "能源热点资讯采集" /TR "python E:/热点资讯/backend/scheduler/run_task.py" /SC MINUTE /MO 30 /RU SYSTEM /RL HIGHEST /F
```

#### 方式二：使用 XML 配置文件

以管理员身份运行 PowerShell：

```powershell
# 导入任务计划
Register-ScheduledTask -Xml (Get-Content -Path "E:/热点资讯/backend/scheduler/windows_task.xml" -Raw) -TaskName "能源热点资讯采集任务"
```

### 3. 手动执行采集任务

```bash
cd E:/热点资讯/backend
python scheduler/run_task.py
```

## 配置说明

在 `config.py` 中修改采集间隔：

```python
SCHEDULER_CONFIG = {
    "crawler_interval": 3600,   # 爬虫执行间隔（秒），默认 1 小时
    "cleanup_interval": 86400,  # 清理任务间隔（秒）
    "enabled": True
}
```

## 日志查看

日志文件位于 `E:/热点资讯/backend/logs/` 目录：
- `app.log` - 应用日志
- `error.log` - 错误日志
- `crawler.log` - 爬虫日志
