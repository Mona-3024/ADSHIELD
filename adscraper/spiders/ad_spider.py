import scrapy

class AdSpiderSpider(scrapy.Spider):
    name = "ad_spider"
    allowed_domains = ["www.programiz.com"]
    start_urls = ["https://www.programiz.com/python-programming/online-compiler/"]

    def parse(self, response):
        # Select all image elements on the webpage
        images = response.css('img')

        for img in images:
            # Extract the image source URL
            image_url = img.attrib.get("src", "")
            if image_url:
                full_image_url = response.urljoin(image_url)  # Convert to absolute URL
            else:
                full_image_url = "No Image URL"

            # Check if the image is inside an <a> tag (i.e., a redirected image)
            parent_link = img.xpath("ancestor::a/@href").get()
            if parent_link:
                redirect_url = response.urljoin(parent_link)
            else:
                redirect_url = "No Redirect"

            yield {
                'image_url': full_image_url,
                'redirect_url': redirect_url
            }