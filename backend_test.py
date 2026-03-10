import requests
import sys
import json
import os
from datetime import datetime
from pathlib import Path

class WoodTechAPITester:
    def __init__(self):
        # Use the public endpoint from frontend .env
        self.base_url = "https://sheet-site-builder.preview.emergentagent.com/api"
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.user_data = None
        self.conference_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                if files:
                    response = requests.post(url, data=data, files=files, headers=headers)
                else:
                    headers['Content-Type'] = 'application/json'
                    response = requests.post(url, json=data, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                
                # Try to parse response
                try:
                    response_data = response.json()
                    print(f"   Response keys: {list(response_data.keys()) if isinstance(response_data, dict) else type(response_data)}")
                    return success, response_data
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error text: {response.text}")

            return success, response.json() if success else {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_user_registration(self):
        """Test user registration"""
        timestamp = datetime.now().strftime('%H%M%S')
        user_data = {
            "email": f"testuser_{timestamp}@example.com",
            "password": "TestPass123!",
            "name": f"Test User {timestamp}",
            "role": "user"
        }
        
        success, response = self.run_test(
            "User Registration",
            "POST",
            "auth/register",
            200,
            data=user_data
        )
        
        if success:
            self.user_data = user_data
            print(f"   User registered with ID: {response.get('id')}")
            return True
        return False

    def test_user_login(self):
        """Test user login"""
        if not self.user_data:
            print("❌ Cannot test login - no user registered")
            return False

        login_data = {
            "email": self.user_data["email"],
            "password": self.user_data["password"]
        }
        
        success, response = self.run_test(
            "User Login",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            print(f"   Login successful, token acquired")
            return True
        return False

    def test_get_me(self):
        """Test get current user info"""
        if not self.token:
            print("❌ Cannot test /auth/me - no token")
            return False

        success, response = self.run_test(
            "Get User Info",
            "GET",
            "auth/me",
            200
        )
        
        if success:
            print(f"   User info: {response.get('name')} ({response.get('email')})")
        return success

    def create_test_excel_files(self):
        """Create minimal test Excel files"""
        import pandas as pd
        import tempfile
        
        # Create temporary directory for test files
        temp_dir = Path("/tmp/test_excel_files")
        temp_dir.mkdir(exist_ok=True)
        
        # Log2 test data
        log2_data = {
            'Número de carga': ['TEST001', 'TEST002', 'TEST003'],
            'Volume Sólido': [100.5, 200.3, 150.7],
            'Data': ['01/01/2026', '02/01/2026', '03/01/2026']
        }
        log2_df = pd.DataFrame(log2_data)
        log2_path = temp_dir / "test_log2.xlsx"
        
        # Create Excel with header in row 2 (index 1)
        with pd.ExcelWriter(log2_path, engine='openpyxl') as writer:
            # Write empty first row
            pd.DataFrame([[''] * len(log2_data.keys())]).to_excel(writer, index=False, header=False)
            # Write data starting from row 2
            log2_df.to_excel(writer, index=False, startrow=1)
        
        # Log3 test data
        log3_data = {
            'ID Cliente': ['TEST001', 'TEST002', 'TEST004'],
            'Peso': [99.8, 201.1, 149.9],
            'Data Carregamento': ['01/01/2026', '02/01/2026', '04/01/2026']
        }
        log3_df = pd.DataFrame(log3_data)
        log3_path = temp_dir / "test_log3.xlsx"
        
        with pd.ExcelWriter(log3_path, engine='openpyxl') as writer:
            pd.DataFrame([[''] * len(log3_data.keys())]).to_excel(writer, index=False, header=False)
            log3_df.to_excel(writer, index=False, startrow=1)
        
        # Cubo 160 test data
        cubo_data = {
            'Serie': ['TEST', 'TEST', 'TEST'],
            'Guia CEM': ['001', '002', '005'],
            'Peso Liquido': [100.2, 200.5, 148.3],
            'Data Criacao': ['01/01/2026', '02/01/2026', '05/01/2026']
        }
        cubo_df = pd.DataFrame(cubo_data)
        cubo_path = temp_dir / "test_cubo160.xlsx"
        
        with pd.ExcelWriter(cubo_path, engine='openpyxl') as writer:
            pd.DataFrame([[''] * len(cubo_data.keys())]).to_excel(writer, index=False, header=False)
            cubo_df.to_excel(writer, index=False, startrow=1)
        
        print(f"   Created test files in {temp_dir}")
        return str(log2_path), str(log3_path), str(cubo_path)

    def test_create_conference(self):
        """Test conference creation with file uploads"""
        if not self.token:
            print("❌ Cannot test conference creation - no token")
            return False

        try:
            # Create test Excel files
            log2_path, log3_path, cubo_path = self.create_test_excel_files()
            
            # Prepare form data and files
            form_data = {
                'name': f'Test Conference {datetime.now().strftime("%H:%M:%S")}',
                'description': 'Automated test conference'
            }
            
            files_data = {
                'log2_file': ('test_log2.xlsx', open(log2_path, 'rb'), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                'log3_file': ('test_log3.xlsx', open(log3_path, 'rb'), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                'cubo_file': ('test_cubo160.xlsx', open(cubo_path, 'rb'), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            }
            
            success, response = self.run_test(
                "Create Conference",
                "POST",
                "conferences",
                200,
                data=form_data,
                files=files_data
            )
            
            # Close files
            for file_obj in files_data.values():
                file_obj[1].close()
            
            if success and 'id' in response:
                self.conference_id = response['id']
                print(f"   Conference created with ID: {self.conference_id}")
                print(f"   Status: {response.get('status')}")
                print(f"   Total records: {response.get('total_records')}")
                print(f"   Matches: {response.get('matches')}")
                print(f"   Divergences: {response.get('divergences')}")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Conference creation failed with error: {e}")
            return False

    def test_get_conferences(self):
        """Test getting all conferences"""
        if not self.token:
            print("❌ Cannot test get conferences - no token")
            return False

        success, response = self.run_test(
            "Get All Conferences",
            "GET",
            "conferences",
            200
        )
        
        if success:
            print(f"   Found {len(response)} conferences")
            if len(response) > 0:
                print(f"   Latest conference: {response[0].get('name')}")
        return success

    def test_get_conference_detail(self):
        """Test getting conference details"""
        if not self.token or not self.conference_id:
            print("❌ Cannot test conference detail - no token or conference ID")
            return False

        success, response = self.run_test(
            "Get Conference Detail",
            "GET",
            f"conferences/{self.conference_id}",
            200
        )
        
        if success:
            print(f"   Conference: {response.get('name')}")
            print(f"   Status: {response.get('status')}")
            print(f"   Total records: {response.get('total_records')}")
        return success

    def test_get_conference_results(self):
        """Test getting conference validation results"""
        if not self.token or not self.conference_id:
            print("❌ Cannot test conference results - no token or conference ID")
            return False

        success, response = self.run_test(
            "Get Conference Results",
            "GET",
            f"conferences/{self.conference_id}/results",
            200
        )
        
        if success:
            print(f"   Found {len(response)} validation results")
            if len(response) > 0:
                print(f"   First result status: {response[0].get('status')}")
        return success

    def test_get_conference_results_filtered(self):
        """Test getting filtered conference results"""
        if not self.token or not self.conference_id:
            print("❌ Cannot test filtered results - no token or conference ID")
            return False

        success, response = self.run_test(
            "Get Conference Results (Match Filter)",
            "GET",
            f"conferences/{self.conference_id}/results?status_filter=match",
            200
        )
        
        if success:
            print(f"   Found {len(response)} match results")
        return success

    def test_dashboard_stats(self):
        """Test dashboard statistics"""
        if not self.token:
            print("❌ Cannot test dashboard stats - no token")
            return False

        success, response = self.run_test(
            "Get Dashboard Stats",
            "GET",
            "dashboard/stats",
            200
        )
        
        if success:
            print(f"   Total conferences: {response.get('total_conferences')}")
            print(f"   Total records processed: {response.get('total_records_processed')}")
            print(f"   Divergence rate: {response.get('divergence_rate')}%")
        return success

def main():
    print("🚀 Starting WoodTech API Tests...")
    print("=" * 50)
    
    tester = WoodTechAPITester()
    
    # Test sequence
    tests = [
        tester.test_user_registration,
        tester.test_user_login,
        tester.test_get_me,
        tester.test_create_conference,
        tester.test_get_conferences,
        tester.test_get_conference_detail,
        tester.test_get_conference_results,
        tester.test_get_conference_results_filtered,
        tester.test_dashboard_stats
    ]
    
    for test in tests:
        test()
    
    print("\n" + "=" * 50)
    print(f"📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    
    success_rate = (tester.tests_passed / tester.tests_run) * 100 if tester.tests_run > 0 else 0
    print(f"📈 Success rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("✅ Backend API tests mostly successful!")
        return 0
    else:
        print("❌ Backend API tests have significant failures!")
        return 1

if __name__ == "__main__":
    sys.exit(main())