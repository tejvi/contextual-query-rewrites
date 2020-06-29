# UI for contextual query rewrites

The UI reads in two queries and displays the rewritten query for each of the models used.

## Running the server
```
python3 server.py
```
This will be accessible on port 8000

## Configuring a reverse proxy

install and setup nginx 
```
sudo apt-get install nginx
sudo systemctl start nginx
```

disable default virtual host:
```
unlink /etc/nginx/sites-enabled/default
```

copy the contents of the reverse-proxy.conf in this repo to reverse-proxy.conf in ```/etc/nginx/sites-available```

Finally, run the following:
```
ln -s /etc/nginx/sites-available/reverse-proxy.conf /etc/nginx/sites-enabled/reverse-proxy.conf
```

Now, the flask application running on port 8000 will be available on port 80 (through the nginx reverse proxy)