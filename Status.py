import discord
from mcstatus import JavaServer

server = JavaServer(host = "pre-01.gbnodes.host",port=25610)
print(server.status().version.name)
print()

print(server.status().latency)
print()

print(server.status().players.online)
print()

print(server.status().players.max)
print()

print(server.status().software)