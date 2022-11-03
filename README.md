# Slobite - Opensource homemade food delivery app

Slobite is building tools to power home-based food delivery businesses. We take the engineering out of building a home-based food delivery business so chefs can focus on delivering tasty homemade meals. Our tool streamlines the administrative side of running a home-based food delivery business by creating an all-in-one solution for registrations,payment processing, menu management, order management, delivery, in-built legal guidance, and revenue reporting. The website is fitted for mobile, tablet and desktop (fully responsive).

 - **Technology stack**: Python, Django, Stripe, Stripe Connect, Amazon Email Service, NGINX, Docker, Bootstrap
- **Demo**: [Here](https://www.youtube.com/watch?v=xDySeqVuV18)



## Download

```bash
git clone https://github.com/sdas-engineer/slobite-rest-api.git
```

## Python & Django version

Python 2.7.16
Django 3.1.7

## Getting started

To start project, run:

```
docker-compose up
```


## Configuration

```python
#SOCIAL AUTH
SOCIAL_AUTH_FACEBOOK_KEY=
SOCIAL_AUTH_FACEBOOK_SECRET=

#STRIPE
STRIPE_PUBLISHABLE_KEY=
STRIPE_CONNECT_CLIENT_ID=
STRIPE_API_KEY=

#SENDGRID & TWILLIO
SENDGRID_API_KEY=
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_NUMBER=

#GOGLE MAPS
PLACES_MAPS_API_KEY=

#CHAT
TAWKTO_ID_SITE=
TAWKTO_IS_SECURE=
TAWKTO_API_KEY=

#AWS
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
AWS_STORAGE_REGION=

```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## Getting help
Contact: sdas.engineer@gmail.com

## License
[GNU General Public License v3.0](https://choosealicense.com/licenses/gpl-3.0/)

