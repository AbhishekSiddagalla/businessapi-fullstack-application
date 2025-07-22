import requests
from django.contrib.auth import authenticate, login, logout
from rest_framework.permissions import IsAuthenticated

from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from menu import api_data

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
            # login(request,user)
            refresh = RefreshToken.for_user(user)
            return Response({
                "response": "login successful",
                "token": str(refresh.access_token)
            }, status=200)
        return Response({"error": "No user found"},status= 401)

#logout API
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        logout(request)


#Refresh Token API
class RefreshTokenView(APIView):
    def post(self,request):
        refresh_token = request.data
        print(refresh_token)

        if not refresh_token:
            return Response({"error": "token is missing"},status=401)

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            return Response({"access_token": access_token},status=200)

        except TokenError:
            return Response({"error":"invalid token"}, status=401)


#Menu API
class MenuView(APIView):
    # permission_classes = [IsAuthenticated]

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

    def get(self, request):
        user = request.user

        if not user :
            return Response({"error": "invalid token"}, status=401)

        if hasattr(user,'role') and user.role:
            return Response({"response": "welcome to dashboard"}, status=200)
        else:
            return Response({"error": "permission denied"}, status=403)


#Send Message API
class SendMessageView(APIView):
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

        header = next((comp for comp in components if comp.get("type") == "header"), None)
        body = next((comp for comp in components if comp.get("type") == "body"), None)

        if not header or not header.get("parameters"):
            return Response({"error": "invalid header params"}, status=400)
        if not body or not body.get("parameters"):
            return Response({"error": "invalid body params"}, status=400)

        footer = next((comp for comp in components if comp.get("type") == "footer"), None)
        if footer and not footer.get("parameters"):
            return Response({"error": "invalid footer params"}, status=400)

        url = f"https://graph.facebook.com/{api_data.api_version}/{api_data.phone_number_id}/messages"

        headers = {
            "Authorization": f"Bearer {api_data.api_access_token}",
            "Content-Type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return Response({"response": "message sent successfully"}, status=200)
        else:
            return Response(response.json(), status=response.status_code)


class TemplatesListView(APIView):

    def get(self, request):
        if not api_data.api_access_token:
            return Response({"error": "invalid token"}, status=401)

        url = f"https://graph.facebook.com/{api_data.api_version}/{api_data.whatsapp_business_account_id}/message_templates"
        headers = {
            "Authorization": f"Bearer {api_data.api_access_token}",
            "Content-Type": "application/json"
        }

        response = requests.get(url,headers=headers)

        if response.status_code == 200:
            return Response({"response": "templates retrieved successfully"})
        elif response.status_code == 401:
            return Response({"error": "invalid token"})
        elif response.status_code == 403:
            return Response({"error": "permission denied"})
        else:
            return Response({"error": response.json()})
