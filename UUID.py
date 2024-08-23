from mojang import *
# Create a Public API instance
api = API()

name = api.get_username("c422ff9b-d4ab-35cb-a4e6-a0ffe460c136")
get_uuid = api.get_uuid("SpreadSheets")

get_profile = api.get_profile("get_uuid")

print(name)
print(get_uuid)
print(get_profile)