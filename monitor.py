from flask import Flask, jsonify
from perma_times import get_objects


app = Flask(__name__)

@app.route('/')
def perma_monitor():
    """hit the Perma API and get the last twenty captures for analysis"""
    limit = 20
    thresholds = {
        'unfinished': 7,
        'statistic': 0.9
    }
    objects = get_objects(limit, 0)

    # how many of the last {limit} captures are not complete?
    unfinished = len([x for x in objects if x[3] is None])

    # what is the ratio of seconds from now to the last completed capture
    # to the seconds from now to {limit} captures ago?
    # 'mrcc' means 'most recent completed capture'
    mrcc = filter(lambda x: x[3] is not None, objects)[0][1]
    nthago = objects[-1][1]
    # previously known as stat2a
    statistic = mrcc / nthago

    report = {
        'status': 'OK',
        'messages': []
    }
    if unfinished > thresholds['unfinished']:
        report['status'] = 'PROBLEM'
        report['messages'].append("{count} uncompleted captures in the last {limit}".format(count=unfinished, limit=limit))

    if statistic > thresholds['statistic']:
        report['status'] = 'PROBLEM'
        report['messages'].append("statistic for time to last successful capture) is {stat}".format(stat=statistic))

    output = {
        'unfinished': unfinished,
        'statistic': statistic,
        'report': report
    }
    return jsonify(**output)