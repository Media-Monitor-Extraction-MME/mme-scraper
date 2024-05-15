'''
Implementation of ICommentRepository interface
'''

#Imports
from .ICommentRepo import ICommentRepository

class CommentRepo(ICommentRepository):
    
    #Fields
    document = [{}]
    collection = str

    #Methods
    def add_comment(document):
        print("add comment")

    def remove_comment(document):
        print("remove comment")

    def update_comment(document):
        print("update comment")

    def search_comment(document):
        print("comment searched")

    def get_comment_by_id(document):
        print("got comment by id")

    def get_comment_id(document):
        print("got comment id")