.PHONY: image_generation_service video_generation_service

image_generation_service:
	cd image_generation_service && \
	source venv/bin/activate && \
	fastapi dev --port 8001

video_generation_service:
	cd video_generation_service && \
	source venv/bin/activate && \
	fastapi dev --port 8002