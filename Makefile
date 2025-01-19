main = src/main.py
data = src web config.json

run:
	python $(main)

build-and-run:
	$(MAKE) build
	dist/main.exe

build: src/* web/*
	pyinstaller --onefile --add-data "web:web" --add-data "config.json:." $(main)

clean:
	-rm -r build
	-rm -r dist
	-rm main.spec
