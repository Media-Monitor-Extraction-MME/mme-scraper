'''
Twitter scraper implementation
'''
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#Imports
from .AccountClass import *
from .TweetEntity import *
# from AccountClass import *
# from TweetEntity import *
from InterfaceScraper import IScraper
from playwright.async_api import async_playwright

import asyncio
import re
from bson import ObjectId
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TwitterScraper(IScraper):
	def __init__(self, link_gather_account_username, link_gather_account_password, keyword):
		self.link_gather_account_username = link_gather_account_username
		self.link_gather_account_password = link_gather_account_password
		self.keyword = keyword


	async def login_account(self, browser):
		context = None

		try:
				context = await browser.new_context(no_viewport=True)
				if context is None:
					logging.error("Failed to create new browser context")
					return None
				
				page = await context.new_page()
				await page.goto("https://twitter.com/i/flow/login")

				name_selector = 'input[type="text"][name="text"]'
				await page.type(name_selector, self.link_gather_account_username, delay=150)
				await asyncio.sleep(2)

				button_selector = "text='Next'"
				await page.click(button_selector)
				await asyncio.sleep(2)

				password_selector = 'input[name="password"]'
				await page.type(password_selector, self.link_gather_account_password, delay=150)
				await asyncio.sleep(2)

				login_btn_selector = '[data-testid="LoginForm_Login_Button"]'				
				await page.click(login_btn_selector)

				await page.wait_for_load_state()
				await asyncio.sleep(5)

				logging.info("Login successful")
				return page

		except (asyncio.TimeoutError, Exception) as e:
				logging.error(f"An error occurred: {str(e)}")
	
	async def link_gatherer(self, page):
		links = []

		search_selector_id = '[data-testid="SearchBox_Search_Input"]'
		search_query = f"{self.keyword} min_faves:500 since:2024-01-01"
		await page.type(search_selector_id, search_query, delay=150)
		await page.keyboard.press('Enter')

		logger.debug("Entered search query : %s", search_query)

		cookies_button = await page.get_by_text("Refuse non-essential cookies")
		if cookies_button:
			await cookies_button.click()
			logger.debug("Clicked on cookie button")
		else:
			logger.debug("No cookie button found")

		_prev_height = -1
		_max_scrolls = 10
		_scroll_count = 0
		while _scroll_count < _max_scrolls:
			await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
			await page.wait_for_timeout(100)

			anchor_tags = await page.query_selector_all('a')
			logger.debug("Found %d anchor tags", len(anchor_tags))

			for link_element in anchor_tags:
				href = await link_element.get_attribute('href')
				if href and re.match(r'\/[A-Za-z0-9_]+\/status\/[0-9]+$', href):
					links.append("https://twitter.com" + href)
			
			logger.debug("Links collected so far: %s", links)

			new_height = await page.evaluate("document.body.scrollHeight")
			if new_height == _prev_height:
				logger.debug("Reached the bottom of page, or no new content found")
				break
			_prev_height = new_height
			_scroll_count += 1
			logger.debug("Scroll count: %d", _scroll_count)
		await asyncio.sleep(5)

		await page.goto('https://twitter.com/logout')
		logger.debug("Navigated to logout")
		await page.close()
		logger.debug("Page closed")
			
		logger.debug("Final links collected: %s", links)	
		return list(set(links))

	
	async def scraper(self, browser, links):
		results = []
		contexts = []

		#Creates context with fixed number of pages
		pages_per_context = 10

		for i in range(0, len(links), pages_per_context):
			context = await browser.new_context()
			contexts.append(context)
			pages = await asyncio.gather(*[context.new_page() for _ in range(pages_per_context)])
			async def scraping_logic(page, link):
						try:
							await page.goto(link)
							num_code = (re.match(r'https://twitter\.com/[A-Za-z_\-0-9]+\/status/([0-9]+)$', link)).group(1)
							url = (re.match(r'https://twitter\.com(/[A-Za-z_\-0-9]+\/status/[0-9]+)$', link)).group(1)


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
							date_pattern = r"(\d{1,2}:\d{2} [ap]m · \d{1,2} \w+ \d{4})"
							date = re.search(date_pattern, tweet_content)
							tweet_date = date.group(0) if date else None

							# Extract views, reposts, quotes, likes, and bookmarks
							views_pattern = r"(\d[\d,.KkMm]*) Views"
							reposts_pattern = r"(\d[\d,.KkMm]*) Reposts"
							likes_pattern = r"(\d[\d,.KkMm]*) Likes"

							views = re.search(views_pattern, tweet_content)
							reposts = re.search(reposts_pattern, tweet_content)
							likes = re.search(likes_pattern, tweet_content)

							tweet_views = views.group(1) if views else None
							tweet_reposts = reposts.group(1) if reposts else None
							tweet_likes = likes.group(1) if likes else None

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

							hex_string = num_code.zfill(24)
							objectId = ObjectId(hex_string)

							tweet = Tweet(
										_id=objectId,
										url=url, 
										title='',
										description=tweet_content_with_emoji, 
										time=tweet_date, 
										upvotes=tweet_likes,
										views=tweet_views, 
										reposts=tweet_reposts 
										)
						
							await page.close()
							return tweet.to_doc() 

						except Exception as e:
							print(f"Error in scraping: {e}, link: {link}")
							if 'num_code' not in locals():
								print(f'Failed to extract num_code from link: {link}')
							num_code = (re.match(r'https://twitter\.com/[A-Za-z_\-0-9]+\/status/([0-9]+)$', link)).group(1)
							url = (re.match(r"/[a-zA-Z0-9_]+/status/\d+", link))
							objectId = ObjectId(num_code.zfill(24))
							fallback_tweet = Tweet(
								_id=objectId,
								url=url,
								title='',
								description='',
								time='',
								upvotes='',
								views='',
								reposts=''
								)
							await page.close()
							return fallback_tweet.to_doc()

			#Assign links to pages
			tasks = []
			for page, link in zip(pages, links[i:i+pages_per_context]):		
				tasks.append(scraping_logic(page, link))
			results.extend(await asyncio.gather(*tasks))

		# Close all contexts
		for context in contexts:
			await context.close()

		return results
	
	async def scrape(self):
		async with async_playwright() as p:
			start_time = time.time()
			browser = await p.chromium.launch(args=['--start-maximized'], headless=False)

			page = await self.login_account(browser=browser)
			if page is None:
				logging.error("Page is none")
			links = await self.link_gatherer(page=page)
			twitterdata = await self.scraper(browser=browser, links=links)
			links_len = len(links)
			end_time = time.time()
			total_time = end_time - start_time
			print(f'{self.keyword}: {links_len} tweets scraped in {total_time} seconds.')
			await browser.close()

		return twitterdata
			




