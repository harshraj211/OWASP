FROM php:8.3-apache

WORKDIR /var/www/html

COPY src/ /var/www/html/
COPY docker/security.conf /etc/apache2/conf-enabled/security.conf
COPY docker/entrypoint.sh /usr/local/bin/docker-entrypoint.sh

RUN chmod +x /usr/local/bin/docker-entrypoint.sh \
    && mkdir -p /var/www/data \
    && chown -R www-data:www-data /var/www/html /var/www/data \
    && find /var/www/html -type d -exec chmod 755 {} \; \
    && find /var/www/html -type f -exec chmod 644 {} \;

EXPOSE 80

ENTRYPOINT ["docker-entrypoint.sh"]
