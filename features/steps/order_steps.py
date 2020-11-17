"""
Order Steps
Steps file for Order.feature
"""
from os import getenv
import logging
import json
import requests
from behave import *
from compare import expect, ensure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions

WAIT_SECONDS = int(getenv('WAIT_SECONDS', '60'))
ID_PREFIX = 'order_'


@given('the following orders')
def step_impl(context):
    """ Delete all Orders and load new ones """
    headers = {'Content-Type': 'application/json'}
    # list all of the orders and delete them one by one
    context.resp = requests.get(context.base_url + '/orders', headers=headers)
    expect(context.resp.status_code).to_equal(200)
    for order in context.resp.json():
        context.resp = requests.delete(context.base_url + '/orders/' + str(order["id"]), headers=headers)
        expect(context.resp.status_code).to_equal(204)

    # load the database with new orders
    create_url = context.base_url + '/orders'
    for row in context.table:
        items = str(row['order_items']).split('&')
        order_items = []
        for item in items:
            item_details = item.split(',')
            order_items.append({
                "product_id": int(item_details[0]),
                "quantity": int(item_details[1]),
                "price": float(item_details[2]),
                "status": item_details[3]
            })
        data = {
            "customer_id": int(row['customer_id']),
            "order_items": order_items,
        }
        payload = json.dumps(data)
        context.resp = requests.post(create_url, data=payload, headers=headers)
        expect(context.resp.status_code).to_equal(201)


@when('I visit the "home page"')
def step_impl(context):
    """ Make a call to the base URL """
    context.driver.get(context.base_url)


@then('I should see "{message}" in the title')
def step_impl(context, message):
    """ Check the document title for a message """
    expect(context.driver.title).to_contain(message)


@then('I should not see "{message}"')
def step_impl(context, message):
    error_msg = "I should not see '%s' in '%s'" % (message, context.resp.text)
    ensure(message in context.resp.text, False, error_msg)


@when('I set the "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    element_id = ID_PREFIX + element_name.lower()
    element = context.driver.find_element_by_id(element_id)
    element.clear()
    element.send_keys(text_string)


##################################################################
# These two function simulate dropdown behaviors
##################################################################
@when('I select "{text}" in the "{element_name}" dropdown')
def step_impl(context, text, element_name):
    element_id = ID_PREFIX + element_name.lower()
    element = Select(context.driver.find_element_by_id(element_id))
    element.select_by_visible_text(text)


@then('I should see "{text}" in the "{element_name}" dropdown')
def step_impl(context, text, element_name):
    element_id = ID_PREFIX + element_name.lower()
    element = Select(context.driver.find_element_by_id(element_id))
    expect(element.first_selected_option.text).to_equal(text)


@when('I press the "{button}" button')
def step_impl(context, button):
    button_id = button.lower() + '-btn'
    context.driver.find_element_by_id(button_id).click()


@then('I should see order for customer_id "{customer_id}" in the results')
def step_impl(context, customer_id):
    found = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, 'results'),
            customer_id
        )
    )
    expect(found).to_be(True)


@then('I should not see order for customer_id "{customer_id}" in the results')
def step_impl(context, customer_id):
    element = context.driver.find_element_by_id('results')
    error_msg = "I should not see '%s' in '%s'" % (customer_id, element.text)
    ensure(customer_id in element.text, False, error_msg)


@then('the "{element_name}" field should be empty')
def step_impl(context, element_name):
    element_id = ID_PREFIX + element_name.lower()
    element = context.driver.find_element_by_id(element_id)
    expect(element.get_attribute('value')).to_be(u'')


##################################################################
# These two function simulate copy and paste
##################################################################
@when('I copy the "{element_name}" field')
def step_impl(context, element_name):
    element_id = ID_PREFIX + element_name.lower()
    element = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    context.clipboard = element.get_attribute('value')
    logging.info('Clipboard contains: %s', context.clipboard)


@when('I paste the "{element_name}" field')
def step_impl(context, element_name):
    element_id = ID_PREFIX + element_name.lower()
    # element = context.driver.find_element_by_id(element_id)
    element = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(context.clipboard)


@then('I should see "{text_string}" in the "{element_name}" field')
def step_impl(context, text_string, element_name):
    element_id = ID_PREFIX + element_name.lower()
    found = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element_value(
            (By.ID, element_id),
            text_string
        )
    )
    expect(found).to_be(True)


@then('I should see the message "{message}"')
def step_impl(context, message):
    found = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, 'flash_message'),
            message
        )
    )
    expect(found).to_be(True)
