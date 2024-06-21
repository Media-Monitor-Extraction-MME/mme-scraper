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
from General.RepoStructure.IRepos import IPostRepository
from playwright.async_api import async_playwright

import asyncio
import re
from bson import ObjectId
import logging
import requests
import aiohttp

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TwitterScraper(IScraper):
	'''
	A class to scrape twitter for tweets based on keyword queries

	Fields:
	-------
	link_gather_account_username : str
		Username for twitter account used for link gathering
	link_gather_account_password : str
		Password for twitter account used for link gathering
	keyword : str
		Keyword used for search query
	'''
	def __init__(self, link_gather_account_username, link_gather_account_password, keyword):
		self.link_gather_account_username = link_gather_account_username
		self.link_gather_account_password = link_gather_account_password
		self.keyword = keyword


	async def _login_account(self, browser):
		'''
		A method to login to twitter based on the account passed in the constructor

		Parameters:
		-----------
		self : TwitterScraper
			Gives access to account username and password
		browser: Any
			Allows playwright to open contexts/pages to use

		Returns:
		--------
		page : Any
			Returns a twitter homepage where the search can be starteds
		'''

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
	
	async def _link_gatherer(self, page):
		'''
		A method used to gather links from the Twitter page based on a specified keyword

		Parameters:
		-----------
		page: Any
			Page object representing the twitter page to scrape

		Returns:
		links : [str]
			A list of gathered tweet URL's
		'''

		links = []

		search_selector_id = '[data-testid="SearchBox_Search_Input"]'
		search_query = f"{self.keyword} min_faves:500 since:2024-01-01"
		await page.type(search_selector_id, search_query, delay=150)
		await page.keyboard.press('Enter')

		logger.debug("Entered search query : %s", search_query)

		async def extract_links(page):
			#Using JS in the page.evaluate function
			js_extract_links = """
			const links = document.querySelectorAll('a');
			const linkArray = Array.from(links).map(link => link.href);
			linkArray;
			"""

			links = await page.evaluate(js_extract_links)
			return links
		
		
		#####################################################################################################
		# We collect links while scrolling since Twitter uses a script that only loads 7 tweets at all times.
		# By scrolling while gathering links we ensure we end up with >7 links.
		#####################################################################################################

		_prev_height = -1
		_max_scrolls = 20
		_scroll_count = 0
		while _scroll_count < _max_scrolls:
			await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
			await page.wait_for_timeout(1000)

			current_links = await extract_links(page)
			for href in current_links:
					regex = r'https?://(www\.)?x\.com/[A-Za-z0-9_]+/status/[0-9]+$'
					if href and re.match(regex, href):
						links.append(href)

			
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
		return list(set(links)) #Using set to ensure we have no duplicates

	#############################################################################
	# This function is no longer in use, but I just wanted to show the algorithm.	
	#############################################################################

	async def _scraper(self, browser, links):
		results = []
		contexts = []

		#Creates context with fixed number of pages
		pages_per_context = 10

		for i in range(0, len(links), pages_per_context):
			context = await browser.new_context()
			contexts.append(context)
			pages = await asyncio.gather(*[context.new_page() for _ in range(pages_per_context)])
			async def _scraping_logic(page, link):
						try:
							await page.goto(link)
							regex = r'https?://(www\.)?x\.com/[A-Za-z0-9_]+/status/[0-9]+$'
							num_code = (re.match(r'https?://(www\.)?x\.com/[A-Za-z0-9_]+/status/([0-9]+)$', link)).group(2)
							url = (re.match(r'https?://(www\.)?x\.com(/[A-Za-z0-9_]+/status/[0-9]+)$', link)).group(2)


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
								reposts=''
								)
							await page.close()
							return fallback_tweet.to_doc()

			#Assign links to pages
			tasks = []
			for page, link in zip(pages, links[i:i+pages_per_context]):		
				tasks.append(_scraping_logic(page, link))
			results.extend(await asyncio.gather(*tasks))

		# Close all contexts
		for context in contexts:
			await context.close()

		return results
	
	async def _api_implementation(self, links):
		'''
		Fetches tweet details based on the undocumented embedding API

		Parameters:
		-----------
		links: []
			A list of tweet URL's to fetch details for

		Returns:
		--------
		tweets : [{}]
			A list of dicts (tweet data) ready for DB insertion
		'''
		async def _fetch_single_tweet(session, link):
			try:
				url = (re.match(r'https?://(www\.)?x\.com(/[A-Za-z0-9_]+/status/[0-9]+)$', link)).group(2)
				link_id = (re.match(r'https?://(www\.)?x\.com/[A-Za-z0-9_]+/status/([0-9]+)$', link)).group(2)
				api_url = f"https://cdn.syndication.twimg.com/tweet-result?features=tfw_timeline_list%3A%3Btfw_follower_count_sunset%3Atrue%3Btfw_tweet_edit_backend%3Aon%3Btfw_refsrc_session%3Aon%3Btfw_fosnr_soft_interventions_enabled%3Aon%3Btfw_mixed_media_15897%3Atreatment%3Btfw_experiments_cookie_expiration%3A1209600%3Btfw_show_birdwatch_pivots_enabled%3Aon%3Btfw_duplicate_scribes_to_settings%3Aon%3Btfw_use_profile_image_shape_enabled%3Aon%3Btfw_video_hls_dynamic_manifests_15082%3Atrue_bitrate%3Btfw_legacy_timeline_sunset%3Atrue%3Btfw_tweet_edit_frontend%3Aon&id={link_id}&lang=en&token=4ctznymvoer"
				logger.debug(f"API URL: {api_url}")
				async with session.get(api_url) as response:
					logger.debug(f"Response status: {response.status}")
					if response.status == 200:
						tweet_data = await response.json()
						logger.debug(f"Response data: {tweet_data}")

						tweet_id = ObjectId(link_id.zfill(24))
						tweet_content = tweet_data.get('text', '')
						tweet_date = tweet_data.get('created_at', '')
						tweet_likes = tweet_data.get('favorite_count', '')

						tweet = Tweet(
							_id=tweet_id, 
							url=url,
							title='',
							description=tweet_content,
							time=tweet_date,
							upvotes=tweet_likes)
						return tweet.to_doc()
					else:
						logger.debug(f"Failed to retrieve data for {link}: {response.status}")
						return None
			except Exception as e:
				logger.debug(f"Error fetching data for {link}: {e}")
				return None

		tweets = []

		async with aiohttp.ClientSession() as session:
			tasks = []

			for i in range(0, len(links), 10):
				chunk = links[i:i+10]
				tasks.extend([_fetch_single_tweet(session=session, link=link) for link in chunk])

				results = await asyncio.gather(*tasks)

				tweets.extend([result for result in results if results is not None])

				tasks.clear()
				asyncio.sleep(1)

		logger.debug(tweets)
		return tweets


	async def scrape(self, post_repo: IPostRepository):
		'''
		This function combines all of the previous declared functions, allowing the frontend to call this function and get the expected result

		Parameters:
		-----------
		post_repo: IPostRepository
			Used to implement repo structure to enforce data access layer seperated from business logic

		Returns:
		--------
		post_results : 
			For now returns tweets as they were inserted into DB
		'''
		async with async_playwright() as p:
			start_time = time.time()
			browser = await p.firefox.launch(args=['--start-maximized'])

			page = await self._login_account(browser=browser)
			if page is None:
				logging.error("Page is none")

			links = await self._link_gatherer(page=page)
			#twitterdata = await self.scraper(browser=browser, links=links)
			end_time_links = time.time()
			total_time_links = end_time_links - start_time

			start_time_api = time.time()
			twitterdata = await self._api_implementation(links=links)
			end_time_api = time.time()
			total_time_api = end_time_api - start_time_api
			links_len = len(links)

			start_time_repo = time.time()
			post_results = await asyncio.gather(*[post_repo.add_post(post) for post in twitterdata])
			end_time_repo =  time.time()
			total_time_repo = end_time_repo - start_time_repo

			end_time = time.time()
			total_time = end_time - start_time
			print(f'{self.keyword}: {links_len} tweets scraped in {total_time} seconds.\nLink Gathering took: {total_time_links}\nAPI Calls took: {total_time_api}\nPushing to DB via Repo took: {total_time_repo}')
			await browser.close()

		return post_results
			




