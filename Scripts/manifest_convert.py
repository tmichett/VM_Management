#!/usr/bin/env python3
"""
manifest_convert.py - Convert YAML manifest files to simplified format

This script reads a YAML manifest file and extracts filenames with specific
extensions (.qcow2, .raw, .iso, .tgz, .tar.gz, .xml) to create a new simplified
YAML file with a static target directory.
"""

import yaml
import sys
import os
import argparse
from pathlib import Path


def extract_filename_prefix(filename):
    """Extract the prefix from a filename (everything before the first dash or dot)."""
    basename = os.path.basename(filename)
    # Remove extension first
    name_without_ext = os.path.splitext(basename)[0]
    # Find the first dash or dot and take everything before it
    for char in ['-', '.']:
        if char in name_without_ext:
            return name_without_ext.split(char)[0]
    return name_without_ext


def is_target_extension(filename):
    """Check if filename has one of the target extensions."""
    target_extensions = ['.qcow2', '.raw', '.iso', '.tgz', '.xml']
    filename_lower = filename.lower()
    
    # Special handling for .tar.gz (must be checked first since it's two extensions)
    if filename_lower.endswith('.tar.gz'):
        return True
    
    # Check other extensions
    for ext in target_extensions:
        if filename_lower.endswith(ext):
            return True
    
    return False


def process_manifest(input_file):
    """Process the manifest file and extract target filenames."""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
        return None
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        return None
    
    # Extract the name prefix from the input filename
    name_prefix = extract_filename_prefix(input_file)
    
    # Find all artifacts with target extensions
    curriculum = data.get('curriculum', {})
    artifacts = curriculum.get('artifacts', [])
    if not artifacts:
        print("Warning: No 'artifacts' section found in the manifest.")
        return None
    
    target_files = []
    
    for artifact in artifacts:
        if isinstance(artifact, dict) and 'filename' in artifact:
            filename = artifact['filename']
            if is_target_extension(filename):
                target_files.append({
                    'filename': filename,
                    'target_directory': '/content'
                })
    
    if not target_files:
        print("No files found with target extensions (.qcow2, .raw, .iso, .tgz, .tar.gz, .xml)")
        return None
    
    # Create the output structure
    output_data = {
        'name': name_prefix,
        'files': target_files
    }
    
    return output_data


def write_output_file(output_data, output_file):
    """Write the processed data to a YAML file."""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            # Write the complete YAML structure using the yaml library for proper formatting
            yaml.dump(output_data, f, default_flow_style=False, sort_keys=False)
        
        print(f"Successfully created '{output_file}'")
        print(f"Processed {len(output_data['files'])} files")
        
    except IOError as e:
        print(f"Error writing output file: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Convert YAML manifest files to simplified format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 manifest_convert.py LB0000-RHEL10.0-1.r2025080813-ILT+RAV-8-en_US.icmf
  python3 manifest_convert.py /path/to/manifest.yaml
        """
    )
    
    parser.add_argument(
        'input_file',
        help='Input YAML manifest file to process'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output filename (default: <prefix>.yml based on input filename)'
    )
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.isfile(args.input_file):
        print(f"Error: Input file '{args.input_file}' does not exist.")
        sys.exit(1)
    
    # Determine output filename
    if args.output:
        output_file = args.output
    else:
        prefix = extract_filename_prefix(args.input_file)
        output_file = f"{prefix}.yml"
    
    # Process the manifest
    output_data = process_manifest(args.input_file)
    if output_data is None:
        sys.exit(1)
    
    # Write the output file
    write_output_file(output_data, output_file)


if __name__ == "__main__":
    main()
