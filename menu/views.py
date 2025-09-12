import os
import json

import requests
from django.contrib.auth import authenticate, login, logout
from requests.auth import HTTPBasicAuth
from rest_framework.permissions import IsAuthenticated

from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from menu import api_data_config
from menu.notifications import send_message_to_teams
from menu.api_data_config import notification_url

#creating private class for authentication
class PrivateView(APIView):
    permission_classes = [IsAuthenticated]

#Login API
class LoginView(APIView):
    def post(self,request):
        try:
            username = request.data.get("username")
            password = request.data.get("password")

            if not username :
                return Response({"error": "username is required"}, status= 401)

            if not password :
                return Response({"error": "password is required"}, status=401)

            if username == "buguser":
                raise Exception

            user = authenticate(username=username, password=password)

            if user is not None:
                login(request,user)
                refresh = RefreshToken.for_user(user)
                return Response({
                    "response": "login successful",
                    "token": str(refresh.access_token),
                    "refresh": str(refresh)
                }, status=200)
            return Response({"error": "No user found"},status= 401)
        except Exception as e:
            print(f"Error:{e}")
            msg = "something went wrong while logging in"
            send_message_to_teams(notification_url, msg)

#logout API

class LogoutView(APIView):

    def post(self,request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()  # invalidating the existing token
            logout(request)
            return Response({"response": "logout successful"}, status=200)
        except Exception as e:
            print("logout error:", str(e))
            return Response({"error": "invalid token"}, status=401)


#Refresh Token API
class RefreshTokenView(PrivateView):

    def post(self,request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response({"error": "token is missing"},status=401)

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            return Response({"access_token": access_token},status=200)

        except TokenError:
            return Response({"error":"invalid token"}, status=401)


# Token Validation API
class ValidateTokenView(PrivateView):

    def get(self,request):
        return Response({"response": "valid token"}, status=200)


#Menu API
class MenuView(PrivateView):

    def get(self,request):
        user = request.user

        if hasattr(user,'role') and user.role:
            if user.role == "admin":
                permissions = [
                    "user profile settings",
                    "send message",
                    "template list",
                    "create template",
                    "reports"
                ]
            else:
                permissions = [
                    "send message",
                    "template list",
                    "create template",
                    "reports"
                ]
        else:
            return Response({"error": "permission denied"}, status=403)
        return Response({"permissions": permissions},status=200)


class DashboardView(PrivateView):

    def get(self, request):
        user = request.user

        if hasattr(user,'role') and user.role:
            return Response({"response": "welcome to dashboard"}, status=200)
        else:
            return Response({"error": "permission denied"}, status=403)


#Send Message API
class SendMessageView(PrivateView):

    def post(self, request):
        payload = request.data

        print(json.dumps(payload, indent=2))

        to = payload.get("to")
        template = payload.get("template")
        components = template.get("components") if template else None
        language = template.get("language") if template else None

        if not to:
            return Response({"error": "invalid or incorrect phone number"}, status=400)
        if not template or not template.get("name"):
            return Response({"error": "invalid template name"}, status=400)
        if not language or not language.get("code"):
            return Response({"error": "unsupported language format"}, status=400)
        if not components:
            return Response({"error": "invalid message components"}, status=400)

        if components:
            header = next((component for component in components if component.get("type") == "header"), None)
            body = next((component for component in components if component.get("type") == "body"), None)

            if not header or not header.get("parameters"):
                return Response({"error": "invalid header params"}, status=400)
            if not body or not body.get("parameters"):
                return Response({"error": "invalid body params"}, status=400)

            footer = next((comp for comp in components if comp.get("type") == "footer"), None)
            if footer and not footer.get("parameters"):
                return Response({"error": "invalid footer params"}, status=400)

        url = f"https://graph.facebook.com/{api_data_config.api_version}/{api_data_config.phone_number_id}/messages"

        headers = {
            "Authorization": f"Bearer {api_data_config.api_access_token}",
            "Content-Type": "application/json"
        }

        response = requests.post(url, headers=headers, json=payload)
        print(response.json())
        if response.status_code == 200:
            return Response({"response": "message sent successfully"}, status=200)
        elif response.status_code == 401:
            return Response({"error": "invalid token"}, status=401)
        elif response.status_code == 403:
            return Response({"error": "permission denied"}, status=403)
        else:
            return Response({"error": response.json()})


# Template list API
class TemplatesListView(APIView):

    def get(self, request):

        url = f"https://graph.facebook.com/{api_data_config.api_version}/{api_data_config.whatsapp_business_account_id}/message_templates"
        headers = {
            "Authorization": f"Bearer {api_data_config.api_access_token}",
            "Content-Type": "application/json"
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()

            return Response({"templates": data}, status=200)
        elif response.status_code == 401:
            return Response({"error": "invalid token"},status=401)
        elif response.status_code == 403:
            return Response({"error": "permission denied"}, status=403)
        else:
            return Response({"error": response.json()})

class CreateTemplateView(PrivateView):

    def media_upload_session(self, media_file_type):
        try:
            file_length = os.path.getsize(api_data_config.media_file_name)

        except FileNotFoundError:
            return Response({"error": "invalid filename"},status=400)

        url = (
               f"https://graph.facebook.com/{api_data_config.api_version}/{api_data_config.app_id}/uploads"
               f"?file_name={api_data_config.media_file_name}"
               f"&file_length={file_length}"
               f"&file_type={media_file_type}"
               f"&access_token={api_data_config.api_access_token}"
               )
        headers = {
            "Authorization": f"Bearer {api_data_config.api_access_token}"
        }

        response = requests.post(url, headers=headers)
        if response.status_code != 200:
            return Response({"error": "media upload failed"},status = response.status_code)
        return response.json().get("id")

    def fetch_header_handle(self, session_id):
        url = f"https://graph.facebook.com/{api_data_config.api_version}/{session_id}"
        headers = {
            "Authorization": f"Bearer {api_data_config.api_access_token}",
            "file_offset": "0"
        }
        response = requests.post(url, headers=headers)
        if response.status_code != 200:
            return Response({"error": "header handle fetch failed"}, status = response.status_code)
        return response.json().get("h")


    def post(self, request):
        data = request.data

        #validating required fields
        required_fields = ["name", "category", "language", "components"]
        for field in required_fields:
            if field not in data:
                return Response({"error": f"invalid {field}"},status=400)

        #fetching media type from request body
        components = data.get("components")
        for component in components:
            if component["type"] == "HEADER" and component["format"] in ["IMAGE", "VIDEO", "DOCUMENT"]:
                media_file_type = component["format"]

                session_id = self.media_upload_session(media_file_type)
                header_handle = self.fetch_header_handle(session_id)

                component["example"] = {"header_handle": [header_handle]}

        url = f"https://graph.facebook.com/{api_data_config.api_version}/{api_data_config.whatsapp_business_account_id}/message_templates"
        headers = {
            "Authorization": f"Bearer {api_data_config.api_access_token}",
            "Content-Type": "application/json"
        }

        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return Response({"response": "template created successfully"})
        elif response.status_code == 401:
            return Response({"error": "invalid token"},status=401)
        elif response.status_code == 403:
            return Response({"error": "permission denied"}, status=403)
        else:
            return Response({"error": response.json()}, status=response.status_code)

# Templates Report API
class TemplatesReportView(APIView):
    def get(self, request):
        url = (f"https://graph.facebook.com/{api_data_config.api_version}/{api_data_config.whatsapp_business_account_id}"
               f"?fields=analytics"
               f".start(1696118400)" # UNIX TimeStamp
               f".end(1698796800)" # UNIX TimeStamp
               f".granularity(DAY)"
               f".dimensions([CONVERSATION_CATEGORY, CONVERSATION_TYPE, COUNTRY, PHONE])"
               f"&access_token={api_data_config.api_access_token}")

        response = requests.get(url)
        print(response.json())
        return Response({"response": response.json()})

# Creation of flow template
class CreateFlowTemplateView(APIView):
    def payload(self):
        flow_json = {
            "version": "5.0",
            "screens": [
                {
                    "id": "COUNTRY_SCREEN",
                    "terminal": True,
                    "title": "Select Your Country",
                    "layout": {
                        "type": "SingleColumnLayout",
                        "children": [
                            {
                                "type": "Dropdown",
                                "label": "Choose a country",
                                "name": "country",
                                "data-source": [
                                    {"id": "1", "title": "India", "description": "india"},
                                    {"id": "2", "title": "United State of America", "description": "usa"},
                                    {"id": "3", "title": "Canada", "description": "canada"},
                                    {"id": "4", "title": "United Kingdom", "description": "uk"}
                                ]
                            },
                            {
                                "type": "Footer",
                                "label": "Next",
                                "on-click-action": {
                                    "name": "navigate",
                                    "next": {
                                        "type": "screen",
                                        "name": "STATE_SCREEN"
                                    },
                                    "payload": {}
                                }
                            }
                        ]
                    }
                },
                {
                    "id": "STATE_SCREEN",
                    "terminal": True,
                    "title": "state screen",
                    "layout": {
                        "type": "SingleColumnLayout",
                        "children": [
                            {
                                "type": "Dropdown",
                                "label": "choose a state",
                                "name": "state",
                                "data-source": [
                                    {"id": "1", "title": "Telangana", "description": "TS"},
                                    {"id": "2", "title": "Karnataka", "description": "KA"},
                                    {"id": "3", "title": "Maharashtra", "description": "MH"},
                                    {"id": "4", "title": "Tamil Nadu", "description": "TN"}
                                ]
                            },
                            {
                                "type": "Footer",
                                "label": "Next",
                                "on-click-action": {
                                    "name": "navigate",
                                    "next": {
                                        "type": "screen",
                                        "name": "CITY_SCREEN"
                                    },
                                    "payload": {}
                                }
                            }
                        ]
                    }
                },
                {
                    "id": "CITY_SCREEN",
                    "terminal": True,
                    "title": "Select Your City",
                    "layout": {
                        "type": "SingleColumnLayout",
                        "children": [
                            {
                                "type": "Dropdown",
                                "label": "Choose a city",
                                "name": "city",
                                "data-source": [
                                    {"id": "1", "title": "Hyderabad", "description": "HYD"},
                                    {"id": "2", "title": "Bangalore", "description": "BAN"},
                                    {"id": "3", "title": "Mumbai", "description": "MUM"},
                                    {"id": "4", "title": "Chennai", "description": "CHN"}
                                ]
                            },
                            {
                                "type": "Footer",
                                "label": "Next",
                                "on-click-action": {
                                    "name": "complete",
                                    "payload": {}
                                }
                            }
                        ]
                    }
                }

            ]
        }
        return {
            "name": "location_flow",
            "language": "en_US",
            "category": "UTILITY",
            "components": [
                {
                    "type": "BODY",
                    "text": "please select your locality from the below options",
                },
                {
                    "type": "BUTTONS",
                    "buttons": [
                        {
                            "type": "FLOW",
                            "text": "select location flow",
                            "flow_json": json.dumps(flow_json)
                        }
                    ]
                }
            ]
        }

    def post(self, request):
        # flow template url
        base_url = f"https://graph.facebook.com/v16.0/{api_data_config.whatsapp_business_account_id}/message_templates"
        headers = {
            "Authorization": f"Bearer {api_data_config.api_access_token}",
            "Content-Type": "application/json"
        }
        _json = self.payload()
        response = requests.post(base_url, headers=headers, json=_json)
        return Response({"response_data": response.json()})

class SendFlowTemplateView(APIView):
    def payload(self):
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": "+919391528446",
            "type": "template",
            "template": {
                "name": "location_flow",
                "language": {
                    "code": "en_US"
                },
                "components": [
                    {
                        "type": "button",
                        "sub_type": "flow",
                        "index": "0",
                        "parameters": [
                            {
                                "type": "action",
                                "action": {
                                    "flow_token":  "1890417281903687"
                                }
                            }
                        ]
                    }
                ]
            }
        }

    def post (self,request):
        base_url = f"https://graph.facebook.com/v16.0/{api_data_config.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {api_data_config.api_access_token}",
            "Content-Type": "application/json"
        }
        _json = self.payload()
        response = requests.post(base_url, headers=headers, json= _json)
        return Response({"response": response.json()})