import os
import aiohttp
import requests
from dotenv import load_dotenv

from models import UserCredentials


load_dotenv()


def get_tokens(credentials: UserCredentials) -> dict:
    url = f'https://{credentials.subdomain}.amocrm.ru/oauth2/access_token'
    data = {
        'client_id': credentials.client_id,
        'client_secret': credentials.secret_key,
        'grant_type': 'authorization_code',
        'code': credentials.auth_code,
        'redirect_uri': credentials.redirect_url
    }
    response = requests.post(url, data=data)
    return response


def update_access_and_refresh_tokens(credentials: UserCredentials, refresh_token: str):
    url = f'https://{credentials.subdomain}.amocrm.ru/oauth2/access_token'
    data = {
        'client_id': credentials.client_id,
        'client_secret': credentials.secret_key,
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'redirect_uri': credentials.redirect_url
    }
    response = requests.post(url, data=data)
    return response


def get_revenue_by_manager(subdomain: str, access_token: str) -> str:
    url = f'https://{subdomain}.amocrm.ru/api/v4/leads'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url, headers=headers)
    report = dict()
    if response.status_code == 200:
        data = response.json()
        leads = data["_embedded"]["leads"]
        for lead in leads:
            if lead['responsible_user_id'] in report.keys():
                report[lead['responsible_user_id']] += lead['price']
            else:
                report[lead['responsible_user_id']] = lead['price']

        report_str = []
        for key, value in report.items():
            formatted_item = f"ID менеджера: {key}- Выручка: {value}руб."
            report_str.append(formatted_item)

        result_string = '\n'.join(report_str)
        return result_string
    else:
        return response.text
