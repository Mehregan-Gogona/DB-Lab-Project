

-- === RESTORING THE DATABASE === --
-- RESTORE FILELISTONLY 
-- FROM DISK = '/var/opt/mssql/backup/DormDuty.bak';

-- RESTORE DATABASE DormDuty
-- FROM DISK = '/var/opt/mssql/backup/DormDuty.bak'
-- WITH MOVE 'DormDuty' TO '/var/opt/mssql/data/DormDuty.mdf',
--      MOVE 'DormDuty_log' TO '/var/opt/mssql/data/DormDuty_log.ldf',
--      REPLACE;


-- SELECT TABLE_NAME
-- FROM INFORMATION_SCHEMA.TABLES
-- WHERE TABLE_TYPE = 'BASE TABLE';

