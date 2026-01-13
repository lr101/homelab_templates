#!/usr/bin/env python3
"""
Generate README.md with service tables based on docker-compose files.
One row per container service with annotations defining metadata.
"""

import yaml
from pathlib import Path
from typing import Dict, List, Tuple
import re
import argparse

REPO_ROOT = Path(__file__).parent.parent


def parse_docker_compose(file_path: Path) -> Dict:
    """Parse a docker-compose.yml file."""
    try:
        with open(file_path, 'r') as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return {}


def extract_annotation(annotations, key: str) -> str:
    """Extract a specific annotation value."""
    if not isinstance(annotations, list):
        return None
    
    for annotation in annotations:
        if isinstance(annotation, str) and annotation.startswith(f"de.lr-projects.{key}="):
            return annotation.split('=', 1)[1]
    
    return None


def extract_domain(service_data: Dict) -> str:
    """Extract domain from traefik labels in a service."""
    labels = service_data.get('labels', [])
    
    if isinstance(labels, dict):
        label_list = [f"{k}={v}" for k, v in labels.items()]
    else:
        label_list = labels if isinstance(labels, list) else []
    
    for label in label_list:
        label_str = str(label)
        if 'traefik.http.routers' in label_str and 'rule=Host' in label_str:
            match = re.search(r'Host\(`([^`]+)`\)', label_str)
            if match:
                return match.group(1)
    
    return "-"


def get_watchtower_info(service_data: Dict) -> str:
    """Extract watchtower info from service labels."""
    labels = service_data.get('labels', [])
    
    if isinstance(labels, dict):
        label_list = [f"{k}={v}" for k, v in labels.items()]
    else:
        label_list = labels if isinstance(labels, list) else []
    
    for label in label_list:
        label_str = str(label)
        if 'com.centurylinklabs.watchtower.enable' in label_str:
            if 'false' not in label_str:
                return "✅"
    
    return "manual"


def parse_autorestic(device: str) -> Dict[str, list]:
    """Parse autorestic config to find which folders are backed up."""
    autorestic_path = REPO_ROOT / device / ".autorestic.yml"
    
    folder_to_backends = {}
    
    if not autorestic_path.exists():
        return folder_to_backends
    
    try:
        with open(autorestic_path, 'r') as f:
            data = yaml.safe_load(f) or {}
        
        locations = data.get('locations', {})
        for location_name, location_data in locations.items():
            if isinstance(location_data, dict):
                from_paths = location_data.get('from', [])
                to_backends = location_data.get('to', [])
                
                for from_path in from_paths:
                    # Normalize path - remove ./ prefix
                    normalized = from_path.replace('./', '')
                    folder_to_backends[normalized] = to_backends
    except Exception as e:
        print(f"Error parsing autorestic for {device}: {e}")
    
    return folder_to_backends


def get_backup_status(folder: str, folder_to_backends: Dict[str, list]) -> str:
    """Get backup status by checking if folder is in autorestic config."""
    # Check if this folder is in any autorestic location
    if folder in folder_to_backends:
        return "✅"
    return "-"


def process_device(device: str) -> Tuple[str, List[Dict]]:
    """Process all services for a device and return table data (one row per service)."""
    device_path = REPO_ROOT / device
    folder_to_backends = parse_autorestic(device)
    
    # Also check shared folder for backup status
    shared_to_backends = parse_autorestic("shared")
    folder_to_backends.update(shared_to_backends)
    
    services_data = []
    
    # Find all docker-compose files in subdirectories
    for service_dir in sorted(device_path.iterdir()):
        if not service_dir.is_dir():
            continue
        if service_dir.name.startswith('.'):
            continue
        
        compose_file = service_dir / "docker-compose.yml"
        if not compose_file.exists():
            compose_file = service_dir / "docker-compose.yaml"
        if not compose_file.exists():
            continue
        
        compose_data = parse_docker_compose(compose_file)
        services = compose_data.get('services', {})
        
        # Create one row per service
        for service_name, service_data in services.items():
            if not isinstance(service_data, dict):
                continue
            
            annotations = service_data.get('annotations', [])
            
            # Extract metadata from annotations
            description = extract_annotation(annotations, 'description') or "-"
            sso = extract_annotation(annotations, 'sso')
            
            # Get other info
            domain = extract_domain(service_data)
            backup_status = get_backup_status(service_dir.name, folder_to_backends)
            update_status = get_watchtower_info(service_data)
            sso_status = "✅" if sso and sso.lower() == "true" else "-"
            
            service_entry = {
                'name': service_name.replace('-', ' ').replace('_', ' ').title(),
                'folder': service_dir.name,
                'description': description,
                'domain': domain,
                'backup': backup_status,
                'update': update_status,
                'sso': sso_status,
            }
            services_data.append(service_entry)
    
    # Process shared folder for services deployed on this device
    shared_path = REPO_ROOT / "shared"
    if shared_path.exists():
        for service_dir in sorted(shared_path.iterdir()):
            if not service_dir.is_dir():
                continue
            if service_dir.name.startswith('.'):
                continue
            
            compose_file = service_dir / "docker-compose.yml"
            if not compose_file.exists():
                compose_file = service_dir / "docker-compose.yaml"
            if not compose_file.exists():
                continue
            
            compose_data = parse_docker_compose(compose_file)
            services = compose_data.get('services', {})
            
            # Create one row per service in shared folder
            for service_name, service_data in services.items():
                if not isinstance(service_data, dict):
                    continue
                
                annotations = service_data.get('annotations', [])
                
                # Check if this service is deployed on this device
                deployed_on = extract_annotation(annotations, 'deployed_on')
                if not deployed_on:
                    continue
                
                deployed_devices = [d.strip() for d in deployed_on.split(',')]
                if device not in deployed_devices:
                    continue
                
                # Extract metadata from annotations
                description = extract_annotation(annotations, 'description') or "-"
                sso = extract_annotation(annotations, 'sso')
                
                # Get other info
                domain = extract_domain(service_data)
                # For shared services, check the shared folder in backup
                backup_status = get_backup_status(service_dir.name, folder_to_backends)
                update_status = get_watchtower_info(service_data)
                sso_status = "✅" if sso and sso.lower() == "true" else "-"
                
                service_entry = {
                    'name': service_name.replace('-', ' ').replace('_', ' ').title(),
                    'folder': f"shared/{service_dir.name}",
                    'description': description,
                    'domain': domain,
                    'backup': backup_status,
                    'update': update_status,
                    'sso': sso_status,
                }
                services_data.append(service_entry)
    
    return device, services_data


def generate_markdown_table(services: List[Dict]) -> str:
    """Generate a markdown table for the services."""
    if not services:
        return ""
    
    table = "| Name | Description | Domain | Backup | Update | SSO |\n"
    table += "| ---- | ----------- | ------ | ------ | ------ | --- |\n"
    
    for service in services:
        name = service['name']
        description = service['description']
        domain = service['domain']
        if domain != "-" and '$' not in domain:
            domain = f"[{domain}](https://{domain})"
        backup = service['backup']
        update = service['update']
        sso = service['sso']
        
        table += f"| {name} | {description} | {domain} | {backup} | {update} | {sso} |\n"
    
    return table


def generate_tables(devices) -> str:
    """Generate all device tables."""
    tables_content = ""
    
    for device in devices:
        device_path = REPO_ROOT / device
        if not device_path.exists():
            continue
        
        device_title = device.capitalize()
        tables_content += f"### {device_title}\n\n"
        
        device_name, services = process_device(device)
        
        if services:
            table = generate_markdown_table(services)
            tables_content += table
            tables_content += "\n\n"
        else:
            tables_content += "No services configured.\n\n"
    
    return tables_content


def generate_readme(devices: list[str]) -> str:
    """Generate the complete README.md content using template."""
    template_path = REPO_ROOT / "scripts" / "README_TEMPLATE.md"
    
    if not template_path.exists():
        raise FileNotFoundError(f"Template file not found: {template_path}")
    
    # Read template
    with open(template_path, 'r') as f:
        template = f.read()
    
    # Generate tables
    tables = generate_tables(devices)
    
    # Replace placeholder
    readme = template.replace("{{tables}}", tables)
    
    return readme


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate README.md with service tables")
    parser.add_argument('devices', nargs='*', default=[],
                        help=f"List of devices to process")
    args = parser.parse_args()

    readme_content = generate_readme(args.devices)
    output_path = REPO_ROOT / "README.md"
    
    with open(output_path, 'w') as f:
        f.write(readme_content)
    
    print(f"Generated README.md at {output_path}")


if __name__ == '__main__':
    main()
