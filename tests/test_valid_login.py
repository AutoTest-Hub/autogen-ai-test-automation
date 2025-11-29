import pytest
import logging
from playwright.sync_api import Page, expect

def test_valid_login(page):
    logging.info("Navigate to login page")
    page.goto("https://the-internet.herokuapp.com/login")  # Navigate using the provided URL directly as selector is not available
    
    username = "user@example.com"  # Assuming a generic placeholder for username, replace with actual valid one if known beforehand or discoverable via Playwright's capabilities
    password = "validpassword123!"  # Replace this with the actual valid credentials provided by your application context
    
    logging.info("Enter valid username")
    page.fill("#username", username)  # Assuming '#username' is a generic selector for input field, replace if necessary after discovery or use Playwright capabilities to find it dynamically
    
    logging.info("Enter valid password")
    page.fill("#password", password)  # Replace with the actual password placeholder and value as known beforehand or discoverable via Playwright's capabilities
    
    login_button = "input[type='submit']"  # Assuming 'input type="submit"' is used for logging in, replace if necessary after discovery or use Playwright capabilities to find it dynamically
    
    page.click(login_button)
    
    expect(page).to_have_url("https://the-internet.herokuapp.com/dashboard")  # Assuming the dashboard URL is known beforehand, replace with actual expected url after login success or discoverable via Playwright's capabilities