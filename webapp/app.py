#!/usr/bin/env python3

import auxiliary
from flask import Flask, render_template
from generatetopo import odl_topo_builder
from get_stats import Odl_Stat_Collector
from deviceInfo import odl_switch_info

app = Flask(__name__)

# odlControllerList = auxiliary.device_scan()
# controllerIP = odlControllerList[0]
controllerIP = "134.117.89.138"


@app.route("/")
def index():
    return render_template('home.html')


@app.route("/topology")
def topology():
    parser = odl_topo_builder(controllerIP)
    return render_template('topo.html', topologyInfo=parser.fetch_topology())


@app.route("/node-stats")
def node_stats():
    o = Odl_Stat_Collector(controllerIP)
    return render_template('nodes.html', nodes=o.run())


@app.route("/device-info")
def device_info():
    o = odl_switch_info(controllerIP)
    return render_template('deviceInfo.html', nodes=o.run())

 
@app.route("/controller")
def getControllerIP():
    # print(odlControllerList)
    return render_template('settings.html', odlList=controllerIP)


if __name__ == "__main__":
    app.run(debug=True)
