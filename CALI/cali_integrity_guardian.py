#!/usr/bin/env python3
"""
CALI SKG Integrity Guardian
Critical security script to protect CALI's core intelligence from tampering
Run this script regularly to verify CALI SKG file integrity
"""

import json
import hashlib
import hmac
from pathlib import Path
from datetime import datetime
import sys
import logging

class CALIIntegrityGuardian:
    """Guardian class for CALI SKG file integrity"""

    def __init__(self):
        self.base_path = Path(__file__).resolve().parent.parent  # Go up one level from CALI/
        self.cali_file = self.base_path / "CALI" / "cali_skg.py"
        self.manifest_file = self.base_path / "CALI" / "cali_skg_security_manifest.json"
        self.backup_file = self.base_path / "CALI" / "cali_skg.FROZEN_BACKUP.py"

        # Setup logging
        self._setup_logging()

    def _setup_logging(self):
        """Setup security logging"""
        log_file = self.base_path / "CALI" / "logs" / "cali_integrity_guardian.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)

        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - CALI_GUARDIAN - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("CALI_GUARDIAN")

    def verify_integrity(self) -> bool:
        """Verify CALI SKG file integrity against frozen manifest"""

        self.logger.info("Starting CALI SKG integrity verification")

        # Check if all required files exist
        if not self.manifest_file.exists():
            self.logger.critical("Security manifest missing!")
            print("🚨 CRITICAL: Security manifest missing!")
            return False

        if not self.cali_file.exists():
            self.logger.critical("CALI SKG file missing!")
            print("🚨 CRITICAL: CALI SKG file missing!")
            return False

        if not self.backup_file.exists():
            self.logger.warning("Frozen backup missing - creating from manifest")
            self._restore_from_backup()

        # Load manifest
        try:
            manifest = json.loads(self.manifest_file.read_text())
        except Exception as e:
            self.logger.critical(f"Failed to load security manifest: {e}")
            print("🚨 CRITICAL: Security manifest corrupted!")
            return False

        # Read current CALI content
        try:
            current_content = self.cali_file.read_text()
        except Exception as e:
            self.logger.critical(f"Failed to read CALI SKG file: {e}")
            print("🚨 CRITICAL: Cannot read CALI SKG file!")
            return False

        # Verify all hash types
        current_hashes = {
            'sha256': hashlib.sha256(current_content.encode()).hexdigest(),
            'sha512': hashlib.sha512(current_content.encode()).hexdigest(),
            'blake2b': hashlib.blake2b(current_content.encode()).hexdigest()
        }

        stored_hashes = manifest['hashes']

        # Check integrity
        integrity_ok = (
            current_hashes['sha256'] == stored_hashes['sha256'] and
            current_hashes['sha512'] == stored_hashes['sha512'] and
            current_hashes['blake2b'] == stored_hashes['blake2b'] and
            len(current_content) == manifest['code_length']
        )

        if integrity_ok:
            self.logger.info("✅ CALI SKG integrity verified - file is authentic and unchanged")
            print("✅ CALI SKG integrity verified - file is authentic and unchanged")
            return True
        else:
            self.logger.critical("🚨 CRITICAL: CALI SKG integrity violation detected!")
            print("🚨 CRITICAL: CALI SKG integrity violation detected!")
            print(f"Expected SHA256: {stored_hashes['sha256'][:16]}...")
            print(f"Current SHA256:  {current_hashes['sha256'][:16]}...")

            # Attempt restoration
            self._attempt_restoration()
            return False

    def _restore_from_backup(self):
        """Restore CALI SKG from frozen backup if available"""
        if self.backup_file.exists():
            try:
                backup_content = self.backup_file.read_text()
                self.cali_file.write_text(backup_content)
                self.logger.warning("CALI SKG restored from frozen backup")
                print("⚠️ CALI SKG restored from frozen backup")
            except Exception as e:
                self.logger.critical(f"Failed to restore from backup: {e}")
                print("🚨 CRITICAL: Backup restoration failed!")

    def _attempt_restoration(self):
        """Attempt to restore integrity"""
        print("🔧 Attempting automatic restoration...")

        # Try backup first
        if self.backup_file.exists():
            self._restore_from_backup()
            # Re-verify
            if self.verify_integrity():
                print("✅ Restoration successful")
                return

        print("🚨 MANUAL INTERVENTION REQUIRED: Contact system administrator")
        print("🚨 CALI SKG integrity compromised - system may be unsafe")

    def create_additional_backups(self):
        """Create additional backup copies in secure locations"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create backups in different locations
        backup_locations = [
            self.base_path / "core4_vault" / "master_keys" / f"cali_skg_backup_{timestamp}.py",
            self.base_path / "CALI" / "backups" / f"cali_skg_backup_{timestamp}.py",
            self.base_path / "legacy_archive" / f"cali_skg_backup_{timestamp}.py"
        ]

        content = self.cali_file.read_text()

        for backup_path in backup_locations:
            try:
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                backup_path.write_text(content)
                self.logger.info(f"Additional backup created: {backup_path}")
            except Exception as e:
                self.logger.error(f"Failed to create backup at {backup_path}: {e}")

def main():
    """Main guardian function"""
    guardian = CALIIntegrityGuardian()

    print("🛡️ CALI Integrity Guardian Activated")
    print("=" * 50)

    # Verify integrity
    integrity_ok = guardian.verify_integrity()

    if integrity_ok:
        # Create additional backups for redundancy
        guardian.create_additional_backups()
        print("📦 Additional secure backups created")

    print("=" * 50)
    print("🛡️ Guardian cycle complete")

    return 0 if integrity_ok else 1

if __name__ == "__main__":
    sys.exit(main())