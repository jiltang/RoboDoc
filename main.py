# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START gae_flex_quickstart]
import logging
import numpy as np

from math import ceil

from flask import Flask, render_template, request, jsonify
from google.cloud import datastore
logging.basicConfig(level=logging.DEBUG)

NUM_SYMPTOMS = 23

DIAGNOSIS = 137
NEW_QUESTION = 138

NUM_COMMON = 23

app = Flask(__name__)

@app.route('/apiTest', methods=['POST'])
def apiTest():
    content = request.get_json()
    return "JSON output:\n" + str(content)

@app.route('/')
def hello():
    return render_template('index.html')

def calculateProbabilityScore(mappingsArr, symptomsWeights):
        return mappingsArr @ symptomsWeights

def printSymptomsWeights(probabilityScores):
        diseasesNP = np.array(diseases)
        diseasesNP.shape = (-1, 1)
        out = np.c_[diseasesNP, probabilityScores]
        out = out[out[:,1].astype(np.float).argsort()[::-1]]
        return str(out)
    
def generateQuestionForPatient(patient):
    print(patient['weights'])
    np.set_printoptions(formatter={'float': lambda x: "{0:0.3f}".format(x)})

    symptomsFile = open('symptomsList.txt', 'r')
    symptoms = [x.strip() for x in symptomsFile.readlines()]
    symptomsFile.close()
    
    diseasesFile = open('diseases.txt', 'r')
    diseases = [x.strip() for x in diseasesFile.readlines()]
    diseasesFile.close()

    #labels
    diseasesNP = np.array(diseases)
    diseasesNP.shape = (-1, 1)
    
    mappingsArr = np.loadtxt('weights-output.txt', delimiter='\t', usecols=range(1, len(symptoms)+1))
    mappingsArr[0:23, 1:] = mappingsArr[0:23, 1:] * 10
    print(mappingsArr)
    mappingsArr = mappingsArr / mappingsArr.sum(axis=0)
    logging.info(mappingsArr)
    
    runningScores = np.c_[diseasesNP, np.zeros((len(diseases), 1))]
    
    weights = np.array(patient['weights'])    
    logging.info(weights)
    logging.info(calculateProbabilityScore(mappingsArr, weights))
    runningScores[:, 1] = np.squeeze(calculateProbabilityScore(mappingsArr, weights))
    runningScoresNew = runningScores[runningScores[:,1].astype(np.float).argsort()[::-1]]
    logging.info(runningScoresNew)
    numDiseases = len(diseases)
    numSymptoms = len(symptoms)
    doneIndices = list(np.nonzero(weights)[0])
    numQuestions = len(doneIndices)
    print(np.std(runningScores[:, 1].astype(np.float)))
    if numQuestions == NUM_SYMPTOMS or (numQuestions >= 3 and np.std(runningScores[:, 1].astype(np.float)) > 0.15):
        # we're finished
        nums = runningScores[:, 1].astype(np.float)
        bestScore = np.max(nums)
        winningIndices =  nums.argsort()[-3:][::-1]
        print(winningIndices)
        winningDiseases = runningScores[np.array(winningIndices)]
        return DIAGNOSIS, winningDiseases
        
    else:
        numTop = ceil(numDiseases - (numDiseases/numSymptoms) * (numQuestions - 1))
        subset = np.squeeze(runningScoresNew[0:numTop, 0])
        indices = np.vectorize(lambda x: diseases.index(x))(subset)
        mappingsArrNew = mappingsArr[indices]
        stdevs = np.std(mappingsArrNew, axis=0)
        ranking = list(np.argsort(stdevs)[::-1])

        remaining = list(filter(lambda x : x not in doneIndices, ranking))
        bestSymptom = symptoms[remaining[0]]
        options = {"Yes": "1", "Maybe": "0.25", "No": "-0.5"}

        questions = open('questions.txt', 'r')
        questions = dict([line.lower().split(': ') for line in questions.readlines()])
        question = questions[bestSymptom].capitalize()

        return NEW_QUESTION, question, options, bestSymptom


@app.route('/createPatientID', methods=['POST'])
def createPatientID():
    ds = datastore.Client()
    logging.info(request.mimetype)
    logging.info(request.data)
    info = request.get_json()
    logging.info("Test2!!")
    age = info['age']
    sex = info['sex']
    weights = [0] * NUM_SYMPTOMS
    entity = datastore.Entity(key=ds.key('patient'))
    entity['age'] = age
    entity['sex'] = sex
    entity['weights'] = weights

    ds.put(entity)

    patientKey = str(entity.key.to_legacy_urlsafe())

    output = generateQuestionForPatient(entity)
    returnType = output[0]
    if returnType == DIAGNOSIS:
        returnType, winningDiseases = output
        winningDiseases = winningDiseases.tolist()
        data = {
            "type": "diagnosis",
            "diagnoses": diagnoses
        }
    else:
        returnType, question, options, questionID = output
        data = {
            "type": "question",
            "ID": patientKey,
            "question": question,
            "options": options,
            "questionID": questionID
        }
    return jsonify(data)

@app.route('/receiveResponse', methods=['POST'])
def receiveResponse():
    ds = datastore.Client()
    info = request.get_json()
    patientID = info['patientID']
    if patientID.startswith("b'"): patientID = patientID[2:-1]
    print("ID:", patientID)
    questionID = info['questionID']
    answer = info['answer']
    
    weights = [0] * NUM_SYMPTOMS
    entity = ds.get(datastore.key.Key.from_legacy_urlsafe(patientID))
    
    # we find the index we need to update
    
    symptomsFile = open('symptomsList.txt', 'r')
    symptoms = [x.strip() for x in symptomsFile.readlines()]
    symptomsFile.close()
    
    index = symptoms.index(questionID)
    entity['weights'][index] = float(answer)
    
    ds.put(entity)
    
    output = generateQuestionForPatient(entity)
    returnType = output[0]

    if returnType == DIAGNOSIS:
        print("A")
        returnType, winningDiseases = output
        winningDiseases = winningDiseases.tolist()
        data = {
            "type": "diagnosis",
            "diagnoses": winningDiseases
        }
    else:
        returnType, question, options, questionID = output
        data = {
            "type": "question",
            "ID": patientID,
            "question": question,
            "options": options,
            "questionID": questionID
        }
    return jsonify(data)

@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='0.0.0.0', port=3000, debug=True)
# [END gae_flex_quickstart]
