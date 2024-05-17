'''
Comment entity. 
Comments need to be morphed into this structure to enforce correct data storage
'''

class Comment:
    def __init__(self, _id, postID, parentID, score, comment):
        self._id = _id
        self.postID = postID
        self.parentID = parentID
        self.score = score
        self.comment = comment

    def to_doc(self):
        return {
            "_id": self._id,
            "PostID": self.postID,
            "ParentID": self.parentID,
            "Score": self.score,
            "Comment": self.comment
        }