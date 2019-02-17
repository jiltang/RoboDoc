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



#class Patient(ndb.Model):
#    weights = ndb.FloatProperty(repeated=True)
#    sex = ndb.StringProperty()
#    age = ndb.IntegerProperty()

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
    
    mappingsArr = np.loadtxt('symptomsOut.txt', delimiter='\t', usecols=range(1, len(symptoms)+1))
    mappingsArr = mappingsArr / mappingsArr.sum(axis=0)
    logging.info(mappingsArr)
    
    runningScores = np.c_[diseasesNP, np.zeros((len(diseases), 1))]
    
    weights = np.array(patient['weights'])    
    logging.info(weights)
    logging.info(calculateProbabilityScore(mappingsArr, weights))
    runningScores[:, 1] = np.squeeze(calculateProbabilityScore(mappingsArr, weights))
    runningScoresNew = runningScores[runningScores[:,1].astype(np.float).argsort()[::-1]]
    logging.info(runningScoresNew)
    numTop = 5 # ceil(len(diseases) - (len(diseases)/len(symptoms)) * (numQuestions - 1))
    subset = np.squeeze(runningScoresNew[0:numTop, 0])
    indices = np.vectorize(lambda x: diseases.index(x))(subset)
    mappingsArrNew = mappingsArr[indices]
    stdevs = np.std(mappingsArrNew, axis=0)
    ranking = list(np.argsort(stdevs)[::-1])
    doneIndices = list(np.nonzero(weights)[0])
    remaining = list(filter(lambda x : x not in doneIndices, ranking))
    bestSymptom = symptoms[remaining[0]]
    options = {"Yes": "1", "Maybe": "0", "No": "-0.5"}
    
    questions = open('questions.txt', 'r')
    questions = dict([map(lambda x: x.lower().strip(), line.split(': ')) for line in questions.readlines()])
    question = questions[bestSymptom]
    
    return question, options, bestSymptom


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
    print(entity['weights'])

    question, options, questionID = generateQuestionForPatient(entity)
    
    output = {
        "ID": patientKey,
        "question": question,
        "options": options,
        "questionID": questionID
    }
    return jsonify(output)

@app.route('/receiveResponse', methods=['POST'])
def receiveResponse():
    ds = datastore.Client()
    print("Line 135!")
    info = request.get_json()
    print("Line 137!")
    patientID = info['patientID']
    print("Line 139!")
    patientID = patientID[2:-1]
    print("Line 141!")
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
    
    question, options, questionID = generateQuestionForPatient(entity)
    
    output = {
        "ID": patientID,
        "question": question,
        "options": options,
        "questionID": questionID
    }
    return jsonify(output)

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
