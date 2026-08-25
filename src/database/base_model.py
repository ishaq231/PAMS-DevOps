"""
24030388 - Ishaq Modassir Mushtaq

Shared base class for all database model classes.
Provides dict-compatible and attribute-style access.
"""


class BaseModel:
    """Base class providing dict-compatible access and from_dict/to_dict."""

    @classmethod
    def from_dict(cls, data):
        """Create an instance from a dictionary.

        All key-value pairs are set as instance attributes, including
        extra columns from JOINs that are not in __init__.
        Returns None if *data* is None.
        """
        if data is None:
            return None
        instance = cls()
        for key, value in data.items():
            setattr(instance, key, value)
        return instance

    def to_dict(self):
        """Convert instance attributes to a plain dict (excludes private attrs)."""
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}

    # Dict-compatible access for backward compatibility with GUI code.

    def __getitem__(self, key):
        """Support row['field'] access."""
        try:
            return getattr(self, key)
        except AttributeError:
            raise KeyError(key)

    def __setitem__(self, key, value):
        """Support row['field'] = value."""
        setattr(self, key, value)

    def __contains__(self, key):
        """Support 'field' in row."""
        return hasattr(self, key)

    def get(self, key, default=None):
        """Support row.get('field', default)."""
        return getattr(self, key, default)

    def keys(self):
        return self.to_dict().keys()

    def values(self):
        return self.to_dict().values()

    def items(self):
        return self.to_dict().items()

    def __iter__(self):
        """Allow dict(instance) and iteration over keys."""
        return iter(self.to_dict())

    def __repr__(self):
        cls_name = self.__class__.__name__
        attrs = ', '.join(f'{k}={v!r}' for k, v in self.to_dict().items())
        return f'{cls_name}({attrs})'
