'''
Tweet entity. 
Tweets need to be morphed into this structure to enforce correct data storage
'''

class Tweet:
    def __init__(self, _id: str, url: str, title: str, description: str, time: str, upvotes: str, views: str, reposts: str, origin: str ="Twitter"):
        self._id = _id
        self.url = url
        self.title = title
        self.description = description
        self.time = time
        self.upvotes = upvotes
        self.views = views
        self.reposts = reposts
        self.origin = origin

    def to_doc(self):
        return {
            "_id": self._id,
            "url": self.url,
            "title": self.title,
            "description": self.description,
            "time": self.time,
            "upvotes": self.upvotes,
            "views": self.views,
            "reposts": self.reposts,
            "origin": self.origin
            }
