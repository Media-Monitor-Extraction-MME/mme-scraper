import twint
 
# Configure
c = twint.Config()
c.Search = "search term"  # Replace with your search term
c.Limit = 100  # Number of tweets to retrieve
 
# Run
twint.run.Search(c)