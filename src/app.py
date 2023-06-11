import os
import json
import asyncio
from fastapi import FastAPI
import requests
from src.utils import *
from src.schemas import createCourse , processCourse , getTopic, getCourse, fetchTopic , rephraseRequest
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# get catalog
@app.get("/catalog")
def get_catalog():
    return fetch_catalog()


# /create curriculum
@app.post("/create_curriculum")
def create_curriculum(req : createCourse):
    req = req.dict()
    logger.info(f"req --- {req}")
    nearest_course = find_duplicate_course(req["topic"], req["domain"])

    if nearest_course:
        # res.status_code = 203
        return {"msg":"present", "closest_match":nearest_course}
    curriculum = prepare_curricullum(req["topic"] ,req["domain"], req["depth"])

    logger.info(f"create -curriculum result ---- {curriculum}")
    return curriculum

# /create course
@app.post("/create_course")
def create_course(req : processCourse):
    req = req.dict()
    generate_course(req["course_id"])
    return {"msg":"generation_complete"}

# /fetch course
@app.post("/fetch_course")
def fetch_course(req :getCourse):
    req = req.dict()
    course = fetch_course_db(req["course_id"])
    return course
# /fetch curriculu

# /fetch topic
@app.post("/fetch_topic")
def fetch_topic(req : getTopic):
    logger.info(f"req to fetch topic -- {req}")
    req = req.dict()
    logger.info(f"req to fetch topic -- {req}")
    topic = fetch_topic_db(req["topic_id"])
    return topic

# /rephrase
@app.post("/rephrase")
def rephrase_req(req : rephraseRequest):
    req = req.dict()
    rephrased = rephrase(req)
    return rephrased


# /fetch video
@app.post("/fetch_video")
def fetch_video(req):
    pass
