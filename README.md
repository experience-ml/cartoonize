# Cartoonizer

> Convert images and videos into a cartoon!

The webapp is deployed here - 

## Installation

### Prerequisites for Google Cloud and Algorithmia

### Using Docker

The easiest way to get the webapp running is by using the Dockerfile:

1. `cd` into the root directory and build the image
```
docker build -t cartoonize .
```
2. Run the container by exposing the appropriate ports
```
docker run -p 8080:8080 cartoonize
```

**Note**: In the `Dockerfile`, you'll have to change the port in the `gunicorn` command to `8080` to make the above instruction work! The value `$PORT` pertains to Google Cloud Run requirements.

### Using `virtualenv`

1. Make a virtual environment using `virutalenv` and activate it
```
virtualenv -p python3 cartoonize
source cartoonize/bin/activate
```
2. Install python dependencies
```
pip install -r requirements.txt
```
3. Run the webapp (run locally unless you have cloud run and algorithmia setup)
```
python app.py --run_local 1
```

## License
