#Requires -Module ActiveDirectory
#Requires -RunAsAdministrator

<#
.DESCRIPTION
    Hi! this script:
    - Deletes users from Active Directory
    - Changes user passwords
    - Mass creates users from CSV files
    - Mass creates groups from CSV files
    It is meant to make daily AD tasks quicker in

.AUTHOR
    Tom!

#>

# ========================================
# CONFIGURATION FOR PATHS AND LOGS WITH ERROR HANDLING
# ========================================

$LogPath = "C:\Logs\AD_Automation"
$ErrorLogFile = Join-Path $LogPath "errors_$(Get-Date -Format 'MMdd_HHmmss').log"
$SuccessLogFile = Join-Path $LogPath "success_$(Get-Date -Format 'MMdd_HHmmss').log"

# Create log directory if it doesn't exist
if (-not (Test-Path $LogPath)) {
    New-Item -ItemType Directory -Path $LogPath -Force | Out-Null
}

# ========================================
# LOGGING AND DEBUGGER
# ========================================

function Write-Log {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Message,
        
        [Parameter(Mandatory=$false)]
        [ValidateSet("Info", "Warning", "Error", "Success")]
        [string]$Level = "Info"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    
    Write-Host $logMessage -ForegroundColor $(
        switch ($Level) {
            "Error"   { "Red" }
            "Warning" { "Yellow" }
            "Success" { "Green" }
            default   { "White" }
        }
    )
    
    if ($Level -eq "Error") {
        Add-Content -Path $ErrorLogFile -Value $logMessage
    } else {
        Add-Content -Path $SuccessLogFile -Value $logMessage
    }
}

# ========================================
# USER DELETE AND PASSWORD CHANGE FUNCTION
# ========================================

function Delete-ADUserByUsername {
    <#
    .Overview
        This script deletes an AD user 
    
    .PARAMETER Username
        The SAMAccountName of the user to delete
    
    .PARAMETER Confirm
        If $false, deletion will proceed without confirmation
    #>
    param(
        [Parameter(Mandatory=$true)]
        [string]$Username,
        
        [Parameter(Mandatory=$false)]
        [bool]$Confirm = $true
    )
    
    try {
        $user = Get-ADUser -Filter { SamAccountName -eq $Username }
        
        if (-not $user) {
            Write-Log -Message "User '$Username' not found" -Level Warning
            return $false
        }
        
        if ($Confirm) {
            $response = Read-Host "Are you sure you want to delete user '$Username'? (yes/no)"
            if ($response -ne "yes") {
                Write-Log -Message "Deletion of user '$Username' cancelled by user" -Level Warning
                return $false
            }
        }
        
        Remove-ADUser -Identity $user -Confirm:$false
        Write-Log -Message "Successfully deleted user: $Username" -Level Success
        return $true
    }
    catch {
        Write-Log -Message "Error deleting user '$Username': $($_.Exception.Message)" -Level Error
        return $false
    }
}

function Change-ADUserPassword {
    <#
    .SYNOPSIS
        Changes the password for an Active Directory user
    
    .PARAMETER Username
        The SAMAccountName of the user
    
    .PARAMETER NewPassword
        The new password (if not provided, user will be prompted)
    #>
    param(
        [Parameter(Mandatory=$true)]
        [string]$Username,
        
        [Parameter(Mandatory=$false)]
        [securestring]$NewPassword
    )
    
    try {
        $user = Get-ADUser -Filter { SamAccountName -eq $Username }
        
        if (-not $user) {
            Write-Log -Message "User '$Username' not found" -Level Warning
            return $false
        }
        
        if (-not $NewPassword) {
            $NewPassword = Read-Host -Prompt "Enter new password for $Username" -AsSecureString
        }
        
        Set-ADAccountPassword -Identity $user -NewPassword $NewPassword -Reset
        Set-ADUser -Identity $user -ChangePasswordAtLogon $true
        
        Write-Log -Message "Successfully changed password for user: $Username" -Level Success
        return $true
    }
    catch {
        Write-Log -Message "Error changing password for user '$Username': $($_.Exception.Message)" -Level Error
        return $false
    }
}

# ========================================
# BULK USER CREATION
# ========================================

function New-ADUsersFromCSV {
    <#
    .SYNOPSIS
        Creates multiple users from a CSV file
    
    .PARAMETER CSVPath
        Path to the CSV file
    
    .PARAMETER OrganizationalUnit
        Distinguished Name of the OU where users will be created
    
    .PARAMETER DefaultPassword
        Default password for new users (optional, prompts if not provided)
    
    .DESCRIPTION
        CSV file should have the following columns:
        - FirstName
        - LastName
        - Username (SAMAccountName)
        - Email
        - (Optional) Department, Title, Office, Phone, etc.
    #>
    param(
        [Parameter(Mandatory=$true)]
        [string]$CSVPath,
        
        [Parameter(Mandatory=$true)]
        [string]$OrganizationalUnit,
        
        [Parameter(Mandatory=$false)]
        [securestring]$DefaultPassword
    )
    
    try {
        if (-not (Test-Path $CSVPath)) {
            Write-Log -Message "CSV file not found at: $CSVPath" -Level Error
            return
        }
        
        $users = Import-Csv -Path $CSVPath
        $successCount = 0
        $failureCount = 0
        
        if (-not $DefaultPassword) {
            $DefaultPassword = Read-Host -Prompt "Enter default password for new users" -AsSecureString
        }
        
        foreach ($user in $users) {
            try {
                # Validate required fields
                if (-not $user.FirstName -or -not $user.LastName -or -not $user.Username) {
                    Write-Log -Message "Skipping user due to missing required fields: $($user.Username)" -Level Warning
                    $failureCount++
                    continue
                }
                
                $displayName = "$($user.FirstName) $($user.LastName)"
                
                # Create the user
                $newUserParams = @{
                    GivenName             = $user.FirstName
                    Surname               = $user.LastName
                    Name                  = $displayName
                    SamAccountName        = $user.Username
                    UserPrincipalName     = "$($user.Username)@$(($OrganizationalUnit -split ',')[0] -replace 'DC=').replace('DC=','.'))"
                    Path                  = $OrganizationalUnit
                    AccountPassword       = $DefaultPassword
                    Enabled               = $true
                    ChangePasswordAtLogon = $true
                }
                
                # Add optional properties if they exist in CSV
                if ($user.Email) { $newUserParams.EmailAddress = $user.Email }
                if ($user.Department) { $newUserParams.Department = $user.Department }
                if ($user.Title) { $newUserParams.Title = $user.Title }
                if ($user.Office) { $newUserParams.Office = $user.Office }
                if ($user.Phone) { $newUserParams.OfficePhone = $user.Phone }
                
                New-ADUser @newUserParams
                Write-Log -Message "Created user: $($user.Username)" -Level Success
                $successCount++
            }
            catch {
                Write-Log -Message "Error creating user '$($user.Username)': $($_.Exception.Message)" -Level Error
                $failureCount++
            }
        }
        
        Write-Log -Message "User creation complete. Success: $successCount | Failures: $failureCount" -Level Info
    }
    catch {
        Write-Log -Message "Error in bulk user creation: $($_.Exception.Message)" -Level Error
    }
}

# ========================================
# BULK GROUP CREATION
# ========================================

function New-ADGroupsFromCSV {
    <#
    .SYNOPSIS
        Creates multiple groups from a CSV file
    
    .PARAMETER CSVPath
        Path to the CSV file
    
    .PARAMETER OrganizationalUnit
        Distinguished Name of the OU where groups will be created
    
    .DESCRIPTION
        CSV file should have the following columns:
        - GroupName
        - GroupScope (Global, Local, or Universal)
        - GroupCategory (Security or Distribution)
        - (Optional) Description, Email, Manager, etc.
    #>
    param(
        [Parameter(Mandatory=$true)]
        [string]$CSVPath,
        
        [Parameter(Mandatory=$true)]
        [string]$OrganizationalUnit
    )
    
    try {
        if (-not (Test-Path $CSVPath)) {
            Write-Log -Message "CSV file not found at: $CSVPath" -Level Error
            return
        }
        
        $groups = Import-Csv -Path $CSVPath
        $successCount = 0
        $failureCount = 0
        
        foreach ($group in $groups) {
            try {
                # Validate required fields
                if (-not $group.GroupName) {
                    Write-Log -Message "Skipping group due to missing name" -Level Warning
                    $failureCount++
                    continue
                }
                
                $groupScope = if ($group.GroupScope) { $group.GroupScope } else { "Global" }
                $groupCategory = if ($group.GroupCategory) { $group.GroupCategory } else { "Security" }
                
                $newGroupParams = @{
                    Name            = $group.GroupName
                    SamAccountName  = $group.GroupName -replace '\s', ''
                    Path            = $OrganizationalUnit
                    GroupScope      = $groupScope
                    GroupCategory   = $groupCategory
                }
                
                # Add optional properties if they exist
                if ($group.Description) { $newGroupParams.Description = $group.Description }
                if ($group.Email) { $newGroupParams.EmailAddress = $group.Email }
                
                New-ADGroup @newGroupParams
                Write-Log -Message "Created group: $($group.GroupName)" -Level Success
                $successCount++
            }
            catch {
                Write-Log -Message "Error creating group '$($group.GroupName)': $($_.Exception.Message)" -Level Error
                $failureCount++
            }
        }
        
        Write-Log -Message "Group creation complete. Success: $successCount | Failures: $failureCount" -Level Info
    }
    catch {
        Write-Log -Message "Error in bulk group creation: $($_.Exception.Message)" -Level Error
    }
}

# ========================================
# ADDITIONAL UTILITY FUNCTIONS
# ========================================

function Add-UserToADGroup {
    <#
    .SYNOPSIS
        Adds a user to an Active Directory group
    
    .PARAMETER Username
        The SAMAccountName of the user
    
    .PARAMETER GroupName
        The name of the group
    #>
    param(
        [Parameter(Mandatory=$true)]
        [string]$Username,
        
        [Parameter(Mandatory=$true)]
        [string]$GroupName
    )
    
    try {
        $user = Get-ADUser -Filter { SamAccountName -eq $Username }
        $group = Get-ADGroup -Filter { Name -eq $GroupName }
        
        if (-not $user) {
            Write-Log -Message "User '$Username' not found" -Level Warning
            return $false
        }
        
        if (-not $group) {
            Write-Log -Message "Group '$GroupName' not found" -Level Warning
            return $false
        }
        
        Add-ADGroupMember -Identity $group -Members $user
        Write-Log -Message "Added user '$Username' to group '$GroupName'" -Level Success
        return $true
    }
    catch {
        Write-Log -Message "Error adding user to group: $($_.Exception.Message)" -Level Error
        return $false
    }
}

# ========================================
# MAIN MENU
# ========================================

function Show-Menu {
    Write-Host "`n======================================" -ForegroundColor Cyan
    Write-Host "   AD Automation Framework" -ForegroundColor Cyan
    Write-Host "======================================" -ForegroundColor Cyan
    Write-Host "1. Delete a user"
    Write-Host "2. Change user password"
    Write-Host "3. Create users from CSV"
    Write-Host "4. Create groups from CSV"
    Write-Host "5. Add user to group"
    Write-Host "6. Exit"
    Write-Host "======================================" -ForegroundColor Cyan
}

function Invoke-ADAutomation {
    do {
        Show-Menu
        $choice = Read-Host "Select an option (1-6)"
        
        switch ($choice) {
            "1" {
                $username = Read-Host "Enter username to delete"
                Delete-ADUserByUsername -Username $username
            }
            "2" {
                $username = Read-Host "Enter username"
                Change-ADUserPassword -Username $username
            }
            "3" {
                $csvPath = Read-Host "Enter full path to CSV file (e.g., C:\users.csv)"
                $ou = Read-Host "Enter OU Distinguished Name (e.g., 'OU=Users,DC=company,DC=com')"
                New-ADUsersFromCSV -CSVPath $csvPath -OrganizationalUnit $ou
            }
            "4" {
                $csvPath = Read-Host "Enter full path to CSV file"
                $ou = Read-Host "Enter OU Distinguished Name"
                New-ADGroupsFromCSV -CSVPath $csvPath -OrganizationalUnit $ou
            }
            "5" {
                $username = Read-Host "Enter username"
                $groupName = Read-Host "Enter group name"
                Add-UserToADGroup -Username $username -GroupName $groupName
            }
            "6" {
                Write-Host "Exiting AD Automation Framework..." -ForegroundColor Green
                break
            }
            default {
                Write-Host "Invalid option. Please try again." -ForegroundColor Red
            }
        }
    } while ($choice -ne "6")
}

# Uncomment the line below to run the interactive menu
# Invoke-ADAutomation