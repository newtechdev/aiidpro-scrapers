import scrapy
import json
from scrapy_playwright.page import PageMethod
import unicodedata
from scrapy.selector import Selector  


class IdentIqSpider(scrapy.Spider):
    name = "ident_iq"
    allowed_domains = ["identityiq.com", "consumerconnect.tui.transunion.com"]
    start_urls = ["https://www.identityiq.com/"]


    # TEST REPORT PARSING FROM LOCAL FILE M54428039_4-2-2024.html
    # def start_requests(self) -> Iterable[scrapy.Request]:
    #     url = "file:/Users/milan/scraping/vince_wynn/IdentityIQ/M54428039_4-2-2024.html"
    #     yield scrapy.Request( url, method='GET', 
    #                 callback=self.parse_CreditReport, 
    #                 meta=dict(
    #                     playwright=True,
    #                     playwright_include_page=True,
    #                     playwright_page_methods=[
    #                         PageMethod("wait_for_selector", "div#CreditScore"),
    #                         PageMethod("evaluate", "window.scrollBy(0, document.body.scrollHeight)"),
    #                         PageMethod("wait_for_selector", "div#CreditorContacts"),
    #                         ],
    #                     )
    #                 )


    def parse(self, response):
        yield scrapy.Request(url="https://member.identityiq.com/", callback=self.parse_login)

    def parse_login(self, response):
        form_data = {
            "username": self.http_user,
            "password": self.http_pass
            }

        url = "https://member.identityiq.com/RedesignLogin.aspx/auth"
        yield scrapy.Request( url, method='POST', 
                            callback=self.parse_auth,
                            body=json.dumps(form_data), 
                            headers={'Content-Type':'application/json'} )


    def parse_auth(self, response):
        # response.body should be b'{"d":"{\\"RedirectUrl\\":\\"security-question\\",\\"ErrorMessage\\":null}"}'
        form_data = {}

        url = "https://member.identityiq.com/SecurityQuestions.aspx/Initialize"
        yield scrapy.Request( url, method='POST', 
                            callback=self.parse_SecurityQuestions_Initialize,
                            body=json.dumps(form_data), 
                            headers={'Content-Type':'application/json'} )
        

    def parse_SecurityQuestions_Initialize(self, response):
        print("parse_SecurityQuestions_Initialize")
        # response.body should be b'{"d":"{}"}'
        form_data = {}

        url = "https://member.identityiq.com/SecurityQuestions.aspx/GetSecurityQuestion"
        yield scrapy.Request( url, method='POST', 
                            callback=self.parse_SecurityQuestions_GetSecurityQuestion,
                            body=json.dumps(form_data), 
                            headers={'Content-Type':'application/json'} )


    def parse_SecurityQuestions_GetSecurityQuestion(self, response):
        # response.body should be b'{"d":"{\\"SecurityQuestion\\":\\"Last four digits of your SSN?\\"}"}'
        form_data = {"userSecurityAnswer": self.last_four_digits}

        url = "https://member.identityiq.com/SecurityQuestions.aspx/SubmitSecurityAnswer"
        yield scrapy.Request( url, method='POST', 
                            callback=self.parse_SecurityQuestions_SubmitSecurityAnswer, 
                            body=json.dumps(form_data), 
                            headers={'Content-Type':'application/json'} )
 

    def parse_SecurityQuestions_SubmitSecurityAnswer(self, response):
        # response.body should be b'{"d":"{\\"RedirectUrl\\":\\"Dashboard.aspx\\"}"}'
        url = "https://member.identityiq.com/Dashboard.aspx"
        yield scrapy.Request( url, method='GET', 
                            callback=self.parse_Dashboard,
                            )


    def parse_Dashboard(self, response):
        url = "https://member.identityiq.com/CreditReport.aspx"
        yield scrapy.Request( url, method='GET', 
                    callback=self.parse_CreditReport, 
                    meta=dict(
                        playwright=True,
                        playwright_include_page=True,
                        playwright_page_methods=[
                            PageMethod("wait_for_load_state", "load"),
                            PageMethod("wait_for_selector", 'a[onclick="downloadCreditReport()"]'),
                            PageMethod("wait_for_selector", "div#CreditScore"),
                            PageMethod("wait_for_selector", "div#AccountHistory"),
                            PageMethod("evaluate", "window.scrollBy(0, document.body.scrollHeight)"),
                            PageMethod("wait_for_selector", "div#CreditorContacts"),
                            ],

                        handle_httpstatus_all=True

                        )
                    )
        

    async def parse_CreditReport(self, response):
        page = response.meta["playwright_page"]

        # Loop to handle infinite scrolling
        while True:
            last_height = await page.evaluate("() => document.body.scrollHeight")
            # Scroll to bottom
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            # Wait for page to load new items, adjust the wait time and conditions according to the site's behavior
            await page.wait_for_timeout(2000)  # Wait a bit for loading to occur
            new_height = await page.evaluate("() => document.body.scrollHeight")
            if new_height == last_height:
                break  # Break the loop if no new content loaded

        content = await page.content()  # Retrieve the content after all scrolling

        # Do something with the content or extract data
        new_response = Selector(text=content)

        # write full page, after scroll to bottom, to a file
        # may be a good idea to save each page/report for debugging
        # with open("infinite_scrolled_page.html", "w") as f:
        #     f.write(content)
        
        # save screenshot of page after scroll to bottom
        # may be a good idea to save each page/report for debugging
        # await page.screenshot(path="CreditReport_2.png", full_page=True)
        
        json_data = {}
        json_data['general_info'] = {
            'name': new_response.xpath('//div[@class="reportTopHeader"]/text()').get().strip(),
            'reference': new_response.xpath('//h3[text()="Reference #:"]/following-sibling::p/text()').get().strip(),
            'report_date': new_response.xpath('//h3[text()="Report Date:"]/following-sibling::p//*/text()').get().strip(),
        }

        # for each section call the appropriate function name
        # example: section Credit Score calls function get_credit_score
        sections = new_response.xpath('//div[@id="ctrlCreditReport"]//div[@id="reportTop"]/following-sibling::div[not(@class="content_divider")]//table/parent::div[contains(@class, "rpt_content_wrapper")]')
        for section in sections:
            section_title = section.xpath('.//div[@class="rpt_fullReport_header"]//text()').getall()
            section_title = [title.strip() for title in section_title if title.strip()][0].lower().replace(' ', '_')

            function_name = f"self.get_{section_title}"
            json_data[section_title] = eval(function_name)(section)

        yield(json_data)

        await page.close()  # Always close the page when done


    def table_with_headers__to_json(self, table):
        json_table = {}
        headers = []
        for row in table.xpath('./tbody/tr'):
            if (not headers):
                headers = row.xpath('.//th[@class]/text()').getall()
                headers = [header.strip() for header in headers if header.strip()]
                continue
            name = row.xpath('.//td[contains(@class, "label")]/text()').get()
            name = self.clean_name(name)
            for index, header in enumerate(headers):
                json_table[header] = {} if header not in json_table.keys() else json_table[header]

                cell_data_unformatted = row.xpath('.//td[contains(@class, "info")]')[index]
                cell_data = [data.strip() for data in cell_data_unformatted.xpath('.//text()').getall() if data.strip()]

                if cell_data == '-':
                    json_table[header][name] = cell_data
                    break

                cell_data_1 = [data.strip() for data in cell_data_unformatted.xpath('.//*/text()').getall() if data.strip()]
                cell_data_1 = [ ' '.join([item.strip() for item in field.xpath('.//text()').getall() if item.strip()]) for field in cell_data_unformatted.xpath('./*')]
                if cell_data_1:
                    cell_data = cell_data_1
                if '-' in cell_data:
                    cell_data.remove('-')

                cell_data = [" ".join(data.split()) for data in cell_data]
                cell_data = '; '.join(cell_data)

                json_table[header][name] = cell_data

        return json_table
    

    def table_with_extra_info__to_json(self, table, delimiter=" "):
        json_table = {}
        for row in table.xpath('.//tr'):
            header = row.xpath('.//td[1]/text()').get().strip().replace(':','')
            if header == '':
                continue
            text = [unicodedata.normalize("NFKD", text.strip()) for text in row.xpath('.//td[2]/ng-repeat/text()').getall() if text.strip()]
            if not text:
                text = [unicodedata.normalize("NFKD", text.strip()) for text in row.xpath('.//td[2]/*[not(@class="ng-hide")]//text()').getall() if text.strip()]
            json_table[header] = ' '.join( f'{delimiter}'.join(text).split() ) 
            
        return json_table
    

    def table_with_addr_history__to_json(self, table):
        json_table = []

        first_column = table.xpath('./tbody/tr//td[1]/text()').getall()
        first_column = [self.clean_name(cell) for cell in first_column]

        for column_number in range(1, len( table.xpath('./tbody/tr[1]/td') )+1 )[1:]:
            column_data = {}
            for index, row in enumerate(table.xpath(f'./tbody/tr/td[{column_number}]')):
                name = row.xpath('.//text()').getall()
                name = [string for string in name if string.strip()]
                name = name[0] if name else ''
                name = self.clean_name(name)
                
                column_data[first_column[index]] = name
                
            json_table.append(column_data)

        return json_table
    

    def get_table_type(self, table):
        if table.xpath('.//th'):
            table_type = 'table_with_headers'
        elif table.css('.extra_info'):
            table_type = 'table_with_extra_info'
        elif table.css('.addr_hsrty'):
            table_type = 'table_with_addr_history'
        elif len(table.xpath('.//tbody//td'))==1:
            table_type = 'skip'
        else:
            table_type = 'Unknown'
        return table_type


    def clean_name(self, string):
        return string.strip().replace(':','').replace(' / ','_').replace(' ','_').replace('-','_').replace('/','_').lower()
    

    def get_table_name_in_camel_case(self, table):
        table_names = table.xpath('./preceding-sibling::div//text()').getall()
        table_name = [self.clean_name(name) for name in table_names if name.strip() ]
        table_name = table_name[0] if table_name else 'extra_info'
        return table_name
    

    def get_original_table_name(self, table):
        table_names = table.xpath('./preceding-sibling::div//text()').getall()
        table_name = [name.strip() for name in table_names if name.strip() ]
        table_name = table_name[0] if table_name else 'extra_info'
        return table_name
    

    def get_customer_statement(self, section):
        return self.table_with_extra_info__to_json( section.xpath('./table[not(@class="help_text")][not(descendant::table)]'), delimiter=" ")
    

    def get_personal_information(self, section):
        return self.table_with_headers__to_json( section.xpath('./table[not(@class="help_text")][not(descendant::table)]') )


    def get_credit_score(self, section):
        return self.parse_section_with_multiple_tables(section)


    def get_summary(self, section):
        return self.table_with_headers__to_json( section.xpath('./table[not(@class="help_text")][not(descendant::table)]') )


    def get_account_history(self, section):
        return self.parse_section_with_multiple_tables(section)


    def parse_section_with_multiple_tables(self, section):
        print("parse_section_with_multiple_tables")
        section_json = {}
        for table in section.xpath('.//table[not(@class="help_text")][not(descendant::table)]'):
            table_type = self.get_table_type(table)
            table_name = self.get_table_name_in_camel_case(table)
            if table_type == 'skip':
                section_json[table_name] = 'No data'
                return section_json
        
            if table_name in section_json.keys():
                index = [ int(name.split("_")[-1])  for name in section_json.keys() if table_name in name if name.split("_")[-1].isdigit() ]
                index = max(index)+1 if index else 1
                table_name = f"{table_name}_{index}" # make sure table_name is unique

            if table_type == 'table_with_headers':
                section_json[table_name] = self.table_with_headers__to_json(table)
                section_json[table_name]['original_account_name'] = self.get_original_table_name(table)
                main_table_name = table_name
            elif table_type == 'table_with_extra_info':
                section_json[table_name] = self.table_with_extra_info__to_json(table)
                main_table_name = table_name
            elif table_type == 'table_with_addr_history':
                section_json[main_table_name][table_name] = self.table_with_addr_history__to_json(table)
            else:
                raise Exception("Table type not defined!!!")
        return section_json


    def table_regular__to_json(self, table):
        table_json = []
        headers = [self.clean_name(header.get()) for header in table.xpath('.//th/text()')]
        for row in table.xpath('.//tr')[1:]:
            row_data = {}
            for index, header in enumerate(headers):
                cell_data = row.xpath(f'.//td')[index].xpath('./text()').get().strip()
                row_data[header] = cell_data
            table_json.append(row_data)
        return table_json  


    def get_inquiries(self, section):
        table = section.xpath('./table[not(@class="help_text")][not(descendant::table)]')
        return self.table_regular__to_json(table)


    def get_public_information(self, section):
        return self.parse_section_with_multiple_tables(section)


    def get_creditor_contacts(self, section):
        table = section.xpath('./table[not(@class="help_text")][not(descendant::table)]')
        return self.table_regular__to_json(table)

