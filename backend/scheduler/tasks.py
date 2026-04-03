"""定时任务模块
方案B：直接从数据库信源出发，用 Jina Reader 采集各信源首页新闻
"""
import asyncio
import hashlib
import re
from datetime import datetime
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse, urljoin
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from loguru import logger

from config import SCHEDULER_CONFIG
from database import AsyncSessionLocal, init_db
from models.news import News
from models.source import Source
from services.energy_filter import energy_filter


# 板块 → 新闻 category 映射
BOARD_CATEGORY_MAP = {
    '油气行业': 'oil_gas',
    '海上风电': 'wind_power',
    'FFML': 'ffml',
}

# 每板块每次采集的信源数上限（按权重取 top N）
SOURCES_PER_BOARD = 25

# 每个信源最多采集的文章数
ARTICLES_PER_SOURCE = 8


class CrawlTask:
    def __init__(self):
        self.scheduler = None
        self.is_running = False

    # ------------------------------------------------------------------ #
    #  网络请求
    # ------------------------------------------------------------------ #

    async def _get(self, url: str, timeout: float = 20.0) -> Optional[str]:
        """通用 HTTP GET，返回文本"""
        import httpx
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,*/*",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            }
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(timeout),
                follow_redirects=True,
                headers=headers,
                verify=False,
            ) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                # 自动检测编码：优先使用网页声明的编码，中文网页常用 gbk/gb2312
                encoding = resp.charset_encoding
                if not encoding or encoding.lower() in ('iso-8859-1', 'latin1'):
                    # 尝试从 content-type 或 meta 标签检测编码
                    content_type = resp.headers.get('content-type', '').lower()
                    if 'charset=gbk' in content_type or 'charset=gb2312' in content_type:
                        encoding = 'gbk'
                    elif 'charset=utf-8' in content_type:
                        encoding = 'utf-8'
                    else:
                        # 尝试用 chardet 检测编码
                        try:
                            import chardet
                            detected = chardet.detect(resp.content[:10000])
                            encoding = detected.get('encoding', 'utf-8') or 'utf-8'
                        except:
                            encoding = 'utf-8'
                # 使用检测到的编码解码
                try:
                    return resp.content.decode(encoding, errors='ignore')
                except:
                    # 解码失败时尝试 utf-8
                    return resp.content.decode('utf-8', errors='ignore')
        except Exception as e:
            logger.debug(f"HTTP 请求失败 {url}: {e}")
            return None

    async def fetch_via_jina(self, url: str) -> Optional[str]:
        """用 Jina Reader (r.jina.ai) 获取干净的 Markdown 内容"""
        import httpx
        jina_url = f"https://r.jina.ai/{url}"
        try:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(25.0),
                follow_redirects=True,
                verify=False,
            ) as client:
                resp = await client.get(jina_url)
                text = resp.text
                if resp.status_code == 200 and len(text) > 80:
                    return text
                logger.debug(f"Jina 返回异常 {resp.status_code} for {url}")
        except Exception as e:
            logger.debug(f"Jina Reader 失败 {url}: {e}")
        return None

    # ------------------------------------------------------------------ #
    #  链接提取
    # ------------------------------------------------------------------ #

    def extract_links_from_jina(self, markdown: str, source_url: str) -> List[Dict]:
        """
        从 Jina 返回的 Markdown 中提取同域名新闻链接。
        Jina 格式：[标题](url) 或 ![图片](url)
        """
        source_domain = urlparse(source_url).netloc

        # 只匹配普通链接，排除图片（![ 开头）
        pattern = r'(?<!!)\[([^\]]{5,200})\]\((https?://[^\)\s]+)\)'
        matches = re.findall(pattern, markdown)

        links = []
        seen: set = set()

        # 资源/导航排除词
        skip_url_parts = [
            'login', 'register', 'search', 'contact', 'about', 'sitemap',
            'privacy', 'terms', 'javascript', 'mailto:', 'tel:',
            'weibo', 'wechat', 'twitter', 'facebook', 'youtube', 'rss', 'feed',
            'globalassets', 'static', 'assets', 'media', 'cdn', 'img', 'image',
            'download', 'pdf', 'doc', 'xls', 'zip', 'services?', 'service/',
        ]
        # 资源文件扩展名
        skip_extensions = re.compile(
            r'\.(jpg|jpeg|png|gif|svg|webp|pdf|doc|docx|xls|xlsx|zip|rar|mp4|mp3)(\?.*)?$',
            re.IGNORECASE
        )

        for text, url in matches:
            text = text.strip()
            url = url.strip().rstrip(')')

            if url in seen or not url.startswith('http'):
                continue

            # 跳过图片/文件
            if skip_extensions.search(url):
                continue

            # 跳过明显非文章链接
            url_lower = url.lower()
            if any(k in url_lower for k in skip_url_parts):
                continue

            # 文字不能是 ![...] 图片 alt
            if text.startswith('Image') or text.startswith('图片'):
                continue

            seen.add(url)

            link_domain = urlparse(url).netloc
            base = source_domain.replace('www.', '')

            # 只保留同域或子域链接
            same_domain = (
                source_domain in link_domain
                or link_domain in source_domain
                or base in link_domain
            )
            if not same_domain:
                continue

            if len(text) < 8:
                continue

            # 评分：越像新闻文章分越高
            score = 0
            if re.search(r'\d{4}', url):         # URL 含年份
                score += 3
            if re.search(r'\d{6,8}', url):       # URL 含日期串
                score += 2
            if re.search(r'\.(s?html?|aspx|php|jsp)$', url):
                score += 1
            if len(text) > 15:
                score += 1
            if len(text) > 30:
                score += 1
            # 中文标题加分
            if re.search(r'[\u4e00-\u9fff]{4,}', text):
                score += 2

            links.append({'text': text, 'url': url, 'score': score})

        links.sort(key=lambda x: -x['score'])
        return links[:25]

    def extract_links_from_html(self, html: str, source_url: str) -> List[Dict]:
        """备用：从 HTML 中智能发现新闻链接"""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        source_domain = urlparse(source_url).netloc

        candidates = []
        for ul in soup.find_all('ul'):
            lis = ul.find_all('li')
            found = []
            for li in lis:
                a = li.find('a')
                if not a:
                    continue
                text = a.get_text(strip=True)
                href = a.get('href', '')
                if len(text) > 8 and href:
                    full_url = self._normalize_url(href, source_url)
                    if full_url:
                        found.append({'text': text, 'url': full_url, 'score': 0})
            if len(found) >= 5:
                candidates.extend(found[:20])

        seen: set = set()
        result = []
        for item in candidates:
            if item['url'] not in seen:
                seen.add(item['url'])
                result.append(item)
        return result[:25]

    def _normalize_url(self, url: str, base_url: str) -> str:
        if not url or url.startswith('#') or url.startswith('javascript'):
            return ''
        if url.startswith('http://') or url.startswith('https://'):
            return url
        if url.startswith('//'):
            return 'https:' + url
        return urljoin(base_url, url)

    # ------------------------------------------------------------------ #
    #  文章解析
    # ------------------------------------------------------------------ #

    def parse_jina_article(self, jina_text: str, fallback_title: str = '') -> tuple:
        """
        从 Jina Markdown 输出中提取 (title, content)。
        Jina 格式通常：
          Title: <标题>
          URL Source: <url>
          ...
          # <标题>
          <正文>
        """
        title = fallback_title
        content = jina_text

        lines = jina_text.strip().split('\n')

        # 方式1：Jina 元数据行 "Title: ..."
        for line in lines[:15]:
            m = re.match(r'^Title:\s*(.+)', line.strip())
            if m:
                title = m.group(1).strip()
                break

        # 方式2：第一个 # 标题
        if not title or title == fallback_title:
            for line in lines[:20]:
                line = line.strip()
                if line.startswith('# ') and len(line) > 4:
                    candidate = line[2:].strip()
                    if len(candidate) > 5:
                        title = candidate
                        break

        # 去掉 Jina 头部元数据，保留正文
        body_start = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('# ') or (i > 5 and line.strip()):
                body_start = i
                break
        content = '\n'.join(lines[body_start:]).strip()

        return title, content

    # ------------------------------------------------------------------ #
    #  数据库操作
    # ------------------------------------------------------------------ #

    def compute_hash(self, text: str) -> str:
        return hashlib.sha256(text.encode('utf-8', errors='ignore')).hexdigest()

    async def save_article(self, data: Dict) -> bool:
        """保存文章，URL 已存在则跳过，自动过滤非能源内容"""
        try:
            async with AsyncSessionLocal() as session:
                from sqlalchemy import select
                stmt = select(News).where(News.source_url == data['url'])
                existing = await session.execute(stmt)
                if existing.scalar_one_or_none():
                    return False

                title = (data.get('title') or '').strip()
                if not title or len(title) < 4:
                    return False

                content = data.get('content', '')
                source_name = data.get('source_name', '')

                # 【能源内容筛选】过滤掉与能源无关的内容
                is_energy_related, category = energy_filter.is_energy_related(title, content)

                # 如果是政府网站，适当放宽条件
                is_gov_source = energy_filter.is_government_source(source_name, data.get('url', ''))

                # 非能源内容且非政府来源，直接过滤
                if not is_energy_related and not is_gov_source:
                    logger.debug(f"过滤非能源内容：{title[:50]}")
                    return False

                # 计算相关性得分
                relevance_score = energy_filter.calculate_relevance_score(title, content, source_name)

                # 相关性得分太低的内容过滤掉（政府来源可放宽）
                min_score = 5 if is_gov_source else 15
                if relevance_score < min_score:
                    logger.debug(f"相关性得分过低 ({relevance_score})：{title[:50]}")
                    return False

                news = News(
                    title=title,
                    content=content,
                    summary=content[:300] if content else '',
                    source_url=data['url'],
                    source_id=data.get('source_id'),
                    publish_time=data.get('publish_time') or datetime.now(),
                    category=data.get('category', ''),
                    score=relevance_score,
                    content_hash=self.compute_hash(content[:500] if content else title),
                )
                session.add(news)
                await session.commit()
                logger.debug(f"新增：{title[:50]} (类别:{category}, 得分:{relevance_score})")
                return True
        except Exception as e:
            logger.error(f"保存文章失败：{e}")
            return False


    # ------------------------------------------------------------------ #
    #  单信源采集（方案 B 核心）
    # ------------------------------------------------------------------ #

    async def crawl_source(self, source_url: str, source_name: str,
                           category: str, source_id: int) -> int:
        """
        方案 B：用 Jina Reader 采集单个信源
        1. 抓信源首页 → 提取新闻链接
        2. 逐篇抓文章 → 保存
        """
        logger.info(f"  > {source_name}")

        # Step 1：用 Jina 抓首页
        homepage_md = await self.fetch_via_jina(source_url)

        if homepage_md:
            links = self.extract_links_from_jina(homepage_md, source_url)
        else:
            # Jina 失败 → 直接 HTTP + HTML 解析
            html = await self._get(source_url)
            if not html:
                logger.debug(f"    无法访问: {source_url}")
                return 0
            links = self.extract_links_from_html(html, source_url)

        if not links:
            logger.debug(f"    未发现新闻链接: {source_name}")
            return 0

        logger.debug(f"    发现 {len(links)} 个候选链接")

        count = 0
        for link in links[:ARTICLES_PER_SOURCE]:
            url = link.get('url', '')
            fallback_title = link.get('text', '')

            if not url or not url.startswith('http'):
                continue

            # Step 2：抓文章详情
            article_md = await self.fetch_via_jina(url)
            if article_md:
                title, content = self.parse_jina_article(article_md, fallback_title)
            else:
                # 降级：直接 HTTP
                html = await self._get(url)
                if not html:
                    continue
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html, 'html.parser')
                title_el = soup.find('h1') or soup.find('h2') or soup.find('title')
                title = title_el.get_text(strip=True) if title_el else fallback_title
                paras = soup.find_all('p')
                content = '\n'.join(p.get_text(strip=True) for p in paras if len(p.get_text(strip=True)) > 20)

            saved = await self.save_article({
                'title': title,
                'content': content,
                'url': url,
                'category': category,
                'source_id': source_id,
                'score': 15,
            })
            if saved:
                count += 1

            await asyncio.sleep(0.4)

        return count

    # ------------------------------------------------------------------ #
    #  完整采集任务
    # ------------------------------------------------------------------ #

    async def run_crawl_task(self) -> Dict:
        """
        方案 B 主任务：
        - 按板块从数据库取 top-N（权重最高）的信源
        - 逐一调用 crawl_source
        """
        from sqlalchemy import select

        logger.info("=" * 55)
        logger.info(f"采集任务开始 [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
        logger.info(f"策略：Jina Reader，每板块 {SOURCES_PER_BOARD} 信源，每源 {ARTICLES_PER_SOURCE} 篇")
        logger.info("=" * 55)

        total = 0
        results: Dict[str, int] = {}

        async with AsyncSessionLocal() as session:
            for board, category in BOARD_CATEGORY_MAP.items():
                stmt = (
                    select(Source)
                    .where(Source.board == board)
                    .order_by(Source.weight.desc())
                    .limit(SOURCES_PER_BOARD)
                )
                result = await session.execute(stmt)
                sources = result.scalars().all()

                logger.info(f"[{board}] 选取 {len(sources)} 个信源开始采集...")

                board_total = 0
                for source in sources:
                    try:
                        n = await self.crawl_source(
                            source_url=source.url,
                            source_name=source.name,
                            category=category,
                            source_id=source.id,
                        )
                        results[source.name] = n
                        board_total += n
                        total += n
                    except Exception as e:
                        logger.error(f"    采集 {source.name} 异常: {e}")
                        results[source.name] = 0

                    await asyncio.sleep(0.3)

                logger.info(f"[{board}] 完成，新增 {board_total} 篇")

        logger.info(f"采集任务完成，共新增 {total} 篇")
        logger.info("=" * 55)
        return {"total": total, "sites": results, "time": datetime.now().isoformat()}


crawl_task = CrawlTask()


async def run_crawl_task() -> Dict:
    return await crawl_task.run_crawl_task()


def start_scheduler():
    scheduler = AsyncIOScheduler()
    interval = SCHEDULER_CONFIG.get("crawler_interval", 3600)
    scheduler.add_job(
        run_crawl_task,
        trigger=IntervalTrigger(seconds=interval),
        id="crawl_task",
        name="News Crawl Task",
        replace_existing=True,
    )
    scheduler.start()
    crawl_task.scheduler = scheduler
    crawl_task.is_running = True
    logger.info(f"调度器已启动，采集间隔: {interval}s")
    return scheduler


def stop_scheduler():
    if crawl_task.scheduler:
        crawl_task.scheduler.shutdown(wait=False)
        crawl_task.is_running = False
        logger.info("调度器已停止")


def get_scheduler():
    return crawl_task.scheduler
