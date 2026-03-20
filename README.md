### AUTOMATED NETWORK SECURTIY COMPLIANCE FRAMEWORK
## PROBLEM STATEMENT
Network security compliance at scale becomes a problem when done manually. For multiple routers and switches, confirming each device has:
  - telnet disabled
  - SNMPv3 configured 
  - logging enabled
  - banners in place 

requires logging into every system individually and reviewing the configuration by hand. 

## ABOUT
Ansible framework for auditing and hardening Cisco network devices against CIS benchmarks. Checks compliance, fixes what's broken, and generates an HTML report showing what passed and failed.

The pipeline runs on a schedule through GitHub Actions so you always have a current picture without touching a device manually.


1. audits every device in inventory against CIS controls 
2. remediates anything that fails
3. generates a HTML and JSON compliance report with scores and severity breakdown


## STRUCTURE
inventories/
  production/
    hosts.yml                   device inventory
    group_vars/
      network_devices.yml       all policy variables
      vault.yml                 encrypted secrets

roles/
  hardening/                    applies CIS controls
    tasks/
      main.yml
      ssh.yml
      aaa.yml
      ntp.yml
      logging.yml
      snmp.yml
      services.yml
      passwords.yml
      banners.yml
      backup.yml
  auditing/                     reads device state, scores compliance
    tasks/main.yml
  reporting/                    builds HTML + JSON report from audit results
    tasks/main.yml
    templates/report.html.j2

playbooks/
  site.yml                      full pipeline
  audit_only.yml                read-only scan
  rollback.yml                  restore from backup

## HOW IT WORKS

pre-audit -> hardening -> post-audit -> report


- pre-audit scores every device before touching anything
- hardening backs up config first, then remediates failures
- post-audit re-runs checks to verify fixes
- report aggregates everything into HTML + JSON

## USAGE INSTRUCTIONS

bash
# read-only compliance scan (safe to run anytime)
ansible-playbook playbooks/audit_only.yml

# see what would change without touching anything
ansible-playbook playbooks/site.yml -e "check_only=true"

# full run
ansible-playbook playbooks/site.yml

# target one device
ansible-playbook playbooks/site.yml --limit rtr-core-01

# only fix ssh config
ansible-playbook playbooks/site.yml --tags ssh

# rollback a device
ansible-playbook playbooks/rollback.yml --limit rtr-core-01 \
  -e "backup_file=backups/rtr-core-01/2024-01-15/rtr-core-01_1705305600.cfg"

## SETUP

bash
pip install ansible netmiko
ansible-galaxy collection install -r requirements.yml

# create vault password file — never commit this
echo "your-password" > .vault_pass

# encrypt secrets before committing
ansible-vault encrypt inventories/production/group_vars/vault.yml

# update hosts.yml with your device IPs
