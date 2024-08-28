import os
import finnhub

finnhub_client = finnhub.Client(api_key="cqnpr21r01qo8864oasgcqnpr21r01qo8864oat0")

ETH_current_price = finnhub_client.quote(symbol="ETH-USD")["c"]
BTC_current_price = finnhub_client.quote(symbol="BTC-USD")["c"]
BNB_current_price = finnhub_client.quote(symbol="BNB-USD")["c"]
SOL_current_price = finnhub_client.quote(symbol="SOL-USD")["c"]
AVAX_current_price = finnhub_client.quote(symbol="AVAX-USD")["c"]

print(f"ETH: {ETH_current_price}")
print(f"BTC: {BTC_current_price}")
print(f"BNB: {BNB_current_price}")
print(f"SOL: {SOL_current_price}")
print(f"AVAX: {AVAX_current_price}")
