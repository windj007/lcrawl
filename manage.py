#!/usr/bin/env python

import argh

from scrapy.crawler import CrawlerProcess

from lcrawl.loading import load_config
from lcrawl.spiders.main import MainSpider
from lcrawl.decision.train import convert_pickled_pages_to_csv_dataset


def work(crawl_config_file, **kwargs):
    conf = load_config(crawl_config_file)
    conf.update(kwargs)
    process = CrawlerProcess(conf)
    process.crawl(MainSpider)
    process.start()


if __name__ == "__main__":
    parser = argh.ArghParser()
    parser.add_commands([work,
                         convert_pickled_pages_to_csv_dataset])
    parser.dispatch()
