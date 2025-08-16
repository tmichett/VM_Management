# VM Management System

A comprehensive virtual machine management suite for educational and training environments, providing tools for content distribution, VM lifecycle management, and manifest processing.

## Overview

The VM Management System consists of several interconnected tools designed to handle the complete lifecycle of virtual machine environments, from content preparation and distribution to individual VM management and control.

## System Components

### Core Tools

1. **[vm-usb.py](vm-usb-guide.md)** - Content distribution and manifest management
2. **[vmctl.py](vmctl-guide.md)** - Individual VM lifecycle management
3. **[manifest_convert.py](Scripts/manifest_convert.py)** - Manifest format conversion utility

### Utility Scripts

- **vm-usb.py**: Comprehensive tool for managing VM content, USB operations, and deployment
- **vmctl.py**: VM control utility for starting, stopping, and managing individual VMs
- **manifest_convert.py**: Converts ICMF manifest files to simplified YAML format

## Quick Start

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd VM_Management
   ```

2. Set up vm-usb.py configuration:
   ```bash
   sudo python3 Scripts/vm-usb.py config_create
   ```

3. Verify virtualization setup:
   ```bash
   python3 Scripts/vmctl.py status all
   ```

### Basic Workflow

1. **Convert and deploy content**:
   ```bash
   # Convert ICMF to YAML format
   python3 Scripts/manifest_convert.py Scripts/LB0000-RHEL10.0-1.r2025080813-ILT+RAV-8-en_US.icmf
   
   # Copy to repository
   cp Scripts/LB0000.yml ~/vm_repository/
   
   # Deploy artifacts
   sudo python3 Scripts/vm-usb.py load_manifest LB0000.yml
   ```

2. **Manage VMs**:
   ```bash
   # Download and setup VMs
   python3 Scripts/vmctl.py get all
   
   # Start VMs
   python3 Scripts/vmctl.py start classroom servera
   
   # Save state
   python3 Scripts/vmctl.py save all "initial-setup"
   ```

## Documentation

### Detailed Guides

- **[VM-USB Management Guide](vm-usb-guide.md)**: Complete guide for content distribution and manifest management
- **[VM Control Guide](vmctl-guide.md)**: Comprehensive VM lifecycle management documentation

### Key Features

#### VM-USB Management (vm-usb.py)

- **Content Distribution**: Deploy VM artifacts to target directories
- **USB Operations**: Prepare bootable USB devices with VM content
- **Cache Management**: Maintain local repository of VM artifacts
- **Manifest Processing**: Handle both ICMF and YAML manifest formats
- **Remote Operations**: Support for rsync and rclone transfers
- **Verification**: Checksum validation and integrity checking

#### VM Control (vmctl.py)

- **VM Lifecycle**: Start, stop, restart, and reset VMs
- **State Management**: Save and restore VM states
- **Image Management**: Download and manage VM disk images
- **Overlay Support**: Non-destructive VM modifications with overlays
- **Batch Operations**: Manage multiple VMs simultaneously

#### Manifest Conversion (manifest_convert.py)

- **Format Conversion**: Convert ICMF files to simplified YAML
- **File Filtering**: Extract specific file types (.qcow2, .raw, .iso, .xml, .tgz, .tar.gz)
- **Target Directory Mapping**: Configure deployment destinations
- **Automated Processing**: Command-line interface for batch operations

## Architecture

### Data Flow

```
ICMF Manifest → manifest_convert.py → YAML Manifest → vm-usb.py → Deployed Content
                                                           ↓
USB/Remote Storage ←                                Target Directories
                                                           ↓
                     vmctl.py ← VM Images/Artifacts ← Content Server
```

### File Structure

```
VM_Management/
├── README.md                    # This file
├── vm-usb-guide.md             # VM-USB documentation
├── vmctl-guide.md              # VM Control documentation
└── Scripts/
    ├── vm-usb.py               # Content distribution tool
    ├── vmctl.py                # VM control utility
    ├── manifest_convert.py     # Manifest conversion utility
    └── LB0000-RHEL10.0-1.r2025080813-ILT+RAV-8-en_US.icmf  # Example manifest
```

### Configuration Files

- **`~/vm_repo_config.yml`**: VM-USB repository configuration
- **`/etc/rht`**: VM Control system configuration
- **Manifest Files**: YAML files describing VM content and deployment

## Use Cases

### Educational Training

- **Course Deployment**: Distribute VM images and content for training courses
- **Lab Environment Setup**: Prepare standardized lab environments
- **Student Workstations**: Manage individual student VM environments

### Development and Testing

- **Environment Provisioning**: Quickly set up development environments
- **State Management**: Create checkpoints for testing scenarios
- **Content Distribution**: Distribute test data and configurations

### System Administration

- **VM Farm Management**: Manage multiple VM environments
- **Backup and Recovery**: Create and restore VM snapshots
- **Content Synchronization**: Keep VM content synchronized across systems

## System Requirements

### Hardware

- **CPU**: Modern processor with virtualization support (Intel VT-x or AMD-V)
- **RAM**: Minimum 8GB (16GB+ recommended for multiple VMs)
- **Storage**: 100GB+ available space for VM images and content
- **Network**: Reliable internet connection for content downloads

### Software

- **Operating System**: Linux (RHEL, CentOS, Fedora, Ubuntu)
- **Python**: Python 3.6 or later
- **Virtualization**: KVM/QEMU, libvirt
- **Tools**: rsync, virt-manager tools, PyYAML

### Python Dependencies

```bash
pip install PyYAML
```

## Security Considerations

### Permissions

- Most operations require root/sudo privileges
- VM storage requires appropriate file system permissions
- Network operations may need firewall configuration

### Best Practices

- Regular integrity checking with verification commands
- Secure storage of configuration files
- Network security for remote operations
- Regular updates of VM images and system components

## Troubleshooting

### Common Issues

1. **Permission Errors**: Ensure proper sudo/root access
2. **Storage Issues**: Monitor disk space and clean unused content
3. **Network Problems**: Verify connectivity to content servers
4. **VM Issues**: Check virtualization support and libvirt configuration

### Getting Help

1. Use built-in help: `python3 vm-usb.py help` or `python3 vmctl.py --help`
2. Check log files in `/tmp/` for detailed error information
3. Review system logs: `sudo journalctl -u libvirtd`
4. Validate configuration files and system setup

## Development

### Contributing

1. Fork the repository
2. Create feature branches
3. Test thoroughly with different VM configurations
4. Submit pull requests with clear descriptions

### Testing

- Test with various manifest formats
- Verify VM operations on different hypervisors
- Check USB operations with different device types
- Validate network operations in various environments

## Changelog

### Recent Updates

- Added YAML manifest support in vm-usb.py
- Enhanced manifest conversion with XML file support
- Improved error handling and validation
- Updated documentation with comprehensive guides

## License

Copyright 2025 VM Management System

This project is provided for educational and training purposes.

## Support

For issues and questions:
1. Review the detailed documentation guides
2. Check troubleshooting sections
3. Verify system requirements and configuration
4. Test with minimal configurations to isolate issues

---

**Note**: This system is designed for educational and training environments. Ensure proper testing and validation before production use.