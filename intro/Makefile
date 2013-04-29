mything:
	gcc mything.c -o mything

run-mything: mything
	./mything

extension:
	python setup.py build

run-extension: extension
	python example.py

test-interpreter:
	cd build/lib.linux-i686-2.6 && python

clean:
	rm -rf build
