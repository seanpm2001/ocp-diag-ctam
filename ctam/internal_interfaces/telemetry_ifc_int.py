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







