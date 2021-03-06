#!/usr/bin/env python3
"""Monitoring Agent that tracks port counters."""
import mysql.connector
from mysql.connector import errorcode
import json

from abstract_agent import AbstractAgent


class PortCounterAgent(AbstractAgent):
    def __init__(self, controller_ip, node):
        """Initializer for the PortCounterObject"""
        super().__init__(controller_ip)
        self.node = node
        self.create_pc_table(self.node)
        self.int_counter_str = ("opendaylight-port-statistics:"
                                "flow-capable-node-connector-statistics")
        self.int_state = "flow-node-inventory:state"

    def create_pc_table(self, node):
        """Creates a DB table listing port counters
        for a switch."""
        table = (
            f"CREATE TABLE {node}_counters("
            "ID INT NOT NULL AUTO_INCREMENT,"
            "Interface VARCHAR(32) NOT NULL,"
            "Timestamp DATETIME NOT NULL,"
            "Rx_pckts BLOB NOT NULL,"
            "Tx_pckts BLOB NOT NULL,"
            "Rx_bytes BLOB NOT NULL,"
            "Tx_bytes BLOB NOT NULL,"
            "Rx_drops INT NOT NULL,"
            "Tx_drops INT NOT NULL,"
            "Rx_errs INT NOT NULL,"
            "Tx_errs INT NOT NULL,"
            "Port_down BOOL NOT NULL,"
            "STP_state VARCHAR(20) NOT NULL,"
            "PRIMARY KEY (ID) );")
        self.sql_tool.create_sql_table(table)

    # TODO: Add this to an SQL Utility module
    def get_interfaces(self, node):
        query = f"SELECT * FROM {node}_interfaces"
        int_tuples = self.sql_tool.send_select(query)
        interface_list = [interface[0] for interface in int_tuples]
        return interface_list

    def get_data(self):
        """Get_data executes the logic necessary to make the API
        calls for the port counters and organizes the data to be parsed
        by parse_data.

        Returns:
            Dict -- Returns a dictionary of the API calls for the port
            counters. Adds a key that corresponds to the interface for
            the given API calls.
        """
        response_dict = {}
        interface_list = self.get_interfaces(self.node)
        for interface in interface_list:
            response_dict[interface] = self.get_counters(interface)
        return response_dict

    def get_counters(self, interface):
        """Helper method that sends API calls for counters of every port.

        Arguments:
            interface [str] -- Target interface name for the API call.

        Returns:
            dict -- Returns the response of the API call as a dict.
        """
        restconf_node = f"opendaylight-inventory:nodes/node/{self.node}/"
        restconf_int = f"node-connector/{interface}/"
        url = self.base_url + restconf_node + restconf_int
        response = self.send_get_request(url)
        return response

    def parse_response(self, response):
        """Parses API response to create a lean dictionary of port stats.

        Arguments:
            response {dict} -- A dictionary of port stats from the API call,
            formatted by the get_counters method.

        Returns:
            Dictionary -- Returns a nested dictionary of interface: port stats,
            the fields should correspond to the SD_Lens SQL tables.
        """
        port_stats = {}
        stp_key = 'stp-status-aware-node-connector:status'
        for interface in response:
            try:
                int_id = interface
                int_params = response[interface]['node-connector'][0]
                int_stats = response[interface]['node-connector'][0][self.int_counter_str]
                int_status = response[interface]['node-connector'][0][self.int_state]
                port_stats[int_id] = {}
                port_stats[int_id]["rx-pckts"] = int_stats["packets"]["received"]
                port_stats[int_id]["tx-pckts"] = int_stats["packets"]["transmitted"]
                port_stats[int_id]["rx-bytes"] = int_stats["bytes"]["received"]
                port_stats[int_id]["tx-bytes"] = int_stats["bytes"]["transmitted"]
                port_stats[int_id]["rx-drops"] = int_stats["receive-drops"]
                port_stats[int_id]["tx-drops"] = int_stats["transmit-drops"]
                port_stats[int_id]["rx-errs"] = int_stats["receive-errors"]
                port_stats[int_id]["tx-errs"] = int_stats["transmit-errors"]
                port_stats[int_id]['port-down'] = int_status["link-down"]
                port_stats[int_id]["timestamp"] = self.add_timestamp()
                keys = response[interface]['node-connector'][0].keys()

                if (stp_key in keys):
                    if (int_params[stp_key] == 'discarding'):
                        port_stats[int_id]['stp_state'] = 'Discarding'
                    elif (int_params[stp_key] == 'forwarding'):
                        port_stats[int_id]['stp_state'] = 'Forwarding'
                else:
                    port_stats[int_id]['stp_state'] = 'N/A'
            except:
                continue
        return port_stats

    def store_data(self, data):
        """Takes the parsed API responses for the port counters and
        stores them in the sdlens DBs.
        Arguments:
            data {dict} -- Takes the dictionary returned my parse_data
            as the argument.
        """
        for interface in data:

            int_data = data[interface]
            sql_insert = (f"INSERT INTO {self.node}_counters "
                          "(Interface, Timestamp, Rx_pckts, Tx_pckts, "
                          "Rx_bytes, Tx_bytes, Rx_drops, Tx_drops, "
                          "Rx_errs, Tx_errs, Port_down, STP_state) VALUES "
                          "('{}', '{}', {}, {}, {}, {}, {}, {}, {}, {}, {}, {})")
            query = sql_insert.format(interface, int_data['timestamp'],
                                      int_data['rx-pckts'], int_data['tx-pckts'],
                                      int_data['rx-bytes'], int_data['tx-bytes'],
                                      int_data['rx-drops'], int_data['tx-drops'],
                                      int_data['rx-errs'], int_data['tx-errs'],
                                      int_data['port-down'], "'"+int_data['stp_state']+"'")
            self.sql_tool.send_insert(query)

