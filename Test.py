import finnhub

avax = finnhub.Client(api_key="cqnpr21r01qo8864oasgcqnpr21r01qo8864oat0")
print(avax.quote('AVAX-USD'))