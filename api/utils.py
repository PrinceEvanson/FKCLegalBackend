import base64
from datetime import datetime, timezone, timedelta
import requests
from django.conf import settings


def get_mpesa_access_token():
    consumer_key = str(settings.MPESA_CONSUMER_KEY).strip()
    consumer_secret = str(settings.MPESA_CONSUMER_SECRET).strip()
    api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    r = requests.get(api_URL, auth=(consumer_key, consumer_secret))
    return r.json().get('access_token')


def initiate_stk_push(phone_number, amount, account_reference, description):
    access_token = get_mpesa_access_token()
    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

    eat_tz = timezone(timedelta(hours=3))
    timestamp = datetime.now(eat_tz).strftime('%Y%m%d%H%M%S')

    business_shortcode = str(settings.MPESA_SHORTCODE).strip()
    passkey = str(settings.MPESA_PASSKEY).strip()

    data_to_encode = f"{business_shortcode}{passkey}{timestamp}"
    password = base64.b64encode(data_to_encode.encode()).decode('utf-8')

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "BusinessShortCode": business_shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": str(amount),
        "PartyA": phone_number,
        "PartyB": business_shortcode,
        "PhoneNumber": phone_number,
        "CallBackURL": str(settings.MPESA_CALLBACK_URL).strip(),
        "AccountReference": account_reference,
        "TransactionDesc": description
    }

    print(
        f"DEBUG M-Pesa -> Timestamp: {timestamp} | Shortcode: {business_shortcode}")

    response = requests.post(api_url, json=payload, headers=headers)
    return response.json()
