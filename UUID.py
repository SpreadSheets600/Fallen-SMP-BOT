from mojang import *
# Create a Public API instance
api = API()

name = api.get_username("c422ff9b-d4ab-35cb-a4e6-a0ffe460c136")
print(name)