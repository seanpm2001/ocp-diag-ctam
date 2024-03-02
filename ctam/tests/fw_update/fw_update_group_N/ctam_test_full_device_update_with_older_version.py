"""
Copyright (c) Microsoft Corporation
This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.

:Test Name: CTAM Test Full Device Update With Older Version
:Test ID: F19
:Group Name: fw_update
:Score Weight: 10

:Description: This test case focuses on updating the firmware of the full device using an older or previous version
of the current version that is already installed.
:Usage 1: python ctam.py -w ..\workspace -t F19
:Usage 2: python ctam.py -w ..\workspace -t "CTAM Test Full Device Update With Older Version"

"""

from typing import Optional, List
from tests.test_case import TestCase
from ocptv.output import (
    DiagnosisType,
    LogSeverity,
    SoftwareType,
    TestResult,
    TestStatus,
)
from tests.fw_update.fw_update_group_N._fw_update_group_N import (
    FWUpdateTestGroupN,
)


class CTAMTestFullDeviceUpdateWithOlderVersion(TestCase):
    """
    Verify values of Software Inventory Collection are present

    :param TestCase: super class for all test cases
    :type TestCase:
    """

    test_name: str = "CTAM Test Full Device Update With Older Version"
    test_id: str = "F19"
    score_weight: int = 10
    tags: List[str] = ["L3"]
    compliance_level: str = "L3"

    def __init__(self, group: FWUpdateTestGroupN):
        """
        _summary_
        """
        super().__init__()
        self.group = group

    def setup(self):
        """
        set environment state for this test only
        """
        # call super first
        super().setup()

        # add custom setup here
        step1 = self.test_run().add_step(f"{self.__class__.__name__}  setup()...")
        with step1.scope():
            pass

    def run(self) -> TestResult:
        """
        actual test verification
        """

        result = True
        image_t = "old_version"

        if result:
            step1 = self.test_run().add_step(f"{self.__class__.__name__} run(), step1")  # type: ignore
            with step1.scope():
                if not self.group.fw_update_ifc.ctam_fw_update_precheck(
                    image_type=image_t
                ):
                    step1.add_log(
                        LogSeverity.INFO, f"{self.test_id} : FW Update Capable"
                    )
                else:
                    step1.add_log(
                        LogSeverity.INFO, f"{self.test_id} : FW Update Not Required"
                    )

        if result:
            step2 = self.test_run().add_step(f"{self.__class__.__name__} run(), step2")  # type: ignore
            with step2.scope():
                if self.group.fw_update_ifc.ctam_stage_fw(image_type=image_t):
                    step2.add_log(
                        LogSeverity.INFO, f"{self.test_id} : FW Update Staged"
                    )
                else:
                    step2.add_log(
                        LogSeverity.ERROR, f"{self.test_id} : FW Update Stage Failed"
                    )
                    result = False

        if result:
            step3 = self.test_run().add_step(f"{self.__class__.__name__} run(), step3")  # type: ignore
            with step3.scope():
                if self.group.fw_update_ifc.ctam_activate_ac():
                    step3.add_log(
                        LogSeverity.INFO, f"{self.test_id} : FW Update Activate"
                    )
                else:
                    step3.add_log(
                        LogSeverity.ERROR,
                        f"{self.test_id} : FW Update Activation Failed",
                    )
                    result = False

        if result:
            step4 = self.test_run().add_step(f"{self.__class__.__name__} run(), step4")
            with step4.scope():
                if self.group.fw_update_ifc.ctam_fw_update_verify(image_type=image_t):
                    step4.add_log(
                        LogSeverity.INFO,
                        f"{self.test_id} : Update Verification Completed",
                    )
                else:
                    step4.add_log(
                        LogSeverity.ERROR,
                        f"{self.test_id} : Update Verification Failed",
                    )
                    result = False

        # ensure setting of self.result and self.score prior to calling super().run()

        self.result = TestResult.PASS if result else TestResult.FAIL
        if self.result == TestResult.PASS:
            self.score = self.score_weight

        # call super last to log result and score
        super().run()
        return self.result

    def teardown(self):
        """
        undo environment state change from setup() above, this function is called even if run() fails or raises exception
        """
        # add custom teardown here
        step1 = self.test_run().add_step(f"{self.__class__.__name__}  teardown()...")
        with step1.scope():
            pass

        # call super teardown last
        super().teardown()
