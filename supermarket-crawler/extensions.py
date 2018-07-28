from scrapy import signals

from .models import Session, CrawlerStats


class StatsLogger(object):

    def __init__(self, stats):
        self.stats = stats

    @classmethod
    def from_crawler(cls, crawler):
        ext = cls(crawler.stats)
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)
        return ext

    def spider_closed(self, spider):
        session = Session()
        stats = self.stats.get_stats()
        session.add(CrawlerStats(
            downloader_request_bytes=stats.get("downloader/request_bytes", None),
            downloader_request_count=stats.get("downloader/request_count", None),
            downloader_response_bytes=stats.get("downloader/response_bytes", None),
            downloader_response_count=stats.get("downloader/response_count", None),
            dupefilter_filtered=stats.get("dupefilter/filtered", None),
            finish_reason=stats.get("finish_reason", None),
            finish_time=stats.get("finish_time", None),
            item_scraped_count=stats.get("item_scraped_count", None),
            log_count_debug=stats.get("log_count/DEBUG", None),
            log_count_info=stats.get("log_count/INFO", None),
            memusage_max=stats.get("memusage/max", None),
            memusage_startup=stats.get("memusage/startup", None),
            request_depth_max=stats.get("request_depth_max", None),
            response_received_count=stats.get("response_received_count", None),
            scheduler_dequeued=stats.get("scheduler/dequeued", None),
            scheduler_dequeued_memory=stats.get("scheduler/dequeued_memory", None),
            scheduler_enqueued=stats.get("scheduler/enqueued", None),
            scheduler_enqueued_memory=stats.get("scheduler/enqueued/memory", None),
            start_time=stats.get("start_time", None)
        ))
        session.commit()
