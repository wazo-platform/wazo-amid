# Changelog

## 26.02

* `POST` and `PATCH` request bodies to endpoints accepting JSON payload are systematically parsed as JSON, with or without a proper `Content-Type` header;
* `POST` and `PATCH` requests to endpoints accepting JSON payload and which are missing a body now return a `400` status response;
  previously those invalid requests could be treated as valid when Content-Type was missing and bodies were not parsed;

## 23.01

* Changed the following bus configuration keys in config file:

  * `exchange_name` value was changed to 'wazo-headers'
  * `exchange_type` key was removed
  * `exchange_durable` key was removed
  * `startup_connection_tries` key was removed
  * `startup_connection_delay` key was removed

## 20.05

* Deprecate SSL configuration
