compile: examples/example.oppo
	python3 oppo.py --compile sickvm --output example --debug TRUE examples/example.oppo

run: example.sickc
	sick --file example.sickc

example.sickc:
	python3 oppo.py --compile sickvm --output example --debug TRUE examples/example.oppo