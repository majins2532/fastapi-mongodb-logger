build_production:
	docker-compose -f docker-compose.build.yml build live
push_production:
	docker-compose -f docker-compose.build.yml push live
pull_production:
	docker-compose -f docker-compose.build.yml pull live
restart:
	docker-compose restart
start_live:
	docker-compose up -d live
down:
	docker-compose down
