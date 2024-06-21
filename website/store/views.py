from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.urls import reverse

from django.http import FileResponse, Http404
from django.http import JsonResponse
from django.http import HttpResponse

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test

from django.views.generic.edit import CreateView
from django.views.generic import View


from django.core.paginator import Paginator
from django import template

import os
import csv
import io
from io import BytesIO
import socket
import uuid

import urllib.request
from django.core.files.base import ContentFile

from django.db.models import Q

from django.utils import timezone  # Import Django's timezone module

import json

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



from PIL import Image
import openai
import requests

from django.views.decorators.csrf import csrf_exempt
from django.template.context_processors import csrf
from lxml import html
import pandas as pd


from datetime import datetime
from django.utils.dateparse import parse_datetime

from django.core.serializers import serialize

register = template.Library()
import time 
import re
import os

def get_wallet_balance(request):
    solana_rpc_key = os.getenv('SOLANA_RPC_KEY')
    rpc_url = f"https://weathered-long-wind.solana-mainnet.quiknode.pro/{solana_rpc_key}/"

    wallet_address = request.GET.get('wallet_address', '')
    # Initialize a Solana RPC client
    # Define RPC server details
    
    # Wallet address for which you want to check the balance
    wallet_address = wallet_address

    # JSON-RPC request payload to get balance
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getBalance",
        "params": [wallet_address]
    }

    # Make the request
    try:
        response = requests.post(rpc_url, json=payload)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()
        balance = data["result"]["value"]
        print("Balance:", balance)
        sol_balance = balance / 10**9    

        if sol_balance is not None:
            print(f"Number of Bundled Transactions: {sol_balance}")
            return JsonResponse({'number_of_transactions': sol_balance})
        else:
            print("Unable to extract number of bundled transactions.")
            return JsonResponse({'number_of_transactions': None})

    except requests.exceptions.RequestException as e:
        print("Error:", e)

def extract_number_from_page_source(page_source):
    """
    Extracts the number of bundled transactions from the page source.
    Example page source: "Bundled Transactions: 0"
    """
    try:
        # Use regex to find "Bundled Transactions: <number>"
        match = re.search(r'Bundled Transactions:\s*(\d+)', page_source)
        if match:
            number_of_transactions = int(match.group(1))
            return number_of_transactions
        else:
            return None
    except Exception as e:
        # Handle any errors gracefully
        print(f"Exception occurred: {e}")
        return None

def bundlecheckerview(request):
    ca_address = request.GET.get('ca_address', '')

    options = webdriver.ChromeOptions()
    options.binary_location = '/usr/bin/google-chrome'  # Specify Chrome binary location if needed
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    try:
        driver = webdriver.Chrome(options=options)
        
        driver.get("https://pumpv2.fun/bundleChecker")
        time.sleep(3)  # Adjust as needed

        input_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Pump Fun Token Address']"))
        )
        input_element.click()
        input_element.clear()
        input_element.send_keys(ca_address)
        input_element.submit()

        # Wait for the page to load completely (adjust wait time as needed)
        time.sleep(12)

        # Extract the page source after waiting
        page_source = driver.page_source

        # Extract number of transactions
        number_of_transactions = extract_number_from_page_source(page_source)

        if number_of_transactions is not None:
            print(f"Number of Bundled Transactions: {number_of_transactions}")
            return JsonResponse({'number_of_transactions': number_of_transactions})
        else:
            print("Unable to extract number of bundled transactions.")
            return JsonResponse({'number_of_transactions': None})


    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

    finally:
        if driver is not None:
            driver.quit()



