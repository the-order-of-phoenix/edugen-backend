import json
from pydantic import BaseModel , conlist , confloat , AnyHttpUrl
from typing import Dict , Optional
from enum import Enum
from fastapi import Query
#### front end callls
# create curriculum
create_curricullum = {
    "request":{
        "topic":"",
        "domain":"",
        "depth":""
    },
    "response":{
        "curriculum":{
            "course_id":"",
            "domain":"",
            "title":"",
            "descritpion":"",
            "level":"",
            "modules":{
                "topic_id":"topic",
            }
        }
    },
    "response_203":{
        "msg":"present",
        "closest_match":""
    }
}

# create course
create_course = {
    "request":{
        "course_id":""
    },
    "response":{
        "course_id":""
    }
}

# fetch course
featch_course = {
    "request":{
        "course_id":""
    },
    "response":{
        "is_processed":False,
        "curriculum":{
            "course_id":"",
            "domain":"",
            "title":"",
            "descritpion":"",
            "level":"",
            "modules":{
                "topic_id":"topic",
            }
        }
    }
}

# featch topiv
fetch_topic = {
    "request":{
        "topic_id":""
    },
    "response":{
        "topic_id":"",
        "text":""
    }
}


# rephrase
rephrase = {
    "request":{
        "topic_id":"",
        "analogy":"",
        "depth":""
    },
    "response":{
        "topic_id":"",
        "text":""
    }
}

### video generator calls

# generate video
generate_video = {
    "request":{
        "text":""
    },
    "response":{
        "videoUrl":""
    }
}

class CreateCurriculum(BaseModel):
    topic : str
    domain : str
    depth : str


class createCourse(CreateCurriculum):
    pass


class genCourse(BaseModel):
    course_id: str

class processCourse(genCourse):
    pass

class getCourse(genCourse):
    pass
class fetchTopic(BaseModel):
    topic_id: str

class getTopic(fetchTopic):
    pass

class rephrase(BaseModel):
    topic_id :str
    analogy : str
    depth: str

class rephraseRequest(rephrase):
    pass