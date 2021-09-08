FROM nginx:1.19.0-alpine

RUN mkdir /etc/certs

COPY ssl/slobite_com.crt /etc/certs/slobite_com.crt
COPY ssl/definesys.key /etc/certs/definesys.key

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d

# USER root

# RUN mkdir -p /vol/static
# RUN chmod 755 /vol/static

# USER nginx