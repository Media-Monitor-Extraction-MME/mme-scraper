'''
Twitter scraper implementation
'''

#Imports
from AccountClass import *
from TweetEntity import *
import asyncio
from bson import ObjectId

class TwitterScraper:
    def __init__(self, link_gather_account, link):
        self.link_gather_account = link_gather_account
        self.link = link

    link_gather_account = Account
    link = str

    async def login_account(self, account, context):
        account_location = 'account_data/accounts.txt'
        with open(account_location, 'r') as file:
            for last_line in file:
                pass
        
        account = last_line.split(', ')
        username = account[1].strip()
        password = account[3].strip()

        async with async_playwright():
            page = await context.new_page()
            await page.goto("https://twitter.com/i/flow/login")

            name_selector = 'input[type="text"][name="text"]'
            await page.type(name_selector, username, delay=150)

            button_selector = "text='Next'"
            await page.click(button_selector)

            password_selector = 'input[name="password"]'
            await page.type(password_selector, password, delay=150)

            login_btn_selector = '[data-testid="LoginForm_Login_Button"]'
            
            await page.click(login_btn_selector)
            search_box_selector = '[data-testid="SearchBox_Search_Input"]'

            try:
                await asyncio.wait_for(
                    page.wait_for_selector(search_box_selector),
                    timeout=5  
                )

            except asyncio.TimeoutError:
                print("Login process took too long or failed.")
                page.close()
                await Account.create_account(context)

            else:
                #Check if 2fa frame pops up
                no2fa_selector = '[data-testid="app-bar-close"]'
                no2fa_selector_check = await page.query_selector(no2fa_selector)

                if no2fa_selector_check:
                    await page.click(no2fa_selector)

                print("Login successful")
                return page
    
    async def link_gatherer(self, page, keyword):
        
        
        links = [str]

        return links
    
    async def scraper(self, links):
        tweet = Tweet.to_doc

        return tweet


