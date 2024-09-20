import scrapy
import json

class BusinessSpider(scrapy.Spider):
    name = 'business_spider'
    allowed_domains = ['firststop.sos.nd.gov']
    start_urls = ['https://firststop.sos.nd.gov/api/Records/businesssearch']

    def start_requests(self):
        for letter in ['X']:  # Only querying businesses starting with 'X'
            data = {
                "searchTerm": letter,
                "status": "Active",  # Only active companies
                # Additional search parameters may be needed
            }
            yield scrapy.Request(
                url='https://firststop.sos.nd.gov/api/Records/businesssearch',
                method='POST',
                body=json.dumps(data),
                headers={'Content-Type': 'application/json'},
                callback=self.parse
            )

    def parse(self, response):
        # Parse the response JSON
        businesses = json.loads(response.text)
        for business in businesses.get('results', []):
            yield {
                'owner': business.get('name'),
                'registered_agent': business.get('Registered Agent', {}).get('name'),
                'commercial_registered_agent': business.get('Commercial Registered Agent', {}).get('name'),
                # Include other fields as needed
            }
