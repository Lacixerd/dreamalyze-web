
# Dreamalyze API Dokümantasyonu

Bu dokümantasyon, Dreamalyze web uygulamasının backend API'larını kullanmak için gereken tüm bilgileri içerir.

## Base URL
```
http://localhost:8000/api/
```

## Kimlik Doğrulama (Authentication)

API'nin çoğu endpoint'i JWT (JSON Web Token) tabanlı kimlik doğrulama kullanır. Token'ları şu şekilde kullanın:

```
Authorization: Bearer <access_token>
```

## API Endpoints

### 1. Kullanıcı Kaydı (User Registration)

**Endpoint:** `POST /api/user/register/`
**Kimlik Doğrulama:** Gerekli değil
**Açıklama:** Yeni kullanıcı kaydı yapar ve otomatik olarak Free plan atar, 1 kredi verir.

#### Request Format:
```json
{
    "username": "kullanici_adi",
    "email": "kullanici@email.com",
    "password": "güvenli_şifre"
}
```

#### Response Format:
**Başarılı (201 Created):**
```json
{
    "id": "uuid",
    "username": "kullanici_adi",
    "email": "kullanici@email.com",
    "is_active": true,
    "image": null,
    "google_id": null,
    "last_chat_at": null,
    "user_created_at": "2025-09-20T10:00:00Z",
    "user_updated_at": "2025-09-20T10:00:00Z",
    "user_deleted_at": null,
    "credits": {
        "total_amount": 1,
        "amount": 1
    }
}
```

**Hata (400 Bad Request):**
```json
{
    "username": ["Bu alan gereklidir."],
    "email": ["Geçerli bir email adresi girin."]
}
```

---

### 2. Kullanıcı Girişi (User Login)

**Endpoint:** `POST /api/user/login/`
**Kimlik Doğrulama:** Gerekli değil
**Açıklama:** Email ve şifre ile giriş yapar, JWT token'ları döndürür.

#### Request Format:
```json
{
    "email": "kullanici@email.com",
    "password": "şifre"
}
```

#### Response Format:
**Başarılı (200 OK):**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "id": "uuid",
        "username": "kullanici_adi",
        "email": "kullanici@email.com",
        "is_active": true,
        "image": null,
        "google_id": null,
        "last_chat_at": null,
        "user_created_at": "2025-09-20T10:00:00Z",
        "user_updated_at": "2025-09-20T10:00:00Z",
        "user_deleted_at": null,
        "credits": {
            "total_amount": 1,
            "amount": 1
        }
    }
}
```

**Hata (400 Bad Request):**
```json
{
    "error": "Email and password are required"
}
```

**Hata (401 Unauthorized):**
```json
{
    "error": "Password or email is incorrect"
}
```

---

### 3. Google ile Giriş (Google Login)

**Endpoint:** `POST /api/user/google-login/`
**Kimlik Doğrulama:** Gerekli değil
**Açıklama:** Google ID token ile giriş yapar. Kullanıcı yoksa otomatik oluşturur.

#### Request Format:
```json
{
    "token": "google_id_token_buraya"
}
```

#### Response Format:
**Başarılı (200 OK):**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "id": "uuid",
        "username": "kullanici_adi",
        "email": "kullanici@email.com",
        "is_active": true,
        "image": "https://lh3.googleusercontent.com/...",
        "google_id": "google_user_id",
        "last_chat_at": null,
        "user_created_at": "2025-09-20T10:00:00Z",
        "user_updated_at": "2025-09-20T10:00:00Z",
        "user_deleted_at": null,
        "credits": {
            "total_amount": 1,
            "amount": 1
        }
    }
}
```

**Hata (400 Bad Request):**
```json
{
    "error": "Token is required"
}
```

**Hata (400 Bad Request - Geçersiz Token):**
```json
{
    "error": "Invalid Google token"
}
```

---

### 4. Google Token Yenileme (Google Token Refresh)

**Endpoint:** `POST /api/user/google-token-refresh/`
**Kimlik Doğrulama:** Gerekli değil
**Açıklama:** Google ID token ile mevcut kullanıcı için yeni JWT token'ları oluşturur.

#### Request Format:
```json
{
    "token": "google_id_token_buraya"
}
```

#### Response Format:
**Başarılı (200 OK):**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "id": "uuid",
        "username": "kullanici_adi",
        "email": "kullanici@email.com",
        // ... diğer kullanıcı bilgileri
    }
}
```

**Hata (404 Not Found):**
```json
{
    "error": "User not found"
}
```

---

### 5. JWT Token İşlemleri

#### Token Alma (Token Obtain Pair)
**Endpoint:** `POST /api/user/token/`
**Kimlik Doğrulama:** Gerekli değil
**Açıklama:** Email ve şifre ile JWT token'ları alır.

#### Token Yenileme (Token Refresh)
**Endpoint:** `POST /api/user/token/refresh/`
**Kimlik Doğrulama:** Gerekli değil
**Açıklama:** Refresh token ile yeni access token alır.

#### Request Format:
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Token Doğrulama (Token Verify)
**Endpoint:** `POST /api/user/token/verify/`
**Kimlik Doğrulama:** Gerekli değil
**Açıklama:** Verilen token'ın geçerliliğini kontrol eder.

#### Request Format:
```json
{
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

### 6. Kullanıcı Profili (User Profile)

**Endpoint:** `GET /api/user/me/`
**Kimlik Doğrulama:** Gerekli (Bearer Token)
**Açıklama:** Giriş yapmış kullanıcının profil bilgilerini getirir.

#### Response Format:
**Başarılı (200 OK):**
```json
{
    "id": "uuid",
    "username": "kullanici_adi",
    "email": "kullanici@email.com",
    "is_active": true,
    "image": "https://lh3.googleusercontent.com/...",
    "google_id": "google_user_id",
    "last_chat_at": "2025-09-20T15:30:00Z",
    "user_created_at": "2025-09-20T10:00:00Z",
    "user_updated_at": "2025-09-20T10:00:00Z",
    "user_deleted_at": null,
    "credits": {
        "total_amount": 5,
        "amount": 3
    }
}
```

---

### 7. Kullanıcı Rüyaları (User Dreams)

#### Rüya Listesi Getirme
**Endpoint:** `GET /api/user/me/dreams/`
**Kimlik Doğrulama:** Gerekli (Bearer Token)
**Açıklama:** Kullanıcının tüm rüyalarını en yeniden eskiye sıralar.

#### Response Format:
**Başarılı (200 OK):**
```json
[
    {
        "id": "uuid",
        "author": "kullanici@email.com",
        "title": "Rüya Başlığı",
        "description": "Rüya açıklaması ilk 45 karakter...",
        "created_at": "2025-09-20T14:00:00Z",
        "updated_at": "2025-09-20T14:00:00Z",
        "deleted_at": null,
        "is_active": true
    },
    {
        "id": "uuid2",
        "author": "kullanici@email.com",
        "title": "Başka Rüya",
        "description": "Başka rüya açıklaması...",
        "created_at": "2025-09-19T10:00:00Z",
        "updated_at": "2025-09-19T10:00:00Z",
        "deleted_at": null,
        "is_active": true
    }
]
```

#### Yeni Rüya Oluşturma
**Endpoint:** `POST /api/user/me/dreams/`
**Kimlik Doğrulama:** Gerekli (Bearer Token)
**Açıklama:** Yeni rüya oluşturur. Kullanıcının kredi bakiyesi kontrol edilir.

#### Request Format:
```json
{
    "title": "Rüya Başlığı (Opsiyonel)",
    "description": "Rüya açıklaması (Opsiyonel)"
}
```

#### Response Format:
**Başarılı (201 Created):**
```json
{
    "id": "uuid",
    "author": "kullanici@email.com",
    "title": "Rüya Başlığı",
    "description": null,
    "created_at": "2025-09-20T16:00:00Z",
    "updated_at": "2025-09-20T16:00:00Z",
    "deleted_at": null,
    "is_active": true
}
```

**Hata (Yetersiz Kredi):**
```json
{
    "error": "Your credit is insufficient"
}
```

**Hata (400 Bad Request):**
```json
{
    "title": ["Bu alan boş olamaz."]
}
```

---

### 8. Rüya Mesajları (Dream Messages)

**Endpoint:** `GET /api/user/me/dream/<uuid:id>/messages/`
**Kimlik Doğrulama:** Gerekli (Bearer Token)
**Açıklama:** Belirtilen rüyaya ait tüm mesajları kronolojik sırayla getirir.

#### Response Format:
**Başarılı (200 OK):**
```json
[
    {
        "id": 1,
        "dream": "rüya_uuid",
        "role": "user",
        "message": "Dün gece çok garip bir rüya gördüm...",
        "created_at": "2025-09-20T14:00:00Z"
    },
    {
        "id": 2,
        "dream": "rüya_uuid",
        "role": "analyst",
        "message": "Bu rüya çok ilginç! Size şu analizi sunabilirim...",
        "created_at": "2025-09-20T14:01:00Z"
    },
    {
        "id": 3,
        "dream": "rüya_uuid",
        "role": "system",
        "message": "Analiz tamamlandı.",
        "created_at": "2025-09-20T14:02:00Z"
    }
]
```

**Hata (404 Not Found):**
```json
{
    "detail": "Sayfa bulunamadı."
}
```

---

## Hata Kodları

### HTTP Status Kodları
- **200 OK:** İstek başarılı
- **201 Created:** Kaynak başarıyla oluşturuldu
- **400 Bad Request:** Geçersiz istek formatı
- **401 Unauthorized:** Kimlik doğrulama gerekli veya başarısız
- **403 Forbidden:** Erişim izni yok
- **404 Not Found:** Kaynak bulunamadı
- **500 Internal Server Error:** Sunucu hatası

### Yaygın Hata Mesajları
```json
{
    "error": "Email and password are required"
}
```

```json
{
    "error": "Password or email is incorrect"
}
```

```json
{
    "error": "Your credit is insufficient"
}
```

```json
{
    "detail": "Authentication credentials were not provided."
}
```

```json
{
    "detail": "Given token not valid for any token type"
}
```

---

## Kullanım Örnekleri

### JavaScript ile Kullanım

#### 1. Kullanıcı Kaydı
```javascript
const registerUser = async (userData) => {
    const response = await fetch('http://localhost:8000/api/user/register/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData)
    });
    
    const data = await response.json();
    
    if (response.ok) {
        console.log('Kullanıcı başarıyla kaydedildi:', data);
    } else {
        console.error('Kayıt hatası:', data);
    }
};

// Kullanım
registerUser({
    username: "yeni_kullanici",
    email: "yeni@email.com",
    password: "güvenli_şifre123"
});
```

#### 2. Giriş Yapma ve Token Saklama
```javascript
const loginUser = async (credentials) => {
    const response = await fetch('http://localhost:8000/api/user/login/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials)
    });
    
    const data = await response.json();
    
    if (response.ok) {
        // Token'ları sakla
        localStorage.setItem('access_token', data.access);
        localStorage.setItem('refresh_token', data.refresh);
        localStorage.setItem('user', JSON.stringify(data.user));
        
        console.log('Giriş başarılı:', data.user);
    } else {
        console.error('Giriş hatası:', data);
    }
};
```

#### 3. Kimlik Doğrulamalı İstek Yapma
```javascript
const fetchUserProfile = async () => {
    const token = localStorage.getItem('access_token');
    
    const response = await fetch('http://localhost:8000/api/user/me/', {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        }
    });
    
    const data = await response.json();
    
    if (response.ok) {
        console.log('Kullanıcı profili:', data);
    } else {
        console.error('Profil getirme hatası:', data);
    }
};
```

#### 4. Rüya Listesi Getirme
```javascript
const fetchUserDreams = async () => {
    const token = localStorage.getItem('access_token');
    
    const response = await fetch('http://localhost:8000/api/user/me/dreams/', {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        }
    });
    
    const dreams = await response.json();
    
    if (response.ok) {
        console.log('Kullanıcı rüyaları:', dreams);
        return dreams;
    } else {
        console.error('Rüya listesi hatası:', dreams);
    }
};
```

#### 5. Yeni Rüya Oluşturma
```javascript
const createDream = async (dreamData) => {
    const token = localStorage.getItem('access_token');
    
    const response = await fetch('http://localhost:8000/api/user/me/dreams/', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(dreamData)
    });
    
    const data = await response.json();
    
    if (response.ok) {
        console.log('Rüya oluşturuldu:', data);
    } else {
        console.error('Rüya oluşturma hatası:', data);
    }
};

// Kullanım
createDream({
    title: "Garip Rüyam",
    description: "Dün gece çok garip bir rüya gördüm..."
});
```

#### 6. Rüya Mesajlarını Getirme
```javascript
const fetchDreamMessages = async (dreamId) => {
    const token = localStorage.getItem('access_token');
    
    const response = await fetch(`http://localhost:8000/api/user/me/dream/${dreamId}/messages/`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        }
    });
    
    const messages = await response.json();
    
    if (response.ok) {
        console.log('Rüya mesajları:', messages);
        return messages;
    } else {
        console.error('Mesaj getirme hatası:', messages);
    }
};
```

---

## Önemli Notlar

1. **Kredi Sistemi:** Yeni rüya oluştururken kullanıcının kredi bakiyesi kontrol edilir. Kredi yetersizse işlem gerçekleşmez.

2. **Token Yönetimi:** Access token'lar belirli bir süre sonra geçersiz olur. Refresh token ile yenileme yapmanız gerekir.

3. **Cihaz Takibi:** Her giriş işleminde kullanıcının IP adresi kaydedilir ve cihaz takibi yapılır.

4. **Google Entegrasyonu:** Google ile giriş yaparken, kullanıcı mevcut değilse otomatik olarak oluşturulur ve Free plan atanır.

5. **Rüya Açıklaması:** Rüya açıklaması otomatik olarak ilk mesajın ilk 45 karakterinden oluşturulur.

6. **Mesaj Rolleri:** Mesajlar 3 farklı rol ile kaydedilir:
   - `user`: Kullanıcı mesajları
   - `analyst`: AI analist cevapları  
   - `system`: Sistem mesajları

Bu dokümantasyon, mevcut API yapısına göre hazırlanmıştır. API'de yapılacak değişiklikler bu dokümantasyona yansıtılmalıdır.
