# Database Backup & Restore Guide

## Current Database Status

The database currently contains **4 memos**:
1. Test Memo
2. Test from nginx
3. Updated: Memo Service Works
4. 10/6 (repository cleanup note)

## Backup Scripts

### Create a Backup

```bash
cd /home/rvnnt/sogangcomputerclub.org
./backup-database.sh
```

This will:
- Create a timestamped SQL backup file
- Compress it with gzip
- Keep only the last 30 backups (older ones are automatically deleted)

### Restore from Backup

```bash
cd /home/rvnnt/sogangcomputerclub.org
./restore-database.sh backups/memo_app_backup_YYYYMMDD_HHMMSS.sql.gz
```

Or with an uncompressed file:
```bash
./restore-database.sh backups/memo_app_backup_YYYYMMDD_HHMMSS.sql
```

This will:
- Show a confirmation prompt
- Restore the database from the specified backup file
- Replace all current data with backup data

## Automated Backups (Recommended)

### Set up a daily cron job:

```bash
# Edit crontab
crontab -e

# Add this line to run backup daily at 3 AM
0 3 * * * /home/rvnnt/sogangcomputerclub.org/backup-database.sh >> /home/rvnnt/sogangcomputerclub.org/backups/backup.log 2>&1
```

### Or set up hourly backups:

```bash
# Backup every hour
0 * * * * /home/rvnnt/sogangcomputerclub.org/backup-database.sh >> /home/rvnnt/sogangcomputerclub.org/backups/backup.log 2>&1
```

## Manual Database Operations

### List all memos:
```bash
docker exec sogangcomputercluborg-mariadb-1 mysql -umemo_user -pphoenix memo_app -e "SELECT * FROM memos;"
```

### Count memos:
```bash
docker exec sogangcomputercluborg-mariadb-1 mysql -umemo_user -pphoenix memo_app -e "SELECT COUNT(*) FROM memos;"
```

### Create manual backup:
```bash
docker exec sogangcomputercluborg-mariadb-1 mysqldump -umemo_user -pphoenix memo_app > backups/manual_backup_$(date +%Y%m%d_%H%M%S).sql
```

### Restore manual backup:
```bash
docker exec -i sogangcomputercluborg-mariadb-1 mysql -umemo_user -pphoenix memo_app < backups/manual_backup_YYYYMMDD_HHMMSS.sql
```

## Docker Volume Backup

The database is stored in a Docker volume: `sogangcomputercluborg_mariadb_data`

### Backup the entire volume:
```bash
docker run --rm -v sogangcomputercluborg_mariadb_data:/data -v /home/rvnnt/sogangcomputerclub.org/backups:/backup ubuntu tar czf /backup/mariadb_volume_$(date +%Y%m%d_%H%M%S).tar.gz -C /data .
```

### Restore volume:
```bash
docker run --rm -v sogangcomputercluborg_mariadb_data:/data -v /home/rvnnt/sogangcomputerclub.org/backups:/backup ubuntu tar xzf /backup/mariadb_volume_YYYYMMDD_HHMMSS.tar.gz -C /data
```

## Recovery Options

### If data was recently lost:

1. **Check existing backups** in this directory
2. **Check Docker volume** - data persists even if containers are recreated
3. **Check application logs** - may contain recent API requests with memo content

### If no backups exist:

Unfortunately, without backups, data cannot be recovered. The current 4 memos are all that remain in the database.

## Prevention

To prevent future data loss:

1. ✅ **Set up automated backups** (cron job recommended)
2. ✅ **Use Docker volumes** (already configured)
3. ✅ **Regular manual backups** before major changes
4. 📝 **Export important memos** to files
5. 🔄 **Version control** - commit exported data to git

## First Backup Created

- Date: 2025-10-06 02:51:25
- File: `memo_app_backup_20251006_025125.sql`
- Contains: 4 memos (all current data)
