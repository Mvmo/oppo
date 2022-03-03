compile: examples/example.oppo
	python3 oppo.py --target sickvm --output example --debug TRUE examples/example.oppo

clean:
	rm -rf example.sickc

run: example.sickc
	sick --file example.sickc

example.sickc:
	python3 oppo.py --target sickvm --output example examples/example.oppo