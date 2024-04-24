'''
Account for link gathering in twitter_scraper
'''

class Account:
    def __init__(self, first_name, last_name, email, date_of_birth, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.date_of_birth = date_of_birth
        self.password = password

    @staticmethod
    async def email_generator():
        ...

    @staticmethod
    async def random_credentials_generator():
        ...

    async def create_account():
        ...