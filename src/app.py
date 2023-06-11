import os
import json
import asyncio
from fastapi import FastAPI
import requests
from utils import *
from schemas import *

app = FastAPI()

# get catalog
@app.get("/catalog")
def get_catalog(request):
    return fetch_catalog()


# /create curriculum
@app.post("/create_curriculum")
def create_curriculum(res , req):
    req = req.json()
    nearest_course = find_duplicate_course(req["topic"], req["domain"])
    if not nearest_course:
        res.status_code = 203
        return {"msg":"present", "closest_match":nearest_course}
    curriculum = prepare_curricullum(req["topic"] ,req["domain"], req["depth"])
    return curriculum

# /create course
@app.post("/create_course")
def create_course(res , req):
    req = req.json()
    generate_course(req["course_id"])
    return {"msg":"generation_complete"}

# /fetch course
@app.post("/fetch_course")
def fetch_course(res , req):
    req = req.json()
    course = fetch_course(req["course_id"])
    return course
# /fetch curriculu

# /fetch topic
@app.post("/fetch_topic")
def fetch_topic(res , req):
    req = req.json()
    topic = fetch_topic(req["topic_id"])
    return topic

# /rephrase
@app.post("/rephrase")
def rephrase(res , req):
    req = req.json()
    rephrased = rephrase(req)
    return rephrased


# /fetch video
@app.post("/fetch_video")
def fetch_video(res , req):
    pass
