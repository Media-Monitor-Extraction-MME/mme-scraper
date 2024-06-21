# from fp.fp import FreeProxy
# import asyncio

# def collect_proxies(num_proxies=10):
#     proxies = []

#     while len(proxies) < num_proxies:
#         try:
#             proxy = FreeProxy(https=True).get()
#             proxies.add(proxy)

#         except Exception as e:
#             print(f"Error fetching proxy: {e}")
#             continue

#     return list(set(proxies))

# proxies_list = collect_proxies(10)

# print("\nCollected Proxies:")
# for proxy in proxies_list:
#     print(proxy)

import requests

response = requests.get('https://api.getproxylist.com/proxy')
if response.status_code == 200:
    proxy = response.json()
    print(proxy)

print(response)







