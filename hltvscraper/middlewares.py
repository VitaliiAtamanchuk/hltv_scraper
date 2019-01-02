import random

from scrapy import signals

from hltvscraper.user_agents import user_agents


class RotatingProxyUserAgentMiddleware(object):
    """User-Agent"""

    def __init__(self):
        self.requests_metas = []

        for proxy in proxies:
            self.requests_metas.append({
                'proxy': proxy,
                'agent': random.choice(user_agents)
            })

    def process_request(self, request, spider):
        meta = random.choice(self.requests_metas)
        request.meta['proxy'] = meta['proxy']
        request.headers["User-Agent"] = meta['agent']
