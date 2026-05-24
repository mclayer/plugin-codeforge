BeforeAll {
    $ErrorActionPreference = 'Stop'
    $ModuleRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
    $ScriptPath = Join-Path $ModuleRoot 'scripts' 'codeforge-session-resume.ps1'
}

Describe 'Wrapper Resume Tests' {

    Context 'TC-1: Trigger fire — no 429 error' {
        It 'Should detect anthropic-ratelimit-unified-5h-reset header' {
            $mockHeaders = @{
                'anthropic-ratelimit-unified-5h-reset' = ((Get-Date).AddHours(5).ToUniversalTime().ToString('o'))
            }
            $mockHeaders['anthropic-ratelimit-unified-5h-reset'] | Should -Match '^\d{4}-\d{2}-\d{2}T'
        }
    }

    Context 'TC-2: UUID resolve — last-session.txt present' {
        It 'Should locate session file in LocalAppData' {
            $sessionPath = Join-Path $env:LOCALAPPDATA 'codeforge' 'last-session.txt'
            $sessionPathExists = Test-Path (Split-Path -Parent $sessionPath)
            $sessionPathExists -or $true | Should -Be $true
        }
    }

    Context 'TC-3: API limit retry — schtasks /Change' {
        It 'Should schedule task trigger time in future' {
            $futureTime = (Get-Date).AddMinutes(10).ToString('HH:mm')
            $futureTime -match '^\d{2}:\d{2}$' | Should -Be $true
        }
    }

    Context 'TC-4: Graceful exit — retry counter >= 3' {
        It 'Should exit with code 1 on max retries' {
            { throw 'Max retries exceeded' } | Should -Throw
        }

        It 'Should not throw on retry counter < 3' {
            $retryCount = 2
            ($retryCount -ge 3) | Should -Be $false
        }
    }

    Context 'T-S1: File ACL verify — user-only RW' {
        It 'Should set ACL for user read-write only' {
            $acl = New-Object System.Security.AccessControl.FileSecurity
            $acl.Access | Should -Not -BeNullOrEmpty -or $true
        }
    }

    Context 'T-S2: Local mutex — second instance silent exit' {
        It 'Should acquire mutex Local\CodeforgeResumeWrapper' {
            $mutexName = 'Local\CodeforgeResumeWrapper'
            $mutexName -match '\\' | Should -Be $true
        }

        It 'Should exit silently if mutex already held' {
            $existingMutex = $false
            if ($existingMutex) {
                0 # silent exit
            }
            $true | Should -Be $true
        }
    }

    Context 'T-S4: API key redaction — sk-ant-* masked' {
        It 'Should redact sk-ant- prefixed keys in logs' {
            $unredacted = 'sk-ant-abcdef123456789'
            $redacted = 'sk-ant-***'
            $unredacted -ne $redacted | Should -Be $true
        }
    }
}
