-include .env

.PHONY: run
run:
	- docker network create $(SHOP_BOT_NETWORK)
	- mkdir -p $(SHOP_BOT_DATA_PATH)
	- sleep 1
	- docker build -t $(SHOP_BOT_DB_IMAGE_NAME) -f db.Dockerfile .
	- docker build -t $(SHOP_BOT_MIGRATIONS_IMAGE_NAME) -f migrations.Dockerfile .
	- docker build -t $(SHOP_BOT_TG_IMAGE_NAME) -f tg_bot.Dockerfile .
	- docker build -t $(SHOP_BOT_ADMIN_IMAGE_NAME) -f admin.Dockerfile .
	- docker-compose up
