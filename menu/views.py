import os

import requests
from django.contrib.auth import authenticate, login, logout
from rest_framework.permissions import IsAuthenticated

from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from menu import api_data_config

#Login API
class LoginView(APIView):
    def post(self,request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username :
            return Response({"error": "username is required"}, status= 401)

        if not password :
            return Response({"error": "password is required"}, status=401)

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
class RefreshTokenView(APIView):
    permission_classes = [IsAuthenticated]

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
class ValidateTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        return Response({"response": "valid token"}, status=200)


#Menu API
class MenuView(APIView):
    permission_classes = [IsAuthenticated]

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


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if hasattr(user,'role') and user.role:
            return Response({"response": "welcome to dashboard"}, status=200)
        else:
            return Response({"error": "permission denied"}, status=403)


#Send Message API
class SendMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        payload = request.data

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

        response = requests.post(url, json=payload, headers=headers)
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
    permission_classes = [IsAuthenticated]

    def get(self, request):

        url = f"https://graph.facebook.com/{api_data_config.api_version}/{api_data_config.whatsapp_business_account_id}/message_templates"
        headers = {
            "Authorization": f"Bearer {api_data_config.api_access_token}",
            "Content-Type": "application/json"
        }

        response = requests.get(url,headers=headers)

        if response.status_code == 200:
            data = response.json()

            templates = data.get("data", [])

            templates_table = [ {
                "name": template.get("name"),
                "status": template.get("status"),
                "category": template.get("category")
            } for template in templates]

            return Response({
                "response": "templates retrieved successfully",
                "templates_table": templates_table
                             }, status=200)
        elif response.status_code == 401:
            return Response({"error": "invalid token"},status=401)
        elif response.status_code == 403:
            return Response({"error": "permission denied"}, status=403)
        else:
            return Response({"error": response.json()})

class CreateTemplateView(APIView):
    permission_classes = [IsAuthenticated]
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

        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            return Response({"response": "template created successfully"})
        elif response.status_code == 401:
            return Response({"error": "invalid token"},status=401)
        elif response.status_code == 403:
            return Response({"error": "permission denied"}, status=403)
        else:
            return Response({"error": response.json()}, status=response.status_code)