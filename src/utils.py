import json
import requests
import asyncio
import pymongo
import os
import uuid
from bson.objectid import ObjectId

# connect the db
client = pymongo.MongoClient(os.get_env("MONGO_URI"))
db = client[os.get_env("MONGO_DB")]

bard_token = os.get_env("BARD_TOKEN")

# update db
def update_db(collection , query , update_querr):
    collection = db[collection]

    update_query = {"$set":update_query}
    # Update documents in the collection based on the filter query
    collection.update_many(query, update_query)


# insert into db
def insert_db(collection_name , document):
    # db = client[database_name]
    # Access the specified collection
    collection = db[collection_name]
    # Insert the document into the collection
    inserted_document = collection.insert_one(document)
    return inserted_document

# > insert curricullum
def insert_course(curricullum):
    curricullum["is_processed"] = False
    inserted_document = insert_db("courses", curricullum)
    return inserted_document

# > insert topic
def insert_topic(topic):
    return insert_db("topic", topic)

# fetch from db
def fetch_from_db(collection, query):
    collection = db[collection]

    # Fetch documents from the collection based on the query
    if query is None:
        documents = collection.find()
    else:
        documents = collection.find(query)
    return documents

def fetch_course(course_id):
    return fetch_from_db("courses", {"_id": ObjectId(course_id)})

def fetch_topic(topic_id):
    return fetch_from_db("topic", {"_id": ObjectId(topic_id)})

def fetch_catalog():
    courses = fetch_from_db("courses" , None)
    catalog = []
    for course in courses:
        del course["modules"]
        catalog.append(course)

    return catalog

## Bard function
def prepare_curricullum(topic , domain , depth):
    schema = {
        "title":"title",
        "level":"level",
        "description":"",
        "domain":"",
        "modules":[
            {
            "titles":"titles",
            "description":"description",
            "topics":[
                "topic1",
                "topic2"
                ]
            }
        ]
    }
    prompt = f"give me the curriculum for the topic {topic}, the depth of the curriculum should be {depth} related to the domain of {domain}, return in proper json string that can be directed loaded as json object , whole scheme should look like this {schema} "
    API_ENDPOINT = "us-central1-aiplatform.googleapis.com"
    PROJECT_ID = "signzy-india-apis"
    MODEL_ID = "text-bison@001"

    url = f"https://{API_ENDPOINT}/v1/projects/{PROJECT_ID}/locations/us-central1/publishers/google/models/{MODEL_ID}:predict"
    headers = {
        "Authorization": f"Bearer {bard_token}",  # Replace YOUR_ACCESS_TOKEN with your actual access token
        "Content-Type": "application/json"
    }

    data = {
        "instances": [
            {
                "content": prompt
            }
        ],
        "parameters": {
            "temperature": 0.2,
            "maxOutputTokens": 1024,
            "topP": 0.8,
            "topK": 40,
            "allow_unsafe":True
        }
    }

    response = requests.post(url, headers=headers, json=data)
    result=""
    if response.status_code == 200:
        result = response.json()["predictions"][0]["content"]
    else:
        print("Request failed with status code:", response.status_code)

    result = clean_curricullum_json(result)

    _ = insert_course(result)
    return result

def clean_curricullum_json(response):
    response = response.replace(" ","")
    response = response.replace("```", "")
    response = response.replace("\n", "")

    curr = json.loads(response)

    modules = curr["modules"]

    modules_dict = {str(uuid.uuid4()): mod for mod in modules}

    curr["modules"] = modules_dict
    # curr["course_id"] = str(uuid.uuid4())

    return curr

# generate explanation
def get_explanation(prompt):

    API_ENDPOINT = "us-central1-aiplatform.googleapis.com"
    PROJECT_ID = "signzy-india-apis"
    MODEL_ID = "text-bison@001"

    url = f"https://{API_ENDPOINT}/v1/projects/{PROJECT_ID}/locations/us-central1/publishers/google/models/{MODEL_ID}:predict"
    headers = {
        "Authorization": f"Bearer {bard_token}",  # Replace YOUR_ACCESS_TOKEN with your actual access token
        "Content-Type": "application/json"
    }

    data = {
        "instances": [
            {
                "content": prompt
            }
        ],
        "parameters": {
            "temperature": 0.2,
            "maxOutputTokens": 1024,
            "topP": 0.8,
            "topK": 40,
            "allow_unsafe":True
        }
    }

    response = requests.post(url, headers=headers, json=data)
    result=""
    if response.status_code == 200:
        result = response.json()["predictions"][0]["content"]
    else:
        print("Request failed with status code:", response.status_code)
    return result


def generate_prompt(topic , analogy):
    prompt = f"can you explain the following topic as much as you can {topic}"
    if analogy:
        prompt += f"with the analogy of {analogy}"
    return prompt

# course generation
def generate_course(course_id):
    curr  = fetch_course(course_id)
    modules = curr["modules"]

    for topic_id , topic in modules:
        prompt = generate_prompt(topic, analogy=None)
        text = get_explanation(prompt)

        temp_dict = {
            "topic": topic,
            "text":text
        }

        _ = insert_topic(temp_dict)

    update_db("courses", {"_id":ObjectId(course_id)} , {"is_processed":True})

# rephrase
def rephrase(criteria):
    topic_id = criteria["topic_id"]
    depth = criteria["depth"]
    analogy = criteria["analogy"]

    topic = fetch_topic(topic_id)

    prompt = f"can you rephrase the following text with the analogy of {analogy} and {depth} its depth"

    text = get_explanation(prompt)
    return {
        "_id":topic_id,
        "text":text
    }

# levenstien
def calculate_levenshtein_distance(phrase1, phrase2):
    m = len(phrase1)
    n = len(phrase2)

    # Create a matrix to store the distances
    distance = [[0] * (n + 1) for _ in range(m + 1)]

    # Initialize the first row and column of the matrix
    for i in range(m + 1):
        distance[i][0] = i
    for j in range(n + 1):
        distance[0][j] = j

    # Calculate the Levenshtein distance
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if phrase1[i - 1] == phrase2[j - 1]:
                cost = 0
            else:
                cost = 1

            distance[i][j] = min(
                distance[i - 1][j] + 1,  # Deletion
                distance[i][j - 1] + 1,  # Insertion
                distance[i - 1][j - 1] + cost  # Substitution
            )

    return distance[m][n]

# find nearest subjects
def find_nearest_subjects(list_of_subjects , source_subject):
    scores = {}
    for sub in list_of_subjects:
        lev_score = calculate_levenshtein_distance(sub , source_subject)
        scores[sub] = lev_score

    threshold = 4
    min_value = min(scores , key=scores.get)
    min_key = min_value
    min_value = scores[min_key]

    if threshold <= min_value:
        return min_key
    return None

# fetch all related domains
def fetch_related_courses(domain):
    courses = fetch_from_db("courses" , query={"domain":domain})
    related_courses = []

    for course in courses:
        c = course["title"]
        related_courses.append(c)

    return related_courses


def find_duplicate_course(domain, source_subject):
    related_course = fetch_related_courses(domain)
    nearest_subject = find_nearest_subjects(related_course, source_subject)
    return nearest_subject


# fetch video