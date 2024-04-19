'''
Implementation of  ICommunityRepository interface
'''

#Imports
import ICommunityRepository

class CommunityRepo(ICommunityRepository):

    #Fields
    document = [{}]
    collection = str

    #Methods
    def add_community(document):
        print("add ICommunity")

    def remove_community(document):
        print("remove ICommunity")

    def update_community(document):
        print("update ICommunity")

    def search_community(document):
        print("community searched")

    def get_community_by_id(document):
        print("got community by id")

    def get_community_id(document):
        print("got community id")