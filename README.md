# NASA Mars Pics API

## Concept

NASA provides [many publicly available APIs](https://api.nasa.gov/). One of them
returns photos gathered by rovers sent to Mars. Unfortunately, many photos are
relatively dull (you can read about it in
[this post](http://pfertyk.me/2017/06/getting-mars-photos-from-nasa-using-aiohttp/)).
This program is supposed to gather the links to photos, check if they might contain
interesting content, and then display a random photo when a URL is accessed.

## Setup

Clone this repository, then create a `.env` file:

```
DATABASE_URL=postgresql://nasa:nasa@db:5432/nasa
NASA_API_KEY={YOUR_NASA_API_KEY}
```

You can apply for a NASA API key [here](https://api.nasa.gov/). Without it, a
`DEMO_KEY` value will be used, which does not provide adequate performance
(you will not be allowed to access the API frequently enough to index the data).

You can build and run the project using `docker-compose`:

```
docker-compose build
docker-compose up
```

## Usage

To index the data access <http://localhost:8888/index>. This will run a loop that
accesses NASA API, saves the image links in the database, and checks the attributes
of images (size and color mode) to decide if an image is worth displaying.

To get a random image, access <http://localhost:8888>.

## Deploying to Heroku

You can easily run this on Heroku. You need to add Heroku Postgres add-on and
provide the same 2 config vars as in the `.env` file

## Demo

Demo is available [here](https://nasa-mars-pics.herokuapp.com/). Keep in mind that,
since it's Heroku and the application falls asleep after a while ,
it can take a while for the first image to be shown.
