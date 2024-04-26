'''
Tweet entity. 
Tweets need to be morphed into this structure to enforce correct data storage
'''

class Tweet:
    def __init__(self, _id, link, content, date, likes, reposts, quotes, bookmarks, views, comments):
        self._id = _id
        self.link = link
        self.content = content
        self.date = date
        self.likes = likes
        self.reposts = reposts
        self.quotes = quotes
        self.bookmarks = bookmarks
        self.views = views
        self.comments = comments

    def to_doc(self):
        return {
            "id": self._id,
            "link": self.link,
            "content": self.content,
            "date": self.date,
            "likes": self.likes,
            "reposts": self.reposts,
            "quotes": self.quotes,
            "bookmarks": self.bookmarks,
            "views": self.views,
            "comments": self.comments
        }
