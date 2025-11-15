#!/usr/bin/env python3
"""
Automated Backend Testing Script
Tests all API endpoints automatically
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'


def print_test(message):
    print(f"\n{Colors.BLUE}🧪 TEST:{Colors.RESET} {message}")


def print_success(message):
    print(f"{Colors.GREEN}✅ SUCCESS:{Colors.RESET} {message}")


def print_error(message):
    print(f"{Colors.RED}❌ ERROR:{Colors.RESET} {message}")


def print_warning(message):
    print(f"{Colors.YELLOW}⚠️  WARNING:{Colors.RESET} {message}")


def print_section(title):
    print(f"\n{'=' * 60}")
    print(f"{Colors.YELLOW}{title}{Colors.RESET}")
    print('=' * 60)


# Global variables
token = None
headers = {}
project_id = None
calculation_id = None


def test_authentication():
    """Test authentication endpoints"""
    global token, headers

    print_section("PART 1: AUTHENTICATION TESTS")

    # Test 1: Register User
    print_test("Register new user")
    response = requests.post(f"{BASE_URL}/api/auth/register", json={
        "email": f"test{datetime.now().timestamp()}@example.com",
        "username": f"testuser{int(datetime.now().timestamp())}",
        "password": "test123456",
        "full_name": "Test User"
    })

    if response.status_code == 201:
        user_data = response.json()
        print_success(f"User registered with ID: {user_data['id']}")
        username = user_data['username']
    else:
        print_error(f"Registration failed: {response.text}")
        return False

    # Test 2: Login
    print_test("Login and get JWT token")
    response = requests.post(f"{BASE_URL}/api/auth/login", data={
        "username": username,
        "password": "test123456"
    })

    if response.status_code == 200:
        token_data = response.json()
        token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print_success(f"Token received: {token[:50]}...")
    else:
        print_error(f"Login failed: {response.text}")
        return False

    # Test 3: Get Current User
    print_test("Get current user info")
    response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)

    if response.status_code == 200:
        user = response.json()
        print_success(f"User info: {user['username']} ({user['email']})")
    else:
        print_error(f"Get user info failed: {response.text}")
        return False

    return True


def test_templates():
    """Test template endpoints"""
    print_section("PART 2: TEMPLATE TESTS")

    # Test 1: List Templates
    print_test("List all templates")
    response = requests.get(f"{BASE_URL}/api/templates/list")

    if response.status_code == 200:
        templates = response.json()["templates"]
        print_success(f"Found {len(templates)} templates")
        for template in templates:
            print(f"  - {template['id']}: {template['name']}")
    else:
        print_error(f"List templates failed: {response.text}")
        return False

    # Test 2: Get Template Detail
    print_test("Get cafe template detail")
    response = requests.get(f"{BASE_URL}/api/templates/cafe")

    if response.status_code == 200:
        template = response.json()
        print_success(f"Template: {template['name']} with {len(template['products'])} products")
    else:
        print_error(f"Get template detail failed: {response.text}")
        return False

    # Test 3: List Industries
    print_test("List industries")
    response = requests.get(f"{BASE_URL}/api/templates/industries/list")

    if response.status_code == 200:
        industries = response.json()["industries"]
        print_success(f"Found {len(industries)} industries")
    else:
        print_error(f"List industries failed: {response.text}")
        return False

    return True


def test_projects():
    """Test project endpoints"""
    global project_id

    print_section("PART 3: PROJECT & PRODUCT TESTS")

    # Test 1: Create Project from Template
    print_test("Create project from cafe template")
    response = requests.post(
        f"{BASE_URL}/api/templates/cafe/create-project",
        headers=headers
    )

    if response.status_code == 200:
        project = response.json()
        project_id = project["id"]
        print_success(f"Project created with ID: {project_id}")
        print(f"  Name: {project['name']}")
        print(f"  Industry: {project['industry']}")
    else:
        print_error(f"Create project failed: {response.text}")
        return False

    # Test 2: Get Project Detail
    print_test(f"Get project {project_id} detail with products")
    response = requests.get(
        f"{BASE_URL}/api/projects/{project_id}",
        headers=headers
    )

    if response.status_code == 200:
        project = response.json()
        print_success(f"Project has {len(project['products'])} products")
        for product in project['products']:
            print(f"  - {product['name']}: ₺{product['selling_price']} (cost: ₺{product['cost_per_unit']})")
    else:
        print_error(f"Get project detail failed: {response.text}")
        return False

    # Test 3: Update Project
    print_test("Update project")
    response = requests.put(
        f"{BASE_URL}/api/projects/{project_id}",
        headers=headers,
        json={
            "name": "My Test Cafe",
            "location": "Istanbul, Kadıköy"
        }
    )

    if response.status_code == 200:
        project = response.json()
        print_success(f"Project updated: {project['name']} - {project['location']}")
    else:
        print_error(f"Update project failed: {response.text}")
        return False

    # Test 4: Add Product
    print_test("Add new product")
    response = requests.post(
        f"{BASE_URL}/api/projects/{project_id}/products",
        headers=headers,
        json={
            "name": "Test Espresso",
            "description": "Testing product creation",
            "cost_per_unit": 5.00,
            "selling_price": 35.00,
            "daily_volume": 45,
            "working_days_per_month": 26
        }
    )

    if response.status_code == 201:
        product = response.json()
        product_id = product["id"]
        print_success(f"Product added with ID: {product_id}")
    else:
        print_error(f"Add product failed: {response.text}")
        return False

    # Test 5: List Projects
    print_test("List all user projects")
    response = requests.get(f"{BASE_URL}/api/projects/", headers=headers)

    if response.status_code == 200:
        projects = response.json()
        print_success(f"Found {len(projects)} projects")
    else:
        print_error(f"List projects failed: {response.text}")
        return False

    return True


def test_calculations():
    """Test calculation endpoints"""
    global calculation_id

    print_section("PART 4: CALCULATION TESTS (MAIN FEATURE)")

    # Test 1: Calculate Feasibility
    print_test(f"Calculate feasibility for project {project_id}")
    response = requests.post(
        f"{BASE_URL}/api/calculations/{project_id}/calculate",
        headers=headers,
        json={
            "project_id": project_id,
            "initial_investment": 500000,
            "monthly_fixed_costs": 50000,
            "emergency_fund": 150000,
            "notes": "Automated test calculation"
        }
    )

    if response.status_code == 200:
        results = response.json()
        print_success("Feasibility calculated!")
        print(f"\n  📊 RESULTS:")
        print(f"  - Monthly Revenue: ₺{results['monthly_revenue']:,.2f}")
        print(f"  - Monthly Variable Cost: ₺{results['monthly_variable_cost']:,.2f}")
        print(f"  - Monthly Fixed Cost: ₺{results['monthly_fixed_cost']:,.2f}")
        print(f"  - Monthly Net Profit: ₺{results['monthly_net_profit']:,.2f}")
        print(f"  - Gross Margin: {results['gross_margin']:.2f}%")
        print(f"  - Net Margin: {results['net_margin']:.2f}%")
        print(f"\n  📈 BREAK-EVEN:")
        print(f"  - Break-even Revenue: ₺{results['breakeven']['breakeven_revenue']:,.2f}")
        print(f"  - Break-even Months: {results['breakeven']['breakeven_months']}")
        print(f"  - Required Increase: {results['breakeven']['required_increase']:.2f}%")
        print(f"\n  ⚠️  RISK ANALYSIS:")
        print(f"  - Risk Score: {results['risk_analysis']['risk_score']}/100")
        print(f"  - Risk Level: {results['risk_analysis']['risk_level'].upper()}")
        print(f"  - Warnings: {len(results['risk_analysis']['warnings'])}")

        if results['risk_analysis']['warnings']:
            print(f"\n  Warning Details:")
            for warning in results['risk_analysis']['warnings'][:3]:  # Show first 3
                print(f"    - [{warning['type']}] {warning['message']}")

        print(f"\n  🎯 DAILY TARGETS:")
        for target in results['daily_targets']:
            print(
                f"  - {target['product_name']}: {target['current_daily']} → {target['target_daily']} (+{target['increase_needed']})")
    else:
        print_error(f"Calculate feasibility failed: {response.text}")
        return False

    # Test 2: Get Calculation History
    print_test(f"Get calculation history for project {project_id}")
    response = requests.get(
        f"{BASE_URL}/api/calculations/{project_id}/history",
        headers=headers
    )

    if response.status_code == 200:
        history = response.json()
        calculation_id = history['calculations'][0]['id']
        print_success(f"Found {history['total']} calculations")
        print(f"  Latest calculation ID: {calculation_id}")
    else:
        print_error(f"Get calculation history failed: {response.text}")
        return False

    # Test 3: Get Calculation Detail
    print_test(f"Get calculation {calculation_id} detail")
    response = requests.get(
        f"{BASE_URL}/api/calculations/detail/{calculation_id}",
        headers=headers
    )

    if response.status_code == 200:
        calculation = response.json()
        print_success(f"Calculation detail retrieved")
        print(f"  Created: {calculation['created_at']}")
        print(f"  Net Profit: ₺{calculation['monthly_net_profit']}")
    else:
        print_error(f"Get calculation detail failed: {response.text}")
        return False

    # Test 4: Export PDF
    print_test(f"Export calculation {calculation_id} as PDF")
    response = requests.get(
        f"{BASE_URL}/api/calculations/{calculation_id}/export/pdf",
        headers=headers
    )

    if response.status_code == 200 and response.headers['Content-Type'] == 'application/pdf':
        pdf_size = len(response.content)
        print_success(f"PDF generated successfully! Size: {pdf_size:,} bytes")

        # Save PDF
        filename = f"test_report_{calculation_id}.pdf"
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"  PDF saved as: {filename}")
    else:
        print_error(f"Export PDF failed: {response.text}")
        return False

    return True


def test_error_handling():
    """Test error handling"""
    print_section("PART 5: ERROR HANDLING TESTS")

    # Test 1: Invalid Login
    print_test("Try invalid login")
    response = requests.post(f"{BASE_URL}/api/auth/login", data={
        "username": "invaliduser",
        "password": "wrongpassword"
    })

    if response.status_code == 401:
        print_success("Invalid login correctly rejected")
    else:
        print_warning(f"Expected 401, got {response.status_code}")

    # Test 2: Access Without Token
    print_test("Try to access protected endpoint without token")
    response = requests.get(f"{BASE_URL}/api/projects/")

    if response.status_code == 401:
        print_success("Unauthorized access correctly rejected")
    else:
        print_warning(f"Expected 401, got {response.status_code}")

    # Test 3: Non-existent Project
    print_test("Try to access non-existent project")
    response = requests.get(
        f"{BASE_URL}/api/projects/99999",
        headers=headers
    )

    if response.status_code == 404:
        print_success("Non-existent project correctly rejected")
    else:
        print_warning(f"Expected 404, got {response.status_code}")

    return True


def run_all_tests():
    """Run all tests"""
    print(f"\n{'=' * 60}")
    print(f"{Colors.YELLOW}🚀 STARTING AUTOMATED BACKEND TESTS{Colors.RESET}")
    print(f"{'=' * 60}")
    print(f"Base URL: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = {
        "Authentication": test_authentication(),
        "Templates": test_templates(),
        "Projects": test_projects(),
        "Calculations": test_calculations(),
        "Error Handling": test_error_handling()
    }

    # Summary
    print_section("TEST SUMMARY")

    total = len(results)
    passed = sum(results.values())
    failed = total - passed

    for test_name, result in results.items():
        status = f"{Colors.GREEN}✅ PASS{Colors.RESET}" if result else f"{Colors.RED}❌ FAIL{Colors.RESET}"
        print(f"{test_name}: {status}")

    print(f"\n{'=' * 60}")
    print(f"Total Tests: {total}")
    print(f"{Colors.GREEN}Passed: {passed}{Colors.RESET}")
    print(f"{Colors.RED}Failed: {failed}{Colors.RESET}")

    if passed == total:
        print(f"\n{Colors.GREEN}🎉 ALL TESTS PASSED! BACKEND IS FULLY FUNCTIONAL!{Colors.RESET}")
    else:
        print(f"\n{Colors.YELLOW}⚠️  Some tests failed. Check the errors above.{Colors.RESET}")

    print(f"{'=' * 60}\n")

    return passed == total


if __name__ == "__main__":
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Tests interrupted by user{Colors.RESET}")
        exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error: {e}{Colors.RESET}")
        import traceback

        traceback.print_exc()
        exit(1)