################################

docker build -t st-geovisor-api:0.1

For use see shell e.sh

#Comments

Install gdal for linux in virtual env

sudo pip3 install GDAL==$(gdal-config --version | awk -F'[.]' '{print $1"."$2}') --global-option=build_ext --global-option="-I/usr/include/gdal"

