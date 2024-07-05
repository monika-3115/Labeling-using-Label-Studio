from dagster import asset, AssetExecutionContext
import scrapy
from scrapy.crawler import CrawlerProcess

@asset(group_name= "dagster_s")
def scraped_data(context: AssetExecutionContext):
    """
    scrapped data using zyte is here
    """
    
    context.log.info("scraping asset msg")

    class McSpider(scrapy.Spider):
        name = "mc"
        allowed_domains = ["azure.microsoft.com"]
        start_urls = ["https://azure.microsoft.com/en-in/support/",
                    "https://azure.microsoft.com/en-in/support/1/",
                    "https://azure.microsoft.com/en-in/support/2/",
                    "https://azure.microsoft.com/en-in/support/3/",
                    "https://azure.microsoft.com/en-in/support/4/",
                    "https://azure.microsoft.com/en-in/support/5/",]

        def parse(self, response):
            QUOTE_SELECTOR = '.col'
            TEXT_SELECTOR = 'p::text'
            AUTHOR_SELECTOR = 'h3::text'
            
            NEXT_SELECTOR = 'a::attr("href")'

            for quote in response.css(QUOTE_SELECTOR):
                yield {
                    'text': quote.css(TEXT_SELECTOR).extract_first(),
                    'header': quote.css(AUTHOR_SELECTOR).extract_first(),
                    'link': quote.css(NEXT_SELECTOR).extract_first(),
                }

            next_page = response.css(NEXT_SELECTOR).extract_first()
            if next_page:
                yield scrapy.Request(
                    response.urljoin(next_page),
                )
    process = CrawlerProcess(
        settings={
            "FEEDS": {
                "scrapped_data.csv": {"format": "csv"},
            },
        }
    )
        
    process.crawl(McSpider)
    process.start()

    

@asset(deps=[scraped_data], group_name= "dagster_s")
def labled_data(context: AssetExecutionContext):
    """
    labled data using datasaur is here
    """

    file_path = "sample.py"
    with open(file_path, "r") as file :
        lines = file.readlines()


    context.log.info("labeling asset msg")
    return lines

@asset(deps=[labled_data], group_name= "dagster_s")
def milvus_cloud(context: AssetExecutionContext):
    """
    uploaded cloud data is here
    """

    context.log.info("milvus asset msg")
    return [7, 8, 9]