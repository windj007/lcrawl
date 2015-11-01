#!/usr/bin/env python

import argh

from scrapy.crawler import CrawlerProcess

from lcrawl.loading import load_config
from lcrawl.spiders.main import MainSpider


def work(crawl_config_file, **kwargs):
    conf = load_config(crawl_config_file)
    conf.update(kwargs)
    process = CrawlerProcess(conf)
    process.crawl(MainSpider)
    process.start()


if __name__ == "__main__":
    parser = argh.ArghParser()
    parser.add_commands([work])
    parser.dispatch()
