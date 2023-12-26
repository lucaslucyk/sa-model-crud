# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [0.4.0] 2023-10-24
### Removed
- Remove `id` field from `BaseModel`.

### Changed
- Rename `uid` to `id` in crud params.


## [0.3.2] 2023-10-24
### Removed
- Remove files used by `setuptools` to use `poetry` only.


## [0.3.1] 2023-10-24
### Changed
- Get requirements from files on `setup.py`.
- Change github action to build with `poetry`.


## [0.3.0] 2023-10-16
### Changed
- Rename rename internal save methods from `save` and `save_all` to `_save` and `_save_all`.
- Rename `skip` argument to `offset` on methods `list`, `filter` and `find`.
- Change init `model` argument to abstract property on `CRUDBase`.


## [0.1.0] 2023-10-15
### Changed
- Rename package name from `sa_model_crud` to `sa_modelcrud`.


## [0.0.1] 2023-10-12
### Added
- Initial version.