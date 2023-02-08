import scrapy
import csv
from ..items import USCISResponseItem

class USICSSpider(scrapy.Spider):
    # Spider Name: Used in cmd
    name = "USCIS"

    def start_requests(self):
        
        # Read receipt number from file
        with open('active_cases/active_cases.csv') as f:
            reader = csv.reader(f)
            data = list(reader)

        # Pull case status for each rcptnum
        for receipt_number in data:
            # USICS Case Status URL
            url = 'https://egov.uscis.gov/casestatus/mycasestatus.do'
            # Insert Recipt Number to check status
            data = {"changeLocale":"","appReceiptNum":receipt_number[0],"initCaseSearch":"CHECK STATUS"}
            # Send Request and parse response
            yield scrapy.FormRequest(url=url, callback=self.parse, formdata=data)

    
    def parse(self, response):

        items = USCISResponseItem()

        # Parse recieved response

        case_status = response.css('div h1').xpath('text()').get()
        descp = response.css('div p').xpath('text()').get()

        ind = descp.find("Receipt")
        items["Reciept_Number"] = descp[ind+15:ind+28]

        items['Case_Status'] = case_status
        items['Description'] = descp

        yield items