FROM php:8.3-cli
WORKDIR /app
COPY --from=composer:latest /usr/bin/composer /usr/bin/composer
COPY composer.* ./
RUN composer install 2>/dev/null || true
COPY . .
CMD ["php", "-S", "0.0.0.0:8080", "-t", "public", "||", "php", "index.php"]
