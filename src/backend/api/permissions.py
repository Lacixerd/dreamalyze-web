from rest_framework.permissions import BasePermission
import hmac
import hashlib
    
class IsAuthenticatedClient(BasePermission):
    SECRET_KEY = b"super-secret-client-key" 

    def has_permission(self, request, view):
        client_signature = request.headers.get("X-Signature")
        if not client_signature:
            return False
        
        body = request.body or b""
        expected_signature = hmac.new(self.SECRET_KEY, body, hashlib.sha256).hexdigest()

        return hmac.compare_digest(client_signature, expected_signature)