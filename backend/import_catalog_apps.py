"""
Import applications from output/catalog_apps.json into the database.

Usage:
    python import_catalog_apps.py

This will:
- Ensure groups exist for each agrupador discovered in catalog_apps.json
- Create or update applications for each entry in catalog_apps.json
- Set bapp_id and availability_url so they can be used from the UI
"""

import json
from pathlib import Path
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Application, ApplicationStatus, Group


def get_or_create_group(db: Session, name: str) -> Group:
    """Return a group by name, creating it if needed."""
    name = (name or "").strip() or "Disponibilidad"

    group = db.query(Group).filter(Group.name == name).first()
    if group:
        return group

    group = Group(
        name=name,
        description="Agrupador importado desde el dashboard de disponibilidad",
    )
    db.add(group)
    db.commit()
    db.refresh(group)

    print(f"Created group: {group.name} (id={group.id})")
    return group


def load_catalog() -> List[Dict[str, Any]]:
    """Load catalog_apps.json from the output directory."""
    path = Path("output") / "catalog_apps.json"
    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {path}. Run the scraping command first "
            "to generate catalog_apps.json."
        )

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("catalog_apps.json must contain a JSON array")

    return data


def import_catalog() -> None:
    """Import all catalog applications into the database."""
    db = SessionLocal()

    try:
        catalog = load_catalog()

        created = 0
        updated = 0

        for item in catalog:
            name = (item.get("name") or "").strip()
            bapp_id = str(item.get("bapp_id")).strip() if item.get("bapp_id") else None
            href = (item.get("href") or "").strip()
            group_name = (item.get("group_name") or "").strip() or "Disponibilidad"
            gitlab_url = (item.get("gitlab_url") or "").strip() or None

            if not name:
                continue

            group = get_or_create_group(db, group_name)

            # Try to match by bapp_id first, then by name/group
            app = None
            if bapp_id:
                app = (
                    db.query(Application)
                    .filter(Application.bapp_id == bapp_id)
                    .first()
                )

            if not app:
                app = (
                    db.query(Application)
                    .filter(
                        Application.name == name,
                        Application.group_id == group.id,
                    )
                    .first()
                )

            if app:
                # Update existing application
                app.bapp_id = bapp_id or app.bapp_id
                app.availability_url = href or app.availability_url
                app.gitlab_project_url = gitlab_url or app.gitlab_project_url
                app.group_id = group.id
                if not app.description:
                    app.description = (
                        "Aplicación importada desde el dashboard de disponibilidad"
                    )
                if not app.status:
                    app.status = ApplicationStatus.ACTIVE
                updated += 1
            else:
                # Create new application
                app = Application(
                    name=name,
                    description=(
                        "Aplicación importada desde el dashboard de disponibilidad"
                    ),
                    status=ApplicationStatus.ACTIVE,
                    group_id=group.id,
                    bapp_id=bapp_id,
                    availability_url=href,
                    gitlab_project_url=gitlab_url,
                )
                db.add(app)
                created += 1

        db.commit()

        print("Import finished.")
        print(f"  Created applications: {created}")
        print(f"  Updated applications: {updated}")

    except Exception as exc:  # noqa: BLE001
        db.rollback()
        print(f"Import failed: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import_catalog()


