#!/usr/bin/env python3

# Copyright 2025 VM Management
#
# NAME
#     vmctl - VM Management virtual machine control utility
#
# SYNOPSIS
#     vmctl -h|--help
#     vmctl [-y|--yes] VMCMD VMNAME [DATETIME]
#     vmctl [-i|--inquire] VMCMD VMNAME [DATETIME]
#
#     where VMCMD is one of the following:
#       view      - runs virt-viewer on VMNAME
#       start     - if stopped, start VMNAME (obtain and overlay image if
#                   not there)
#       stop      - if running, stop VMNAME
#       restart   - if running, stop VMNAME then start VMNAME
#       poweroff  - if running, poweroff VMNAME
#       reset     - poweroff, recreate/restore latest overlay, start
#       save      - stop, backup overlay, start (this is typically used as
#                   a checkpoint for sequential labs that build on each other)
#       restore   - stop, restore overlay (to DATETIME), start
#       listsaves - list the saves of VMNAME
#       status    - show status of VMNAME on this system
#       get       - download image, create overlay
#       remove    - remove VMNAME from system
#       fullreset - poweroff, delete images/all saves, redownload image, 
#                   recreate overlay, start
#                   (this subcommand is used when a bad save has been made)
#
# DESCRIPTION
#     This tool is used to manage the virtual machines on this
#     local hypervisor layer system.
#
#     File naming conventions:
#        $RHT_COURSE-$VMNAME.xml - libvirt VM XML definition
#        $RHT_COURSE-$VMNAME-vdZ.qcow2 - master image vdZ
#        $RHT_COURSE-$VMNAME-vdZ.ovl - overlay of vdZ
#        $RHT_COURSE-$VMNAME-vdZ.ovl-$SAVE - backup of overlay

import os
import sys
import subprocess
import argparse
import glob
import time
import re
import shutil
from datetime import datetime
from pathlib import Path

# Global configuration
CONTENTSERVER = "http://foundation0.ilt.example.com"
VMBLKPATH = "/var/lib/libvirt/images"

class VMController:
    def __init__(self):
        self.debug_mode = False
        self.quiet = False
        self.inquire = False
        self.nostart = False
        self.nodelete = False
        self.gui = False
        self.config_loaded = False
        
    def load_config(self):
        """Load configuration from /etc/rht and /etc/os-release"""
        try:
            # Load OS release info
            self.version_id = "9.0"  # Default version
            try:
                with open('/etc/os-release', 'r') as f:
                    for line in f:
                        if line.startswith('VERSION_ID='):
                            self.version_id = line.split('=')[1].strip().strip('"')
                            break
            except FileNotFoundError:
                pass  # Use default
            
            # Load VM configuration
            self.rht_config = {}
            config_file = '/etc/rht'
            
            # Try to load existing config, or use defaults
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            if '=' in line:
                                key, value = line.split('=', 1)
                                self.rht_config[key] = value.strip().strip('"')
            else:
                print(f"Warning: Configuration file {config_file} not found. Using defaults.")
                print("You can create a configuration file or run with default settings.")
                
                # Create default configuration
                self.rht_config = {
                    'RHT_VENUE': 'ilt',
                    'RHT_ENROLLMENT': '1',
                    'RHT_COURSE': 'vm-course',
                    'RHT_ROLE': 'student',
                    'RHT_VMTREE': 'rhel9.0/x86_64',
                    'RHT_VMS': 'desktop server',
                    'RHT_VM0': 'foundation',
                    'RHT_STOPTIMEVMS': '20'
                }
                
                # Don't prompt for config creation during initialization
                # This will be handled later if needed for actual VM operations
            
            # Validate required variables
            required_vars = ['RHT_ENROLLMENT', 'RHT_COURSE', 'RHT_VMS', 'RHT_VMTREE']
            for var in required_vars:
                if var not in self.rht_config:
                    print(f"Warning: Missing variable {var}, using default")
                    if var == 'RHT_ENROLLMENT':
                        self.rht_config[var] = '1'
                    elif var == 'RHT_COURSE':
                        self.rht_config[var] = 'vm-course'
                    elif var == 'RHT_VMS':
                        self.rht_config[var] = 'desktop server'
                    elif var == 'RHT_VMTREE':
                        self.rht_config[var] = 'rhel9.0/x86_64'
            
            # Check for vILT
            if self.rht_config.get('RHT_VENUE') == 'vilt':
                print("System configured for vILT, there are no VMs to manage")
                sys.exit(2)
            
            # Set enrollment for RHT_ENROLLMENT >= 512
            self.enrollment = int(self.rht_config['RHT_ENROLLMENT']) % 512
            
        except Exception as e:
            print(f"Error loading configuration: {e}")
            print("Using minimal default configuration.")
            self.rht_config = {
                'RHT_VENUE': 'ilt',
                'RHT_ENROLLMENT': '1',
                'RHT_COURSE': 'vm-course',
                'RHT_VMS': 'desktop server',
                'RHT_VMTREE': 'rhel9.0/x86_64'
            }
            self.enrollment = 1
    
    def create_default_config(self, config_file):
        """Create a default configuration file"""
        config_content = """# VM Management Configuration File
# This file contains configuration variables for the VM management system

# Venue type (ilt = Instructor Led Training)
RHT_VENUE=ilt

# Student enrollment number
RHT_ENROLLMENT=1

# Course identifier
RHT_COURSE=vm-course

# Student role
RHT_ROLE=student

# VM tree path for downloads
RHT_VMTREE=rhel9.0/x86_64

# List of available VMs
RHT_VMS=desktop server

# Infrastructure VMs (foundation systems)
RHT_VM0=foundation

# VM stop timeout in seconds
RHT_STOPTIMEVMS=20
"""
        try:
            with open(config_file, 'w') as f:
                f.write(config_content)
            print(f"Created default configuration file: {config_file}")
            print("You can edit this file to customize VM settings.")
        except PermissionError:
            print(f"Permission denied: Cannot create {config_file}")
            print("You may need to run with sudo to create system configuration files.")
        except Exception as e:
            print(f"Error creating config file: {e}")
    
    def debug(self, message):
        """Print debug message if debug mode is enabled"""
        if self.debug_mode:
            print(f"DEBUG: {message}")
    
    def confirm_yn(self, message):
        """Ask for yes/no confirmation"""
        if self.quiet:
            return True
        
        while True:
            response = input(f"{message} (y/n): ").lower().strip()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print("Please answer 'y' or 'n'")
    
    def run_command(self, cmd, check=True, capture_output=True):
        """Run a system command"""
        self.debug(f"Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
        try:
            if isinstance(cmd, str):
                result = subprocess.run(cmd, shell=True, capture_output=capture_output, 
                                      text=True, check=check)
            else:
                result = subprocess.run(cmd, capture_output=capture_output, 
                                      text=True, check=check)
            return result
        except subprocess.CalledProcessError as e:
            if check:
                print(f"Command failed: {e}")
                return None
            return e
    
    def is_running(self, vmname):
        """Check if VM is running"""
        result = self.run_command(['virsh', 'domstate', vmname], check=False)
        return result and result.returncode == 0 and 'running' in result.stdout.lower()
    
    def is_defined(self, vmname):
        """Check if VM is defined in libvirt"""
        result = self.run_command(['virsh', 'dominfo', vmname], check=False)
        return result and result.returncode == 0
    
    def get_latest_save(self, pattern):
        """Get the latest file matching a pattern"""
        files = glob.glob(pattern)
        if not files:
            return None
        return max(files, key=os.path.getctime)
    
    def drop_vm_blocks(self, vmname, block_type):
        """Remove VM disk blocks (overlay, master, saves)"""
        xml_file = f"{VMBLKPATH}/{self.rht_config['RHT_COURSE']}-{vmname}.xml"
        
        if not os.path.exists(xml_file):
            return
        
        # Find QCOW2 disks
        with open(xml_file, 'r') as f:
            content = f.read()
        
        ovl_pattern = f"{self.rht_config['RHT_COURSE']}-{vmname}-.*\\.ovl"
        iso_pattern = f"{self.rht_config['RHT_COURSE']}-{vmname}-.*\\.iso"
        
        ovl_disks = re.findall(ovl_pattern, content)
        iso_disks = re.findall(iso_pattern, content)
        
        for vdisk in ovl_disks:
            vdisk_base = vdisk.replace('.ovl', '')
            self.debug(f"Dropping {vdisk_base}-{block_type}")
            
            if block_type == "saves":
                for save_file in glob.glob(f"{VMBLKPATH}/{vdisk}-*"):
                    os.remove(save_file)
            elif block_type == "overlay":
                overlay_file = f"{VMBLKPATH}/{vdisk}"
                if os.path.exists(overlay_file):
                    os.remove(overlay_file)
            elif block_type == "master":
                # Remove saves and overlay
                for save_file in glob.glob(f"{VMBLKPATH}/{vdisk}-*"):
                    os.remove(save_file)
                overlay_file = f"{VMBLKPATH}/{vdisk}"
                if os.path.exists(overlay_file):
                    os.remove(overlay_file)
                
                # Remove master qcow2 if not infrastructure VM
                vm0_list = self.rht_config.get('RHT_VM0', '').split()
                if vmname not in vm0_list:
                    qcow2_file = f"{VMBLKPATH}/{vdisk_base}.qcow2"
                    if os.path.exists(qcow2_file):
                        os.remove(qcow2_file)
        
        # Handle ISO disks
        for iso_disk in iso_disks:
            if block_type == "master":
                vm0_list = self.rht_config.get('RHT_VM0', '').split()
                if vmname not in vm0_list:
                    iso_file = f"{VMBLKPATH}/{iso_disk}"
                    if os.path.exists(iso_file):
                        os.remove(iso_file)
        
        # If removing master, also undefine and remove XML
        if block_type == "master":
            self.debug(f"Undefining {vmname}")
            self.run_command(['virsh', 'undefine', vmname], check=False)
            
            vm0_list = self.rht_config.get('RHT_VM0', '').split()
            if vmname not in vm0_list and os.path.exists(xml_file):
                os.remove(xml_file)
            
            # Remove from known_hosts
            for ssh_file in ['/root/.ssh/known_hosts', '/home/kiosk/.ssh/known_hosts']:
                if os.path.exists(ssh_file):
                    self.run_command(['sed', '-i', f'/^{vmname}/d', ssh_file], check=False)
    
    def get_vm(self, vmlist):
        """Download and setup VM images"""
        for vmname in vmlist:
            lockfile = f"/tmp/.lock-vmctl-{vmname}"
            
            if self.is_running(vmname):
                self.debug(f"Not getting. {vmname} is already running.")
                continue
            
            # Check for lockfile
            if os.path.exists(lockfile):
                print(f"Lockfile exists. Another {vmname} get is in progress.")
                continue
            
            # Create lockfile
            Path(lockfile).touch()
            
            try:
                # Get XML definition
                xml_file = f"{VMBLKPATH}/{self.rht_config['RHT_COURSE']}-{vmname}.xml"
                if not os.path.exists(xml_file):
                    vm0_list = self.rht_config.get('RHT_VM0', '').split()
                    if vmname in vm0_list:
                        print(f"Error: missing libvirt XML definition - {xml_file}")
                        sys.exit(12)
                    
                    print(f"Downloading virtual machine definition file for {vmname}.")
                    xml_source = f"{self.rht_config['RHT_VMTREE']}/vms/{self.rht_config['RHT_COURSE']}-{vmname}.xml"
                    
                    # Try local content first
                    local_xml = f"/content/{xml_source}"
                    if os.path.exists(local_xml):
                        shutil.copy2(local_xml, xml_file)
                    else:
                        # Download from server
                        result = self.run_command(['curl', '-#', '-f', '-o', xml_file, 
                                                 f"{CONTENTSERVER}/{xml_source}"], check=False)
                        if result.returncode != 0:
                            print(f"Error: Unable to download XML definition - {xml_file}")
                            sys.exit(12)
                
                # Modify XML for current environment
                self.modify_vm_xml(xml_file, vmname)
                
                # Process disk images
                self.process_vm_disks(xml_file, vmname)
                
                # Define VM in libvirt
                if not self.is_defined(vmname):
                    self.debug(f"Defining {vmname} from its xml file.")
                    self.run_command(['virsh', 'define', xml_file])
                
            finally:
                # Remove lockfile
                if os.path.exists(lockfile):
                    os.remove(lockfile)
    
    def modify_vm_xml(self, xml_file, vmname):
        """Modify VM XML for current environment"""
        enrollment_hex = f"{self.enrollment:02X}"
        
        # Read XML content
        with open(xml_file, 'r') as f:
            content = f.read()
        
        # Apply modifications
        content = content.replace('RHT_ENROLLMENT_HEX', enrollment_hex)
        content = content.replace('.qcow2', '.ovl')
        
        # Version-specific modifications for RHEL 9+
        if hasattr(self, 'version_id') and int(self.version_id.split('.')[0]) >= 9:
            # Remove spice-related elements
            content = re.sub(r'<channel.*?spice.*?</channel>', '', content, flags=re.DOTALL)
            content = re.sub(r'<redirdev.*?spice.*?</redirdev>', '', content, flags=re.DOTALL)
            content = content.replace('spice', 'vnc')
            
            # Change graphics from qxl to virtio
            content = re.sub(r"model type.*?qxl.*?", "model type='virtio' heads='1' primary='yes'/>", content)
            
            # Update machine type
            content = content.replace('pc-q35-rhel8.2.0', 'q35')
        
        # Add virtualport for OpenVSwitch if needed
        if self.rht_config.get('RHT_PRIVUSEOVS') == 'yes':
            if 'openvswitch' not in content:
                # Add virtualport elements (simplified implementation)
                content = re.sub(r'(privbr[0-9]+)', r'\1\n\t\t\t<virtualport type="openvswitch"/>', content)
        
        # Write modified content back
        with open(xml_file, 'w') as f:
            f.write(content)
    
    def process_vm_disks(self, xml_file, vmname):
        """Process VM disk images (download, create overlays)"""
        with open(xml_file, 'r') as f:
            content = f.read()
        
        # Find disk definitions
        ovl_pattern = f"{self.rht_config['RHT_COURSE']}-{vmname}-.*\\.ovl"
        iso_pattern = f"{self.rht_config['RHT_COURSE']}-{vmname}-.*\\.iso"
        
        ovl_disks = re.findall(ovl_pattern, content)
        iso_disks = re.findall(iso_pattern, content)
        
        # Process QCOW2 disks
        for vdisk in ovl_disks:
            vdisk_base = vdisk.replace('.ovl', '')
            qcow2_file = f"{VMBLKPATH}/{vdisk_base}.qcow2"
            overlay_file = f"{VMBLKPATH}/{vdisk}"
            
            # Download master image if needed
            if not os.path.exists(qcow2_file):
                vm0_list = self.rht_config.get('RHT_VM0', '').split()
                if vmname in vm0_list:
                    print(f"Error: missing master QCOW2 image - {qcow2_file}")
                    sys.exit(12)
                
                # Remove any existing overlays
                for old_ovl in glob.glob(f"{VMBLKPATH}/{vdisk_base}.ovl*"):
                    os.remove(old_ovl)
                
                print(f"Downloading virtual machine disk image {vdisk_base}.qcow2")
                qcow_source = f"{self.rht_config['RHT_VMTREE']}/vms/{vdisk_base}.qcow2"
                
                # Try local content first
                local_qcow = f"/content/{qcow_source}"
                if os.path.exists(local_qcow):
                    shutil.copy2(local_qcow, qcow2_file)
                else:
                    # Download from server
                    result = self.run_command(['curl', '-#', '-f', '-o', qcow2_file,
                                             f"{CONTENTSERVER}/{qcow_source}"], check=False)
                    if result.returncode != 0:
                        print(f"Error: Unable to download image - {qcow2_file}")
                        sys.exit(12)
            
            # Create or restore overlay
            if not os.path.exists(overlay_file):
                latest_save = self.get_latest_save(f"{VMBLKPATH}/{vdisk}-*")
                
                if not latest_save:
                    print(f"Creating virtual machine disk overlay for {vdisk_base}.qcow2")
                    self.run_command(['qemu-img', 'create', '-q', '-f', 'qcow2', '-F', 'qcow2',
                                    '-b', qcow2_file, overlay_file])
                else:
                    print(f"Restoring from {latest_save}")
                    shutil.copy2(latest_save, overlay_file)
        
        # Process ISO disks
        for iso_disk in iso_disks:
            iso_file = f"{VMBLKPATH}/{iso_disk}"
            
            if not os.path.exists(iso_file):
                vm0_list = self.rht_config.get('RHT_VM0', '').split()
                if vmname in vm0_list:
                    print(f"Error: missing ISO image - {iso_file}")
                    sys.exit(12)
                
                print(f"Downloading virtual machine disk image {iso_disk}")
                iso_source = f"{self.rht_config['RHT_VMTREE']}/vms/{iso_disk}"
                
                # Try local content first
                local_iso = f"/content/{iso_source}"
                if os.path.exists(local_iso):
                    shutil.copy2(local_iso, iso_file)
                else:
                    # Download from server
                    result = self.run_command(['curl', '-#', '-f', '-o', iso_file,
                                             f"{CONTENTSERVER}/{iso_source}"], check=False)
                    if result.returncode != 0:
                        print(f"Error: Unable to download ISO image - {iso_file}")
                        sys.exit(12)
    
    def start_vm(self, vmlist):
        """Start VMs"""
        for vmname in vmlist:
            if self.is_running(vmname):
                print(f"Error: {vmname} not started (is already running)")
                continue
            
            self.get_vm([vmname])
            
            if not self.is_defined(vmname):
                self.debug(f"Defining {vmname} from its xml file.")
                xml_file = f"{VMBLKPATH}/{self.rht_config['RHT_COURSE']}-{vmname}.xml"
                self.run_command(['virsh', 'define', xml_file])
            
            if not self.nostart:
                nostarts = self.rht_config.get('RHT_NOSTARTVMS', '').split()
                if vmname in nostarts:
                    print(f"Not starting {vmname}.")
                else:
                    print(f"Starting {vmname}.")
                    self.run_command(['virsh', '-q', 'start', vmname])
                    
                    # Set autostart for infrastructure VMs
                    vm0_list = self.rht_config.get('RHT_VM0', '').split()
                    if vmname in vm0_list:
                        self.debug(f"Configuring {vmname} to autostart.")
                        self.run_command(['virsh', 'autostart', vmname])
    
    def stop_vm(self, vmlist):
        """Stop VMs gracefully"""
        for vmname in vmlist:
            print(f"Stopping {vmname}.", end='', flush=True)
            
            # Try graceful shutdown first
            stop_time = int(self.rht_config.get('RHT_STOPTIMEVMS', 20))
            while self.is_running(vmname) and stop_time > 0:
                self.run_command(['virsh', 'shutdown', vmname], check=False)
                time.sleep(5)
                stop_time -= 1
                print('.', end='', flush=True)
            
            print()  # New line
            
            # Force poweroff if still running
            if self.is_running(vmname):
                old_quiet = self.quiet
                self.quiet = True
                self.poweroff_vm([vmname])
                self.quiet = old_quiet
            
            if self.is_running(vmname):
                print(f"Error: unable to stop {vmname}.")
                print("Try manually shutting it down then try again.")
    
    def restart_vm(self, vmlist):
        """Restart VMs"""
        for vmname in vmlist:
            if self.is_running(vmname):
                print(f"Restarting {vmname}:")
                old_quiet = self.quiet
                self.quiet = True
                self.stop_vm([vmname])
                self.quiet = old_quiet
                
                if self.is_running(vmname):
                    print(f"Error: unable to restart {vmname}.")
                else:
                    self.start_vm([vmname])
            else:
                print(f"Not running {vmname}.")
    
    def poweroff_vm(self, vmlist):
        """Force poweroff VMs"""
        if self.confirm_yn(f"Are you sure you want to poweroff {' '.join(vmlist)}?"):
            for vmname in vmlist:
                print(f"Powering off {vmname}.", end='', flush=True)
                
                attempts = 60
                while self.is_running(vmname) and attempts > 0:
                    self.run_command(['virsh', 'destroy', vmname], check=False)
                    attempts -= 1
                    print('.', end='', flush=True)
                
                print()  # New line
                
                if self.is_running(vmname):
                    print(f"Error: unable to poweroff {vmname}.")
                    print("Try manually stopping it then try again.")
    
    def reset_vm(self, vmlist):
        """Reset VMs to clean state"""
        if self.confirm_yn(f"Are you sure you want to reset {' '.join(vmlist)}?"):
            for vmname in vmlist:
                old_quiet = self.quiet
                self.quiet = True
                self.poweroff_vm([vmname])
                self.quiet = old_quiet
            
            for vmname in vmlist:
                print(f"Resetting {vmname}.")
                self.drop_vm_blocks(vmname, "overlay")
                lockfile = f"/tmp/.lock-vmctl-{vmname}"
                if os.path.exists(lockfile):
                    os.remove(lockfile)
                self.start_vm([vmname])
    
    def fullreset_vm(self, vmlist):
        """Full reset VMs (redownload everything)"""
        if self.confirm_yn(f"Are you sure you want to full reset {' '.join(vmlist)}?"):
            for vmname in vmlist:
                old_quiet = self.quiet
                self.quiet = True
                self.poweroff_vm([vmname])
                self.quiet = old_quiet
            
            for vmname in vmlist:
                print(f"Full resetting {vmname}.")
                self.drop_vm_blocks(vmname, "master")
                lockfile = f"/tmp/.lock-vmctl-{vmname}"
                if os.path.exists(lockfile):
                    os.remove(lockfile)
                self.start_vm([vmname])
    
    def remove_vm(self, vmlist):
        """Remove VMs from system"""
        if self.confirm_yn(f"Are you sure you want to remove {' '.join(vmlist)}?"):
            for vmname in vmlist:
                if not self.nodelete:
                    old_quiet = self.quiet
                    self.quiet = True
                    self.poweroff_vm([vmname])
                    self.quiet = old_quiet
                    print(f"Removing {vmname}.")
                    self.drop_vm_blocks(vmname, "master")
                else:
                    self.stop_vm([vmname])
                    self.debug(f"Undefining {vmname}.")
                    self.run_command(['virsh', 'undefine', vmname], check=False)
                    
                    # Remove from known_hosts
                    for ssh_file in ['/root/.ssh/known_hosts', '/home/kiosk/.ssh/known_hosts']:
                        if os.path.exists(ssh_file):
                            self.run_command(['sed', '-i', f'/^{vmname}/d', ssh_file], check=False)
                
                lockfile = f"/tmp/.lock-vmctl-{vmname}"
                if os.path.exists(lockfile):
                    os.remove(lockfile)
    
    def save_vm(self, vmlist, save_name=None):
        """Save VM state"""
        for vmname in vmlist:
            if not self.is_defined(vmname):
                print(f"Error: {vmname} is not defined - nothing to save.")
            else:
                self.stop_vm([vmname])
                print(f"Saving {vmname} disk image.")
                
                if not save_name:
                    save_name = datetime.now().strftime('%Y%m%d%H%M')
                
                xml_file = f"{VMBLKPATH}/{self.rht_config['RHT_COURSE']}-{vmname}.xml"
                if os.path.exists(xml_file):
                    with open(xml_file, 'r') as f:
                        content = f.read()
                    
                    ovl_pattern = f"{self.rht_config['RHT_COURSE']}-{vmname}-.*\\.ovl"
                    ovl_disks = re.findall(ovl_pattern, content)
                    
                    for vdisk in ovl_disks:
                        src_file = f"{VMBLKPATH}/{vdisk}"
                        dst_file = f"{VMBLKPATH}/{vdisk}-{save_name}"
                        if os.path.exists(src_file):
                            shutil.copy2(src_file, dst_file)
                
                self.start_vm([vmname])
    
    def restore_vm(self, vmlist, restore_name=None):
        """Restore VM from save"""
        if self.confirm_yn(f"Are you sure you want to restore {' '.join(vmlist)}?"):
            for vmname in vmlist:
                if not self.is_defined(vmname):
                    print(f"Error: {vmname} is not defined - nothing to restore.")
                    continue
                
                xml_file = f"{VMBLKPATH}/{self.rht_config['RHT_COURSE']}-{vmname}.xml"
                if not os.path.exists(xml_file):
                    continue
                
                with open(xml_file, 'r') as f:
                    content = f.read()
                
                ovl_pattern = f"{self.rht_config['RHT_COURSE']}-{vmname}-.*\\.ovl"
                ovl_disks = re.findall(ovl_pattern, content)
                
                if not restore_name:
                    # Find latest save
                    for vdisk in ovl_disks:
                        latest = self.get_latest_save(f"{VMBLKPATH}/{vdisk}-*")
                        if latest:
                            restore_name = latest.split('-')[-1]
                            break
                
                if not restore_name:
                    print(f"Error: {vmname} does not have a save - nothing to restore")
                    continue
                
                # Validate save exists for all disks
                valid = True
                for vdisk in ovl_disks:
                    save_file = f"{VMBLKPATH}/{vdisk}-{restore_name}"
                    if not os.path.exists(save_file):
                        print(f"Error: {vmname} missing save {vdisk}-{restore_name}.")
                        valid = False
                        break
                
                if not valid:
                    continue
                
                # Perform restore
                old_quiet = self.quiet
                self.quiet = True
                self.poweroff_vm([vmname])
                self.quiet = old_quiet
                
                print(f"Restoring disk image for {vmname} to {restore_name}.")
                
                for vdisk in ovl_disks:
                    src_file = f"{VMBLKPATH}/{vdisk}-{restore_name}"
                    dst_file = f"{VMBLKPATH}/{vdisk}"
                    shutil.copy2(src_file, dst_file)
                
                self.start_vm([vmname])
    
    def listsaves_vm(self, vmlist):
        """List saves for VMs"""
        for vmname in vmlist:
            if not self.is_defined(vmname):
                print(f"Error: {vmname} is not defined - nothing to list.")
            else:
                xml_file = f"{VMBLKPATH}/{self.rht_config['RHT_COURSE']}-{vmname}.xml"
                if os.path.exists(xml_file):
                    with open(xml_file, 'r') as f:
                        content = f.read()
                    
                    ovl_pattern = f"{self.rht_config['RHT_COURSE']}-{vmname}-.*\\.ovl"
                    ovl_disks = re.findall(ovl_pattern, content)
                    
                    for vdisk in ovl_disks:
                        vdisk_base = vdisk.replace('.ovl', '')
                        print(f"Saves for {vdisk_base}:")
                        
                        saves = glob.glob(f"{VMBLKPATH}/{vdisk}-*")
                        if not saves:
                            print("   Error: No saves.")
                        else:
                            for save in sorted(saves):
                                save_name = save.split('-')[-1]
                                print(f"   {save_name}")
                        break
    
    def view_vm(self, vmlist):
        """Launch viewer for VMs"""
        print("Functionality moved to new utility vmview.")
    
    def status_vm(self, vmlist):
        """Show status of VMs"""
        for vmname in vmlist:
            lockfile = f"/tmp/.lock-vmctl-{vmname}"
            
            if self.is_running(vmname):
                print(f"{vmname} \033[1;32mRUNNING\033[0;39m")
            elif self.is_defined(vmname):
                print(f"{vmname} \033[1;33mDEFINED\033[0;39m")
            elif os.path.exists(lockfile):
                print(f"{vmname} \033[1;35mPULLING\033[0;39m")
            else:
                print(f"{vmname} \033[1;31mMISSING\033[0;39m")
    
    def validate_virtualization(self):
        """Validate virtualization capabilities"""
        result = self.run_command(['virt-host-validate', 'qemu'], check=False)
        if result and 'FAIL' in result.stderr:
            print("Error: Failure in validating virtualization capabilities")
            print(result.stderr)
            sys.exit(101)
    
    def parse_vm_names(self, vmname):
        """Parse and expand VM names"""
        all_vms = self.rht_config['RHT_VMS'].split()
        vm0_list = self.rht_config.get('RHT_VM0', '').split()
        
        if vmname == "everything":
            return vm0_list + all_vms
        elif vmname == "all":
            return all_vms
        else:
            # Check for VM groups
            vmgrp = self.rht_config.get('RHT_VMGRP', '').split()
            if vmname in vmgrp:
                group_var = f"RHT_VMG_{vmname}"
                return self.rht_config.get(group_var, '').split()
            
            # Validate individual VM names
            valid_vms = all_vms + vm0_list
            vm_list = vmname.split()
            for vm in vm_list:
                if vm not in valid_vms:
                    print(f"Error: unrecognized VMNAME specified, {vm}.")
                    self.print_usage()
                    sys.exit(1)
            
            return vm_list
    
    def print_usage(self):
        """Print usage information"""
        print("""
This utility manages the VM Management supplied VMs on the local
hypervisor.

Usage: vmctl [-y|--yes] VMCMD VMNAME [DATETIME]
       vmctl [-i|--inquire] VMCMD VMNAME [DATETIME]
       vmctl -h|--help

  where VMCMD is one of:
    view       - launches console viewer of VMNAME
    start      - obtain and start up VMNAME
    stop       - stop a running VMNAME
    restart    - if running, stop then start VMNAME
    poweroff   - if running, force stop VMNAME
    reset      - poweroff, return to saved or original state, start VMNAME
    save       - stop, save image, start VMNAME (to DATETIME)
    restore    - poweroff, restore to save (to DATETIME), start VMNAME
    listsaves  - list the saves of VMNAME
    status     - display libvirt status of VMNAME
    get        - if not here, obtain VMNAME from server
    remove     - remove VMNAME from system
    fullreset  - poweroff, reobtain from server, start VMNAME (bad save/image)

  -i|--inquire - confirm each VMNAME first
  -y|--yes     - confirm nothing, just do it

  VMNAME of "all" processes all VMs available in the course
""")
    
    def offer_config_creation(self):
        """Offer to create config file if needed for VM operations"""
        if not os.path.exists('/etc/rht'):
            try:
                if input("Create default config file at /etc/rht? (y/n): ").lower().startswith('y'):
                    self.create_default_config('/etc/rht')
            except (EOFError, KeyboardInterrupt):
                print("\nContinuing with default configuration.")
    
    def main(self):
        """Main entry point"""
        # Parse arguments first to check for help
        parser = argparse.ArgumentParser(description='VM Management virtual machine control utility',
                                       add_help=False)
        parser.add_argument('-h', '--help', action='store_true', help='show this help message and exit')
        parser.add_argument('-y', '--yes', '-q', '--quiet', action='store_true', 
                          help='confirm nothing, just do it')
        parser.add_argument('-i', '--inquire', action='store_true', 
                          help='confirm each VMNAME first')
        parser.add_argument('-d', '--debug', action='store_true', 
                          help='enable debug output')
        parser.add_argument('-n', '--nostart', action='store_true', 
                          help='do not start VM (just do whatever else was requested)')
        parser.add_argument('-k', '--keep', action='store_true', 
                          help='do not delete files (just do whatever else was requested)')
        parser.add_argument('-g', '--gui', action='store_true', 
                          help='identify whether we are launched from GUI')
        parser.add_argument('command', nargs='?', help='VM command')
        parser.add_argument('vmname', nargs='?', help='VM name or "all"')
        parser.add_argument('datetime', nargs='?', help='datetime for save/restore operations')
        
        args = parser.parse_args()
        
        if args.help:
            self.print_usage()
            sys.exit(0)
        
        # Check if running as root for actual VM operations
        if os.geteuid() != 0:
            self.debug('Using sudo to become root.')
            os.execvp('sudo', ['sudo'] + sys.argv)
        
        # Set flags
        self.quiet = args.yes
        self.inquire = args.inquire
        self.debug_mode = args.debug
        self.nostart = args.nostart
        self.nodelete = args.keep
        self.gui = args.gui
        
        # Validate arguments
        if not args.command or not args.vmname:
            print("Error: missing subcommand or VMNAME.")
            self.print_usage()
            sys.exit(1)
        
        valid_commands = ['start', 'stop', 'restart', 'poweroff', 'reset', 'fullreset', 
                         'listsaves', 'get', 'view', 'status', 'remove', 'save', 'restore']
        
        if args.command not in valid_commands:
            self.print_usage()
            sys.exit(1)
        
        # Load configuration now that we know we need it for VM operations
        if not self.config_loaded:
            self.load_config()
            self.config_loaded = True
            
            # Offer to create config file if it doesn't exist
            if not self.quiet:
                self.offer_config_creation()
        
        # Parse VM names
        vm_list = self.parse_vm_names(args.vmname)
        
        # Validate virtualization
        self.validate_virtualization()
        
        # Handle inquire mode
        if self.inquire:
            confirmed_vms = []
            old_quiet = self.quiet
            self.quiet = False
            
            for vm in vm_list:
                if self.confirm_yn(f"Are you sure you want to {args.command} {vm}?"):
                    confirmed_vms.append(vm)
            
            vm_list = confirmed_vms
            self.quiet = True
        
        # Execute command
        if vm_list:
            method_name = f"{args.command}_vm"
            method = getattr(self, method_name)
            
            if args.command in ['save', 'restore']:
                method(vm_list, args.datetime)
            else:
                method(vm_list)

if __name__ == '__main__':
    controller = VMController()
    controller.main()
