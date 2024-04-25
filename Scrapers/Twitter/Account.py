'''
Account for link gathering in twitter_scraper
'''

#Imports
from playwright.async_api import async_playwright 
import time, datetime, random, secrets, string, asyncio

class Account:
    def __init__(self, first_name, last_name, username, password, date_of_birth, email):
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.password = password
        self.date_of_birth = date_of_birth
        self.email = email        
        

    @staticmethod
    async def email_generator(context):
        async with async_playwright():
            page = await context.new_page()
            await page.goto("https://10minutemail.com")

            await page.wait_for_load_state('load')

            mail = await(await page.query_selector('#mail_address')).input_value()

            return mail

    @staticmethod
    async def random_credentials_generator(context, age=None):
        date = datetime.date.today()
        current_year = date.year()

        names_location = "account_data/names.txt"
        with open(names_location, 'r') as file:
            names = [name.strip() for name in file.readlines()]

        name = random.choice(names)
        first_name = name.split()[0]
        last_name = name.split()[1]
        username = f'{first_name}_{last_name}{random.randint(1000, 9999)}'
        password = f'{random.choice(string.ascii_uppercase)}_{secrets.token_hex(4)}'
        months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        birthday = f'{random.randint(1, 28)}-{random.choice(months)}-{(current_year - age) if age else random.randint(1950, current_year - 21)}'
        email = await Account.email_generator(context)

        accounts_location = "account_data/accounts.txt"
        with open(accounts_location, 'a') as file:
            file.write(f'[{time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())}] {first_name} {last_name}, {username}, {email}, {password}, {birthday}\n')

        return first_name, last_name, username, password, birthday, email

    async def create_account(self, context):
        first_name, last_name, username, password, date_of_birth, email = await self.random_credentials_generator(context)
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.password = password
        self.date_of_birth = date_of_birth
        self.email = email

        birth_day, birth_month, birth_year = self.date_of_birth.split('-')

        async with async_playwright():
            page = await context.new_page()
            await page.goto("https://twitter.com/i/flow/signup")  

            asyncio.sleep(1)

            await page.click('div.css-175oi2r:nth-child(5)')

            username_selector = 'div.r-1f1sjgu:nth-child(1) > label:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > input:nth-child(1)'
            email_selector = 'div.r-1f1sjgu:nth-child(2) > label:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > input:nth-child(1)'

            asyncio.sleep(0.5)

            await page.type(username_selector, self.username, delay=150)
            await page.evaluate(f'''() => {{
            const element = document.querySelector("{username_selector}");
            if (element) element.blur();
            }}''')
            asyncio.sleep(0.5)
            await page.type(email_selector, self.email, delay=150)
            await page.evaluate(f'''() => {{
            const element = document.querySelector("{username_selector}");
            if (element) element.blur();
            }}''')

            month_selector = '#SELECTOR_1'
            day_selector = '#SELECTOR_2'
            year_selector = '#SELECTOR_3'

            asyncio.sleep(0.5)
            await page.click(month_selector)
            asyncio.sleep(0.8)
            await page.select_option(month_selector, value = birth_month)
            asyncio.sleep(0.5)
            await page.click(day_selector)
            asyncio.sleep(0.8)
            await page.select_option(day_selector, value = birth_day)
            asyncio.sleep(0.5)
            await page.click(year_selector)
            asyncio.sleep(0.8)
            await page.select_option(year_selector, value = birth_year)
            asyncio.sleep(0.8)
            await page.click(year_selector)

            asyncio.sleep(2)

            selector_string = '[data-testid="ocfSignupNextLink"]'
            element_handle = await page.query_selector(selector_string)

            if element_handle:
                await element_handle.click()
            else:
                print("Element not found")

            asyncio.sleep(2)

            second_selector_string = '[data-testid="ocfSettingsListNextButton"]'
            second_element_handle = await page.query_selector(second_selector_string)
            

            if second_element_handle:
                await second_element_handle.click()
            else:
                print("Element not found")
        
            asyncio.sleep(120)

            pages = context.pages

            ten_minute_mail_page = None
            for page in pages:
                if "10minutemail.com" in page.url:
                    ten_minute_mail_page = page
                    break

            if ten_minute_mail_page:
                inbox_selector = "#mail_messages_content > div"
                await page.click(inbox_selector)
                verification_location = "#mail_messages_content > div > div.message_bottom > table > tbody > tr:nth-child(1) > td > table > tbody > tr:nth-child(1) > td > table:nth-child(1) > tbody > tr > td:nth-child(2) > table > tbody > tr:nth-child(10) > td"
                verification_code_element = await page.query_selector(f'{verification_location}')
                
                if verification_code_element:
                    verification_code_text = await page.evaluate('(element) => element.textContent', verification_code_element)
                    print(verification_code_text)
                else:
                    print("Verification code element not found")
            
            else:
                print("10minutemail page not found")

            twitter_creation_page = None
            for page in pages:
                if "https://twitter.com/i/flow/signup" in page.url:
                    twitter_creation_page = page
                    break
            
            if twitter_creation_page:
                input_selector = 'input[name="verfication_code"]'
                await page.type(input_selector, verification_code_text, delay=150)
    
                button_selector = "text='Next'"
                await page.wait_for_selector(button_selector, state="visible")
                
                try:
                    await page.click(button_selector)
                except Exception as e:
                    print(f"Error clicking the button: {e}")

                asyncio.sleep(0.8)

                password_selector = 'input[name="password"]'
                await page.type(password_selector, password, delay=150)
                
                password_button = '[data-testid="LoginForm_Login_Button"]'
                await page.click(password_button)

                #Here the Arkose comes in
                asyncio.sleep(10)
                locked_account_button = 'input[type="submit"][value="Start"]'
                locked_account_button_check = await page.query_selector(locked_account_button)

                if locked_account_button_check:
                    await page.click(locked_account_button)

                    asyncio.sleep(1)

                    continue_button = 'input[type="submit"][value="Continue to X"]'
                    await page.click(continue_button)

                    asyncio.sleep(5)
                    ok_button = '[data-testid="confirmationSheetConfirm"]'
                    await page.click(ok_button)

                else:
                    skip_pfp = '[data-testid="ocfSelectAvatarSkipForNowButton"]'
                    await page.click(skip_pfp)
                    asyncio.sleep(1)

                    skip_username = '[data-testid="ocfEnterUsernameSkipButton"]'
                    await page.click(skip_username)
                    asyncio.sleep(1)

                    no_notifs = '#layers > div:nth-child(2) > div > div > div > div > div > div.css-175oi2r.r-1ny4l3l.r-18u37iz.r-1pi2tsx.r-1777fci.r-1xcajam.r-ipm5af.r-g6jmlv.r-1awozwy > div.css-175oi2r.r-1wbh5a2.r-htvplk.r-1udh08x.r-1867qdf.r-kwpbio.r-rsyp9y.r-1pjcn9w.r-1279nm1 > div > div > div.css-175oi2r.r-1ny4l3l.r-6koalj.r-16y2uox.r-kemksi.r-1wbh5a2 > div.css-175oi2r.r-16y2uox.r-1wbh5a2.r-1jgb5lz.r-13qz1uu.r-1ye8kvj > div > div > div > div > div > div.css-175oi2r.r-98ikmy.r-hvns9x > div.css-175oi2r.r-13qz1uu > div.css-175oi2r.r-sdzlij.r-1phboty.r-rs99b7.r-lrvibr.r-1wzrnnt.r-19yznuf.r-64el8z.r-1dye5f7.r-1loqt21.r-o7ynqc.r-6416eg.r-1ny4l3l'
                    await page.click(no_notifs)
                    asyncio.sleep(1)

                    interest_music_selector = '#verticalGridItem-0-categoryrecommendations-1772591907453534208 > div > div > div > div'
                    interest_entertainment_selector = '#verticalGridItem-1-categoryrecommendations-1772591907453534208 > div > div > div > div'
                    interest_sports_selector = '#verticalGridItem-2-categoryrecommendations-1772591907453534208 > div > div > div > div'
                    interest_gaming_selector = '#verticalGridItem-3-categoryrecommendations-1772591907453534208 > div > div > div > div'
                    interest_fashionbeauty_selector = '#verticalGridItem-4-categoryrecommendations-1772591907453534208 > div > div > div > div'
                    interest_food_selector = '#verticalGridItem-5-categoryrecommendations-1772591907453534208 > div > div > div > div'
                    interest_businessfinance_selector = '#verticalGridItem-6-categoryrecommendations-1772591907453534208 > div > div > div > div'
                    interest_artsculture_selector = '#verticalGridItem-7-categoryrecommendations-1772591907453534208 > div > div > div > div'
                    interest_technology_selector = '#verticalGridItem-8-categoryrecommendations-1772591907453534208 > div > div > div > div'
                    interest_travel_selector = '#verticalGridItem-9-categoryrecommendations-1772591907453534208 > div > div > div > div'
                    interest_outdoors_selector = '#verticalGridItem-10-categoryrecommendations-1772591907453534208 > div > div > div > div'
                    interest_fitness_selector = '#verticalGridItem-11-categoryrecommendations-1772591907453534208 > div > div > div > div'
                    interest_careers_selector = '#verticalGridItem-12-categoryrecommendations-1772591907453534208 > div > div > div > div'
                    interest_animationcomics_selector = '#verticalGridItem-13-categoryrecommendations-1772591907453534208 > div > div > div > div'
                    interest_familyrelationships_selector = '#verticalGridItem-14-categoryrecommendations-1772591907453534208 > div > div > div > div'
                    interest_science_selector = '#verticalGridItem-15-categoryrecommendations-1772591907453534208 > div > div > div > div'
                    
                    page.click(interest_music_selector, 
                            interest_entertainment_selector, 
                            interest_sports_selector, 
                            interest_gaming_selector, 
                            interest_fashionbeauty_selector,
                            interest_food_selector,
                            interest_businessfinance_selector,
                            interest_artsculture_selector,
                            interest_technology_selector,
                            interest_travel_selector,
                            interest_outdoors_selector,
                            interest_fitness_selector,
                            interest_careers_selector,
                            interest_animationcomics_selector,
                            interest_familyrelationships_selector,
                            interest_science_selector, 
                            delay=100)
                
                
                no_cookies = "text='Refuse non-essential cookies'"
                await page.click(no_cookies)

                #Retrieve username and update file
                # Select the element using data-testid attribute
                test_id = await page.get_attribute('div[data-testid^="UserAvatar-Container"]')
                if test_id:
                    parts = test_id.split('-')
                    username = parts[2]
                print(test_id)                    

            else: 
                print("Twitter not found")