# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json
import os

class AdsJsonPipeline:
    file_path = 'ads.json'

    def open_spider(self, spider):
        # Check if ads.json exists and if it's empty
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r+') as file:
                try:
                    content = json.load(file)
                except json.JSONDecodeError:
                    content = None  # Assume empty if JSON error
                if content:  # If not empty, clear its contents
                    file.seek(0)
                    file.truncate()  # Clear file
                else:
                    spider.logger.info("ads.json is empty. Proceeding to write new results.")
        else:
            spider.logger.info("ads.json does not exist. Proceeding to write new results.")

    def process_item(self, item, spider):
        return item

