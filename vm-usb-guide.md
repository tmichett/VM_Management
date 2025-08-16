# VM-USB Management Guide

## Overview

`vm-usb.py` is a comprehensive VM management utility designed to handle manifest files, content distribution, and repository management for VM environments. It provides functionality for managing VM artifacts, USB operations, cache management, and deployment operations.

## Table of Contents

1. [Installation and Setup](#installation-and-setup)
2. [Configuration](#configuration)
3. [Core Concepts](#core-concepts)
4. [Command Reference](#command-reference)
5. [Workflow Examples](#workflow-examples)
6. [Troubleshooting](#troubleshooting)

## Installation and Setup

### Prerequisites

- Python 3.x with PyYAML library
- Root privileges (most operations require sudo)
- rsync utility
- Available storage space for VM artifacts

### Installation

1. Place `vm-usb.py` in your desired location
2. Make it executable:
   ```bash
   chmod +x vm-usb.py
   ```
3. Create configuration using the built-in command:
   ```bash
   sudo python3 vm-usb.py config_create
   ```

## Configuration

### Configuration File

The script uses `~/vm_repo_config.yml` for configuration:

```yaml
repository: /home/user/vm_repository
```

### Configuration Commands

- **config_create**: Create a new configuration file
  ```bash
  sudo python3 vm-usb.py config_create
  ```

## Core Concepts

### Manifest Files

The script works with two types of manifest files:

1. **ICMF Files**: Original Red Hat Training manifest format (`.icmf`)
2. **YAML Files**: Simplified manifest format (`.yml`)

### Repository Structure

- **Cache Directory**: Local storage for VM artifacts (`~/vm_repository/`)
- **Target Directories**: Destination paths where artifacts are deployed (`/content`)
- **Manifest Files**: Metadata describing artifacts and deployment targets

## Command Reference

### Interactive Mode

Launch interactive shell:
```bash
sudo python3 vm-usb.py
```

### Cache Management

#### List Operations
- **list**: List manifests in cache
  ```bash
  sudo python3 vm-usb.py list
  ```

- **lsartifacts**: List artifacts and their reference status
  ```bash
  sudo python3 vm-usb.py lsartifacts
  ```

- **lsicmfs**: List manifests referencing a specific artifact
  ```bash
  sudo python3 vm-usb.py lsicmfs filename.qcow2
  ```

#### Verification Operations
- **verify**: Verify checksums for manifest artifacts
  ```bash
  sudo python3 vm-usb.py verify manifest.icmf
  sudo python3 vm-usb.py verify all
  ```

- **verifyquick**: Quick existence check (no checksums)
  ```bash
  sudo python3 vm-usb.py verifyquick manifest.icmf
  ```

- **verifynewer**: Verify artifacts newer than specified date
  ```bash
  sudo python3 vm-usb.py verifynewer 2025-01-01
  sudo python3 vm-usb.py verifynewer today
  sudo python3 vm-usb.py verifynewer yesterday
  ```

#### Size Operations
- **size**: Display artifact sizes
  ```bash
  sudo python3 vm-usb.py size manifest.icmf
  sudo python3 vm-usb.py size all
  ```

#### Cleanup Operations
- **remove**: Remove manifest and unique artifacts
  ```bash
  sudo python3 vm-usb.py remove manifest.icmf
  ```

- **removeloop**: Remove manifests by prefix pattern
  ```bash
  sudo python3 vm-usb.py removeloop LB0000
  ```

- **rmobsoletes**: Remove unreferenced artifacts
  ```bash
  sudo python3 vm-usb.py rmobsoletes
  ```

### USB Operations

#### USB Information
- **usblist**: List manifests on USB device
  ```bash
  sudo python3 vm-usb.py usblist
  ```

- **usborphans**: List unreferenced files on USB
  ```bash
  sudo python3 vm-usb.py usborphans
  ```

#### USB Content Management
- **usbadd**: Add manifest to USB
  ```bash
  sudo python3 vm-usb.py usbadd manifest.icmf
  ```

- **usbremove**: Remove manifest from USB
  ```bash
  sudo python3 vm-usb.py usbremove manifest.icmf
  ```

- **usbsizeadd**: Preview size requirements for USB add
  ```bash
  sudo python3 vm-usb.py usbsizeadd manifest.icmf
  ```

- **usbsizeremove**: Preview space savings from USB removal
  ```bash
  sudo python3 vm-usb.py usbsizeremove manifest.icmf
  ```

#### USB Synchronization
- **usbdiff**: Compare cache and USB contents
  ```bash
  sudo python3 vm-usb.py usbdiff
  ```

- **usbupdate**: Update USB with newer manifests from cache
  ```bash
  sudo python3 vm-usb.py usbupdate
  ```

#### USB Verification
- **usbverify**: Verify USB manifest checksums
  ```bash
  sudo python3 vm-usb.py usbverify manifest.icmf
  sudo python3 vm-usb.py usbverify all
  ```

- **usbvalidate**: Validate USB device for installation
  ```bash
  sudo python3 vm-usb.py usbvalidate
  ```

### USB Device Preparation

- **usbmkpart**: Partition USB device
  ```bash
  sudo python3 vm-usb.py usbmkpart /dev/sdX msdos
  sudo python3 vm-usb.py usbmkpart /dev/sdX gpt
  ```

- **usbformat**: Format USB partition
  ```bash
  sudo python3 vm-usb.py usbformat /dev/sdX1
  ```

- **usbmkboot**: Make USB device bootable
  ```bash
  sudo python3 vm-usb.py usbmkboot
  ```

- **usbmkmenu**: Create boot menu on USB
  ```bash
  sudo python3 vm-usb.py usbmkmenu
  ```

### Remote Operations

#### Rsync Operations
- **rsyncget**: Download manifest via rsync
  ```bash
  sudo python3 vm-usb.py rsyncget manifest.icmf user@host:/path/
  ```

- **rsyncput**: Upload manifest via rsync
  ```bash
  sudo python3 vm-usb.py rsyncput manifest.icmf user@host:/path/
  ```

#### Rclone Operations
- **rcloneget**: Download manifest via rclone
  ```bash
  sudo python3 vm-usb.py rcloneget manifest.icmf provider:bucket/path/
  ```

- **rcloneput**: Upload manifest via rclone
  ```bash
  sudo python3 vm-usb.py rcloneput manifest.icmf provider:bucket/path/
  ```

### Foundation0 Operations

#### Foundation0 Information
- **f0list**: List deployed manifests on foundation0
  ```bash
  sudo python3 vm-usb.py f0list
  ```

#### Foundation0 Content Management
- **copy**: Deploy manifest from cache to foundation0
  ```bash
  sudo python3 vm-usb.py copy manifest.icmf
  ```

- **copyusb**: Deploy manifest from USB to foundation0
  ```bash
  sudo python3 vm-usb.py copyusb manifest.icmf
  ```

- **f0remove**: Remove manifest from foundation0
  ```bash
  sudo python3 vm-usb.py f0remove manifest.icmf
  ```

#### Foundation0 Management
- **f0activate**: Activate quiesced manifest on foundation0
  ```bash
  sudo python3 vm-usb.py f0activate manifest.icmf_quiesced
  ```

- **f0validate**: Validate deployed manifests on foundation0
  ```bash
  sudo python3 vm-usb.py f0validate
  ```

### Cache Rebuilding

- **cachef0**: Rebuild cache from foundation0
  ```bash
  sudo python3 vm-usb.py cachef0 manifest.icmf
  ```

- **cacheusb**: Rebuild cache from USB
  ```bash
  sudo python3 vm-usb.py cacheusb manifest.icmf
  ```

### YAML Manifest Operations

#### Load YAML Manifest
- **load_manifest**: Deploy artifacts from YAML manifest
  ```bash
  sudo python3 vm-usb.py load_manifest manifest.yml
  ```

### Utility Commands

- **help**: Display help information
  ```bash
  sudo python3 vm-usb.py help [command]
  ```

- **version**: Show version information
  ```bash
  sudo python3 vm-usb.py version
  ```

- **exit**: Exit interactive mode

## Workflow Examples

### Basic Workflow: From ICMF to Deployment

1. **Convert ICMF to YAML**:
   ```bash
   python3 manifest_convert.py LB0000-RHEL10.0-1.r2025080813-ILT+RAV-8-en_US.icmf
   ```

2. **Copy YAML to repository**:
   ```bash
   cp LB0000.yml ~/vm_repository/
   ```

3. **Deploy artifacts**:
   ```bash
   sudo python3 vm-usb.py load_manifest LB0000.yml
   ```

### Cache Management Workflow

1. **Check cache contents**:
   ```bash
   sudo python3 vm-usb.py list
   ```

2. **Verify integrity**:
   ```bash
   sudo python3 vm-usb.py verify all
   ```

3. **Clean obsolete artifacts**:
   ```bash
   sudo python3 vm-usb.py lsartifacts
   sudo python3 vm-usb.py rmobsoletes
   ```

### USB Preparation Workflow

1. **Partition USB device**:
   ```bash
   sudo python3 vm-usb.py usbmkpart /dev/sdX gpt
   ```

2. **Format partition**:
   ```bash
   sudo python3 vm-usb.py usbformat /dev/sdX1
   ```

3. **Add content**:
   ```bash
   sudo python3 vm-usb.py usbadd manifest.icmf
   ```

4. **Make bootable**:
   ```bash
   sudo python3 vm-usb.py usbmkboot
   sudo python3 vm-usb.py usbmkmenu
   ```

## Troubleshooting

### Common Issues

#### Configuration Problems
- **Error: Configuration file not found**
  ```bash
  sudo python3 vm-usb.py config_create
  ```

#### Permission Issues
- **Error: Permission denied**
  - Ensure running with sudo for most operations
  - Check repository directory permissions

#### Storage Issues
- **Error: No space left on device**
  - Check available space: `df -h`
  - Clean obsolete artifacts: `sudo python3 vm-usb.py rmobsoletes`
  - Remove old manifests: `sudo python3 vm-usb.py remove old_manifest.icmf`

#### USB Issues
- **Error: USB device not detected**
  - Check device connection: `lsblk`
  - Ensure device is unmounted before partitioning
  - Verify device path: `sudo fdisk -l`

#### Manifest Issues
- **Error: Manifest validation failed**
  - Check YAML syntax: `python3 -c "import yaml; yaml.load(open('manifest.yml'))"`
  - Verify required fields (name, files)
  - Use `manifest_convert.py` for ICMF conversion

### Debugging

Enable verbose output with the `-v` flag:
```bash
sudo python3 vm-usb.py -v command
```

Check log files in `/tmp/vm-usb-*.log` for detailed operation logs.

### Recovery Procedures

#### Corrupt Cache Recovery
1. **Verify cache integrity**:
   ```bash
   sudo python3 vm-usb.py verify all
   ```

2. **Rebuild from USB**:
   ```bash
   sudo python3 vm-usb.py cacheusb manifest.icmf
   ```

3. **Rebuild from foundation0**:
   ```bash
   sudo python3 vm-usb.py cachef0 manifest.icmf
   ```

#### USB Recovery
1. **Repartition device**:
   ```bash
   sudo python3 vm-usb.py usbmkpart /dev/sdX gpt
   ```

2. **Reformat and repopulate**:
   ```bash
   sudo python3 vm-usb.py usbformat /dev/sdX1
   sudo python3 vm-usb.py usbadd manifest.icmf
   ```

## Best Practices

### Storage Management
- Regularly run `rmobsoletes` to clean unused artifacts
- Monitor disk space with `size all`
- Use `verifyquick` for routine integrity checks

### USB Operations
- Always validate USB before deployment: `usbvalidate`
- Use `usbsizeadd` to preview space requirements
- Keep USB devices properly unmounted when not in use

### Security
- Always run with appropriate privileges (sudo)
- Verify checksums after remote transfers
- Keep configuration files secure

### Performance
- Use local cache for frequent deployments
- Batch operations when possible
- Consider using `verifyquick` instead of full `verify` for routine checks

## Support

For additional help:
- Use interactive mode: `sudo python3 vm-usb.py`
- Get command help: `sudo python3 vm-usb.py help [command]`
- Check log files in `/tmp/` for detailed error information
