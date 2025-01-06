## Version -.-.-

Unreleased

---

## Version 0.6.1

Released 2025-01-06

- RedisStore.read now returns list in reverse (newest to the top)

---

## Version 0.6.0

Released 2025-01-06

- new store: RedisStore
- removed sqlalchemy dependency
- add exceptions for required packages not installed
- add optional installation extras

---

## Version 0.5.0

Released 2024-12-07

- add `host_url` to logging
- add `endpoint` to logging

---

## Version 0.4.1

Released 2024-12-07

- update TOC and minimal example on readme.

---

## Version 0.4.0

Released 2024-12-07

- add `read` method to all stores.
- update example app to include `read` method.

---

## Version 0.3.0

Released 2024-12-05

- bug fix to LogPolicy.
- bug fix to datetime conversion in SQLStore.
- LogPolicy now has 'on_endpoints', 'skip_endpoints', 'on_status_codes',
  'skip_status_codes' attrs to skip or scope.
- `log_only_on_exception` and `skip_log_on_exception` renamed to
  `only_on_exception` and `skip_on_exception`.

---

## Version 0.2.0

Released 2024-12-03

- change `LogPolicy` from default `False` attrs to default `True` attrs.
- remove attr setting from `LogPolicy` init.
- add methods `set_from_true` and `set_from_false` to `LogPolicy` for attr setting.
- move `log_only_on_exception` and `skip_log_on_exception` to `LogPolicy` init.
- update various docstrings.

---

## Version 0.1.1

Released 2024-12-03

- added docstrings for relevant classes and methods.
- rename `ORMStore` to `SQLORMStore`.
- rename `ORMTrafficMixin` to `SQLORMModelMixin`.

---

## Version 0.1.0

Released 2024-12-03

- Alpha release.
- Stores: `JSONStore`, `CSVStore`, `SQLStore`, `ORMStore`.

---

## Version 0.0.1

Released 2024-12-01

- Initial release.

---
