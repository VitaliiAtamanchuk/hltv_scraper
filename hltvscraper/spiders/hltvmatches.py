import scrapy

from hltvscraper.items import Match, Map


# TODO: use proxies
# TODO: user agents
class HltvmatchesSpider(scrapy.Spider):
    name = 'hltvmatches'
    allowed_domains = ['https://www.hltv.org/results']
    host = 'https://www.hltv.org'

    def start_requests(self):
        for page_index in range(110 + 1):
            yield scrapy.Request(
                f'https://www.hltv.org/results?offset={page_index*100}',
                self.parse_match_list)

    def parse_match_list(self, response):
        matches_links = response.css('.result-con a.a-reset::attr(href)').extract()
        for match_link in matches_links:
            yield scrapy.Request(self.host + match_link, self.parse_match)

    def parse_match(self, response):
        # check if all stats for all maps
        maps_stat_link = response.css('.mapholder .results a.results-stats::attr(href)').extract()
        maps_played = response.css('.mapholder .results').extract()
        if len(map_stat_link) != len(maps_played):
            return

        url = response.request.url
        date = response.css('.standard-box.teamsBox .timeAndEvent::attr(data-time-format)').extract_first()
        score = list(filter(None, [
            response.css('.standard-box.teamsBox .team .team1-gradient .lost::text').extract_first(),
            response.css('.standard-box.teamsBox .team .team1-gradient .won::text').extract_first(),
            response.css('.standard-box.teamsBox .team .team2-gradient .lost::text').extract_first(),
            response.css('.standard-box.teamsBox .team .team2-gradient .won::text').extract_first()
        ]))
        score = list(map(int, score))
        players = response.css('#all-content td.players div.gtSmartphone-only::text').extract()
        m = Match(url=url, date=date, score=score, players=players)
        yield m

        for map_stat_link in maps_stat_link:
            request = scrapy.Request(map_stat_link, self.parse_map)
            request.meta['match_url'] = url
            yield request

    def parse_map(self, response):
        match_url = response.meta['item']
        url = response.request.url
        stats_rows = response.css('.match-info-row')
        score = list(map(
            int,
            stats_rows[0].css('.right span::text')[1].extract()
        ))
        ratings = list(map(
            float,
            stats_rows[1].css('.right::text').extract_first().split(' : ')
        ))
        first_kills = list(map(
            float,
            stats_rows[2].css('.right::text').extract_first().split(' : ')
        ))
        clutches = list(map(
            float,
            stats_rows[3].css('.right::text').extract_first().split(' : ')
        ))
        m = Map(match_url=match_url, url=url, score=score, ratings=ratings,
                first_kills=first_kills, clutches=clutches)
        yield m
