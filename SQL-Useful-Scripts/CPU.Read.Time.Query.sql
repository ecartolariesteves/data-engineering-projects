-- Top consultas por consumo de CPU, lecturas lógicas y duración
SELECT 
    TOP 50
    qs.total_worker_time / qs.execution_count AS AvgCPUTime,           -- Tiempo de CPU promedio
    qs.total_elapsed_time / qs.execution_count AS AvgElapsedTime,      -- Tiempo total promedio
    qs.execution_count,                                                -- Número de ejecuciones
    qs.total_logical_reads,                                            -- Lecturas lógicas
    qs.total_logical_reads / qs.execution_count AS AvgLogicalReads,    -- Lecturas lógicas promedio
    SUBSTRING(qt.text, qs.statement_start_offset / 2, 
        (CASE WHEN qs.statement_end_offset = -1 
              THEN LEN(CONVERT(NVARCHAR(MAX), qt.text)) * 2 
              ELSE qs.statement_end_offset END - qs.statement_start_offset) / 2) AS query_text,
    qt.dbid,
    DB_NAME(qt.dbid) AS database_name,
    qt.objectid
FROM 
    sys.dm_exec_query_stats qs
CROSS APPLY 
    sys.dm_exec_sql_text(qs.sql_handle) qt
ORDER BY 
    AvgCPUTime DESC;
