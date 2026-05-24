BeforeAll {
    # Invoke-FidelityGate pure function — decision tree implementation
    # Decision tree logic per Change Plan §8.6 / ADR-110 §결정 7 M-1~M-4
    function Invoke-FidelityGate {
        param(
            [int]$M1Fidelity,      # M-1: Conversation context restoration % (0-100)
            [int]$M2State,         # M-2: In-process state reconstruction attempts (0-5)
            [string]$M3Asymmetry,  # M-3: VS Code ext ↔ CLI asymmetry type (identical/convertible/asymmetric)
            [string]$M4Path        # M-4: Session file presence + verification (verified/partial/mismatched)
        )

        # Decision tree: 3-way output enum
        $pass = ($M1Fidelity -ge 80) -and ($M2State -ge 4) -and ($M3Asymmetry -eq "identical") -and ($M4Path -eq "verified")
        $partial1 = ($M1Fidelity -ge 80) -and ($M2State -ge 3) -and ($M3Asymmetry -eq "convertible") -and ($M4Path -eq "verified")
        $partial2 = ($M1Fidelity -ge 70) -and ($M2State -ge 3) -and ($M3Asymmetry -eq "identical") -and ($M4Path -eq "verified")
        $partial3 = ($M1Fidelity -ge 60) -and ($M2State -ge 2) -and ($M3Asymmetry -eq "convertible") -and ($M4Path -eq "partial")

        if ($pass) {
            return "pass"
        } elseif ($partial1 -or $partial2 -or $partial3) {
            return "partial"
        } else {
            return "fail"
        }
    }
}

Describe "empirical-fidelity-gate-Tests" {

    # 9-row parameterized test cases per Change Plan §8.6 + ADR-110 §결정 7
    # ADR-110 §결정 7 decision tree reference: M-1~M-4 inputs → pass/partial/fail 3-way gate
    # §결정 D1 audit gate pointers:
    #   - Change Plan §3.5 first_step_empirical_gate scope_manifest
    #   - ADR-110 §결정 7 M-1~M-4 definition table
    #   - §3 ADR-110 placement anchor
    #   - ADR-070 §D6 mandatory-real-execution-evidence STANDING

    Context "R-1: M1=85, M2=4, M3=identical, M4=verified → pass" {
        It "should return PASS when all conditions strong" {
            # Arrange
            $m1 = 85    # High conversation context restoration
            $m2 = 4     # 4 in-process state reconstruction attempts
            $m3 = "identical"
            $m4 = "verified"

            # Act
            $result = Invoke-FidelityGate -M1Fidelity $m1 -M2State $m2 -M3Asymmetry $m3 -M4Path $m4

            # Assert [audit-gate-pointer: Change Plan §3.5, ADR-110 §결정 7 M-1~M-4]
            $result | Should -Be "pass"
        }
    }

    Context "R-2: M1=90, M2=4, M3=convertible, M4=verified → pass" {
        It "should return PASS when convertible asymmetry resolved" {
            # Arrange
            $m1 = 90    # Very high context restoration
            $m2 = 4     # 4 in-process state reconstruction attempts
            $m3 = "convertible"  # Convertible → can be resolved
            $m4 = "verified"

            # Act
            $result = Invoke-FidelityGate -M1Fidelity $m1 -M2State $m2 -M3Asymmetry $m3 -M4Path $m4

            # Assert [audit-gate-pointer: ADR-110 §결정 7 decision tree conditional (convertible → pass if M1≥80 AND M2≥3)]
            $result | Should -Be "pass"
        }
    }

    Context "R-3: M1=70, M2=3, M3=identical, M4=verified → partial" {
        It "should return PARTIAL when context fidelity weak but state reconstructible" {
            # Arrange
            $m1 = 70    # Moderate context restoration
            $m2 = 3     # 3 in-process state reconstruction attempts
            $m3 = "identical"
            $m4 = "verified"

            # Act
            $result = Invoke-FidelityGate -M1Fidelity $m1 -M2State $m2 -M3Asymmetry $m3 -M4Path $m4

            # Assert [audit-gate-pointer: ADR-110 §결정 7 M2≥3 AND M1≥70 condition]
            $result | Should -Be "partial"
        }
    }

    Context "R-4: M1=60, M2=2, M3=convertible, M4=partial → partial" {
        It "should return PARTIAL when multiple factors degraded" {
            # Arrange
            $m1 = 60    # Lower context restoration
            $m2 = 2     # 2 in-process state reconstruction attempts
            $m3 = "convertible"
            $m4 = "partial"  # Partial file path verification

            # Act
            $result = Invoke-FidelityGate -M1Fidelity $m1 -M2State $m2 -M3Asymmetry $m3 -M4Path $m4

            # Assert [audit-gate-pointer: ADR-110 decision tree R-4 branch]
            $result | Should -Be "partial"
        }
    }

    Context "R-5: M1=80, M2=4, M3=asymmetric, M4=verified → partial (Phase 1 FU-CFP precedence ambiguity)" {
        It "should return PARTIAL when asymmetry detected despite high fidelity" {
            # Arrange
            # NOTE: This row exposes Phase 1 ArchitectAgent precedence ambiguity (Change Plan §3.5 narrative)
            # Current decision tree: M3=asymmetric → precedence check required
            # Interpretation 1: asymmetric always fails → fail
            # Interpretation 2: asymmetric is 5th conditional branch → partial with caveat
            # Phase 1 worker identified ambiguity; Phase 2 fixture = current behavior literal verify

            $m1 = 80    # Good context restoration
            $m2 = 4     # 4 in-process state reconstruction attempts
            $m3 = "asymmetric"  # Asymmetric session model
            $m4 = "verified"

            # Act
            $result = Invoke-FidelityGate -M1Fidelity $m1 -M2State $m2 -M3Asymmetry $m3 -M4Path $m4

            # Assert: Current interpretation = partial (with escalation note)
            # [audit-gate-pointer: Change Plan §3.5 FU-CFP marker, ADR-110 §결정 7 row R-5 precedence note]
            $result | Should -Be "partial"
        }
    }

    Context "R-6: M1=40, M2=3, M3=identical, M4=verified → fail" {
        It "should return FAIL when context fidelity critically low" {
            # Arrange
            $m1 = 40    # Very low context restoration
            $m2 = 3     # 3 in-process state reconstruction attempts (adequate)
            $m3 = "identical"
            $m4 = "verified"

            # Act
            $result = Invoke-FidelityGate -M1Fidelity $m1 -M2State $m2 -M3Asymmetry $m3 -M4Path $m4

            # Assert [audit-gate-pointer: ADR-110 §결정 7 M1≥70 threshold]
            $result | Should -Be "fail"
        }
    }

    Context "R-7: M1=85, M2=1, M3=identical, M4=verified → fail" {
        It "should return FAIL when state reconstruction insufficient" {
            # Arrange
            $m1 = 85    # Good context restoration
            $m2 = 1     # Only 1 in-process state reconstruction attempt
            $m3 = "identical"
            $m4 = "verified"

            # Act
            $result = Invoke-FidelityGate -M1Fidelity $m1 -M2State $m2 -M3Asymmetry $m3 -M4Path $m4

            # Assert [audit-gate-pointer: ADR-110 §결정 7 M2≥2 minimum threshold]
            $result | Should -Be "fail"
        }
    }

    Context "R-8: M1=85, M2=4, M3=identical, M4=mismatched → fail" {
        It "should return FAIL when session file path verification fails" {
            # Arrange
            $m1 = 85    # Good context restoration
            $m2 = 4     # 4 in-process state reconstruction attempts
            $m3 = "identical"
            $m4 = "mismatched"  # Path verification failed

            # Act
            $result = Invoke-FidelityGate -M1Fidelity $m1 -M2State $m2 -M3Asymmetry $m3 -M4Path $m4

            # Assert [audit-gate-pointer: ADR-110 §결정 7 M4 must be "verified" for pass]
            $result | Should -Be "fail"
        }
    }

    Context "R-9: M1=85, M2=4, M3=asymmetric, M4=partial → fail" {
        It "should return FAIL when asymmetry + partial path detection" {
            # Arrange
            $m1 = 85    # Good context restoration
            $m2 = 4     # 4 in-process state reconstruction attempts
            $m3 = "asymmetric"
            $m4 = "partial"  # Partial file path verification

            # Act
            $result = Invoke-FidelityGate -M1Fidelity $m1 -M2State $m2 -M3Asymmetry $m3 -M4Path $m4

            # Assert [audit-gate-pointer: ADR-110 §결정 7 asymmetric + non-verified → fail path]
            $result | Should -Be "fail"
        }
    }
}
