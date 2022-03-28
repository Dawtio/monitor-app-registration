# Python App Registration Monitoring Prometheus

> This application will serve to monitor App Registration Secret Expiration and expose the informations to be retrieve by Prometheus.

## Introduction

In order to manage and be alerted of Secret expiration on our Application Registration via Grafana, we need to collect those informations for Azure AD and send them to Prometheus.

## Installation

You first need python3 and prometheus library

```sh
$ pip3 install -r requirements.txt
$ python3 main.py
```

Go to <http://localhost:8000/>

## Configuration

This app need 4 environments variables, the first three correspond to an application registration with graph permissions to read other app registration.

- AZURE_AD_APP_TENANT : `xxx`
- AZURE_AD_APP_ID     : `xxx`
- AZURE_AD_APP_SECRET : `xxx`

The last one correspond to the `object_id` of the app registration to monitor separate by a space ` `.

- AZURE_APP_TO_WATCH : `XXXXX-XXXXXX-... XXXXX-XXXXXX-...`

## Author

- Maxime Brunet <mbrunet@dawtio.cloud>
