eve-path-formatter
==================

> Note: this package will be depecated afer [this pull request](https://github.com/pyeve/eve/pull/1201) merge and release


Module that supports resource urls ends with .xml and .json

Usage:

No application.py:

```python
import eve_path_formatter

eve_path_formatter.install() # before Eve instantiate
```

How it works
------------

Monkey patch on eve creating alternative routes adding extention xml and json
