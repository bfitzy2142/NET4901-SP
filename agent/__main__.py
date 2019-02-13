#!/usr/bin/env python3
"""Main module for the agent component of our app."""
import time

import mysql.connector
from mysql.connector import errorcode

from authenticator import Authenticator
from abstract_agent import AbstractAgent
from topology_agent import TopologyAgent
from link_agent import LinkAgent
from port_counter_agent import PortCounterAgent
from device_agent import DeviceAgent


auth = Authenticator()
yaml_db_creds = auth.working_creds['database']
sql_creds = {"user": yaml_db_creds['MYSQL_USER'],
             "password": yaml_db_creds['MYSQL_PASSWORD'],
             "host": yaml_db_creds['MYSQL_HOST']}
db = auth.working_creds['database']['MYSQL_DB']
controller_ip = auth.working_creds['controller']['controller-ip']


# TODO: Move db functions into its own module
def create_db():
    """creates DB for our monitoring app"""
    try:
        cnx = mysql.connector.connect(**sql_creds, database=db)
        print("db already created")  # debug
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            user = sql_creds['user']
            host = sql_creds['host']
            cnx = mysql.connector.connect(**sql_creds)
            cnx.cmd_query(f'CREATE DATABASE {db}')
            cnx.database = db
            cursor = cnx.cursor()
            cursor.execute(f"GRANT ALL ON {db}.* to '{user}'@'{host}';")
            print("DB created!")  # debug


def get_switches():
    switch_list = []
    cnx = mysql.connector.connect(**sql_creds, database=db)
    cursor = cnx.cursor()
    cursor.execute("SELECT Node FROM nodes WHERE Type='switch';")
    switch_tuples = cursor.fetchall()
    for switch in switch_tuples:
        switch_list.append(switch[0])
    return switch_list

if __name__ == '__main__':
    create_db()
    topo_agent = TopologyAgent(controller_ip)
    topo_agent.run_agent()
    switch_list = get_switches()
    link_agent = LinkAgent(controller_ip)
    link_agent.run_agent()
    counter_agents = {}
    device_agents = {}
    for switch in switch_list:
        counter_agents[switch] = PortCounterAgent(controller_ip, switch)
        device_agents[switch] = DeviceAgent(controller_ip, switch)
        device_agents[switch].run_agent()
    while True:
        for switch in switch_list:
            counter_agents[switch].run_agent()
        time.sleep(10)
