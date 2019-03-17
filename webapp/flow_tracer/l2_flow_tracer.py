#!/usr/bin/env python3
import mysql.connector
from mysql.connector import errorcode


from abstract_flow_tracer import FlowTracer


class L2FlowTracer(FlowTracer):

    def __init__(self):
        super().__init__()

    def trace_flows(self, source, dest):
        source_host = self.find_host(source)
        dest_host = self.find_host(dest)
        source_switch = self.find_switch_by_host(source_host)
        dest_switch = self.find_switch_by_host(dest_host)
        print(f"{source_switch} <-> {dest_switch}")

    def find_host(self, ip):
        """[summary]

        Arguments:
            ip {[type]} -- [description]
        """
        query = ("SELECT HOST FROM host_info "
                 f"WHERE IP_ADDRESS = '{ip}'")
        host_query_result = self.sql_select_query(query)
        host = host_query_result[0][0]
        return host
        # get host-ip pair from host
        # get link tuple?

    def find_switch_by_host(self, host):
        switch = ""
        query = f"SELECT * FROM links WHERE SRC = '{host}' OR DST = '{host}'"
        result = self.sql_select_query(query)
        link_tuple = result[0]
        for node_name in link_tuple[1:3]:
            if node_name != host:
                switch = node_name
        return switch

    def sql_select_query(self, query):
        cursor = self.cnx.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return result


l = L2FlowTracer()
l.trace_flows('10.0.0.1', '10.0.0.5')
