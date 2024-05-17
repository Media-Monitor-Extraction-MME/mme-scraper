'''
Post entity. 
Posts need to be morphed into this structure to enforce correct data storage
'''

class Post:
    def __init__(self, _id, subreddit, title, score, link):
        self._id = _id
        self.subreddit = subreddit
        self.title = title
        self.score = score
        self.link = link

    def to_doc(self):
        return {
            "_id": self._id,
            "Subreddit": self.subreddit,
            "Title": self.title,
            "Score": self.score,
            "Link": self.link
        }
        