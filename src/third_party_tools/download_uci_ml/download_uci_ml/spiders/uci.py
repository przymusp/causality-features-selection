# -*- coding: utf-8 -*-
import scrapy
import os


class UciSpider(scrapy.Spider):
    name = "uci"
    allowed_domains = ["archive.ics.uci.edu"]
    start_urls = ['https://archive.ics.uci.edu/ml/datasets.html?format=&task=&att=&area=&numAtt=&numIns=&type=ts&sort=nameUp&view=table']

    def parse(self, response):
        list_of_repositories = set(response.xpath("//a[contains(@href,'datasets/')]/@href").extract())
        base_ds_url = 'https://archive.ics.uci.edu/ml/'

        self.logger.info('Found %d datasets', len(list_of_repositories))
        for ds in list_of_repositories:
            next_page = base_ds_url + ds
            yield scrapy.Request(next_page, callback=self.parse_dataset_info)

    def parse_dataset_info(self, response):
        page = response.url.split("/")[-1]
        self.logger.info('Parsing dataset %s', page)
        out_dir = "../../../data/"+page+"/"
        os.makedirs(out_dir,exist_ok=True)
        with open(out_dir+ page+".html", 'wb') as f:
            f.write(response.body)
        list_of_directories = response.xpath('//a/font[contains(text(), "Data Folder")]/../@href').extract()
        for ds in list_of_directories:
            ds = ds.split("/")[1:]
            ds = "/".join(ds)
            next_page = "https://archive.ics.uci.edu/ml/"+ ds
            request = scrapy.Request(next_page, callback=self.parse_dataset_files)
            request.meta['out_dir'] = out_dir
            yield request

    def parse_dataset_files(self, response):
        self.logger.info('Downloading files to %s', response.meta['out_dir'])
        list_of_files = response.xpath("//td/a[contains(@href, %s)]/@href"%(response.url.split('/')[-2])).extract()
        self.logger.info('List of files %s', list_of_files)
        for f in list_of_files:
            next_page = response.url + f
            request = scrapy.Request(next_page, callback=self.save_dataset_files)
            request.meta['out_dir'] = response.meta['out_dir']
            yield request

    def save_dataset_files(self, response):
        path = response.meta['out_dir'] + response.url.split("/")[-1]
        with open(path, "wb") as f:
            f.write(response.body)
        

        


