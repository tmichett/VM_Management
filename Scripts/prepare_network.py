#!/usr/bin/env python3
"""
prepare_network.py - Prepare libvirt networks from manifest requirements

This script reads a YAML manifest file, extracts all network requirements from
VM XML files, and ensures the required libvirt networks are created.

It maps bridge references in VM XML files to network definitions in the
Network_Resources directory and creates any missing networks in libvirt.
"""

import yaml
import xml.etree.ElementTree as ET
import subprocess
import sys
import os
import argparse
import logging
from pathlib import Path


def setup_logging(verbose=False):
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(levelname)-8s %(message)s'
    )
    return logging.getLogger('prepare_network')


def load_manifest(manifest_file):
    """Load and parse the YAML manifest file."""
    logger = logging.getLogger('prepare_network')
    
    try:
        with open(manifest_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        logger.error(f"Manifest file not found: {manifest_file}")
        return None
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML manifest: {e}")
        return None
    
    # Validate manifest structure
    if not isinstance(data, dict) or 'files' not in data:
        logger.error("Invalid manifest format: missing 'files' field")
        return None
    
    return data


def get_xml_files_from_manifest(manifest_data, content_dir="/content"):
    """Extract XML file paths from manifest data."""
    logger = logging.getLogger('prepare_network')
    xml_files = []
    
    files_list = manifest_data.get('files', [])
    
    for file_entry in files_list:
        if not isinstance(file_entry, dict) or 'filename' not in file_entry:
            continue
        
        filename = file_entry['filename']
        final_name = file_entry.get('final_name', filename)
        
        # Check if it's an XML file
        if final_name.lower().endswith('.xml'):
            xml_path = os.path.join(content_dir, final_name)
            if os.path.exists(xml_path):
                xml_files.append(xml_path)
                logger.debug(f"Found XML file: {xml_path}")
            else:
                logger.warning(f"XML file not found: {xml_path}")
    
    logger.info(f"Found {len(xml_files)} XML files in manifest")
    return xml_files


def extract_network_interfaces(xml_file):
    """Extract network interface information from a VM XML file."""
    logger = logging.getLogger('prepare_network')
    interfaces = []
    
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Find all interface elements
        for interface in root.findall('.//interface'):
            interface_type = interface.get('type')
            source = interface.find('source')
            
            if source is not None:
                if interface_type == 'network':
                    network = source.get('network')
                    if network:
                        interfaces.append({
                            'type': 'network',
                            'name': network,
                            'xml_file': xml_file
                        })
                elif interface_type == 'bridge':
                    bridge = source.get('bridge')
                    if bridge:
                        interfaces.append({
                            'type': 'bridge',
                            'name': bridge,
                            'xml_file': xml_file
                        })
    
    except ET.ParseError as e:
        logger.error(f"Error parsing XML file {xml_file}: {e}")
    except Exception as e:
        logger.error(f"Error reading XML file {xml_file}: {e}")
    
    if interfaces:
        logger.debug(f"Extracted {len(interfaces)} interfaces from {os.path.basename(xml_file)}")
    
    return interfaces


def load_network_definitions(network_resources_dir):
    """Load network definitions from Network_Resources directory."""
    logger = logging.getLogger('prepare_network')
    network_defs = {}
    
    if not os.path.exists(network_resources_dir):
        logger.error(f"Network_Resources directory not found: {network_resources_dir}")
        return network_defs
    
    # Find all XML files in the Network_Resources directory
    for xml_file in Path(network_resources_dir).glob('*.xml'):
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            # Extract network name and bridge name
            if root.tag == 'network':
                network_name = root.find('name')
                bridge_elem = root.find('bridge')
                
                if network_name is not None and bridge_elem is not None:
                    network_name = network_name.text
                    bridge_name = bridge_elem.get('name')
                    
                    network_defs[bridge_name] = {
                        'network_name': network_name,
                        'definition_file': str(xml_file),
                        'bridge_name': bridge_name
                    }
                    
                    logger.debug(f"Loaded network definition: {network_name} -> {bridge_name}")
        
        except ET.ParseError as e:
            logger.error(f"Error parsing network definition {xml_file}: {e}")
        except Exception as e:
            logger.error(f"Error reading network definition {xml_file}: {e}")
    
    logger.info(f"Loaded {len(network_defs)} network definitions")
    return network_defs


def get_existing_networks():
    """Get list of existing libvirt networks."""
    logger = logging.getLogger('prepare_network')
    
    try:
        result = subprocess.run(
            ['virsh', 'net-list', '--all', '--name'],
            capture_output=True,
            text=True,
            check=True
        )
        
        networks = [line.strip() for line in result.stdout.split('\n') if line.strip()]
        logger.debug(f"Existing networks: {networks}")
        return set(networks)
    
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to list existing networks: {e}")
        return set()
    except FileNotFoundError:
        logger.error("virsh command not found. Please ensure libvirt is installed.")
        return set()


def create_network(network_def):
    """Create a libvirt network from definition file."""
    logger = logging.getLogger('prepare_network')
    
    definition_file = network_def['definition_file']
    network_name = network_def['network_name']
    
    try:
        # Define the network
        logger.info(f"Creating network: {network_name}")
        subprocess.run(
            ['virsh', 'net-define', definition_file],
            check=True,
            capture_output=True,
            text=True
        )
        
        # Start the network
        subprocess.run(
            ['virsh', 'net-start', network_name],
            check=True,
            capture_output=True,
            text=True
        )
        
        # Set autostart
        subprocess.run(
            ['virsh', 'net-autostart', network_name],
            check=True,
            capture_output=True,
            text=True
        )
        
        logger.info(f"Successfully created and started network: {network_name}")
        return True
    
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else str(e)
        logger.error(f"Failed to create network {network_name}: {error_msg}")
        return False


def analyze_and_prepare_networks(manifest_file, content_dir="/content", network_resources_dir=None, dry_run=False):
    """Main function to analyze manifest and prepare networks."""
    logger = logging.getLogger('prepare_network')
    
    # Set default network resources directory
    if network_resources_dir is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        network_resources_dir = os.path.join(os.path.dirname(script_dir), 'Network_Resources')
    
    logger.info(f"Processing manifest: {manifest_file}")
    logger.info(f"Content directory: {content_dir}")
    logger.info(f"Network resources directory: {network_resources_dir}")
    
    # Load manifest
    manifest_data = load_manifest(manifest_file)
    if manifest_data is None:
        return False
    
    # Get XML files from manifest
    xml_files = get_xml_files_from_manifest(manifest_data, content_dir)
    if not xml_files:
        logger.error("No XML files found in manifest")
        return False
    
    # Extract all network interfaces from all XML files
    all_interfaces = []
    for xml_file in xml_files:
        interfaces = extract_network_interfaces(xml_file)
        all_interfaces.extend(interfaces)
    
    if not all_interfaces:
        logger.info("No network interfaces found in XML files")
        return True
    
    # Collect unique bridges/networks
    required_bridges = set()
    required_networks = set()
    
    for interface in all_interfaces:
        if interface['type'] == 'bridge':
            required_bridges.add(interface['name'])
        elif interface['type'] == 'network':
            required_networks.add(interface['name'])
    
    logger.info(f"Required bridges: {sorted(required_bridges)}")
    logger.info(f"Required networks: {sorted(required_networks)}")
    
    # Load network definitions
    network_defs = load_network_definitions(network_resources_dir)
    
    # Get existing networks
    existing_networks = get_existing_networks()
    
    # Determine which networks need to be created
    networks_to_create = []
    missing_definitions = []
    
    # Check bridges - map them to network names using definitions
    for bridge in required_bridges:
        if bridge in network_defs:
            network_name = network_defs[bridge]['network_name']
            if network_name not in existing_networks:
                networks_to_create.append(network_defs[bridge])
                logger.info(f"Will create network: {network_name} (bridge: {bridge})")
            else:
                logger.debug(f"Network already exists: {network_name} (bridge: {bridge})")
        elif bridge == 'virbr0' and 'default' in existing_networks:
            # Special case: virbr0 is the bridge used by the default network
            logger.debug(f"Bridge {bridge} maps to existing 'default' network")
        else:
            missing_definitions.append(bridge)
            logger.warning(f"No network definition found for bridge: {bridge}")
    
    # Check direct network references
    for network in required_networks:
        if network not in existing_networks:
            # Look for a network definition file with this name
            network_file = os.path.join(network_resources_dir, f"{network}.xml")
            if os.path.exists(network_file):
                # Try to extract network info from the definition
                try:
                    tree = ET.parse(network_file)
                    root = tree.getroot()
                    bridge_elem = root.find('bridge')
                    bridge_name = bridge_elem.get('name') if bridge_elem is not None else network
                    
                    net_def = {
                        'network_name': network,
                        'definition_file': network_file,
                        'bridge_name': bridge_name
                    }
                    networks_to_create.append(net_def)
                    logger.info(f"Will create network: {network}")
                except Exception as e:
                    logger.error(f"Error reading network definition {network_file}: {e}")
                    missing_definitions.append(network)
            else:
                missing_definitions.append(network)
                logger.warning(f"No network definition found for: {network}")
        else:
            logger.debug(f"Network already exists: {network}")
    
    # Report missing definitions
    if missing_definitions:
        logger.error(f"Missing network definitions for: {sorted(missing_definitions)}")
        logger.error("Please create network definition files in the Network_Resources directory")
    
    # Create networks
    if networks_to_create:
        if dry_run:
            logger.info(f"DRY RUN: Would create {len(networks_to_create)} networks:")
            for net_def in networks_to_create:
                logger.info(f"  - {net_def['network_name']} (bridge: {net_def['bridge_name']})")
        else:
            logger.info(f"Creating {len(networks_to_create)} networks...")
            success_count = 0
            for net_def in networks_to_create:
                if create_network(net_def):
                    success_count += 1
            
            logger.info(f"Successfully created {success_count}/{len(networks_to_create)} networks")
            
            if success_count < len(networks_to_create):
                return False
    else:
        logger.info("All required networks already exist")
    
    return len(missing_definitions) == 0


def main():
    parser = argparse.ArgumentParser(
        description="Prepare libvirt networks from manifest requirements",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 prepare_network.py LB0000.yml
  python3 prepare_network.py LB0000.yml --content-dir /content --dry-run
  python3 prepare_network.py LB0000.yml --network-resources ../Network_Resources --verbose
        """
    )
    
    parser.add_argument(
        'manifest_file',
        help='YAML manifest file to process'
    )
    
    parser.add_argument(
        '--content-dir',
        default='/content',
        help='Directory containing the manifest files (default: /content)'
    )
    
    parser.add_argument(
        '--network-resources',
        help='Directory containing network definition XML files (default: ../Network_Resources)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without actually creating networks'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Set up logging
    logger = setup_logging(args.verbose)
    
    # Validate manifest file
    if not os.path.isfile(args.manifest_file):
        logger.error(f"Manifest file not found: {args.manifest_file}")
        sys.exit(1)
    
    # Run the analysis and preparation
    success = analyze_and_prepare_networks(
        manifest_file=args.manifest_file,
        content_dir=args.content_dir,
        network_resources_dir=args.network_resources,
        dry_run=args.dry_run
    )
    
    if success:
        logger.info("Network preparation completed successfully")
        sys.exit(0)
    else:
        logger.error("Network preparation failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
