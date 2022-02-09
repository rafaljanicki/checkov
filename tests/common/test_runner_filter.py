import unittest

from checkov.common.bridgecrew.severities import Severities
from checkov.common.checks.base_check import BaseCheck
from checkov.runner_filter import RunnerFilter


class TestRunnerFilter(unittest.TestCase):

    # Expected pseudo-code for when checks should run:
    #    if has_check_flag_specified():
    #        checks_to_run = checks_specifically_included
    #    else:
    #        checks_to_run = all_built_in_checks
    #    if has_checks_dir_specified():
    #       checks_to_run += checks_from_external_dir
    #    for skipped_check in skip_check_flags():
    #        checks_to_run.remove(skipped_check)

    def test_should_run_default(self):
        instance = RunnerFilter()
        self.assertTrue(instance.should_run_check(check_id="CHECK_1"))

    def test_should_run_specific_enable(self):
        instance = RunnerFilter(checks=["CHECK_1"])
        self.assertTrue(instance.should_run_check(check_id="CHECK_1"))

    def test_should_run_specific_enable_bc(self):
        instance = RunnerFilter(checks=["BC_CHECK_1"])
        self.assertTrue(instance.should_run_check(check_id="CHECK_1", bc_check_id="BC_CHECK_1"))

    def test_should_run_wildcard_enable(self):
        instance = RunnerFilter(checks=["CHECK_*"])
        self.assertTrue(instance.should_run_check(check_id="CHECK_1"))

    def test_should_run_wildcard_enable_bc(self):
        instance = RunnerFilter(checks=["BC_CHECK_*"])
        self.assertTrue(instance.should_run_check(check_id="CHECK_1", bc_check_id="BC_CHECK_1"))

    def test_should_run_omitted_specific_enable(self):
        instance = RunnerFilter(checks=["CHECK_1"])
        self.assertFalse(instance.should_run_check(check_id="CHECK_999"))

    def test_should_run_omitted_specific_enable_bc_id(self):
        instance = RunnerFilter(checks=["BC_CHECK_1"])
        self.assertFalse(instance.should_run_check(check_id="CHECK_999", bc_check_id="BC_CHECK_999"))

    def test_should_run_specific_disable(self):
        instance = RunnerFilter(skip_checks=["CHECK_1"])
        self.assertFalse(instance.should_run_check(check_id="CHECK_1"))

    def test_should_run_specific_disable_bc_id(self):
        instance = RunnerFilter(skip_checks=["BC_CHECK_1"])
        self.assertFalse(instance.should_run_check(check_id="CHECK_1", bc_check_id="BC_CHECK_1"))

    def test_should_run_omitted_specific_disable(self):
        instance = RunnerFilter(skip_checks=["CHECK_1"])
        self.assertTrue(instance.should_run_check(check_id="CHECK_999"))

    def test_should_run_omitted_specific_disable_bc_id(self):
        instance = RunnerFilter(skip_checks=["BC_CHECK_1"])
        self.assertTrue(instance.should_run_check(check_id="CHECK_999", bc_check_id="BC_CHECK_999"))

    def test_should_run_external(self):
        instance = RunnerFilter(skip_checks=["CHECK_1"])
        instance.notify_external_check("EXT_CHECK_999")
        self.assertTrue(instance.should_run_check(check_id="EXT_CHECK_999"))

    def test_should_run_external2(self):
        instance = RunnerFilter(checks=["CHECK_1"], skip_checks=["CHECK_2"])
        instance.notify_external_check("EXT_CHECK_999")
        self.assertFalse(instance.should_run_check(check_id="EXT_CHECK_999"))

    def test_should_run_external3(self):
        instance = RunnerFilter(checks=["EXT_CHECK_999"])
        instance.notify_external_check("EXT_CHECK_999")
        self.assertTrue(instance.should_run_check(check_id="EXT_CHECK_999"))

    def test_should_run_external4(self):
        instance = RunnerFilter(checks=["CHECK_1"], skip_checks=["CHECK_2"], all_external=True)
        instance.notify_external_check("EXT_CHECK_999")
        self.assertTrue(instance.should_run_check(check_id="EXT_CHECK_999"))

    def test_should_run_external_disabled(self):
        instance = RunnerFilter(skip_checks=["CHECK_1", "EXT_CHECK_999"])
        instance.notify_external_check("EXT_CHECK_999")
        self.assertFalse(instance.should_run_check(check_id="EXT_CHECK_999"))

    def test_should_run_external_disabled2(self):
        instance = RunnerFilter(skip_checks=["CHECK_1", "EXT_CHECK_999"], all_external=True)
        instance.notify_external_check("EXT_CHECK_999")
        self.assertFalse(instance.should_run_check(check_id="EXT_CHECK_999"))

    def test_should_run_specific_disable_AND_enable(self):
        instance = RunnerFilter(checks=["CHECK_1"], skip_checks=["CHECK_1"])
        self.assertTrue(instance.should_run_check(check_id="CHECK_1"))
    
    def test_should_run_omitted_wildcard(self):
        instance = RunnerFilter(skip_checks=["CHECK_AWS*"])
        self.assertTrue(instance.should_run_check(check_id="CHECK_999"))

    def test_should_run_omitted_wildcard_bc_id(self):
        instance = RunnerFilter(skip_checks=["BC_CHECK_AWS*"])
        self.assertTrue(instance.should_run_check(check_id="CHECK_999", bc_check_id="BC_CHECK_999"))
    
    def test_should_run_omitted_wildcard2(self):
        instance = RunnerFilter(skip_checks=["CHECK_AWS*"])
        self.assertFalse(instance.should_run_check(check_id="CHECK_AWS_909"))

    def test_should_run_omitted_wildcard2_bc_id(self):
        instance = RunnerFilter(skip_checks=["BC_CHECK_AWS*"])
        self.assertFalse(instance.should_run_check(check_id="CHECK_AWS_909", bc_check_id="BC_CHECK_AWS_909"))
    
    def test_should_run_omitted_wildcard3(self):
        instance = RunnerFilter(skip_checks=["CHECK_AWS*","CHECK_AZURE*"])
        self.assertTrue(instance.should_run_check(check_id="EXT_CHECK_909"))

    def test_should_run_omitted_wildcard4(self):
        instance = RunnerFilter(skip_checks=["CHECK_AWS*","CHECK_AZURE_01"])
        self.assertFalse(instance.should_run_check(check_id="CHECK_AZURE_01"))

    def test_should_run_severity1(self):
        instance = RunnerFilter(checks=["LOW"])
        self.assertTrue(instance.should_run_check(severity=Severities.LOW))

    def test_should_run_severity2(self):
        instance = RunnerFilter(skip_checks=["LOW"])
        self.assertTrue(instance.should_run_check(severity=Severities.HIGH))

    def test_should_skip_severity1(self):
        instance = RunnerFilter(checks=["HIGH"])
        self.assertFalse(instance.should_run_check(severity=Severities.LOW))

    def test_should_skip_severity2(self):
        instance = RunnerFilter(skip_checks=["LOW"])
        self.assertFalse(instance.should_run_check(severity=Severities.LOW))

    def test_should_run_check_id(self):
        instance = RunnerFilter(checks=['CKV_AWS_45'])
        from checkov.terraform.checks.resource.aws.LambdaEnvironmentCredentials import check
        self.assertTrue(instance.should_run_check(check=check))

    def test_should_run_check_id_omitted(self):
        instance = RunnerFilter(checks=['CKV_AWS_99'])
        from checkov.terraform.checks.resource.aws.LambdaEnvironmentCredentials import check
        self.assertFalse(instance.should_run_check(check=check))

    def test_should_run_check_bc_id(self):
        instance = RunnerFilter(checks=['BC_AWS_45'])
        from checkov.terraform.checks.resource.aws.LambdaEnvironmentCredentials import check
        check.bc_id = 'BC_AWS_45'
        self.assertTrue(instance.should_run_check(check=check))

    def test_should_run_check_bc_id_omitted(self):
        instance = RunnerFilter(checks=['BC_AWS_99'])
        from checkov.terraform.checks.resource.aws.LambdaEnvironmentCredentials import check
        check.bc_id = 'BC_AWS_45'
        self.assertFalse(instance.should_run_check(check=check))

    def test_should_skip_check_id(self):
        instance = RunnerFilter(skip_checks=['CKV_AWS_45'])
        from checkov.terraform.checks.resource.aws.LambdaEnvironmentCredentials import check
        self.assertFalse(instance.should_run_check(check=check))

    def test_should_skip_check_id_omitted(self):
        instance = RunnerFilter(skip_checks=['CKV_AWS_99'])
        from checkov.terraform.checks.resource.aws.LambdaEnvironmentCredentials import check
        self.assertTrue(instance.should_run_check(check=check))

    def test_should_skip_check_bc_id(self):
        instance = RunnerFilter(skip_checks=['BC_AWS_45'])
        from checkov.terraform.checks.resource.aws.LambdaEnvironmentCredentials import check
        check.bc_id = 'BC_AWS_45'
        self.assertFalse(instance.should_run_check(check=check))

    def test_should_skip_check_bc_id_omitted(self):
        instance = RunnerFilter(skip_checks=['BC_AWS_99'])
        from checkov.terraform.checks.resource.aws.LambdaEnvironmentCredentials import check
        check.bc_id = 'BC_AWS_45'
        self.assertTrue(instance.should_run_check(check=check))

    def test_should_run_check_severity(self):
        instance = RunnerFilter(checks=['LOW'])
        from checkov.terraform.checks.resource.aws.LambdaEnvironmentCredentials import check
        check.bc_severity = Severities.LOW
        self.assertTrue(instance.should_run_check(check=check))

    def test_should_run_check_severity_omitted(self):
        instance = RunnerFilter(checks=['HIGH'])
        from checkov.terraform.checks.resource.aws.LambdaEnvironmentCredentials import check
        check.bc_severity = Severities.LOW
        self.assertFalse(instance.should_run_check(check=check))

    def test_should_skip_check_severity(self):
        instance = RunnerFilter(skip_checks=['LOW'])
        from checkov.terraform.checks.resource.aws.LambdaEnvironmentCredentials import check
        check.bc_severity = Severities.LOW
        self.assertFalse(instance.should_run_check(check=check))

    def test_should_skip_check_severity_omitted(self):
        instance = RunnerFilter(skip_checks=['HIGH'])
        from checkov.terraform.checks.resource.aws.LambdaEnvironmentCredentials import check
        check.bc_severity = Severities.LOW
        self.assertTrue(instance.should_run_check(check=check))


if __name__ == '__main__':
    unittest.main()
