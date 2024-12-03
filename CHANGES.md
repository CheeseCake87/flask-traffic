## Version 0.2.0

---

Released 2024-12-03

- change `LogPolicy` from default `False` attrs to default `True` attrs.
- remove attr setting from `LogPolicy` init.
- add methods `set_from_true` and `set_from_false` to `LogPolicy` for attr setting.
- move `log_only_on_exception` and `skip_log_on_exception` to `LogPolicy` init.
- update various docstrings.


## Version 0.1.1

---

Released 2024-12-03

- added docstrings for relevant classes and methods.
- rename `ORMStore` to `SQLORMStore`.
- rename `ORMTrafficMixin` to `SQLORMModelMixin`.


## Version 0.1.0

---

Released 2024-12-03

- Alpha release.
- Stores: `JSONStore`, `CSVStore`, `SQLStore`, `ORMStore`.


## Version 0.0.1

---

Released 2024-12-01

- Initial release.
