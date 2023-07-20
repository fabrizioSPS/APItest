<> means the variable can be set at will.
[] means it is a file name that can be set at will.
Fastapi deployment with nginx
1) Make a virtual env:
	'python3 -m venv <name>'
	'source <name>/bin/activate'
2) Setup fastapi api, with all the files contained in a directory, in our case [app].
3) Make a [requirements.txt] file, with all the needed packages for the api and including fastapi, uvicorn and gunicorn.
4) If your virtual envirement is activated do: 'pip install -r [requirements.txt]'
5) Set the logging directory in [gunicorn_conf.py]
6) Adjust [fastapi_example.service]:
	- Change 'Description'
	- Change 'User'
	- Set 'WorkingDirectory'
	- adjust path to gunicorn, to the gunicorn_conf and the fastapi api.
7) sudo systemctl start [fastapi_example], name is the previous file without .service.
8) sudo systemctl enable [fastapi_example], this will automatically start the api on server restart.
9) sudo systemctl status [fastapi_example], should return Active: active (running) with additional info.
10) install nginx, 'sudo apt install nginx'
11) 'sudo systemctl start nginx', start service
12) 'sudo systemctl enable nginx', automatically start service
13) Make domainname file, as in the [fastapi_test] file. put in 
 /etc/nginx/sites-available/' directory.
	- Adjust <DomainName>, to the available domain name.
14) Add softlink, 'sudo ln -s /etc/nginx/sites-available/[fastapi_test] /etc/nginx/sites-enabled/'
15) sudo systemctl restart nginx

Now your api should be available trough the set domain, via http.
ps. <DomainName> can be set to the local IP, get it through 'curl ifconfig.me'.

Untested:
We can also obtain an SSL certificate
1) install certbot, 'sudo apt install certbot python3-certbot-nginx'.
2) obtain an SSL certificate, 'sudo certbot --nginx -d [fastapi_test]'.
3) Reload nginx, 'sudo sytemctl restart nginx'

Now your api should be available trough the set domain, via https.