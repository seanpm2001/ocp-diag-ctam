"""
Copyright (c) Microsoft Corporation
Copyright (c) NVIDIA CORPORATION

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.

"""
import time
import json
import os
from typing import Optional, List
from interfaces.functional_ifc import FunctionalIfc

from ocptv.output import LogSeverity


class HealthCheckIfc(FunctionalIfc):
    """
    API's related to general health check of the dut
    """

    _instance: Optional["HealthCheckIfc"] = None

    def __init__(self):
        super().__init__()
        self.logservice_uri_list = []
        self.entries_uri_list = []
        self.eventlog_uri_list = []
        self.dumplog_uri_list = []
        self.journal_uri_list = []

    def __new__(cls, *args, **kwargs):
        """
        ensure only 1 instance can be created

        :return: instance
        :rtype: HealthCheckIfc
        """
        if not isinstance(cls._instance, cls):
            cls._instance = super(HealthCheckIfc, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    @classmethod
    def get_instance(cls, *args, **kwargs):
        """
        if there is an existing instance, return it, otherwise create the singleton instance and return it

        :return: instance
        :rtype: HealthCheckIfc
        """
        if not isinstance(cls._instance, cls):
            cls._instance = cls(*args, **kwargs)
        return cls._instance
    
    def ctam_get_logservice_uris(self):
        if self.logservice_uri_list == []:
            self.ctam_redfish_uri_deep_hunt(
               "/redfish/v1/Systems", "LogServices", self.logservice_uri_list, uri_analyzed=[]
            )
            self.ctam_redfish_uri_deep_hunt(
                "/redfish/v1/Managers", "LogServices", self.logservice_uri_list, uri_analyzed=[]
            )
            self.ctam_redfish_uri_deep_hunt(
               "/redfish/v1/Chassis", "LogServices", self.logservice_uri_list, uri_analyzed=[]
            )
        self.write_test_info("{}".format(self.logservice_uri_list))
        return self.logservice_uri_list

    def ctam_clear_log_dump(self):
        result = True
        if self.dumplog_uri_list == []:
            self.dumplog_uri_list = self.ctam_get_logdump_uris()
            if self.dumplog_uri_list == []:
                result = False
        for dumplog_uri in self.dumplog_uri_list:
            clear_dump_uri = dumplog_uri + "/Actions/LogService.ClearLog"
            print(clear_dump_uri)
            uri = self.dut().uri_builder.format_uri(redfish_str="{GPUMC}" + "{}".format(clear_dump_uri), component_type="GPU")
            self.dut().run_redfish_command(uri=uri, mode="POST")
        self.write_test_info("{}".format(result))
        return result
    
    def trigger_self_test_dump_collection(self):
        """
        :Description:							Trigger Self-test Dump Collection

        :returns:				    			SelfTestDump_Status
        :rtype: 								Bool
        """
        MyName = __name__ + "." + self.trigger_self_test_dump_collection.__qualname__
        StartTime = time.time()

        selftest_dump_collection_uri = self.dut().uri_builder.format_uri(
            redfish_str="{BaseURI}{SystemURI}", component_type="BMC"
        )
        JSONData = self.RedfishTriggerDumpCollection(
            "OEM",
            selftest_dump_collection_uri,
            "SelfTest"
        )
        if self.dut().is_debug_mode():
            self.test_run().add_log(LogSeverity.DEBUG, f"{MyName}  {JSONData}")
            
        # Now Wait for TaskService/Tasks/$ID TaskState to reflect completed.
        if "error" not in JSONData:
            TaskID = JSONData["Id"]
            
            if self.dut().is_debug_mode():
                self.test_run().add_log(LogSeverity.DEBUG, f"Self-test Dump Collection Task ID = {TaskID}")
            DeployTime = time.time()
            Task_Completed, JSONData = self.ctam_monitor_task(TaskID)
            EndTime = time.time()
            if Task_Completed:
                for http_header in JSONData['Payload']['HttpHeaders']:
                    if 'Location' in  http_header:
                        self.selftest_dump_entry_uri=http_header.split(': ')[1]
                        if self.dut().is_debug_mode():
                            self.test_run().add_log(LogSeverity.DEBUG, 
                                "Self-test Dump Location = {}".format(self.selftest_dump_entry_uri)
                            )
                if self.selftest_dump_entry_uri:
                    SelfTestDump_Status = True
                else:
                    SelfTestDump_Status = False
            else:
                SelfTestDump_Status = False
            msg= "{0}: Self-test Dump Trigger Time: {1} Self-test Dump Collection Time: {2} \n Redfish Outcome: {3}".format(
                MyName,
                DeployTime - StartTime,
                EndTime - StartTime,
                json.dumps(JSONData, indent=4),
            )
            self.test_run().add_log(LogSeverity.DEBUG, msg)
            
        else:
            SelfTestDump_Status = False
        
        return SelfTestDump_Status
    
    def download_self_test_dump(self):
        """
        :Description:							Download Self-test Dump

        :returns:				    			SelfTestDump_Status
        :rtype: 								Bool
        """
        MyName = __name__ + "." + self.download_self_test_dump.__qualname__
        
        if self.selftest_dump_entry_uri:
            self.selftest_dump_path  = self.RedfishDownloadDump(self.selftest_dump_entry_uri)
            msg = "Self test Dump location: {}".format(self.selftest_dump_path)
            self.test_run().add_log(LogSeverity.DEBUG, msg)
            self.selftest_dump_entry_uri = None
            
        if self.selftest_dump_path:
            SelfTestDump_Status = True
        else:
            SelfTestDump_Status = False
        
        return SelfTestDump_Status

    def check_self_test_report(self):
        """
        :Description:							Check Self-test Report for any Failure

        :returns:				    			SelfTestReport_Status
        :rtype: 								Bool
        """
        MyName = __name__ + "." + self.download_self_test_dump.__qualname__
        SelfTestReport_Status = False
        
        for root, dirs, files in os.walk(self.selftest_dump_path):
            if "selftest_report.json" in files:
                with open(os.path.join(root, "selftest_report.json"), 'r') as fd:
                    SelfTestReport_JSON = json.load(fd)
                if SelfTestReport_JSON["header"]["summary"]["test-case-failed"] == 0:
                    SelfTestReport_Status = True
                else:
                    msg = "Self-test reported failure with test-case-failed = {}"\
                        .format(SelfTestReport_JSON["header"]["summary"]["test-case-failed"])
                    self.test_run().add_log(LogSeverity.ERROR, msg)

        return SelfTestReport_Status
    
    def ctam_get_logdump_uris(self):
        if self.logservice_uri_list == []:
            self.logservice_uri_list = self.ctam_get_logservice_uris()
        for uri in self.logservice_uri_list:
            self.ctam_redfish_uri_hunt(uri, "Dump", self.dumplog_uri_list)
        self.write_test_info("{}".format(self.dumplog_uri_list))
        return self.dumplog_uri_list
