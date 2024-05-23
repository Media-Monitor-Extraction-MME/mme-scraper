'''
Implementation of IPostRepository interface
'''

#Imports
from .IPostRepo import IPostRepository

class PostRepo(IPostRepository):

    def __init__(self) -> None:
        super().__init__()
        
    #Fields
    document = [{}]
    collection = str

    #Methods
    def add_post(document):
        ...
        

    def remove_post(document):
        print("remove post")

    def update_post(document):
        print("update post")

    def search_post(document):
        print("post searched")

    def get_post_by_id(document):
        print("got post by id")

    def get_post_id(document):
        print("got post id")