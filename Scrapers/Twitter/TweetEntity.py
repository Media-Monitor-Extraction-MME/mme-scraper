'''
Tweet entity. 
Tweets need to be morphed into this structure to enforce correct data storage
'''

class Tweet:
    '''
    A class to represent a Tweet entity

    Attributes:
    -----------
    _id : str
        A tweets unique identifier
    url : str
        Url of a tweet
    title : str
        Tweet title (None, used for Reddit)
    description : str
        The content of a tweet
    time : str
        string representation of timestamp/date
    upvotes : str
        Count of likes
    views : str
        Count of views
    reposts : str
        Count of reposts
    origin : str = "Twitter"
        Platform where the data has been gathered from

    
    '''
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
        '''
        Converts Tweet entity to dictionary to allow for DB insertion.
        Could have also used __dict__ but o well

        Returns:
        --------
        dict
            A dictionary representation of itself (Tweet entity/object)
        '''
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
