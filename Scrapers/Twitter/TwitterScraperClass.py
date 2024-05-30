'''
Twitter scraper implementation
'''
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#Imports
from .AccountClass import *
from .TweetEntity import *
from InterfaceScraper import IScraper
from playwright.async_api import async_playwright

import asyncio
import re
from bson import ObjectId
import logging


class TwitterScraper(IScraper):
	def __init__(self, link_gather_account_username, link_gather_account_password, keyword):
		self.link_gather_account_username = link_gather_account_username
		self.link_gather_account_password = link_gather_account_password
		self.keyword = keyword
		logging.basicConfig(level=logging.INFO)

	link_gather_account = Account
	link = None
	keyword = str

	async def login_account(self, browser, retry_count=0):
		'''
		account_location = 'account_data/accounts.txt'
		try:
			with open(account_location, 'r') as file:
				last_line = file.readlines()[-1]
			
			#account = last_line.split(', ')
			#username = account[1].strip()
			#password = account[3].strip()
		except FileNotFoundError:
			logging.error("Account file not found")
			return None
		'''
		context = None

		try:
			async with async_playwright():
				context = await browser.new_context(no_viewport=True)
				if context is None:
					logging.error("Failed to create new browser context")
					return None
				
				page = await context.new_page()
				await page.goto("https://twitter.com/i/flow/login")

				name_selector = 'input[type="text"][name="text"]'
				await page.type(name_selector, self.link_gather_account_username, delay=150)

				button_selector = "text='Next'"
				await page.click(button_selector)

				password_selector = 'input[name="password"]'
				await page.type(password_selector, self.link_gather_account_password, delay=150)

				login_btn_selector = '[data-testid="LoginForm_Login_Button"]'				
				await page.click(login_btn_selector)

				search_box_selector = '[data-testid="SearchBox_Search_Input"]'
				await asyncio.wait_for(page.wait_for_selector(search_box_selector), timeout=5)
				logging.info("Login successful")
				return page

		except (asyncio.TimeoutError, Exception) as e:
				logging.error(f"An error occurred: {str(e)}")
				'''
				if context:
					await context.close()
				_context = await browser.new_context(no_viewport=True)

				if retry_count < 2:
					retry_count = retry_count + 1
					await asyncio.sleep(10)
					await Account.create_account(_context)
					return await self.login_account(browser), retry_count
				else:
					logging.error("Max login tries reached, the application will now shutdown")
				'''
	
	async def link_gatherer(self, page):
		links = []

		search_selector_id = '[data-testid="SearchBox_Search_Input"]'
		await page.type(search_selector_id, "testing", delay=150)
		await page.keyboard.press('Enter')
			

		#Allows for filtering
		advanced_search = 'text="Advanced search"'
		await page.click(advanced_search)
		await asyncio.sleep(1)

		keyword_selector = 'input[name="allOfTheseWords"]'
		await page.type(keyword_selector, self.keyword, delay=150)
		await asyncio.sleep(2)
			
			#Filtering based on hashtags
		'''
		keyword = f"#{keyword}"
		hashtag_selector = 'input[name="theseHashtags"]'
		await page.type(hashtag_selector, keyword, delay=150)
		'''

		#Filtering based on likes
		likes = "500"
		min_likes = 'input[name="minLikes"]'    
		await page.type(min_likes, likes, delay=150)
		await asyncio.sleep(1)

		#Filtering based on replies
		...

		#Filtering based on reposts/retweets
		...

		#Maybe more filtering (enabling/disabling links/replies)

		advanced_search_button = 'text="Search"'
		await page.click(advanced_search_button)
		await asyncio.sleep(1)

		cookies_button = page.get_by_text("Refuse non-essential cookies")
		if cookies_button:
			await cookies_button.click()
		else:
			return

		_prev_height = -1
		_max_scrolls = 5
		_scroll_count = 0
		while _scroll_count < _max_scrolls:
			# Execute JavaScript to scroll to the bottom of the page
			await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
			# Wait for new content to load (change this value as needed)
			await page.wait_for_timeout(100)
			link_selectors = await page.locator('.css-175oi2r').get_by_role('link').all()
			#print(link_selectors)

			article_elements = await page.get_by_role('article').all()
			#print(article_elements)

			anchor_tags = await page.query_selector_all('a')
			print(anchor_tags)

			for link_element in anchor_tags:
				href = await link_element.get_attribute('href')
				if href and re.match(r'\/[A-Za-z0-9_]+\/status\/[0-9]+$', href):
					links.append("https://twitter.com" + href)
					if len(links) >= 50:  # Break after collecting 20 valid links
						break
				await asyncio.sleep(1)
			# Check whether the scroll height changed - means more pages are there
			new_height = await page.evaluate("document.body.scrollHeight")
			if new_height == _prev_height:
				break
			_prev_height = new_height
			_scroll_count += 1

		await asyncio.sleep(5)
		#await page.wait_for_load_stage()

		'''
		link_selectors = await page.locator('.css-175oi2r').get_by_role('link').all()
		print(link_selectors)

		article_element = await page.get_by_role('article').all()
		print(article_element)

		for link_element in link_selectors:
			href = await link_element.get_attribute('href')
			if href and re.match(r'\/[A-Za-z0-9_]+\/status\/[0-9]+$', href):
				links.append("https://twitter.com" + href)
				if len(links) >= 50:  # Break after collecting 20 valid links
					break
			await asyncio.sleep(1)
		'''

		#Logging out
		'''
		account_selector_testid = '[data-testid="SideNav_AccountSwitcher_Button"]'
		await page.click(account_selector_testid)

		asyncio.sleep(2)

		logout_testid = '[data-testid="AccountSwitcher_Logout_Button"]'
		await page.click(logout_testid)
		'''

		await page.goto('https://twitter.com/logout')

		#confirm_logout = '[data-testid="confirmationSheetConfirm"]'
		#await page.get_by_text("Log out").click()

		#if confirm_logout:
			#await page.click(confirm_logout)
		#else:
			#return
			
		print(links)	
		return links

	
	async def scraper(self, browser, links):
		results = []
		contexts = []

		#Creates context with fixed number of pages
		pages_per_context = 5

		for i in range(0, len(links), pages_per_context):
			context = await browser.new_context()
			contexts.append(context)
			#timeout = 60000
			#page.set_default_timeout(timeout)
			pages = await asyncio.gather(*[context.new_page() for _ in range(pages_per_context)])

			#Assign links to pages
			tasks = []
			for page, link in zip(pages, links[i:i+pages_per_context]):
				async def scraping_logic(page, link):
						print(link)
						try:
							await page.goto(link)
							num_code = (re.match(r'\/[A-Za-z0-9_]+\/status\/[0-9]+$', link)).group(1)
							url = (re.match(r"/[a-zA-Z0-9_]+/status/\d+", link))


							'''
							cookies_button = page.get_by_text("Refuse non-essential cookies")
							if cookies_button:
								await page.get_by_text("Refuse non-essential cookies").click()
							else:
								return
							'''
							
							#Content
							tweet_content = ''
							try:
								element = page.get_by_test_id('tweet')

								if element:
									text_content = await element.text_content()
									tweet_content += text_content

									img_elements = await page.query_selector_all('img')
									for img in img_elements:
										alt_text = await img.get_attribute('alt')
										if alt_text:
											tweet_content += f" {alt_text} "
								else:
									tweet_content = 'Content element error'
							except Exception as e:
								print(f"Error loading tweet content {e}")
								tweet_content = ''

							# Extract the date
							date_pattern = r"\d{1,2}:\d{2} [ap]m · \d{1,2} \w+ \d{4}"
							date = re.search(date_pattern, tweet_content)
							tweet_date = date.group(0) if date else None

							# Extract views, reposts, quotes, likes, and bookmarks
							views_pattern = r"(\d[\d,.KkMm]*) Views"
							reposts_pattern = r"(\d[\d,.KkMm]*) Reposts"
							quotes_pattern = r"(\d[\d,.KkMm]*) Quotes"
							likes_pattern = r"(\d[\d,.KkMm]*) Likes"
							bookmarks_pattern = r"(\d[\d,.KkMm]*) Bookmarks"

							views = re.search(views_pattern, tweet_content)
							reposts = re.search(reposts_pattern, tweet_content)
							quotes = re.search(quotes_pattern, tweet_content)
							likes = re.search(likes_pattern, tweet_content)
							bookmarks = re.search(bookmarks_pattern, tweet_content)

							tweet_views = views.group(1) if views else None
							tweet_reposts = reposts.group(1) if reposts else None
							tweet_quotes = quotes.group(1) if quotes else None
							tweet_likes = likes.group(1) if likes else None
							tweet_bookmarks = bookmarks.group(1) if bookmarks else None

							emoji_pattern = r"[\U00010000-\U0010ffff]"

							# Find the start index of the statistical data
							data_pattern_start = re.search(date_pattern, tweet_content)
							data_start_index = data_pattern_start.start() if data_pattern_start else None

							# Extract text content up to the point where statistical data starts
							if data_start_index:
								tweet_content_text = tweet_content[:data_start_index].strip()
							else:
								tweet_content_text = tweet_content

							# Remove line breaks and multiple spaces
							tweet_content_text = tweet_content_text.replace('\n', ' ')
							tweet_content_text = ' '.join(tweet_content_text.split())

							# Find and append the emojis
							emoji = re.findall(emoji_pattern, tweet_content)
							tweet_content_with_emoji = tweet_content_text + " " + ''.join(emoji).strip()

							tweet_comments = ''

							hex_string = num_code.zfill(24)
							objectId = ObjectId(hex_string)

							tweet = Tweet(_id=objectId,
											url=url, 
											title=tweet_content_with_emoji, 
											time=tweet_date, 
											upvotes=tweet_likes,
											views=tweet_views, 
											reposts=tweet_reposts, 
											)
							
							return tweet.to_doc() 
						except Exception as e:
							print(f"Error in scraping: {e}")
							tweet = Tweet(_id=objectId,
					 						link=link, 
											content='', 
											date='', 
											likes='', 
											reposts='', 
											quotes='', 
											bookmarks='', 
											views='', 
											comments=''
					 						)
						finally:
							await page.close()

				tasks.append(scraping_logic(page, link))

			results.extend(await asyncio.gather(*tasks))

		# Close all contexts
		for context in contexts:
			await context.close()

		return results
	
	async def scrape(self, frequency, keywords):
		...


