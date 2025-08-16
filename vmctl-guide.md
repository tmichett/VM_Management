# VM Control (vmctl) Guide

## Overview

`vmctl.py` is a virtual machine control utility designed to manage individual VMs on a local hypervisor system. It provides comprehensive VM lifecycle management including starting, stopping, resetting, saving/restoring states, and managing VM images and overlays.

## Table of Contents

1. [Installation and Setup](#installation-and-setup)
2. [Configuration](#configuration)
3. [Core Concepts](#core-concepts)
4. [Command Reference](#command-reference)
5. [Workflow Examples](#workflow-examples)
6. [Troubleshooting](#troubleshooting)

## Installation and Setup

### Prerequisites

- Python 3.x
- libvirt and KVM/QEMU virtualization stack
- virt-manager tools (virsh, virt-viewer, etc.)
- Sufficient storage space for VM images
- Network access to content server (for downloading VM images)

### Installation

1. Place `vmctl.py` in your desired location
2. Make it executable:
   ```bash
   chmod +x vmctl.py
   ```
3. Ensure virtualization is properly configured:
   ```bash
   python3 vmctl.py status all
   ```

### Required Packages

Install required virtualization packages:
```bash
# On RHEL/CentOS/Fedora
sudo dnf install qemu-kvm libvirt virt-install virt-viewer

# On Ubuntu/Debian
sudo apt install qemu-kvm libvirt-daemon-system virtinst virt-viewer
```

## Configuration

### Configuration File: `/etc/rht`

The script reads configuration from `/etc/rht`. If this file doesn't exist, vmctl will offer to create it:

```bash
# VM Management Configuration File
RHT_COURSE="LB0000"
RHT_VMHOST="localhost"
RHT_VMS="classroom servera serverb serverc utility workstation"
RHT_VM0="classroom"
RHT_VENUE="ilt"
CONTENTSERVER="http://foundation0.ilt.example.com"
```

### Configuration Parameters

- **RHT_COURSE**: Course identifier (e.g., "LB0000")
- **RHT_VMHOST**: Hypervisor hostname (typically "localhost")
- **RHT_VMS**: Space-separated list of available VMs
- **RHT_VM0**: List of VMs that should start first
- **RHT_VENUE**: Venue type ("ilt" for Instructor-Led Training)
- **CONTENTSERVER**: URL for downloading VM images

### Automatic Configuration

If no configuration exists, vmctl can create a default one:
```bash
python3 vmctl.py get all
# Will prompt to create configuration if needed
```

## Core Concepts

### VM Naming Convention

VMs follow the naming pattern: `{RHT_COURSE}-{VMNAME}`
- Course: LB0000
- VM: classroom
- Full name: LB0000-classroom

### File Naming Conventions

- **XML Definition**: `{COURSE}-{VMNAME}.xml`
- **Master Image**: `{COURSE}-{VMNAME}-vdZ.qcow2`
- **Overlay Image**: `{COURSE}-{VMNAME}-vdZ.ovl`
- **Saved State**: `{COURSE}-{VMNAME}-vdZ.ovl-{TIMESTAMP}`

### VM States

- **Undefined**: VM not known to libvirt
- **Defined**: VM exists but not running
- **Running**: VM is active and running
- **Paused**: VM is temporarily suspended
- **Shut off**: VM is defined but powered off

### Storage Locations

- **VM Images**: `/var/lib/libvirt/images/`
- **XML Definitions**: Managed by libvirt
- **Lock Files**: `/tmp/.lock-vmctl-{VMNAME}`

## Command Reference

### Basic Syntax

```bash
python3 vmctl.py [OPTIONS] COMMAND VMNAME [DATETIME]
```

### Global Options

- **-h, --help**: Show help message
- **-y, --yes**: Auto-confirm all operations
- **-i, --inquire**: Prompt for confirmation on each VM

### VM Management Commands

#### Starting and Stopping

##### start
Start one or more VMs (downloads images if needed):
```bash
python3 vmctl.py start classroom
python3 vmctl.py start servera serverb
python3 vmctl.py start all
```

##### stop
Gracefully stop running VMs:
```bash
python3 vmctl.py stop classroom
python3 vmctl.py stop all
```

##### restart
Stop and then start VMs:
```bash
python3 vmctl.py restart classroom
python3 vmctl.py -y restart all
```

##### poweroff
Force stop VMs (immediate shutdown):
```bash
python3 vmctl.py poweroff classroom
python3 vmctl.py -y poweroff all
```

#### State Management

##### reset
Reset VM to clean state (recreate overlay):
```bash
python3 vmctl.py reset classroom
python3 vmctl.py -y reset servera serverb
```

##### fullreset
Complete reset (redownload images and recreate overlays):
```bash
python3 vmctl.py fullreset classroom
```
**Warning**: This removes all data and saves!

#### Save and Restore Operations

##### save
Create a checkpoint of current VM state:
```bash
# Save with automatic timestamp
python3 vmctl.py save classroom

# Save with custom name
python3 vmctl.py save classroom "before-lab-exercise"

# Save with date/time
python3 vmctl.py save classroom "2025-01-15-14:30"
```

##### restore
Restore VM from a saved state:
```bash
# Restore latest save
python3 vmctl.py restore classroom

# Restore specific save by name
python3 vmctl.py restore classroom "before-lab-exercise"

# Restore by date/time
python3 vmctl.py restore classroom "2025-01-15-14:30"
```

##### listsaves
List available saves for a VM:
```bash
python3 vmctl.py listsaves classroom
python3 vmctl.py listsaves all
```

#### Information and Monitoring

##### status
Show current status of VMs:
```bash
python3 vmctl.py status classroom
python3 vmctl.py status all
```

##### view
Launch graphical console viewer:
```bash
python3 vmctl.py view classroom
```
**Note**: This functionality has been moved to a separate `vmview` utility.

#### Image Management

##### get
Download and set up VM images:
```bash
python3 vmctl.py get classroom
python3 vmctl.py get all
```

##### remove
Remove VM and all associated files:
```bash
python3 vmctl.py remove classroom
python3 vmctl.py -y remove servera serverb
```
**Warning**: This permanently deletes all VM data!

### Special VM Names

- **all**: Operates on all VMs defined in RHT_VMS
- **vm0**: Operates on VMs listed in RHT_VM0 (typically foundation VMs)

## Workflow Examples

### Initial VM Setup

1. **Download and configure all VMs**:
   ```bash
   python3 vmctl.py get all
   ```

2. **Start all VMs**:
   ```bash
   python3 vmctl.py start all
   ```

3. **Check status**:
   ```bash
   python3 vmctl.py status all
   ```

### Lab Exercise Workflow

1. **Start required VMs**:
   ```bash
   python3 vmctl.py start servera serverb
   ```

2. **Create checkpoint before exercise**:
   ```bash
   python3 vmctl.py save servera "before-lab-1"
   python3 vmctl.py save serverb "before-lab-1"
   ```

3. **After completing exercise, save progress**:
   ```bash
   python3 vmctl.py save servera "after-lab-1"
   python3 vmctl.py save serverb "after-lab-1"
   ```

4. **If needed, restore to checkpoint**:
   ```bash
   python3 vmctl.py restore servera "before-lab-1"
   python3 vmctl.py restore serverb "before-lab-1"
   ```

### Course Reset Workflow

1. **Stop all VMs**:
   ```bash
   python3 vmctl.py -y stop all
   ```

2. **Reset all VMs to clean state**:
   ```bash
   python3 vmctl.py -y reset all
   ```

3. **Start foundation VMs**:
   ```bash
   python3 vmctl.py start vm0
   ```

### Maintenance Workflow

1. **Check VM status**:
   ```bash
   python3 vmctl.py status all
   ```

2. **List saves for cleanup**:
   ```bash
   python3 vmctl.py listsaves all
   ```

3. **Remove old/unwanted VMs**:
   ```bash
   python3 vmctl.py remove oldvm
   ```

4. **Full reset if problems occur**:
   ```bash
   python3 vmctl.py fullreset problematic-vm
   ```

## Advanced Usage

### Batch Operations with Confirmation

Use the `-i` flag to confirm each operation:
```bash
python3 vmctl.py -i reset servera serverb serverc
```

This will prompt for each VM individually.

### Automated Scripts

Use the `-y` flag for non-interactive operation:
```bash
python3 vmctl.py -y stop all
python3 vmctl.py -y reset all
python3 vmctl.py -y start all
```

### Custom Save Names

Create meaningful save names for lab progression:
```bash
python3 vmctl.py save classroom "lesson-1-complete"
python3 vmctl.py save servera "database-configured"
python3 vmctl.py save serverb "webserver-installed"
```

## Troubleshooting

### Common Issues

#### VM Won't Start
```bash
# Check VM status
python3 vmctl.py status vmname

# Check if images exist
ls -la /var/lib/libvirt/images/

# Try getting images again
python3 vmctl.py get vmname

# Check virtualization
virt-host-validate qemu
```

#### VM Performance Issues
```bash
# Check system resources
free -h
df -h /var/lib/libvirt/images/

# Stop unnecessary VMs
python3 vmctl.py stop vmname
```

#### Configuration Problems
```bash
# Check configuration
cat /etc/rht

# Recreate configuration
sudo rm /etc/rht
python3 vmctl.py get all  # Will prompt to recreate
```

#### Network/Download Issues
```bash
# Test content server connectivity
curl -I http://foundation0.ilt.example.com

# Check course content URL
curl -I http://foundation0.ilt.example.com/content/courses/LB0000/
```

### Error Messages and Solutions

#### "VM is not defined"
```bash
# Solution: Download VM images
python3 vmctl.py get vmname
```

#### "VM is already running"
```bash
# Solution: Stop VM first
python3 vmctl.py stop vmname
python3 vmctl.py start vmname
```

#### "Permission denied"
```bash
# Solution: Check user permissions for libvirt
sudo usermod -a -G libvirt $USER
# Log out and back in
```

#### "No space left on device"
```bash
# Solution: Clean up old saves and images
python3 vmctl.py listsaves all
python3 vmctl.py remove unused-vm
# Or manually clean /var/lib/libvirt/images/
```

#### "Lock file exists"
```bash
# Solution: Remove stale lock files
sudo rm /tmp/.lock-vmctl-vmname
```

### Recovery Procedures

#### Corrupt VM Recovery
1. **Stop the VM**:
   ```bash
   python3 vmctl.py poweroff vmname
   ```

2. **Reset to clean state**:
   ```bash
   python3 vmctl.py reset vmname
   ```

3. **If still problematic, full reset**:
   ```bash
   python3 vmctl.py fullreset vmname
   ```

#### Storage Issues
1. **Check available space**:
   ```bash
   df -h /var/lib/libvirt/images/
   ```

2. **List and remove old saves**:
   ```bash
   python3 vmctl.py listsaves all
   # Manually remove old .ovl-* files if needed
   ```

3. **Remove unused VMs**:
   ```bash
   python3 vmctl.py remove unused-vm
   ```

### Debugging

#### Enable Debug Mode
Add debug prints in the script or check system logs:
```bash
# Check libvirt logs
sudo journalctl -u libvirtd -f

# Check VM console logs
sudo virsh console vmname

# Check qemu logs
sudo tail -f /var/log/libvirt/qemu/vmname.log
```

#### Manual VM Control
Use virsh directly for low-level operations:
```bash
# List all VMs
virsh list --all

# Start VM manually
virsh start vmname

# Stop VM forcefully
virsh destroy vmname

# Remove VM definition
virsh undefine vmname
```

## Best Practices

### VM Lifecycle Management
- Always use `stop` before `reset` for graceful shutdown
- Create saves before major configuration changes
- Use meaningful save names for easy identification
- Regularly clean up old saves to conserve disk space

### Performance Optimization
- Don't run all VMs simultaneously unless necessary
- Monitor system resources (RAM, CPU, disk space)
- Use SSD storage for better VM performance
- Allocate appropriate resources per VM

### Backup and Recovery
- Create saves at logical checkpoints
- Document save purposes for team members
- Test restore procedures before critical work
- Keep foundation VMs (vm0) clean and accessible

### Security
- Keep VM images updated through course updates
- Use proper file permissions on VM storage
- Limit network access for lab VMs as appropriate
- Regularly update the hypervisor system

### Course Management
- Use consistent naming conventions for saves
- Document course progression in save names
- Clean up between course deliveries
- Maintain master image integrity

## Integration with vm-usb.py

The vmctl.py utility works alongside vm-usb.py:

1. **vm-usb.py**: Handles content distribution and manifest management
2. **vmctl.py**: Manages individual VM operations and lifecycle

Typical integration workflow:
```bash
# Deploy content with vm-usb.py
sudo python3 vm-usb.py load_manifest course.yml

# Manage VMs with vmctl.py
python3 vmctl.py start all
python3 vmctl.py save all "initial-state"
```

## Support

For additional help:
- Check VM status: `python3 vmctl.py status all`
- Validate virtualization: `virt-host-validate qemu`
- Check system logs: `sudo journalctl -u libvirtd`
- Verify configuration: `cat /etc/rht`
- Test network connectivity to content server
