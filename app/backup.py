from __future__ import annotations

import os
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

from app import config
from app.database import init_db

BACKUP_PREFIX = "YNB_On_Muhasebe_Yedek"
DB_BACKUP_NAME = "on_muhasebe_mobile.db"
BELGE_BACKUP_DIR = "belgeler"


class BackupError(Exception):
    pass


def _now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _public_backup_dirs() -> list[Path]:
    candidates: list[Path] = []

    external = os.environ.get("EXTERNAL_STORAGE")
    if external:
        candidates.append(Path(external) / "Download" / BACKUP_PREFIX)

    candidates.append(Path("/sdcard/Download") / BACKUP_PREFIX)
    candidates.append(Path("/storage/emulated/0/Download") / BACKUP_PREFIX)

    # App-private fallback. Bu klasör her zaman yazılabilir ama normal dosya yöneticisinde
    # görünmeyebilir. Bu yüzden public Download önce denenir.
    candidates.append(config.DATA_DIR / "yedekler")

    # Aynı klasör tekrar etmesin.
    unique: list[Path] = []
    seen = set()
    for path in candidates:
        key = str(path)
        if key not in seen:
            unique.append(path)
            seen.add(key)
    return unique


def _choose_writable_backup_dir() -> Path:
    last_error = None
    for directory in _public_backup_dirs():
        try:
            directory.mkdir(parents=True, exist_ok=True)
            test_file = directory / ".write_test"
            test_file.write_text("ok", encoding="utf-8")
            test_file.unlink(missing_ok=True)
            return directory
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            continue
    raise BackupError(f"Yedek klasörü oluşturulamadı: {last_error}")


def create_backup() -> Path:
    """SQLite veritabanını ve belge klasörünü ZIP olarak yedekler."""
    init_db()
    if not config.DATABASE_PATH.exists():
        raise BackupError("Veritabanı dosyası bulunamadı.")

    backup_dir = _choose_writable_backup_dir()
    backup_path = backup_dir / f"{BACKUP_PREFIX}_{_now_stamp()}.zip"

    try:
        with zipfile.ZipFile(backup_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.write(config.DATABASE_PATH, DB_BACKUP_NAME)

            if config.BELGE_DIR.exists():
                for file_path in config.BELGE_DIR.rglob("*"):
                    if file_path.is_file():
                        arcname = Path(BELGE_BACKUP_DIR) / file_path.relative_to(config.BELGE_DIR)
                        zf.write(file_path, str(arcname))

            metadata = (
                "YNB Ön Muhasebe Mobil Yedek\n"
                f"Tarih: {datetime.now().isoformat(timespec='seconds')}\n"
                f"Veritabanı: {DB_BACKUP_NAME}\n"
                "İçerik: SQLite veritabanı + belge/fiş/fatura dosyaları\n"
            )
            zf.writestr("YEDEK_BILGI.txt", metadata)
    except Exception as exc:  # noqa: BLE001
        raise BackupError(f"Yedek alınamadı: {exc}") from exc

    return backup_path


def list_backup_files() -> list[Path]:
    backups: list[Path] = []
    for directory in _public_backup_dirs():
        try:
            if directory.exists():
                backups.extend(directory.glob(f"{BACKUP_PREFIX}_*.zip"))
        except Exception:
            continue
    return sorted(set(backups), key=lambda p: p.stat().st_mtime if p.exists() else 0, reverse=True)


def restore_backup(backup_path: str | Path) -> None:
    """Seçilen ZIP yedeğini uygulama verisine geri yükler."""
    backup = Path(str(backup_path).strip())
    if not backup.exists() or not backup.is_file():
        raise BackupError("Seçilen yedek dosyası bulunamadı.")

    try:
        with zipfile.ZipFile(backup, "r") as zf:
            names = set(zf.namelist())
            if DB_BACKUP_NAME not in names:
                raise BackupError("Bu dosya geçerli YNB yedeği değil. Veritabanı bulunamadı.")

            config.DATA_DIR.mkdir(parents=True, exist_ok=True)
            config.BELGE_DIR.mkdir(parents=True, exist_ok=True)

            # Mevcut veriyi güvenlik için geri yüklemeden önce ayrıca sakla.
            if config.DATABASE_PATH.exists():
                safety = config.DATA_DIR / f"onceki_veri_{_now_stamp()}.db"
                shutil.copy2(config.DATABASE_PATH, safety)

            db_temp = config.DATA_DIR / f"restore_{_now_stamp()}.db"
            with zf.open(DB_BACKUP_NAME) as source, open(db_temp, "wb") as target:
                shutil.copyfileobj(source, target)
            shutil.move(str(db_temp), str(config.DATABASE_PATH))

            # Belge klasörünü temizleyip yedekteki belgeleri geri koy.
            if config.BELGE_DIR.exists():
                shutil.rmtree(config.BELGE_DIR)
            config.BELGE_DIR.mkdir(parents=True, exist_ok=True)

            for name in zf.namelist():
                if not name.startswith(f"{BELGE_BACKUP_DIR}/") or name.endswith("/"):
                    continue
                relative = Path(name).relative_to(BELGE_BACKUP_DIR)
                target_path = config.BELGE_DIR / relative
                target_path.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(name) as source, open(target_path, "wb") as target:
                    shutil.copyfileobj(source, target)

        init_db()
    except BackupError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise BackupError(f"Yedek geri yüklenemedi: {exc}") from exc
