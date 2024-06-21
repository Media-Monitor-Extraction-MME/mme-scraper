'''
This is just a quick prototype script to gather proxies from free-proxy-list.net
'''

import asyncio
from playwright.async_api import async_playwright

async def scrape_proxies():
    async with async_playwright() as p:
        # Launch the browser
        browser = await p.firefox.launch(args=['--start-maximized'], headless=True)
        context = await browser.new_context(no_viewport=True)
        page = await context.new_page()

        # Navigate to the Free Proxy List website
        await page.goto('https://free-proxy-list.net/')

        # Wait for the table to load
        await page.wait_for_selector('#proxylisttable')

        # Extract proxy data where HTTPS is 'yes'
        proxies = await page.evaluate('''() => {
            const rows = Array.from(document.querySelectorAll('#proxylisttable tbody tr'));
            return rows
                .filter(row => row.cells[6].innerText.trim() === 'yes')  # Filter rows where HTTPS is 'yes'
                .map(row => ({
                    ip: row.cells[0].innerText.trim(),
                    port: row.cells[1].innerText.trim(),
                    code: row.cells[2].innerText.trim(),
                    country: row.cells[3].innerText.trim(),
                    anonymity: row.cells[4].innerText.trim(),
                    google: row.cells[5].innerText.trim(),
                    https: row.cells[6].innerText.trim(),
                    lastChecked: row.cells[7].innerText.trim(),
                }));
        }''')

        # Print the extracted proxies
        for proxy in proxies:
            print(proxy)

        # Close the browser
        await browser.close()

# Run the async function
asyncio.run(scrape_proxies())
