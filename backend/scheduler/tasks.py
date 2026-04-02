"""定时任务模块
负责定时采集新闻数据
"""
import asyncio
import hashlib
from datetime import datetime
from typing import Optional, List, Dict, Any
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from loguru import logger

from config import SCHEDULER_CONFIG, SOURCE_WEBSITES
from crawler.spider import GeneralSpider
from database import AsyncSessionLocal, init_db, close_db
from models.news import News


class CrawlTask:
    def __init__(self):
        self.scheduler = None
        self.is_running = False
        self._config = {}
    
    @property
    def config(self):
        return self._config
    
    async def fetch_page(self, url, headers=None):
        import httpx
        try:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(30.0),
                follow_redirects=True,
                headers=headers or {"User-Agent": "Mozilla/5.0"}
            ) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.text
        except Exception as e:
            logger.error(f"Get page failed {url}: {e}")
            return None
    
    def compute_content_hash(self, content):
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    async def save_article(self, article_data):
        try:
            async with AsyncSessionLocal() as session:
                from sqlalchemy import select
                stmt = select(News).where(News.source_url == article_data["url"])
                result = await session.execute(stmt)
                existing = result.scalar_one_or_none()
                
                if existing:
                    logger.debug(f"Article exists, skip: {article_data['title']}")
                    return None
                
                content_hash = self.compute_content_hash(article_data.get("content", "")[:500])
                
                news = News(
                    title=article_data.get("title", ""),
                    content=article_data.get("content", ""),
                    summary=article_data.get("content", "")[:200] if article_data.get("content") else "",
                    source_url=article_data.get("url", ""),
                    publish_time=article_data.get("publish_time"),
                    category=article_data.get("category", ""),
                    content_hash=content_hash,
                )
                
                session.add(news)
                await session.commit()
                logger.info(f"Save article success: {news.title[:30]}...")
                return news
        except Exception as e:
            logger.error(f"Save article failed: {e}")
            return None
    
    async def crawl_site(self, site_config, max_pages=3):
        site_name = site_config.get("name", "unknown")
        base_url = site_config.get("url", "")
        
        if not base_url:
            logger.warning(f"Site {site_name} no URL configured")
            return 0
        
        logger.info(f"Start crawling site: {site_name} ({base_url})")
        
        spider = GeneralSpider({
            "base_url": base_url,
            "user_agent": "Mozilla/5.0",
        })
        
        count = 0
        
        for page in range(1, max_pages + 1):
            list_url = spider.get_list_url(page)
            logger.debug(f"Crawl list page: {list_url}")
            
            html = await self.fetch_page(list_url)
            if not html:
                logger.warning(f"Site {site_name} page {page} fetch failed")
                continue
            
            articles = spider.parse_list(html)
            logger.info(f"Site {site_name} page {page} parsed {len(articles)} articles")
            
            for article in articles:
                detail_url = article.get("url")
                if not detail_url:
                    continue
                
                detail_html = await self.fetch_page(detail_url)
                if not detail_html:
                    continue
                
                result = spider.parse_detail(detail_html, detail_url)
                if result:
                    article_data = {
                        "title": result.title,
                        "content": result.content,
                        "url": result.url,
                        "category": result.source,
                        "publish_time": result.publish_time,
                    }
                    saved = await self.save_article(article_data)
                    if saved:
                        count += 1
            
            await asyncio.sleep(1)
        
        logger.info(f"Site {site_name} crawl done, new articles: {count}")
        return count
    
    async def run_crawl_task(self):
        logger.info("=" * 50)
        logger.info("Start scheduled crawl task")
        logger.info(f"Task start time: {datetime.now()}")
        logger.info("=" * 50)
        
        total_count = 0
        results = {}
        
        await init_db()
        
        try:
            for site in SOURCE_WEBSITES:
                if not site.get("enabled", True):
                    logger.info(f"Site {site.get('name')} disabled, skip")
                    continue
                
                site_name = site.get("name", "unknown")
                try:
                    count = await self.crawl_site(site, max_pages=2)
                    results[site_name] = count
                    total_count += count
                except Exception as e:
                    logger.error(f"Crawl site {site_name} failed: {e}")
                    results[site_name] = 0
                
                await asyncio.sleep(2)
            
            logger.info("=" * 50)
            logger.info("Crawl task completed")
            logger.info(f"Total new articles: {total_count}")
            logger.info(f"Task end time: {datetime.now()}")
            logger.info("=" * 50)
            
        except Exception as e:
            logger.error(f"Crawl task execution failed: {e}")
        finally:
            await close_db()
        
        return {
            "total": total_count,
            "sites": results,
            "time": datetime.now().isoformat()
        }


crawl_task = CrawlTask()


async def run_crawl_task():
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
    
    logger.info(f"Scheduler started, crawl interval: {interval}s")
    return scheduler


def stop_scheduler():
    if crawl_task.scheduler:
        crawl_task.scheduler.shutdown(wait=False)
        crawl_task.is_running = False
        logger.info("Scheduler stopped")


def get_scheduler():
    return crawl_task.scheduler
