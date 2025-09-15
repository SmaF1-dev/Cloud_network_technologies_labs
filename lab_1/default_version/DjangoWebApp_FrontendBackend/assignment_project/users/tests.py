from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import Customer, Staff

# Create your tests here.

class UserViewsTestCase(TestCase):
    """
    Test case for the UserListView API endpoint.
    """

    def setUp(self):
        """
        Set up the environment for the test by creating test data and initializing the API client.
        """

        # Initialize the API client to simulate HTTP requests in the test
        self.client = APIClient()

        # Define the URL for the user list API endpoint
        self.user_list_url = reverse('api_user_list')

        # Creating test customers
        self.customer1 = Customer.objects.create(customer_id=1, first_name='Blue', last_name='Blue', active=True)
        self.customer2 = Customer.objects.create(customer_id=2, first_name='Green', last_name='Green', active=False)
        
        # Creating test staffs
        self.staff1 = Staff.objects.create(staff_id=1, first_name='Pink', last_name='Pink', active=True)
        self.staff2 = Staff.objects.create(staff_id=2, first_name='Lila', last_name='Lila', active=False)

    def test_user_list_view(self):
        """
        This test sends a GET request to the 'user_list_url' and verifies that the API response contains the correct 'active_users' and 'inactive_users' lists.   

        Asserts:
            - The response status code is HTTP 200 OK.
            - The response contains the keys 'active_users' and 'inactive_users'.
            - The 'active_users' list contains exactly 2 users (1 active customer and 1 active staff).
            - The 'inactive_users' list contains exactly 2 users (1 inactive customer and 1 inactive staff).
        """

        # Send a GET request to the user list endpoint
        response = self.client.get(self.user_list_url)

        # Assert the response status code is 200 (OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Parse the response data
        data = response.json()

        # Assert the response contains active and inactive users
        self.assertIn('active_users', data)
        self.assertIn('inactive_users', data)

        # Assert that the active_users list contains exactly 2 users : 1 customer and 1 staff
        active_users = data['active_users']
        self.assertEqual(len(active_users), 2, "Active users list does not contain exactly 2 users.")
        self.assertTrue(any(user['first_name'] == 'Blue' for user in active_users))  # Active customer
        self.assertTrue(any(user['first_name'] == 'Pink' for user in active_users))  # Active staff

        # Assert that the inactive_users list contains exactly 2 users : 1 customer and 1 staff
        inactive_users = data['inactive_users']
        self.assertEqual(len(inactive_users), 2, "Inactive users list does not contain exactly 2 users.")
        self.assertTrue(any(user['first_name'] == 'Green' for user in inactive_users))  # Inactive customer
        self.assertTrue(any(user['first_name'] == 'Lila' for user in inactive_users))  # Inactive staff
    
class UpdateUserStatusViewTests(TestCase):
    """
    Test case for the UpdateUserStatusView API endpoint.
    """

    def setUp(self):
        """
        Set up the environment for the test by creating test data and initializing the API client.
        """

        self.client = APIClient()
        self.update_status_url = reverse('api_update_status')

        self.customer = Customer.objects.create(customer_id=3, first_name='Red', last_name='Customer', active=True)
        self.staff = Staff.objects.create(staff_id=3, first_name='Yellow', last_name='Staff', active=False)
    
    def test_update_customer_status(self):
        """
        Test case to update the status of an active customer to inactive.

        Asserts:
            - An active customer exists for the update.
            - The PATCH request is processed successfully (status code 200).
            - The customer's status is correctly updated in the database.
        """

        customer = Customer.objects.filter(active=True).first()
        self.assertIsNotNone(customer, "No active customer found for testing.")

        # Prepare the data payload for the PATCH request; updating the customer to set 'active' to False
        data = {
            'id': customer.customer_id,
            'type': 'customer',
            'active': False
        }

        # Send a PATCH request to the update status endpoint with the data
        response = self.client.patch(self.update_status_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Refresh the customer object from the database to get the updated status
        customer.refresh_from_db()

        # Assert the customer's status was updated to inactive (False)
        self.assertFalse(customer.active)

    def test_update_staff_status(self):
        """
        Test case to update the status of an inactive staff to active.

        Asserts:
            - An inactive staff exists for the update.
            - The PATCH request is processed successfully (status code 200).
            - The staff's status is correctly updated in the database.
        """
        
        staff = Staff.objects.filter(active=False).first()
        self.assertIsNotNone(staff, "No inactive staff found for testing.")

        # Prepare the data payload for the PATCH request; updating the staff to set 'active' to True
        data = {
            'id': staff.staff_id,
            'type': 'staff',
            'active': True
        }

        response = self.client.patch(self.update_status_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        staff.refresh_from_db()

        # Assert the staff's status was updated to active (True)
        self.assertTrue(staff.active)

    def test_update_invalid_user_type(self):
        """
        Test case to ensure that an invalid user type results in a 400 Bad Request response.

        Asserts:
            - The response status code is 400 (Bad Request).
        """

        data = {
            'id': 3,
            'type': 'artist',  # Invalid user type, should be 'customer' or 'staff'
            'active': False
        }
        response = self.client.patch(self.update_status_url, data, format='json')

        # Assert that the response status code is 400 (Bad Request), as the user type is invalid
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_invalid_user_id(self):
        """
        Test case to ensure that an invalid user id results in a 404 Not Found response.
        """

        data = {
            'id': 1000,       # invalid user ID, no user exists with ID 1000 in the test database
            'type': 'staff',
            'active': True
        }
        response = self.client.patch(self.update_status_url, data, format='json')
        
        # Assert that the response status code is 404 (Not Found), as the user with ID 1000 does not exist
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class SearchFeatureTestCase(TestCase):
    """
    Test case for the search feature in the UserListView API endpoint.
    """

    def setUp(self):
        """
        Set up the environment for the test by creating test data and initializing the API client.
        """
        self.client = APIClient()
        self.user_list_url = reverse('api_user_list')
        self.customer1 = Customer.objects.create(customer_id=1, first_name='Blue', last_name='Turquoise', active=True)
        self.customer2 = Customer.objects.create(customer_id=2, first_name='Green', last_name='Orange', active=False)
        self.staff1 = Staff.objects.create(staff_id=1, first_name='Lila', last_name='Purple', active=True)
        self.staff2 = Staff.objects.create(staff_id=2, first_name='Red', last_name='White', active=False)
    
    def test_search_by_first_name(self):
        """
        Test the search functionality by first name.

        Sends a GET request with the search term as a first name and verifies:
            - The response status is HTTP 200 OK.
            - Only users with the matching first name are returned.
            - The correct user is included in the active users list.
        """

        # GET request to search for users with first name 'Blue'
        response = self.client.get(self.user_list_url, {'search':'Blue'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        active_users = data['active_users']
        inactive_users = data['inactive_users']
        
        # Assert that exactly one active user is returned
        self.assertEqual(len(active_users), 1)
        # Assert that the returned user's first name is 'Blue'
        self.assertEqual(active_users[0]['first_name'], 'Blue')
        # Assert that no inactive users are returned
        self.assertEqual(len(inactive_users), 0)
    
    def test_search_by_last_name(self):
        """
        Test the search functionality by last name.

        Sends a GET request with the search term as a last name and verifies:
            - The response status is HTTP 200 OK.
            - Only users with the matching last name are returned.
            - The correct user is included in the inactive users list.
        """
        response = self.client.get(self.user_list_url, {'search':'White'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        active_users = data['active_users']
        inactive_users = data['inactive_users']

        self.assertEqual(len(active_users), 0)
        # Assert that exactly one inactive user is returned
        self.assertEqual(len(inactive_users), 1)
        # Assert that the returned user's last name is 'White'
        self.assertEqual(inactive_users[0]['last_name'], 'White')

    def test_search_case_insensivity(self):
        """
        Test that the search functionality is case-insensitive.

        Sends a GET request with a lowercase search term ('red') and verifies:
            - The response status is HTTP 200 OK.
            - The correct user with the name 'Red' (originally capitalized) is returned in the inactive users list.
            - Ensures no active users are incorrectly matched.
        """

        response = self.client.get(self.user_list_url, {'search':'red'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        active_users = data['active_users']
        inactive_users = data['inactive_users']
        self.assertEqual(len(active_users),0)

        # Assert that exactly one inactive user is returned with the name 'Red' even though the search term is 'red' (testing case insensitivity)
        self.assertEqual(len(inactive_users),1)
        self.assertEqual(inactive_users[0]['first_name'], 'Red')
    
    def test_search_partial_match(self):
        """
        Test that the search functionality supports partial matches.

        Sends a GET request with a partial search term ('ur') and verifies:
            - The response status is HTTP 200 OK.
            - Users whose last names contain the partial search term are returned.
            - Confirms that both matching active users are correctly returned.
            - Ensures no inactive users are incorrectly matched.
        """

        response = self.client.get(self.user_list_url, {'search':'ur'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        active_users = data['active_users']
        inactive_users = data['inactive_users']

        # Assert that exactly two active users are returned
        self.assertEqual(len(active_users), 2)
        
        # Assert that the returned users have 'Turquoise' and 'Purple' in their last names
        self.assertEqual(active_users[0]['last_name'], 'Turquoise')
        self.assertEqual(active_users[1]['last_name'], 'Purple')

        self.assertEqual(len(inactive_users), 0)
    

    def test_search_no_results(self):
        """
        Test the search functionality when no users match the search term.

        Sends a GET request with a search term ('Ruby') that doesn't exist in any user data and verifies:
            - The response status is HTTP 200 OK.
            - Both active and inactive user lists are empty, ensuring the search returns no results when there are no matches.
        """
        response = self.client.get(self.user_list_url, {'search':'Ruby'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        active_users = data['active_users']
        inactive_users = data['inactive_users']
        self.assertEqual(len(active_users), 0)
        self.assertEqual(len(inactive_users), 0)