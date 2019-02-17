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
import logging, numpy

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
    import numpy as np
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
    
    weights = np.ndarray(patient['weights'])    
    logging.info(weights)
    logging.info(calculateProbabilityScore(mappingsArr, weights))
    runningScores[:, 1] = np.squeeze(calculateProbabilityScore(mappingsArr, weights))
    runningScoresNew = runningScores[runningScores[:,1].astype(np.float).argsort()[::-1]]
    logging.info(runningScoresNew)
    subset = np.squeeze(runningScoresNew[0:5, 0])
    indices = np.vectorize(lambda x: diseases.index(x))(subset)
    mappingsArrNew = mappingsArr[indices]
    stdevs = np.std(mappingsArrNew, axis=0)
    ranking = list(np.argsort(stdevs)[::-1])
    doneIndices = list(np.nonzero(runningWeights)[0])
    remaining = list(filter(lambda x : x not in doneIndices, ranking))
    best = remaining[0]
    logging.info("Best index is: {}.")
    return best


@app.route('/createPatientID', methods=['POST'])
def createPatientID():
    ds = datastore.Client()


    logging.info('hi')
    logging.info('hi')
    info = request.get_json()
    age = info['age']
    sex = info['sex']
    weights = [0] * NUM_SYMPTOMS
    entity = datastore.Entity(key=ds.key('patient'))
    entity.update({
        'age': age,
        'sex': sex,
        'weights': weights,
    })

    ds.put(entity)

    patientKey = str(entity.key.to_legacy_urlsafe())
    
    
    output = {
        "ID": patientKey,
        "question": generateQuestionForPatient(entity)
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
