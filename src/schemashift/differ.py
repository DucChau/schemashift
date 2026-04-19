"""
Schema diff engine: computes field-level changes between two schema snapshots.
"""

from dataclasses import dataclass
from typing import Optional
from .detector import SchemaMap


@dataclass
class FieldChange:
    kind: str           # "added", "removed", "type_changed", "unchanged"
    field: str
    old_type: Optional[str] = None
    new_type: Optional[str] = None


@dataclass
class SchemaDiff:
    file: str
    added: list[FieldChange]
    removed: list[FieldChange]
    type_changed: list[FieldChange]
    unchanged: list[FieldChange]

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.type_changed)

    @property
    def total_fields(self) -> int:
        return len(self.added) + len(self.removed) + len(self.type_changed) + len(self.unchanged)


def diff_schemas(file: str, old: SchemaMap, new: SchemaMap) -> SchemaDiff:
    added = []
    removed = []
    type_changed = []
    unchanged = []

    all_keys = set(old) | set(new)
    for key in sorted(all_keys):
        old_t = old.get(key)
        new_t = new.get(key)

        if old_t is None and new_t is not None:
            added.append(FieldChange(kind="added", field=key, new_type=new_t))
        elif old_t is not None and new_t is None:
            removed.append(FieldChange(kind="removed", field=key, old_type=old_t))
        elif old_t != new_t:
            type_changed.append(FieldChange(kind="type_changed", field=key, old_type=old_t, new_type=new_t))
        else:
            unchanged.append(FieldChange(kind="unchanged", field=key, old_type=old_t, new_type=new_t))

    return SchemaDiff(
        file=file,
        added=added,
        removed=removed,
        type_changed=type_changed,
        unchanged=unchanged,
    )
