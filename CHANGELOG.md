# Changelog

## [0.1.8](https://github.com/zenobi-us/beancount-importer-rules/compare/v0.1.7...v0.1.8) (2024-09-18)


### Bug Fixes

* date fields are treated as strings ([#44](https://github.com/zenobi-us/beancount-importer-rules/issues/44)) ([c814a21](https://github.com/zenobi-us/beancount-importer-rules/commit/c814a2157665ce5b20c999213d5c7ba07be8889c))
* importer now processes all files ([#34](https://github.com/zenobi-us/beancount-importer-rules/issues/34)) ([a0e5eae](https://github.com/zenobi-us/beancount-importer-rules/commit/a0e5eae9d53fd1b604faaf3285f45e5731059cdc))
* properly create and push annotated tag ([#43](https://github.com/zenobi-us/beancount-importer-rules/issues/43)) ([11ccf67](https://github.com/zenobi-us/beancount-importer-rules/commit/11ccf679a42f3a5f4030c40549ed42988a4c0e69))
* regex matcher now more obvious behaviour ([#38](https://github.com/zenobi-us/beancount-importer-rules/issues/38)) ([a19545e](https://github.com/zenobi-us/beancount-importer-rules/commit/a19545e37120005f70adf50ec85396b659fa7f84))
* stringify values before pattern matching ([#41](https://github.com/zenobi-us/beancount-importer-rules/issues/41)) ([9ecd0a7](https://github.com/zenobi-us/beancount-importer-rules/commit/9ecd0a75ae9a8e279dcb178e30369febc1ae0f8c))
* support matching between dates and better regex handling ([#39](https://github.com/zenobi-us/beancount-importer-rules/issues/39)) ([72e2c9a](https://github.com/zenobi-us/beancount-importer-rules/commit/72e2c9a1ee73157b50623152c3f64826efc529b9))


### Documentation

* point to correct website ([#40](https://github.com/zenobi-us/beancount-importer-rules/issues/40)) ([3838cad](https://github.com/zenobi-us/beancount-importer-rules/commit/3838cadadbe2a46aa61722da72189a6b40fa55dc))
* provide correct installation info ([#42](https://github.com/zenobi-us/beancount-importer-rules/issues/42)) ([4b397eb](https://github.com/zenobi-us/beancount-importer-rules/commit/4b397ebb8957aef9cd93330f0954e38633b67462))

## [0.1.7](https://github.com/zenobi-us/beancount-importer-rules/compare/v0.1.6...v0.1.7) (2024-09-10)


### Bug Fixes

* processing of workflow outputs ([#30](https://github.com/zenobi-us/beancount-importer-rules/issues/30)) ([98a88c6](https://github.com/zenobi-us/beancount-importer-rules/commit/98a88c623b57313c9a736a080f371c3799d14233))
* refactor processor to facilitate progress bar ([#22](https://github.com/zenobi-us/beancount-importer-rules/issues/22)) ([97bae20](https://github.com/zenobi-us/beancount-importer-rules/commit/97bae20905f4bc4bd787194eed349a4854771c1f))
* release data output ([#31](https://github.com/zenobi-us/beancount-importer-rules/issues/31)) ([4650882](https://github.com/zenobi-us/beancount-importer-rules/commit/465088239a76a731e35b4098be9407ca4c3400f1))
* use version computation ([#29](https://github.com/zenobi-us/beancount-importer-rules/issues/29)) ([4115987](https://github.com/zenobi-us/beancount-importer-rules/commit/4115987e095bfc26d4f07df8d60143d3e6b69dd5))

## [0.1.6](https://github.com/zenobi-us/beancount-importer-rules/compare/v0.1.5...v0.1.6) (2024-09-08)


### Bug Fixes

* regex matcher  ([#24](https://github.com/zenobi-us/beancount-importer-rules/issues/24)) ([05a95e2](https://github.com/zenobi-us/beancount-importer-rules/commit/05a95e2cffecb0801edecdbf2faf59f4e8496555))

## [0.1.5](https://github.com/zenobi-us/beancount-importer-rules/compare/v0.1.4...v0.1.5) (2024-09-08)


### Bug Fixes

* writing to a non existing directory no longer fails ([#21](https://github.com/zenobi-us/beancount-importer-rules/issues/21)) ([4150fdd](https://github.com/zenobi-us/beancount-importer-rules/commit/4150fdde60214c7266ce36a0595491cbfa3371f7))

## [0.1.4](https://github.com/zenobi-us/beancount-importer-rules/compare/v0.1.3...v0.1.4) (2024-09-07)


### Documentation

* deployment of docs annotated with git author ([#14](https://github.com/zenobi-us/beancount-importer-rules/issues/14)) ([4888a70](https://github.com/zenobi-us/beancount-importer-rules/commit/4888a7052a0f176e4604d4ad8ac994cdc7520620))
* documentation website now available ([#12](https://github.com/zenobi-us/beancount-importer-rules/issues/12)) ([df1157a](https://github.com/zenobi-us/beancount-importer-rules/commit/df1157abe6afe0f778073f412a9bdb5b21723193))
* just use git tags for dev versioning ([#20](https://github.com/zenobi-us/beancount-importer-rules/issues/20)) ([6625150](https://github.com/zenobi-us/beancount-importer-rules/commit/662515044b2ccebc2331c1c587f29aed36982a72))
* publish docs with calculated rc version ([#16](https://github.com/zenobi-us/beancount-importer-rules/issues/16)) ([ac8bda8](https://github.com/zenobi-us/beancount-importer-rules/commit/ac8bda80a3619cd1131e45108a923fa64fc31743))
* update docs ([#18](https://github.com/zenobi-us/beancount-importer-rules/issues/18)) ([e5aa488](https://github.com/zenobi-us/beancount-importer-rules/commit/e5aa488f5b57609c37362065f6ec119de1fd2658))
* use actor when commiting docs ([#15](https://github.com/zenobi-us/beancount-importer-rules/issues/15)) ([cd94e11](https://github.com/zenobi-us/beancount-importer-rules/commit/cd94e110257f4eb3ae495784430ceb7e605b5dc6))
* use correct syntax for version ([#19](https://github.com/zenobi-us/beancount-importer-rules/issues/19)) ([a6b6894](https://github.com/zenobi-us/beancount-importer-rules/commit/a6b68947b862ace6987a09d54546eb6854fd21a3))

## [0.1.3](https://github.com/zenobi-us/beancount-importer-rules/compare/v0.1.2...v0.1.3) (2024-09-03)


### Features

* matchers now support comparing dates ([#10](https://github.com/zenobi-us/beancount-importer-rules/issues/10)) ([85e6355](https://github.com/zenobi-us/beancount-importer-rules/commit/85e6355a1a4b134c5e1c12b006fc2689b523651c))

## [0.1.2](https://github.com/zenobi-us/beancount-importer-rules/compare/v0.1.1...v0.1.2) (2024-08-31)


### Bug Fixes

* Support including import rules from other files ([#8](https://github.com/zenobi-us/beancount-importer-rules/issues/8)) ([1df5c85](https://github.com/zenobi-us/beancount-importer-rules/commit/1df5c85e95ac884aaaaf46303a87360b1583f4ef))

## [0.1.1](https://github.com/zenobi-us/beancount-importer-rules/compare/v0.1.0...v0.1.1) (2024-08-30)


### Bug Fixes

* deployment environments ([#7](https://github.com/zenobi-us/beancount-importer-rules/issues/7)) ([a1de061](https://github.com/zenobi-us/beancount-importer-rules/commit/a1de061143140d09cf0e5b8ce01980f5fe18c936))
* publish-workflow ([#4](https://github.com/zenobi-us/beancount-importer-rules/issues/4)) ([e0d6b29](https://github.com/zenobi-us/beancount-importer-rules/commit/e0d6b293c8e0e90d9c8ae0f2a643deb81f5c1f63))

## 0.1.0 (2024-08-30)


### Features

* Extractors are now importable by the user. ([a6ab1e8](https://github.com/zenobi-us/beancount-importer-rules/commit/a6ab1e87b02277164edfb2bbd9587724587203fd))


### Bug Fixes

* unit tests now account for typesafety changes ([#2](https://github.com/zenobi-us/beancount-importer-rules/issues/2)) ([4413dd5](https://github.com/zenobi-us/beancount-importer-rules/commit/4413dd5c8c1cfc676dae36388bf7626f50ee64f3))


### Documentation

* docs now provide correct schema url ([bbf6c28](https://github.com/zenobi-us/beancount-importer-rules/commit/bbf6c28a1dbe58a3efd33d3a179d24ada5528785))
