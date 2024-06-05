import os

import requests
from database import Users
from flask import json, jsonify, make_response, request

from . import app, client

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


@app.route("/login/callback")
def oauth_redirect():
    code = request.args.get("code")
    if code:
        google_provider_cfg = get_google_provider_cfg()
        token_endpoint = google_provider_cfg["token_endpoint"]

        token_url, headers, body = client.prepare_token_request(
            token_endpoint,
            authorization_response=request.url,
            redirect_url=request.base_url,
            code=code,
        )
        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),  # type: ignore
        )
        if token_response.status_code != 200:
            response_data = {"status": "failure"}
            response = make_response(response_data)
            return response

        client.parse_request_body_response(json.dumps(token_response.json()))

        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        uri, headers, body = client.add_token(userinfo_endpoint)
        userinfo_response = requests.get(uri, headers=headers, data=body)

        if userinfo_response.json().get("email_verified"):
            unique_id = userinfo_response.json()["sub"]
            users_email = userinfo_response.json()["email"]
            picture = userinfo_response.json()["picture"]
            users_name = userinfo_response.json()["given_name"]
        else:
            response_data = {"status": "failure"}
            response = make_response(response_data)
            return response

        existing_user = Users.get_first(email=users_email)
        if not existing_user:
            new_user = Users(
                email=users_email, name=users_name, picture=picture, uid=unique_id
            )
            new_user.save()

        user = Users.get_first(email=users_email)
        if user:
            auth_token = user.encode_auth_token(user.id)
        else:
            auth_token = None
        if auth_token:
            response_data = {"status": "success"}
            response = make_response(jsonify(response_data), 200)
            response.headers["Authorization"] = auth_token
            response.headers["Access-Control-Expose-Headers"] = "Authorization"
            return response
        else:
            response_data = {"status": "failure"}
            response = make_response(response_data)
            return response
    else:
        response_data = {"status": "failure"}
        response = make_response(response_data)
        return response
