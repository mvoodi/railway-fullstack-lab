FROM nginx:alpine
COPY index.html /usr/share/nginx/html/index.html

CMD sed -i -e 's/80/'"$PORT"'/g' /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'