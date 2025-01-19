main = src/main.py
name = ChatWidget

run:
	python $(main)

build-and-run:
	$(MAKE) build
	dist/$(name)

build: src/* web/* icon/*
	pyinstaller --onefile --console --add-data "web:web" --add-data "config.json:." -i icon/sized.ico -n $(name) $(main)

clean:
	-rm -rf dist build *.spec
