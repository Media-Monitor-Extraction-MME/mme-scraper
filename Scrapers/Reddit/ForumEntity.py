'''
Forum entity. 
Forums need to be morphed into this structure to enforce correct data storage
'''

class Forum:
    def __init__(self, _id, title, members, link):
        self._id = _id
        self.title = title
        self.members = members
        self.link = link

    def to_doc(self):
        return {
            "_id": self._id,
            "Title": self.title,
            "Members": self.members,
            "Link": self.link
        }