#!/usr/bin/env python3
"""
Simple script to test requirements JSON files locally
Usage: python test_requirements_locally.py [ecommerce|hrms|banking|all]
"""

import json
import asyncio
import sys
import os
from datetime import datetime

def load_requirements(req_type):
    """Load requirements file based on type"""
    filename = f"requirements_{req_type}.json"
    if not os.path.exists(filename):
        print(f"❌ Requirements file not found: {filename}")
        return None
    
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading {filename}: {e}")
        return None

def analyze_requirements(requirements, req_type):
    """Analyze and display requirements information"""
    print(f"\n🔍 Analyzing {req_type.upper()} Requirements")
    print("=" * 50)
    
    print(f"📱 Application: {requirements.get('app_name', 'N/A')}")
    print(f"🌐 URL: {requirements.get('base_url', 'N/A')}")
    print(f"🏷️  Type: {requirements.get('application_type', 'N/A')}")
    print(f"📋 Description: {requirements.get('description', 'N/A')[:100]}...")
    
    # Priority areas
    priority_areas = requirements.get('priority_areas', [])
    print(f"\n🎯 Priority Areas ({len(priority_areas)}):")
    for area in priority_areas:
        print(f"   • {area}")
    
    # Test scenarios
    test_scenarios = requirements.get('test_scenarios', {})
    print(f"\n🧪 Test Scenarios ({len(test_scenarios)}):")
    for scenario_name, scenario_data in test_scenarios.items():
        priority = scenario_data.get('priority', 'unknown')
        description = scenario_data.get('description', 'No description')
        print(f"   • {scenario_name} [{priority}]: {description[:60]}...")

async def main():
    """Main function"""
    print("🧪 Requirements JSON Testing Tool")
    print("=" * 50)
    
    # Check command line arguments
    if len(sys.argv) != 2:
        print("Usage: python test_requirements_locally.py [ecommerce|hrms|banking|all]")
        print("\nAvailable options:")
        print("  ecommerce - Test e-commerce requirements")
        print("  hrms      - Test HRMS requirements") 
        print("  banking   - Test banking requirements")
        print("  all       - Test all requirements files")
        sys.exit(1)
    
    req_type = sys.argv[1].lower()
    
    # Determine which requirements to test
    if req_type == 'all':
        req_types = ['ecommerce', 'hrms', 'banking']
    elif req_type in ['ecommerce', 'hrms', 'banking']:
        req_types = [req_type]
    else:
        print(f"❌ Invalid requirement type: {req_type}")
        print("Valid options: ecommerce, hrms, banking, all")
        sys.exit(1)
    
    # Test each requirement type
    for req in req_types:
        print(f"\n{'='*60}")
        print(f"Testing {req.upper()} Requirements")
        print(f"{'='*60}")
        
        # Load requirements
        requirements = load_requirements(req)
        if not requirements:
            continue
        
        # Analyze requirements
        analyze_requirements(requirements, req)

if __name__ == "__main__":
    asyncio.run(main())
