"""
Copyright (c) Microsoft Corporation

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.

"""

from typing import Optional, List
import ast, inspect
from datetime import datetime
from prettytable import PrettyTable
from ocptv.output import LogSeverity
from utils.json_utils import *
from itertools import product
import functools 


class TelemetryIfcInt(type):

    def __new__(cls, name, bases, data_dict):
        """

        ensure only 1 instance can be created

        :return: instance
        :rtype: TelemetryIfc
        """
        def ctam_get_all_metric_reports(self):
            mr_uri_list = self.ctam_get_all_metric_reports_uri()
            mr_json = {}
            for URI in mr_uri_list:
                response = self.dut().run_redfish_command(uri="{}{}".format(self.dut().uri_builder.format_uri(redfish_str="{GPUMC}", component_type="GPU"), URI))
                JSONData = response.dict
                for metric_property in JSONData["MetricValues"]:
                    mr_json[metric_property["MetricProperty"]] = metric_property["MetricValue"]
            if self.dut().is_console_log:
                t = PrettyTable(["MetricProperty", "MetricValue"])
                for k, v in mr_json.items():
                    t.add_row([k, v])
                t.align["MetricProperty"] = "r"
                print(t)
            self.write_test_info("{}".format(mr_json))
            return mr_json
        
        def ctam_baseboard_gpu_processor_metrics(self): #need improvement
            """
            :Description:				Read back the data of /redfish/v1/Systems/{BaseboardId}/Processors/{GpuId}/ProcessorMetrics

            :returns:				    Array of all URIs under ProcessorMetrics
            """
            import ast
            MyName = __name__ + "." + self.ctam_baseboard_gpu_processor_metrics.__qualname__
            system_gpu_id = ast.literal_eval(self.dut().uri_builder.format_uri(redfish_str="{SystemGPUIDs}", component_type="GPU"))
            baseboard_id = ast.literal_eval(self.dut().uri_builder.format_uri(redfish_str="{BaseboardIDs}", component_type="GPU"))
            result = True
            for id in baseboard_id:
                for gpu_id in system_gpu_id:
                    uri = "/Systems/" + id + "/Processors/" + gpu_id + "/ProcessorMetrics"
                    gpu_uri = self.dut().uri_builder.format_uri(redfish_str="{BaseURI}" + uri, component_type="GPU")
                    result &= self.ctam_redfish_GET_status_ok(uri=gpu_uri)
            return result
        
        def ctam_get_chassis_environment_metrics(self):
            """
            :Description:				Read back the data of /redfish/v1/Chassis/{ChassisId}/EnvironmentMetrics

            :returns:				    Array of all URIs under EnvironmentMetrics
            """
            import ast, json
            from ocptv.output import LogSeverity

            MyName = __name__ + "." + self.ctam_get_chassis_environment_metrics.__qualname__
            chassis_instances = ast.literal_eval(self.dut().uri_builder.format_uri(redfish_str="{ChassisIDs}", component_type="GPU"))
            result = True
            # reference_uri = r"/redfish/v1/Chassis/{ChassisId}/EnvironmentMetrics"
            for uri in chassis_instances:
                uri = "/Chassis/" + uri + "/EnvironmentMetrics"
                base_uri = self.dut().uri_builder.format_uri(redfish_str="{BaseURI}", component_type="GPU")
                chassis_uri = base_uri + uri
                response = self.dut().run_redfish_command(uri=chassis_uri)
                JSONData = response.dict
                # response_check = self.dut().check_uri_response(reference_uri, JSONData)
                # msg = "Checking for redfish uri for Accelerator Compliance, Result : {}".format( response_check)            
                # self.write_test_info(msg)
                status = response.status
                if (status == 200 or status == 201):
                    self.test_run().add_log(LogSeverity.INFO, "Test JSON")
                    self.test_run().add_log(LogSeverity.INFO, "Chassis with ID Pass: {} : {}".format(uri, json.dumps(JSONData, indent=4)))
                else:
                    self.test_run().add_log(LogSeverity.FATAL, "Chassis with ID Fails: {} : {}".format(uri, JSONData))
                    result = False
            return result
        
        def ctam_systems_baseboard_ids(self, path=""):
            """
            :Description:				Read back the data of /redfish/v1/Systems/{BaseboardId}

            """
            import ast
            MyName = __name__ + "." + self.ctam_systems_baseboard_ids.__qualname__
            systems_instances = ast.literal_eval(self.dut().uri_builder.format_uri(redfish_str="{BaseboardIDs}", component_type="GPU"))
            result = True
            for uri in systems_instances:
                uri = "/Systems/" + uri + "/" + path
                baseboard_uri = self.dut().uri_builder.format_uri(redfish_str="{BaseURI}" + uri, component_type="GPU")
                result &= self.ctam_redfish_GET_status_ok(uri=baseboard_uri)
            return result
    
    
        def ctam_gpu_chassis_thermal_metrics(self, path=None):
            """
            :Description:				Read back the data of /redfish/v1/Chassis/{ChassisId}/ThermalSubsystem/ThermalMetrics

            :returns:				    Array of all URIs under ThermalMetrics
            """
            import ast
            MyName = __name__ + "." + self.ctam_gpu_chassis_thermal_metrics.__qualname__
            if path is None:
                chassis_instances = ast.literal_eval(self.dut().uri_builder.format_uri(redfish_str="{ChassisIDs}", component_type="GPU"))
            elif path == "Retimers":
                chassis_instances = ast.literal_eval(self.dut().uri_builder.format_uri(redfish_str="{ChassisRetimersIDs}", component_type="GPU"))            

            result = True
            for uri in chassis_instances:
                uri = "/Chassis/" + uri + "/ThermalSubsystem/ThermalMetrics"
                gpu_uri = self.dut().uri_builder.format_uri(redfish_str="{BaseURI}" + uri, component_type="GPU")
                result &= self.ctam_redfish_GET_status_ok(uri=gpu_uri)
            return result
        
        def ctam_gpu_thermal_metrics(self):
            """
            :Description:				Read back the data of /redfish/v1/Chassis/{GpuId}/ThermalSubsystem/ThermalMetrics

            :returns:				    Array of all URIs under GpuId ThermalMetrics
            """
            import ast
            MyName = __name__ + "." + self.ctam_gpu_thermal_metrics.__qualname__
            gpu_instances = ast.literal_eval(self.dut().uri_builder.format_uri(redfish_str="{ChassisGPUs}", component_type="GPU"))
            result = True
            for gpu_id in gpu_instances:
                uri = "/Chassis/" + gpu_id + "/ThermalSubsystem/ThermalMetrics"
                gpu_uri = self.dut().uri_builder.format_uri(redfish_str="{BaseURI}" + uri, component_type="GPU")
                result &= self.ctam_redfish_GET_status_ok(uri=gpu_uri)
            return result
        

        
        def ctam_chassis_ids_metrics(self, path=None):
            """
            :Description:				Read back the data of /redfish/v1/Chassis/{ChassisId}

            """
            import ast
            MyName = __name__ + "." + self.ctam_chassis_ids_metrics.__qualname__
            chassis_instances = ast.literal_eval(self.dut().uri_builder.format_uri(redfish_str="{ChassisIDs}", component_type="GPU"))
            result = True
            for uri in chassis_instances:
                if path is None:
                    uri = "/Chassis/" + uri
                else:
                    uri = "/Chassis/" + uri + "/" + path
                
                chassis_uri = self.dut().uri_builder.format_uri(redfish_str="{BaseURI}" + uri, component_type="GPU")
                result &= self.ctam_redfish_GET_status_ok(uri=chassis_uri)
            return result

        
        def ctam_chassis_power_subsystem_metrics(self):
            """
            :Description:				Read back the data of /redfish/v1/Chassis/{ChassisId}/PowerSubsystem

            """
            import ast
            MyName = __name__ + "." + self.ctam_chassis_power_subsystem_metrics.__qualname__
            chassis_instances = ast.literal_eval(self.dut().uri_builder.format_uri(redfish_str="{ChassisIDs}", component_type="GPU"))
            result = True
            for uri in chassis_instances:
                uri = "/Chassis/" + uri + "/PowerSubsystem"
                chassis_uri = self.dut().uri_builder.format_uri(redfish_str="{BaseURI}" + uri, component_type="GPU")
                result &= self.ctam_redfish_GET_status_ok(uri=chassis_uri)
            return result
        
        def ctam_chassis_sensors_metrics(self):
            """
            :Description:				Read back the data of /redfish/v1/Chassis/{ChassisId}/Sensors

            """
            import ast
            MyName = __name__ + "." + self.ctam_chassis_sensors_metrics.__qualname__
            chassis_instances = ast.literal_eval(self.dut().uri_builder.format_uri(redfish_str="{ChassisIDs}", component_type="GPU"))
            result = True
            for uri in chassis_instances:
                uri = "/Chassis/" + uri + "/Sensors"
                sensor_uri = self.dut().uri_builder.format_uri(redfish_str="{BaseURI}" + uri, component_type="GPU")
                result &= self.ctam_redfish_GET_status_ok(uri=sensor_uri)
            return result
        
        # def ctam_chassis_sensor_ids_metrics(self):
        #     """
        #     :Description:				Read back the data of /redfish/v1/Chassis/{ChassisId}/Sensors/{SensorId}

        #     """
        #     MyName = __name__ + "." + self.ctam_chassis_sensor_ids_metrics.__qualname__
        #     chassis_instances = ast.literal_eval(self.dut().uri_builder.format_uri(redfish_str="{ChassisIDs}", component_type="GPU"))
        #     sensor_ids = ast.literal_eval(self.dut().uri_builder.format_uri(redfish_str="{SensorIDs}", component_type="GPU"))
        #     result = True
        #     for uri in chassis_instances:
        #         for ids in sensor_ids:
        #             URI = "/Chassis/" + uri + "/Sensors/" + ids
        #             sensor_uri = self.dut().uri_builder.format_uri(redfish_str="{BaseURI}" + URI, component_type="GPU")
        #             result &= self.ctam_redfish_GET_status_ok(uri=sensor_uri)
        #     return result

        def ctam_chassis_thermal_subsystem_metrics(self):
            """
            :Description:				Read back the data of /redfish/v1/Chassis/{ChassisId}/ThermalSubsystem

            """
            import ast
            MyName = __name__ + "." + self.ctam_chassis_thermal_subsystem_metrics.__qualname__
            chassis_instances = ast.literal_eval(self.dut().uri_builder.format_uri(redfish_str="{ChassisIDs}", component_type="GPU"))
            result = True
            for uri in chassis_instances:
                uri = "/Chassis/" + uri + "/ThermalSubsystem"
                chassis_uri = self.dut().uri_builder.format_uri(redfish_str="{BaseURI}" + uri, component_type="GPU")
                result &= self.ctam_redfish_GET_status_ok(uri=chassis_uri)
            return result
        
        
        
        def ctam_systems_gpu_ids(self, path=""):
            """
            :Description:				Read back the data of /redfish/v1/Systems/{BaseboardId}/Processors/{GpuId}

            """
            import ast
            MyName = __name__ + "." + self.ctam_systems_gpu_ids.__qualname__
            systems_instances = ast.literal_eval(self.dut().uri_builder.format_uri(redfish_str="{BaseboardIDs}", component_type="GPU"))
            gpu_id = ast.literal_eval(self.dut().uri_builder.format_uri(redfish_str="{SystemGPUIDs}", component_type="GPU"))
            result = True
            for uri in systems_instances:
                for id in gpu_id:
                    URI = "/Systems/" + uri + "/Processors/" + id + "/" + path
                    gpu_uri = self.dut().uri_builder.format_uri(redfish_str="{BaseURI}" + URI, component_type="GPU")
                    result &= self.ctam_redfish_GET_status_ok(uri=gpu_uri)
            return result
        
        def ctam_system_gpu_port_ids(self, path=""): # Need improvement
            """
            :Description:				Read back the data of /redfish/v1/Systems/{BaseboardId}/Processors/{GpuId}/Ports/{PortId}

            """
            import ast
            MyName = __name__ + "." + self.ctam_system_gpu_port_ids.__qualname__
            systems_instances = ast.literal_eval(self.dut().uri_builder.format_uri(redfish_str="{BaseboardIDs}", component_type="GPU"))
            gpu_id = ast.literal_eval(self.dut().uri_builder.format_uri(redfish_str="{SystemGPUIDs}", component_type="GPU"))
            port_id = ast.literal_eval(self.dut().uri_builder.format_uri(redfish_str="{SystemGPUPortIDs}", component_type="GPU"))
            result = True
            for uri in systems_instances:
                for id in gpu_id:
                    for port in port_id:
                        URI = "/Systems/" + uri + "/Processors/" + id + "/Ports/" + port + path
                        gpu_uri = self.dut().uri_builder.format_uri(redfish_str="{BaseURI}" + URI, component_type="GPU")
                        result &= self.ctam_redfish_GET_status_ok(uri=gpu_uri)
            return result
        
        def ctam_system_gpu_dram_ids(self, path=""):
            """
            :Description:				Read back the data of /redfish/v1/Systems/{BaseboardId}/Memory/{GpuDramId}

            """
            import ast
            MyName = __name__ + "." + self.ctam_system_gpu_dram_ids.__qualname__
            systems_instances = ast.literal_eval(self.dut().uri_builder.format_uri(redfish_str="{BaseboardIDs}", component_type="GPU"))
            gpu_dram_id = ast.literal_eval(self.dut().uri_builder.format_uri(redfish_str="{GPUDramIDs}", component_type="GPU"))
            
            result = True
            for uri in systems_instances:
                for id in gpu_dram_id:
                    URI = "/Systems/" + uri + "/Memory/" + id + "/" + path
                    gpu_uri = self.dut().uri_builder.format_uri(redfish_str="{BaseURI}" + URI, component_type="GPU")
                    result &= self.ctam_redfish_GET_status_ok(uri=gpu_uri)
            return result
        
        def ctam_managers_read(self):
            """
            :Description:				Read back the data of redfish/v1/Managers/{mgr_instance}

            """
            import ast
            MyName = __name__ + "." + self.ctam_managers_read.__qualname__
            mgr_instance = ast.literal_eval(self.dut().uri_builder.format_uri(redfish_str="{ManagerIDs}", component_type="GPU"))
            result = True
            for uri in mgr_instance:
                URI = "/Managers/" + uri
                gpu_uri = self.dut().uri_builder.format_uri(redfish_str="{BaseURI}" + URI, component_type="GPU")
                result &= self.ctam_redfish_GET_status_ok(uri=gpu_uri)
            return result
        
        def ctam_managers_ethernet_interfaces_usb0(self):
            """
            :Description:				Read back the data of redfish/v1/Managers/{mgr_instance}/EthernetInterfaces/usb0

            """
            import ast
            MyName = __name__ + "." + self.ctam_managers_ethernet_interfaces_usb0.__qualname__
            mgr_instance = ast.literal_eval(self.dut().uri_builder.format_uri(redfish_str="{ManagerIDs}", component_type="GPU"))
            result = True
            for uri in mgr_instance:
                URI = "/Managers/" + uri + "/EthernetInterfaces/usb0"
                gpu_uri = self.dut().uri_builder.format_uri(redfish_str="{BaseURI}" + URI, component_type="GPU")
                # payload = {"IPv4StaticAddresses": [{"Address": "192.168.31.1", "AddressOrigin": "Static", "Gateway":"192.168.31.2", "SubnetMask": "255.255.0.0"}]}
                # head = {"Content-Type: application/json"}
                # response = self.dut().run_redfish_command(gpu_uri, body=payload, headers=head)
                result &= self.ctam_redfish_GET_status_ok(uri=gpu_uri)
            return result
        
        def ctam_managers_ethernet_interfaces_gateway(self): # need improvement
            """
            :Description:				Read back the data of redfish/v1/Managers/{mgr_instance}/EthernetInterfaces/usb0/Gateway property

            """
            import ast
            from ocptv.output import LogSeverity
            MyName = __name__ + "." + self.ctam_managers_ethernet_interfaces_gateway.__qualname__
            mgr_instance = ast.literal_eval(self.dut().uri_builder.format_uri(redfish_str="{ManagerIDs}", component_type="GPU"))
            result = True
            for uri in mgr_instance:
                URI = "/Managers/" + uri + "/EthernetInterfaces/usb0"
                gpu_uri = self.dut().uri_builder.format_uri(redfish_str="{BaseURI}" + URI, component_type="GPU")
                response = self.dut().run_redfish_command(gpu_uri)
                JSONData = response.dict
                status = response.status
                if (status == 200 or status == 201) and ("IPv4StaticAddresses" in JSONData):
                    self.test_run().add_log(LogSeverity.INFO, "Chassis with ID Pass: {} : {}".format(URI, JSONData))
                else:
                    self.test_run().add_log(LogSeverity.FATAL, "Chassis with ID Fails: {} : {}".format(URI, JSONData))
                    result = False
            return result
        
        def ctam_managers_ethernet_interfaces_gateway_write(self):
            """
            :Description:				Read back the data of redfish/v1/Managers/{mgr_instance}/EthernetInterfaces/usb0/Gateway property

            """
            import ast
            from ocptv.output import LogSeverity
            MyName = __name__ + "." + self.ctam_managers_ethernet_interfaces_gateway_write.__qualname__
            mgr_instance = ast.literal_eval(self.dut().uri_builder.format_uri(redfish_str="{ManagerIDs}", component_type="GPU"))
            result = True
            for uri in mgr_instance:
                URI = "/Managers/" + uri + "/EthernetInterfaces/usb0"
                gpu_uri = self.dut().uri_builder.format_uri(redfish_str="{BaseURI}" + URI, component_type="GPU")
                response = self.dut().run_redfish_command(uri=gpu_uri)
                JSONData = response.dict
                JSONData_IPv4StaticAddresses = JSONData["IPv4StaticAddresses"]
                status = response.status
                if status == 200 or status == 201:
                    self.test_run().add_log(LogSeverity.INFO, "Getting IPv4StaticAddresses from Manager with ID Pass: {} : {}".format(uri, JSONData_IPv4StaticAddresses))
                else:
                    self.test_run().add_log(LogSeverity.FATAL, "Getting IPv4StaticAddresses from Manager ID Fails: {} : {}".format(uri, JSONData_IPv4StaticAddresses))
                    result = False
                    break

                for item in JSONData_IPv4StaticAddresses:
                    item.pop("AddressOrigin", None) # Remove the key
                payload = {"IPv4StaticAddresses": JSONData_IPv4StaticAddresses}
                header = {"Content-Type: application/json"}
                response = self.dut().run_redfish_command(gpu_uri, mode="PATCH", body=payload, headers=header)
                status = response.status
                if status == 204:
                    self.test_run().add_log(LogSeverity.INFO, "Chassis with ID Pass: {} : {}".format(URI, status))
                else:
                    self.test_run().add_log(LogSeverity.FATAL, "Chassis with ID Fails: {} : {}".format(URI, response))
                    result = False
            return result


        def ctam_managers_set_sel_time(self): # Probably need improvement
            """
            :Description:				Set sel time at redfish/v1/Managers/{mgr_instance} property

            """
            import ast
            from ocptv.output import LogSeverity
            MyName = __name__ + "." + self.ctam_managers_set_sel_time.__qualname__
            mgr_instance = ast.literal_eval(self.dut().uri_builder.format_uri(redfish_str="{ManagerIDs}", component_type="GPU"))
            result = True
            for uri in mgr_instance:

                URI = "/Managers/" + uri
                gpu_uri = self.dut().uri_builder.format_uri(redfish_str="{BaseURI}" + URI, component_type="GPU")
                response = self.dut().run_redfish_command(uri=gpu_uri)
                JSONData = response.dict
                JSONData_DateTime = JSONData["DateTime"]
                status = response.status
                if status == 200 or status == 201:
                    self.test_run().add_log(LogSeverity.INFO, "Getting Date time from Manager with ID Pass: {} : {}".format(uri, JSONData_DateTime))
                else:
                    self.test_run().add_log(LogSeverity.FATAL, "Getting Date time from Manager ID Fails: {} : {}".format(uri, JSONData_DateTime))
                    result = False
                    break

                payload = {"DateTime": JSONData_DateTime}
                header = {"Content-Type: application/json"}
                response = self.dut().run_redfish_command(gpu_uri, mode="PATCH", body=payload, headers=header)
                JSONData = response.dict
                status = response.status
                if status == 200 or status == 201:
                    if "DateTime" in JSONData:
                        self.test_run().add_log(LogSeverity.INFO, "Setting Sel Time ID Pass: {} : {}".format(URI, JSONData))
                    else:
                        self.test_run().add_log(LogSeverity.FATAL, "Setting Sel Time ID Fails: {} : {}".format(URI, JSONData))
                        result = False
            return result

        def ctam_get_chassis_fpga_metrics(self):
            """
            :Description:				Read back the data of /redfish/v1/Chassis/{ChassisFpgaIDs}

            :returns:				    Dictionary record under of all URIs under /redfish/v1/Chassis/{ChassisFpgaIDs}
            """
            import ast, json
            from ocptv.output import LogSeverity
            MyName = __name__ + "." + self.ctam_get_chassis_fpga_metrics.__qualname__
            systemchassis_instances = ast.literal_eval(self.dut().uri_builder.format_uri(redfish_str="{ChassisFpgaIDs}", component_type="GPU"))
            result = True
            # reference_uri = r"/redfish/v1/Chassis/{ChassisFpgaIDs}"
            for uri in systemchassis_instances:
                uri = "/Chassis/" + uri
                base_uri = self.dut().uri_builder.format_uri(redfish_str="{BaseURI}", component_type="GPU")
                chassis_uri = base_uri + uri
                response = self.dut().run_redfish_command(uri=chassis_uri)
                JSONData = response.dict
                # response_check = self.dut().check_uri_response(reference_uri, JSONData)
                # msg = "Checking for redfish uri for Accelerator Compliance, Result : {}".format( response_check)            
                # self.write_test_info(msg)
                status = response.status
                if (status == 200 or status == 201):
                    self.test_run().add_log(LogSeverity.INFO, "Test JSON")
                    self.test_run().add_log(LogSeverity.INFO, "Chassis with ID Pass: {} : {}".format(uri, json.dumps(JSONData, indent=4)))
                else:
                    self.test_run().add_log(LogSeverity.FATAL, "Chassis with ID Fails: {} : {}/nstatus is {}".format(uri, JSONData, status))
                    result = False
            return result
        
        def ctam_get_chassis_fpga_sensor_metrics(self):
            """
            :Description:				Read back the data of /redfish/v1/Chassis/{ChassisFpgaIDs}/Sensors

            :returns:				    Dictionary record under of all URIs under /redfish/v1/Chassis/{ChassisFpgaIDs}/Sensors
            """
            import ast, json
            from ocptv.output import LogSeverity
            from itertools import product

            MyName = __name__ + "." + self.ctam_get_chassis_fpga_sensor_metrics.__qualname__
            chassis_sensor_list = ast.literal_eval(self.dut().uri_builder.format_uri(redfish_str="{ChassisSensorID}", component_type="GPU"))
            chassis_fpga_list = ast.literal_eval(self.dut().uri_builder.format_uri(redfish_str="{ChassisFpgaIDs}", component_type="GPU"))
            result = True
            # reference_uri = r"/redfish/v1/Chassis/{ChassisFpgaIDs}/Sensors"
            for sensorInstance,fpgaInstance in product(chassis_sensor_list, chassis_fpga_list):
                uri = "/Chassis/" + fpgaInstance + "/Sensors/" + sensorInstance
                base_uri = self.dut().uri_builder.format_uri(redfish_str="{BaseURI}", component_type="GPU")
                chassis_uri = base_uri + uri
                response = self.dut().run_redfish_command(uri=chassis_uri)
                JSONData = response.dict
                # response_check = self.dut().check_uri_response(reference_uri, JSONData)
                # msg = "Checking for redfish uri for Accelerator Compliance, Result : {}".format( response_check)            
                # self.write_test_info(msg)
                status = response.status
                if (status == 200 or status == 201):
                    self.test_run().add_log(LogSeverity.INFO, "Test JSON")
                    self.test_run().add_log(LogSeverity.INFO, "Chassis with ID Pass: {} : {}".format(uri, json.dumps(JSONData, indent=4)))
                else:
                    self.test_run().add_log(LogSeverity.FATAL, "Chassis with ID Fails: {} : {}".format(uri, JSONData))
                    result = False
            return result

        def ctam_get_chassis_sensor_metrics(self, path="ChassisRetimersIDs"):
            """
            :Description:				Read back the data of /redfish/v1/Chassis/{path}/Sensors

            :returns:				    Dictionary record under of all URIs under /redfish/v1/Chassis/{path}/Sensors
            """
            import ast, json
            from ocptv.output import LogSeverity
            MyName = __name__ + "." + self.ctam_get_chassis_sensor_metrics.__qualname__
            sensorNameList = []

            # FIXME: Needs improvement. Can we use the path itself instead of if-else?
            if path == "ChassisRetimersIDs":
                outer_list = ast.literal_eval(self.dut().uri_builder.format_uri(redfish_str="{ChassisRetimersIDs}", component_type="GPU"))
            elif path == "ChassisIDs":
                outer_list = ast.literal_eval(self.dut().uri_builder.format_uri(redfish_str="{ChassisIDs}", component_type="GPU"))

            # reference_uri = r"/redfish/v1/Chassis/{path}/Sensors"
            result = True

            for outler_list_instance in outer_list:
                uri = "/Chassis/" + outler_list_instance + "/Sensors"
                self.test_run().add_log(LogSeverity.INFO, "Outler Loop is {}".format(outler_list_instance))
                base_uri = self.dut().uri_builder.format_uri(redfish_str="{BaseURI}", component_type="GPU")
                chassis_uri = base_uri + uri
                response = self.dut().run_redfish_command(uri=chassis_uri)
                JSONData = response.dict
                sensorMembers = JSONData["Members"]

                for sensorIdRecord in sensorMembers:
                    sensorName = sensorIdRecord["@odata.id"].split('/')[-1].strip()
                    #sensorNameList.append(sensorName)
                    #for sensorInstance in sensorNameList:
                    uri = "/Chassis/" + outler_list_instance + "/Sensors/" + sensorName
                    base_uri = self.dut().uri_builder.format_uri(redfish_str="{BaseURI}", component_type="GPU")
                    chassis_uri = base_uri + uri
                    response = self.dut().run_redfish_command(uri=chassis_uri)
                    JSONData = response.dict
                    # response_check = self.dut().check_uri_response(reference_uri, JSONData)
                    # msg = "Checking for redfish uri for Accelerator Compliance, Result : {}".format( response_check)            
                    # self.write_test_info(msg)
                    status = response.status
                    if (status == 200 or status == 201):
                        self.test_run().add_log(LogSeverity.INFO, "Test JSON")
                        self.test_run().add_log(LogSeverity.INFO, "Chassis with ID Pass: {} : {}".format(uri, json.dumps(JSONData, indent=4)))
                    else:
                        self.test_run().add_log(LogSeverity.FATAL, "Chassis with ID Fails: {} : {}".format(uri, JSONData))
                        result = False
                        return result
            return result

        def ctam_get_chassis_retimers_ThermalSubsystem_metrics(self):
            """
            :Description:				Read back the data of /redfish/v1/Chassis/{ChassisRetimersIDs}/ThermalSubsystem

            :returns:				    Dictionary record under of all URIs under /redfish/v1/Chassis/{ChassisRetimersIDs}/ThermalSubsystem
            """
            import ast, json
            from ocptv.output import LogSeverity
            MyName = __name__ + "." + self.ctam_get_chassis_retimers_ThermalSubsystem_metrics.__qualname__
            chassis_retimer_list = ast.literal_eval(self.dut().uri_builder.format_uri(redfish_str="{ChassisRetimersIDs}", component_type="GPU"))
            result = True
            # reference_uri = r"/redfish/v1/Chassis/{ChassisRetimersIDs}/ThermalSubsystem"
            for retimerInstance in chassis_retimer_list:
                uri = "/Chassis/" + retimerInstance + "/ThermalSubsystem/"
                base_uri = self.dut().uri_builder.format_uri(redfish_str="{BaseURI}", component_type="GPU")
                chassis_uri = base_uri + uri
                response = self.dut().run_redfish_command(uri=chassis_uri)
                JSONData = response.dict
                # response_check = self.dut().check_uri_response(reference_uri, JSONData)
                # msg = "Checking for redfish uri for Accelerator Compliance, Result : {}".format( response_check)            
                # self.write_test_info(msg)
                status = response.status
                if (status == 200 or status == 201):
                    self.test_run().add_log(LogSeverity.INFO, "Test JSON")
                    self.test_run().add_log(LogSeverity.INFO, "Chassis with ID Pass: {} : {}".format(uri, json.dumps(JSONData, indent=4)))
                else:
                    self.test_run().add_log(LogSeverity.FATAL, "Chassis with ID Fails: {} : {}".format(uri, JSONData))
                    result = False
            return result

        def ctam_get_chassis_fpga_Thermal_metrics(self):
                """
                :Description:				Read back the data of /redfish/v1/Chassis/{ChassisFpgaId}/ThermalSubsystem/ThermalMetrics

                :returns:				    Dictionary record under of all URIs under /redfish/v1/Chassis/{ChassisFpgaId}/ThermalSubsystem/ThermalMetrics
                """
                from ocptv.output import LogSeverity
                import ast, json
                MyName = __name__ + "." + self.ctam_get_chassis_fpga_Thermal_metrics.__qualname__
                chassis_list = ast.literal_eval(self.dut().uri_builder.format_uri(redfish_str="{ChassisFpgaIDs}", component_type="GPU"))
                result = True
                # reference_uri = r"/redfish/v1/Chassis/{ChassisFpgaId}/ThermalSubsystem/ThermalMetrics"
                for chassisItem in chassis_list:
                    uri = "/Chassis/" + chassisItem + "/ThermalSubsystem/ThermalMetrics"
                    base_uri = self.dut().uri_builder.format_uri(redfish_str="{BaseURI}", component_type="GPU")
                    chassis_uri = base_uri + uri
                    response = self.dut().run_redfish_command(uri=chassis_uri)
                    JSONData = response.dict
                    # response_check = self.dut().check_uri_response(reference_uri, JSONData)
                    # msg = "Checking for redfish uri for Accelerator Compliance, Result : {}".format( response_check)            
                    # self.write_test_info(msg)
                    status = response.status
                    if (status == 200 or status == 201):
                        self.test_run().add_log(LogSeverity.INFO, "Test JSON")
                        self.test_run().add_log(LogSeverity.INFO, "Chassis with ID Pass: {} : {}".format(uri, json.dumps(JSONData, indent=4)))
                    else:
                        self.test_run().add_log(LogSeverity.FATAL, "Chassis with ID Fails: {} : {}".format(uri, JSONData))
                        result = False
                return result
        
        def get_function_object(f_def):
            # compile the code containing the function definition
            code_obj = compile(ast.Module(body=[f_def], type_ignores=[]), filename='<ast>', mode='exec')

            # evaluate the code object and obtain the function object
            namespace = {}
            exec(code_obj, namespace)
            return namespace[f_def.name]
        
        # iterate and fill data_dict
        src = inspect.getsource(TelemetryIfcInt)
        node = ast.parse(src)
        for func_def in ast.walk(node):
            if  type(func_def).__name__ == 'FunctionDef' and func_def.name != "__new__":
                func_object = get_function_object(func_def)
                data_dict[func_def.name] = func_object

        # Create the class using the super() method
        new_class = super().__new__(cls, name, bases, data_dict)
        return new_class







