# Dreamalyze Dokümantasyonu

Her database oluşturulduğunda:
```
python backend/manage.py makemigrations
python backend/manage.py migrate
python backend/manage.py createfreeplan
```

Linux sunucusuna yaz: 
```
0 0 * * * /path/to/venv/bin/python /path/to/project/manage.py renewcredits

0 0 * * * /path/to/venv/bin/python /path/to/project/manage.py expirycontrol
```

