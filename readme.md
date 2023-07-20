# FastAPI Deployment with Nginx

This guide will walk you through the steps to deploy a FastAPI application with Nginx as a reverse proxy and obtain an SSL certificate for secure HTTPS access.

## Prerequisites

- Python 3

## Steps

1. **Create a Virtual Environment**

	`python3 -m venv <name>`
   
	`source <name>/bin/activate`

2. **Setup FastAPI Application**

	Place all the FastAPI application files in a directory, let's call it [app].

3. **Create Requirements File**

	Create a 'requirements.txt' file with all the required packages for the FastAPI application, including 'fastapi', 'uvicorn', and 'gunicorn'.

4. **Install Required Packages**

	If your virtual environment is activated, install the required packages:
   
	`pip install -r requirements.txt`

5. **Set Logging Directory in 'gunicorn_conf.py'**

	Update the 'gunicorn_conf.py' file to set the desired logging directory.

6. **Make Service, let's call it [fastapi_example.service]**

   - Change 'Description'
   - Change 'User'
   - Set 'WorkingDirectory'
   - Adjust the path to 'gunicorn', 'gunicorn_conf.py', and the FastAPI application.

7. **Start and Enable the Service**

	`sudo systemctl start [fastapi_example]`
   
	`sudo systemctl enable [fastapi_example]`

	This will start the API on server restart.

8. **Check Service Status**

	`sudo systemctl status [fastapi_example]`

	The output should show 'Active: active (running)' with additional information.

9. **Install Nginx**

	`sudo apt install nginx`

10. **Start and Enable Nginx**

	'sudo systemctl start nginx'
	
	'sudo systemctl enable nginx'

11. **Configure Nginx**

	Create a configuration file for your domain (e.g., <DomainName\>). Place it in the '/etc/nginx/sites-available/' directory.
	
	Replace <DomainName\> with the actual domain name you want to use.

12. **Create a Symbolic Link**

	Create a symbolic link to enable the Nginx configuration:
	
	`sudo ln -s /etc/nginx/sites-available/<DomainName> /etc/nginx/sites-enabled/`

13. **Restart Nginx**

	`sudo systemctl restart nginx`
	
	Now your API should be available through the set domain via HTTP.
	
	Note: If you want to access the API through a local IP, find it using 'curl ifconfig.me'.

## Untested: Obtaining an SSL Certificate

If you want to enable HTTPS access with an SSL certificate, follow these additional steps:

1. **Install Certbot**

	`sudo apt install certbot python3-certbot-nginx`

2. **Obtain SSL Certificate**

	Run Certbot to obtain an SSL certificate for your domain:
   
	`sudo certbot --nginx -d <DomainName>`

3. **Reload Nginx**

	`sudo systemctl restart nginx`
   
	Now your API should be available through the set domain via HTTPS.


Please note that the SSL certificate part is untested, so ensure to thoroughly test your setup to ensure everything is working as expected.
