# Project Description

This project integrates various services, including the Auth service, content delivery service, and admin panel. The main focus is on ensuring the reliability of the Auth service, request tracing, and simplifying the user authentication process. Authentication through social services Yandex, VK, and Google is also available.

# Team
- [Stepan Dilman](https://github.com/sdilman)
- [Andrey Nikitsich](https://github.com/AndreyNikitsich)
- [Aleksey Gredyaev](https://github.com/agredyaev)

# How to Deploy
```bash
# Environment Setup
cp admin_panel/.env.example admin_panel/.env && \
cp authorization_service/.env.template authorization_service/.env && \
cp contants_service/.env.example contacts_service/.env

# Build and Run
docker-compose up --build
```
