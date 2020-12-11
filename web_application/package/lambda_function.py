import json
import logging
import collections
logger = logging.getLogger()
logger.setLevel(logging.INFO)

import boto3
import copy
import random
import math
import base64 as b64

from botocore.exceptions import ClientError

def save(D, table, user):
    try:
        response = table.put_item(
           Item={
                'user': user,
                'data': json.dumps(D)
            }
        )
    except ClientError as e:
        logger.info(e.response['Error']['Message'])
    else:
        pass

def load(table, user):
    try:
        response = table.get_item(
            Key={
                'user': user
            }
        )
    except ClientError as e:
        logger.info(e.response['Error']['Message'])
    else:
        if 'Item' in response:
            item = response['Item']
            logger.info("GetItem succeeded:")
            D = json.loads(item["data"])
            return D
    return None

def init_user(M=3, n=30, E=None, snippets=None):
    len_experts = len(E)
    experts = sorted(random.sample(list(E.keys()), min(M,len_experts)))
    M = len(experts)
    Q_new_normalized = {e: 1/M for e in experts}
    P_new = {a: sum([E[e][a] * Q_new_normalized[e] for e in Q_new_normalized]) for a in snippets}
    actions = []
    weights = []
    for a in P_new:
        actions.append(a)
        weights.append(P_new[a])
    A_new = random.choices(actions, weights=weights, k=1)[0]
    DIR = "https://exp4.s3.amazonaws.com/{snippet}"
    snippet = DIR.format(snippet=random.choice(snippets[A_new]))
    R_new = {
        "Q": Q_new_normalized,
        "A": A_new,
        "P": P_new,
        "snippet": snippet
    }
    sess = {
        "current": {
            "rounds": [
                R_new
            ],
            "n": n
        },
        "past": []
    }
    return sess

def new_session(sess, M=3, n=30, E=None, snippets=None):
    len_experts = len(E)
    experts = sorted(random.sample(list(E.keys()), min(M,len_experts)))
    M = len(experts)
    Q_new_normalized = {e: 1/M for e in experts}
    P_new = {a: sum([E[e][a] * Q_new_normalized[e] for e in Q_new_normalized]) for a in snippets}
    actions = []
    weights = []
    for a in P_new:
        actions.append(a)
        weights.append(P_new[a])
    A_new = random.choices(actions, weights=weights, k=1)[0]
    DIR = "https://exp4.s3.amazonaws.com/{snippet}"
    snippet = DIR.format(snippet=random.choice(snippets[A_new]))
    R_new = {
        "Q": Q_new_normalized,
        "A": A_new,
        "P": P_new,
        "snippet": snippet
    }
    sess["past"].append(copy.deepcopy(sess["current"]))
    del sess["current"]
    sess["current"] = {
            "rounds": [
                R_new
            ],
            "n": n
        }


def run_round(sess, X, E=None, snippets=None):
    if len(sess["current"]["rounds"]) > sess["current"]["n"]:
        return False
    R = sess["current"]["rounds"][-1]
    Q = R["Q"]
    M = len(Q)
    A = R["A"]
    P = R["P"]
    n = sess["current"]["n"]
    k = len(snippets)
    learning_rate = math.sqrt( ((2 * math.log(M)) / (n * k)) )
    X_hat = {a: ( (1-((1-X)/P[a])) if (A == a) else 1 ) for a in P}
    X_tilde = {e: sum([E[e][a] * X_hat[a] for a in X_hat]) for e in Q}
    Q_new = {e: math.exp( (learning_rate * X_tilde[e]) ) * Q[e] for e in Q}
    sum_weights = sum((Q_new.values()))
    Q_new_normalized = {e: (Q_new[e] / sum_weights) for e in Q_new}
    P_new = {a: sum([E[e][a] * Q_new_normalized[e] for e in Q_new_normalized]) for a in snippets}
    actions = []
    weights = []
    for a in P_new:
        actions.append(a)
        weights.append(P_new[a])
    A_new = random.choices(actions, weights=weights, k=1)[0]
    DIR = "https://exp4.s3.amazonaws.com/{snippet}"
    snippet = DIR.format(snippet=random.choice(snippets[A_new]))
    R_new = {
        "Q": Q_new_normalized,
        "A": A_new,
        "P": P_new,
        "snippet": snippet
    }
    sess["current"]["rounds"].append(R_new)

def compile_html(sess, round_html = None, stats_html = None, snippets=None):

    #round_html
    #M, r, n, regret, average, audio

    #stats_html
    #M, n, regret, average, experts

    R = sess["current"]["rounds"][-1]
    Q = R["Q"]
    M = len(Q)
    n = sess["current"]["n"]
    r = len(sess["current"]["rounds"])
    k = len(snippets)
    audio = R["snippet"]
    regret = math.sqrt( (2 * math.log(M) * n * k) ) * 5
    average = regret / n
    experts = json.dumps(Q,indent=4).replace("\n","<br>")

    if r > n:
        return stats_html.format(M=M, n=n, regret=regret, average=average, experts=experts)
    else:
        return round_html.format(M=M, r=r, n=n, regret=regret, average=average, audio=audio)


def lambda_handler(event, context):

    user = event.get('pathParameters', {}).get('user', "")

    if user == "":
        user = "default"

    logger.info(json.dumps(event))

    if event["requestContext"]["http"]["method"] == "POST":
        request = parse_qs( b64.b64decode(event["body"].encode('utf-8')).decode('utf-8') )
        for key in request:
            request[key] = request[key][0]
    elif event["requestContext"]["http"]["method"] == "GET":
        request = event.get("queryStringParameters", {})
    else:
        request = {}
        
    if not request:
        request = {}

    with open( "data.json" ) as fis:
        data = json.load(fis)
    E = data["experts"]
    snippets = data["snippets"]

    with open("html/round.html") as fis:
        ROUND_HTML = fis.read()

    with open("html/stats.html") as fis:
        STATS_HTML = fis.read()

    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

    table = dynamodb.Table('exp4')

    sess = load(table, user)

    if not sess:
        if ("M" in request) and ("n" in request):
            sess = init_user(E=E, M=int(request["M"]), n=int(request["n"]), snippets=snippets)
        else:
            sess = init_user(E=E, M=3, n=30, snippets=snippets)
        save(sess, table, user)
    else:
        if ("M" in request) and ("n" in request):
            new_session(sess, E=E, M=int(request["M"]), n=int(request["n"]), snippets=snippets)
            save(sess, table, user)
        elif "X" in request:
            update = run_round(sess, float(request["X"]), E=E, snippets=snippets)
            save(sess, table, user)

    response = compile_html(sess, round_html = ROUND_HTML, stats_html = STATS_HTML, snippets=snippets)

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type' : 'text/html; charset=UTF-8'
        },
        'body': b64.b64encode(bytes(response, encoding="utf-8")).decode("utf-8"),
        "isBase64Encoded": True
    }

