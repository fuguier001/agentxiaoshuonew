# ==========================================
# 多 Agent 协作小说系统 - 数据备份管理
# ==========================================

import shutil
import zipfile
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import logging
import json

logger = logging.getLogger(__name__)


class BackupManager:
    """
    数据备份管理器
    支持自动备份、定期清理、手动恢复
    """
    
    def __init__(self, backup_dir: str = "./backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        self.metadata_file = self.backup_dir / "backup_metadata.json"
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict[str, Any]:
        """加载备份元数据"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "backups": [],
            "last_backup": None,
            "total_backups": 0
        }
    
    def _save_metadata(self):
        """保存备份元数据"""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)
    
    async def create_backup(
        self,
        source_paths: List[str],
        backup_name: Optional[str] = None,
        description: str = "",
        keep: bool = True
    ) -> Dict[str, Any]:
        """
        创建数据备份
        
        Args:
            source_paths: 要备份的源文件路径列表
            backup_name: 备份名称（默认使用时间戳）
            description: 备份描述
            keep: 是否保留（False 则为临时备份）
        
        Returns:
            备份信息字典
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = backup_name or f"backup_{timestamp}"
        backup_filename = f"{backup_name}.zip"
        backup_path = self.backup_dir / backup_filename
        
        try:
            logger.info(f"开始创建备份：{backup_name}")
            
            # 压缩备份
            shutil.make_archive(
                str(backup_path).replace('.zip', ''),
                'zip',
                source_paths[0] if len(source_paths) == 1 else self.backup_dir,
                # 注意：shutil.make_archive 只支持单个目录
                # 多目录备份需要特殊处理
            )
            
            # 如果是多目录，手动创建 zip
            if len(source_paths) > 1:
                await self._create_multi_dir_backup(backup_path, source_paths)
            
            # 记录元数据
            backup_info = {
                "name": backup_name,
                "filename": backup_filename,
                "path": str(backup_path),
                "created_at": datetime.now().isoformat(),
                "source_paths": source_paths,
                "description": description,
                "size_bytes": backup_path.stat().st_size,
                "keep": keep,
                "checksum": await self._calculate_checksum(backup_path)
            }
            
            if keep:
                self.metadata["backups"].append(backup_info)
                self.metadata["last_backup"] = backup_info["created_at"]
                self.metadata["total_backups"] += 1
                self._save_metadata()
            
            logger.info(f"备份创建成功：{backup_name} ({backup_info['size_bytes']} bytes)")
            
            return {
                "status": "success",
                "backup": backup_info
            }
        
        except Exception as e:
            logger.error(f"备份创建失败：{e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "message": "备份创建失败"
            }
    
    async def _create_multi_dir_backup(self, backup_path: Path, source_paths: List[str]):
        """创建多目录备份"""
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for source_path in source_paths:
                source = Path(source_path)
                if source.is_file():
                    zipf.write(source, source.name)
                elif source.is_dir():
                    for file_path in source.rglob("*"):
                        if file_path.is_file():
                            arcname = file_path.relative_to(source.parent)
                            zipf.write(file_path, arcname)
    
    async def _calculate_checksum(self, file_path: Path) -> str:
        """计算文件校验和"""
        import hashlib
        
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()[:16]
    
    def list_backups(self, include_temp: bool = False) -> List[Dict[str, Any]]:
        """
        列出所有备份
        
        Args:
            include_temp: 是否包含临时备份
        
        Returns:
            备份列表
        """
        backups = self.metadata["backups"]
        
        if not include_temp:
            backups = [b for b in backups if b.get("keep", True)]
        
        # 按创建时间倒序
        return sorted(backups, key=lambda x: x["created_at"], reverse=True)
    
    def get_backup(self, backup_name: str) -> Optional[Dict[str, Any]]:
        """获取备份详情"""
        for backup in self.metadata["backups"]:
            if backup["name"] == backup_name:
                return backup
        return None
    
    async def restore_backup(
        self,
        backup_name: str,
        restore_path: Optional[str] = None,
        overwrite: bool = False
    ) -> Dict[str, Any]:
        """
        恢复备份
        
        Args:
            backup_name: 备份名称
            restore_path: 恢复路径（默认恢复到原始位置）
            overwrite: 是否覆盖现有文件
        
        Returns:
            恢复结果
        """
        backup = self.get_backup(backup_name)
        
        if not backup:
            return {
                "status": "error",
                "error": "备份不存在"
            }
        
        backup_path = Path(backup["path"])
        if not backup_path.exists():
            return {
                "status": "error",
                "error": "备份文件不存在"
            }
        
        try:
            logger.info(f"开始恢复备份：{backup_name}")
            
            # 解压备份
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(restore_path or ".")
            
            logger.info(f"备份恢复成功：{backup_name}")
            
            return {
                "status": "success",
                "message": f"备份 {backup_name} 恢复成功",
                "restored_files": backup["source_paths"]
            }
        
        except Exception as e:
            logger.error(f"备份恢复失败：{e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "message": "备份恢复失败"
            }
    
    def delete_backup(self, backup_name: str) -> Dict[str, Any]:
        """
        删除备份
        
        Args:
            backup_name: 备份名称
        
        Returns:
            删除结果
        """
        backup = self.get_backup(backup_name)
        
        if not backup:
            return {
                "status": "error",
                "error": "备份不存在"
            }
        
        try:
            backup_path = Path(backup["path"])
            
            # 删除文件
            if backup_path.exists():
                backup_path.unlink()
            
            # 从元数据中移除
            self.metadata["backups"] = [
                b for b in self.metadata["backups"]
                if b["name"] != backup_name
            ]
            self.metadata["total_backups"] -= 1
            self._save_metadata()
            
            logger.info(f"备份删除成功：{backup_name}")
            
            return {
                "status": "success",
                "message": f"备份 {backup_name} 已删除"
            }
        
        except Exception as e:
            logger.error(f"备份删除失败：{e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "message": "备份删除失败"
            }
    
    def cleanup_old_backups(
        self,
        keep_count: int = 7,
        keep_days: int = 30
    ) -> Dict[str, Any]:
        """
        清理旧备份
        
        Args:
            keep_count: 保留最近 N 个备份
            keep_days: 保留最近 N 天的备份
        
        Returns:
            清理结果
        """
        logger.info(f"开始清理旧备份（保留最近 {keep_count} 个或 {keep_days} 天）")
        
        backups = self.metadata["backups"]
        deleted = []
        kept = []
        
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        
        # 按时间排序
        sorted_backups = sorted(
            backups,
            key=lambda x: x["created_at"],
            reverse=True
        )
        
        for i, backup in enumerate(sorted_backups):
            created_at = datetime.fromisoformat(backup["created_at"])
            
            # 判断是否保留
            should_keep = (
                i < keep_count or  # 前 N 个保留
                created_at > cutoff_date or  # 最近 N 天保留
                backup.get("keep", True) == False  # 临时备份不保留
            )
            
            if should_keep and i < keep_count:
                kept.append(backup["name"])
            else:
                # 删除备份
                result = self.delete_backup(backup["name"])
                if result["status"] == "success":
                    deleted.append(backup["name"])
        
        logger.info(f"清理完成：删除 {len(deleted)} 个备份，保留 {len(kept)} 个备份")
        
        return {
            "status": "success",
            "deleted": deleted,
            "kept": kept,
            "deleted_count": len(deleted),
            "kept_count": len(kept)
        }
    
    def get_backup_stats(self) -> Dict[str, Any]:
        """获取备份统计信息"""
        backups = self.metadata["backups"]
        
        if not backups:
            return {
                "total_backups": 0,
                "total_size_bytes": 0,
                "oldest_backup": None,
                "newest_backup": None
            }
        
        total_size = sum(b.get("size_bytes", 0) for b in backups)
        dates = [datetime.fromisoformat(b["created_at"]) for b in backups]
        
        return {
            "total_backups": len(backups),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "oldest_backup": min(dates).isoformat(),
            "newest_backup": max(dates).isoformat(),
            "average_size_mb": round((total_size / len(backups)) / (1024 * 1024), 2)
        }


# ========== 自动备份调度 ==========

class AutoBackupScheduler:
    """
    自动备份调度器
    支持定时备份、事件触发备份
    """
    
    def __init__(self, backup_manager: BackupManager):
        self.backup_manager = backup_manager
        self.scheduled = False
    
    def schedule_daily_backup(
        self,
        source_paths: List[str],
        hour: int = 2,
        minute: int = 0
    ):
        """
        调度每日自动备份
        
        Args:
            source_paths: 要备份的路径
            hour: 备份时间（小时）
            minute: 备份时间（分钟）
        """
        # 这里可以集成 Celery Beat 或 APScheduler
        logger.info(f"调度每日备份：{hour}:{minute:02d}")
        self.scheduled = True
    
    async def trigger_backup(
        self,
        source_paths: List[str],
        description: str = "自动备份"
    ) -> Dict[str, Any]:
        """
        触发备份
        
        Args:
            source_paths: 要备份的路径
            description: 备份描述
        
        Returns:
            备份结果
        """
        return await self.backup_manager.create_backup(
            source_paths=source_paths,
            description=description,
            keep=True
        )


# ========== 全局实例 ==========

_backup_manager: Optional[BackupManager] = None


def get_backup_manager() -> BackupManager:
    """获取备份管理器单例"""
    global _backup_manager
    if _backup_manager is None:
        _backup_manager = BackupManager()
    return _backup_manager
