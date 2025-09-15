from rest_framework.permissions import BasePermission
import hmac
import hashlib

class IsOwnElement(BasePermission):
    def has_permission(self, request, view):
        pk = view.kwargs.get('pk')
        if pk is None:
            return False
        return str(request.user.id) == str(pk)
    
class IsAuthenticatedClient(BasePermission):
    """
    Sadece izinli client'in isteğine izin verir.
    Frontend veya mobil app secret ile imzalamalıdır.
    """

    SECRET_KEY = b"super-secret-client-key"  # frontend ve mobil app ile aynı olmalı

    def has_permission(self, request, view):
        client_signature = request.headers.get("X-Signature")
        if not client_signature:
            return False
        
        # Request body ve timestamp kullanılarak imza oluşturuluyor
        body = request.body or b""
        expected_signature = hmac.new(self.SECRET_KEY, body, hashlib.sha256).hexdigest()

        return hmac.compare_digest(client_signature, expected_signature)