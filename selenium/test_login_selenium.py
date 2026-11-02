"""Selenium end-to-end tests for the login page (success and failure)."""
import threading

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from werkzeug.serving import make_server

from app import app


@pytest.fixture(scope="module")
def base_url(tmp_path_factory):
    """Run the Flask app in a background thread on a free port."""
    app.config.update(DATABASE=str(tmp_path_factory.mktemp("db") / "selenium.db"))
    server = make_server("127.0.0.1", 0, app)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()


@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    drv = webdriver.Chrome(options=options)
    yield drv
    drv.quit()


def login(driver, base_url, username, password):
    driver.get(f"{base_url}/login")
    driver.find_element(By.ID, "username").send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.ID, "login-button").click()


def test_login_success(driver, base_url):
    login(driver, base_url, "admin", "admin123")

    flash = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "flash"))
    )
    assert "Welcome, admin!" in flash.text
    assert driver.find_element(By.ID, "logout").is_displayed()
    assert not driver.current_url.endswith("/login")


def test_login_failure(driver, base_url):
    login(driver, base_url, "admin", "wrong-password")

    error = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "error"))
    )
    assert "Invalid username or password." in error.text
    assert driver.current_url.endswith("/login")
    assert not driver.find_elements(By.ID, "logout")
