FROM  python:3.8-slim-buster
WORKDIR /app

RUN apt-get update -y && apt-get install -y --no-install-recommends python3-dev build-essential default-libmysqlclient-dev pkg-config wget ffmpeg libtbb2 gfortran apt-utils qt5-default libopenblas-base libopenblas-dev liblapack-dev libatlas-base-dev libavcodec-dev libavformat-dev libavutil-dev libswscale-dev libpng-dev libtiff5-dev libdc1394-22-dev libxine2-dev libv4l-dev libgstreamer1.0 libgstreamer1.0-dev libgstreamer-plugins-base1.0-0 libgstreamer-plugins-base1.0-dev libglew-dev libpostproc-dev libeigen3-dev libtbb-dev zlib1g-dev libsm6 libxext6 libxrender1 vim

COPY requirments.txt /app/

RUN pip3 install -r requirements.txt

COPY . /app/

CMD ["uvicorn", "Core.main:app", "--host", "0.0.0.0", "--port", "6543", "--workers", "4"]